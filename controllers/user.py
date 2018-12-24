# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request
from odoo import fields

from .. import defs
from .base import BaseController
from .tools import get_wx_session_info, get_wx_user_info

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

    @http.route('/<string:sub_domain>/user/wxapp/login', auth='public', methods=['GET'])
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

            data = {
                'token': access_token.token,
                'uid': wechat_user.id
            }
            return self.res_ok(data)

        except AttributeError:
            return self.res_err(404)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e.name)


    @http.route('/<string:sub_domain>/user/wxapp/register/complex', auth='public', methods=['GET'])
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
            request.env(user=1)['wxapp.user'].create({
                'name': user_info['nickName'],
                'open_id': user_info['openId'],
                'gender': user_info['gender'],
                'language': user_info['language'],
                'country': user_info['country'],
                'province': user_info['province'],
                'city': user_info['city'],
                'avatar_url': user_info['avatarUrl'],
                'register_ip': request.httprequest.remote_addr,
            })
            return self.res_ok()

        except AttributeError:
            return self.res_err(404)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e.name)
