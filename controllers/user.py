# -*- coding: utf-8 -*-

import json

import odoo
from odoo import http
from odoo.http import request
from odoo import fields

from .. import defs
from .base import BaseController, jsonapi
from .tools import get_wx_session_info, get_wx_user_info, get_decrypt_info

import logging

_logger = logging.getLogger(__name__)


class WxappUser(http.Controller, BaseController):

    def after_check(self, wechat_user, token, data):
        pass

    def after_login(self, wechat_user, token, data):
        pass

    @http.route('/wxa/<string:sub_domain>/user/check-token', auth='public', methods=['GET'])
    def check_token(self, sub_domain, token=None, **kwargs):
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return self.res_err(609)

            if wechat_user.check_account_ok():
                data = self.get_user_info(wechat_user)
                self.after_check(wechat_user, token, data)
                return self.res_ok(data)
            else:
                return self.res_err(608, u'账号不可用')
        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))

    @http.route(['/wxa/<string:sub_domain>/user/wxapp/login', '/wxa/<string:sub_domain>/user/wxapp/authorize'], auth='public', methods=['GET', 'POST'],csrf=False)
    def login(self, sub_domain, code=None, **kwargs):
        try:
            ret, entry = self._check_domain(sub_domain)
            if ret:return ret

            if not code:
                return self.res_err(300)

            app_id = entry.get_config('app_id')
            secret = entry.get_config('secret')

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
                return self.res_err(10000, {'session_info': session_info})

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
            self.after_login(wechat_user, access_token.token, data)
            return self.res_ok(data)

        except AttributeError:
            import traceback;traceback.print_exc()
            return self.res_err(404)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))


    @http.route('/wxa/<string:sub_domain>/user/wxapp/register/complex', auth='public', methods=['GET', 'POST'], csrf=False)
    def register(self, sub_domain, code=None, encryptedData=None, iv=None, **kwargs):
        '''
        用户注册
        '''
        try:
            ret, entry = self._check_domain(sub_domain)
            if ret:return ret

            session_info = kwargs.get('session_info')
            if session_info:
                session_info = json.loads(session_info)
                user_info = {
                    'nickName': '微信用户',
                    'openId': session_info.get('openid'),
                    'unionId': session_info.get('unionid')
                }
            else:
                encrypted_data = encryptedData
                if not code or not encrypted_data or not iv:
                    return self.res_err(300)

                app_id = entry.get_config('app_id')
                secret = entry.get_config('secret')

                if not app_id or not secret:
                    return self.res_err(404)

                session_key, user_info = get_wx_user_info(app_id, secret, code, encrypted_data, iv)
                if kwargs.get('userInfo'):
                    user_info.update(json.loads(kwargs.get('userInfo')))

            user_id = None
            if hasattr(request, 'user_id'):
                user_id = request.user_id

            vals = {
                'name': user_info['nickName'],
                'nickname': user_info['nickName'],
                'open_id': user_info['openId'],
                'gender': user_info.get('gender'),
                'language': user_info.get('language'),
                'country': user_info.get('country'),
                'province': user_info.get('province'),
                'city': user_info.get('city'),
                'avatar_url': user_info.get('avatarUrl'),
                'register_ip': request.httprequest.remote_addr,
                'user_id': user_id,
                'partner_id': user_id and request.env['res.users'].sudo().browse(user_id).partner_id.id or None,
                'category_id': [(4, request.env.ref('oejia_weshop.res_partner_category_data_1').sudo().id)],
                'entry_id': entry.id,
            }
            if user_id:
                vals['user_id'] = user_id
                vals['partner_id'] = request.env['res.users'].sudo().browse(user_id).partner_id.id
                vals.pop('name')
            try:
                wechat_user = request.env(user=1)['wxapp.user'].create(vals)
            except:
                import traceback;traceback.print_exc()
                return self.res_err(-99, u'账号状态异常')
            wechat_user.action_created(vals)
            request.wechat_user = wechat_user
            request.entry = entry
            return self.res_ok()

        except AttributeError:
            return self.res_err(404)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))

    def get_user_info(self, wechat_user):
        mobile = ''
        if hasattr(wechat_user, 'partner_id'):
            mobile = wechat_user.partner_id.mobile
        data = {
            'base':{
                'mobile': mobile or '',
                'userid': '',
            },
        }
        return data

    def get_user_more(self, wechat_user):
        return {}

    @http.route('/wxa/<string:sub_domain>/user/detail', auth='public', methods=['GET'])
    def detail(self, sub_domain, token=None, **kwargs):
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res

            data = self.get_user_info(wechat_user)
            data.update(self.get_user_more(wechat_user))
            return self.res_ok(data)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))

    @http.route('/wxa/<string:sub_domain>/user/wxapp/bindMobile', auth='public', methods=['GET', 'POST'], csrf=False)
    def bind_mobile(self, sub_domain, token=None, encryptedData=None, iv=None, **kwargs):
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res and not wechat_user:return res

            encrypted_data = encryptedData
            if not token or not encrypted_data or not iv:
                return self.res_err(300)

            app_id = entry.get_config('app_id')
            secret = entry.get_config('secret')

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
            wechat_user.bind_mobile(user_info.get('phoneNumber'))
            ret = {
                'account_ok': wechat_user.check_account_ok(),
                'mobile': wechat_user.mobile,
            }
            return self.res_ok(ret)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))

    @http.route('/wxa/<string:sub_domain>/user/amount', auth='public', methods=['GET'])
    def user_amount(self, sub_domain, token=None, **kwargs):
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:
                if entry and kwargs.get('access_token'):
                    return self.res_ok({'balance': 0, 'score': 0})
                else:
                    return res
            _data = {
                'balance': wechat_user.get_balance(),
                'creditLimit': wechat_user.get_credit_limit(),
                'freeze': 0,
                'score': wechat_user.get_score(),
                'totleConsumed': 0,
            }
            return self.res_ok(_data)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))
