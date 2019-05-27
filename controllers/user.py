# -*- coding: utf-8 -*-

import json

import odoo
from odoo import http
from odoo.http import request
from odoo import fields

from .. import defs
from .base import BaseController
from .tools import get_wx_session_info, get_wx_user_info, get_decrypt_info

import logging

_logger = logging.getLogger(__name__)


class WxappUser(http.Controller, BaseController):


    @http.route('/<string:sub_domain>/user/check-token', auth='public', methods=['GET'])
    def check_token(self, sub_domain, token=None, **kwargs):
        try:
            ret, entry = self._check_domain(sub_domain)
            if ret:return ret

            if not token:
                return self.res_err(300)

            access_token = request.env(user=1)['wxapp.access_token'].search([
                ('token', '=', token),
            ])

            if not access_token:
                return self.res_err(901)

            return self.res_ok()

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e.name)

    @http.route('/<string:sub_domain>/user/wxapp/login', auth='public', methods=['GET', 'POST'],csrf=False)
    def login(self, sub_domain, code=None, **kwargs):
        try:
            ret, entry = self._check_domain(sub_domain)
            if ret:return ret

            config = request.env['wxapp.config'].sudo()

            if not code:
                return self.res_err(300)

            app_id = config.get_config('app_id', sub_domain)
            secret = config.get_config('secret', sub_domain)

            if not app_id or not secret:
                return self.res_err(404)

            session_info = get_wx_session_info(app_id, secret, code)
            if session_info.get('errcode'):
                return self.res_err(-1, session_info.get('errmsg'))

            open_id = session_info['openid']
            wechat_user = request.env(user=1)['wxapp.user'].search([
                ('open_id', '=', open_id),
                #('create_uid', '=', user.id)
            ])
            if not wechat_user:
                return self.res_err(10000)

            wechat_user.write({'last_login': fields.Datetime.now(), 'ip': request.httprequest.remote_addr})
            access_token = request.env(user=1)['wxapp.access_token'].search([
                ('open_id', '=', open_id),
                #('create_uid', '=', user.id)
            ])

            if not access_token:
                session_key = session_info['session_key']
                access_token = request.env(user=1)['wxapp.access_token'].create({
                    'open_id': open_id,
                    'session_key': session_key,
                    'sub_domain': sub_domain,
                })
            else:
                access_token.write({'session_key': session_info['session_key']})

            data = {
                'token': access_token.token,
                'uid': wechat_user.id,
                'info': self.get_user_info(wechat_user)
            }
            return self.res_ok(data)

        except AttributeError:
            return self.res_err(404)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e.name)


    @http.route('/<string:sub_domain>/user/wxapp/register/complex', auth='public', methods=['GET', 'POST'], csrf=False)
    def register(self, sub_domain, code=None, encryptedData=None, iv=None, **kwargs):
        '''
        用户注册
        '''
        try:
            ret, entry = self._check_domain(sub_domain)
            if ret:return ret

            config = request.env['wxapp.config'].sudo()

            encrypted_data = encryptedData
            if not code or not encrypted_data or not iv:
                return self.res_err(300)

            app_id = config.get_config('app_id', sub_domain)
            secret = config.get_config('secret', sub_domain)

            if not app_id or not secret:
                return self.res_err(404)

            session_key, user_info = get_wx_user_info(app_id, secret, code, encrypted_data, iv)

            user_id = None
            if hasattr(request, 'user_id'):
                user_id = request.user_id

            vals = {
                'name': user_info['nickName'],
                'nickname': user_info['nickName'],
                'open_id': user_info['openId'],
                'gender': user_info['gender'],
                'language': user_info['language'],
                'country': user_info['country'],
                'province': user_info['province'],
                'city': user_info['city'],
                'avatar_url': user_info['avatarUrl'],
                'register_ip': request.httprequest.remote_addr,
                'user_id': user_id,
                'partner_id': user_id and request.env['res.users'].sudo().browse(user_id).partner_id.id or None,
            }
            if user_id:
                vals['user_id'] = user_id
                vals['partner_id'] = request.env['res.users'].sudo().browse(user_id).partner_id.id
                vals.pop('name')
            request.env(user=1)['wxapp.user'].create(vals)
            return self.res_ok()

        except AttributeError:
            return self.res_err(404)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e.name)

    def get_user_info(self, wechat_user):
        data = {
            'base':{
                'mobile': wechat_user.phone,
                'userid': '',
            },
        }
        return data

    @http.route('/<string:sub_domain>/user/detail', auth='public', methods=['GET'])
    def detail(self, sub_domain, token=None):
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res

            data = self.get_user_info(wechat_user)
            return self.res_ok(data)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e.name)

    @http.route('/<string:sub_domain>/user/wxapp/bindMobile', auth='public', methods=['GET', 'POST'], csrf=False)
    def bind_mobile(self, sub_domain, token=None, encryptedData=None, iv=None, **kwargs):
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res

            config = request.env['wxapp.config'].sudo()

            encrypted_data = encryptedData
            if not token or not encrypted_data or not iv:
                return self.res_err(300)

            app_id = config.get_config('app_id', sub_domain)
            secret = config.get_config('secret', sub_domain)

            if not app_id or not secret:
                return self.res_err(404)

            access_token = request.env(user=1)['wxapp.access_token'].search([
                ('token', '=', token),
            ])
            if not access_token:
                return self.res_err(901)
            session_key = access_token[0].session_key

            _logger.info('>>> decrypt: %s %s %s %s', app_id, session_key, encrypted_data, iv)
            user_info = get_decrypt_info(app_id, session_key, encrypted_data, iv)
            _logger.info('>>> bind_mobile: %s', user_info)
            wechat_user.write({'phone': user_info.get('phoneNumber')})

            return self.res_ok()

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e.name)

