# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request

from .base import BaseController


import logging

_logger = logging.getLogger(__name__)



class WxappConfig(http.Controller, BaseController):

    @http.route('/<string:sub_domain>/config/get-value', auth='public', methods=['GET'])
    def get_value(self, sub_domain, key=None, **kwargs):
        try:
            ret, entry = self._check_domain(sub_domain)
            if ret:return ret

            if not key:
                return self.res_err(300)

            config = request.env['wxapp.config'].sudo()
            value_obj = config.get_config(key, sub_domain, obj=True)
            if not value_obj:
                return self.res_err(404)

            data = {
                'creatAt': value_obj.create_date,
                'dateType': 0,
                'id': value_obj.id,
                'key': key,
                'remark': '',
                'updateAt': value_obj.write_date,
                'userId': entry.id,
                'value': config.get_config(key, sub_domain)
            }
            return self.res_ok(data)

        except AttributeError:
            return self.res_err(404)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e.message)
