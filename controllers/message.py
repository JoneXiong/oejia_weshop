# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request

from .. import defs
from .base import BaseController

import logging

_logger = logging.getLogger(__name__)


class WxappMessage(http.Controller, BaseController):

    @http.route('/<string:sub_domain>/template-msg/put', auth='public', methods=['POST'], csrf=False, type='http')
    def send_template_msg(self, sub_domain, **kwargs):
        # https://www.it120.cc/apis/92
        # https://github.com/EastWorld/wechat-app-mall/blob/master/app.js
        try:
            _logger.info('>>> kwargs: %s'%kwargs)
            token = kwargs.get('token', None)

            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res

            module = kwargs['module']
            template_id = kwargs['template_id']
            postJsonString = kwargs['postJsonString']
            postJson = json.loads(postJsonString)

            business_id = kwargs.get('business_id', None) # 非immediately
            trigger = kwargs.get('trigger', None) # 非immediately

            form_id = kwargs.get('form_id', None) # type=0 小程序
            url = kwargs.get('url', None) # type=0 小程序
            emphasis_keyword = kwargs.get('emphasis_keyword', None) # type=0 小程序

            from odoo.addons.oejia_wx.rpc import app_client
            entry = app_client.appenv(request.env)

            if trigger=='2':
                template_id = 'qu0K6anpozZNj3uf1gcyyOFZSbM8ZKDTrk_TI0IScXg' #新订单通知
            else:
                template_id = 'ByIUs56ntvPpQ12GeWDLMr_0fQHdVnZz83-LnEkBZUg' #订单取消通知
            entry.client.wxa.send_template_message(wechat_user.open_id, template_id, postJson, form_id, url)

            return self.res_ok()

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))



