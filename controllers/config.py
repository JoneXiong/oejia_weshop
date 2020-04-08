# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request

from .base import BaseController


import logging

_logger = logging.getLogger(__name__)



class WxappConfig(http.Controller, BaseController):

    @http.route('/wxa/<string:sub_domain>/config/get-value', auth='public', methods=['GET'])
    def get_value(self, sub_domain, key=None, **kwargs):
        try:
            ret, entry = self._check_domain(sub_domain)
            if ret:return ret

            if not key:
                return self.res_err(300)

            data = {
                'dbname': request.env.cr.dbname,
                'creatAt': entry.create_date,
                'dateType': 0,
                'id': entry.id,
                'key': key,
                'remark': '',
                'updateAt': entry.write_date,
                'userId': entry.id,
                'value': entry.get_config(key)
            }
            data.update(entry.get_ext_config())
            return self.res_ok(data)

        except AttributeError:
            return self.res_err(404)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))

    @http.route('/wxa/<string:sub_domain>/config/values', auth='public', methods=['GET'])
    def get_values(self, sub_domain, keys=None, **kwargs):
        keys = keys.split(',')
        try:
            ret, entry = self._check_domain(sub_domain)
            if ret:return ret

            if not keys:
                return self.res_err(300)

            data = []
            for key in keys:
                data.append({'key': key, 'value': entry.get_config(key)})

            return self.res_ok(data)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))

    @http.route('/wxa/<string:sub_domain>/config/vipLevel', auth='public', methods=['GET'])
    def get_viplevel(self, sub_domain, key=None, **kwargs):
        try:
            ret, entry = self._check_domain(sub_domain)
            if ret:return ret

            return self.res_ok(entry.get_level())

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))
