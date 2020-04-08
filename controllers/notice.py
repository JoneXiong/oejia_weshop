# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request

from .. import defs
from .base import BaseController
from .base import convert_static_link

import logging

_logger = logging.getLogger(__name__)


class WxappNotice(http.Controller, BaseController):

    @http.route('/wxa/<string:sub_domain>/notice/list', auth='public', methods=['GET', 'POST'], csrf=False)
    def list(self, sub_domain, pageSize=5, **kwargs):
        try:
            ret, entry = self._check_domain(sub_domain)
            if ret:return ret

            notices = request.env['wxapp.notice'].sudo().search([])
            data = {
                'dataList': [
                    {'id': e.id, 'title': e.title} for e in notices
                ]
            }

            return self.res_ok(data)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))

    @http.route('/wxa/<string:sub_domain>/notice/detail', auth='public', methods=['GET'], csrf=False)
    def detail(self, sub_domain, id=False, **kwargs):
        try:
            ret, entry = self._check_domain(sub_domain)
            if ret:return ret

            notice = request.env['wxapp.notice'].sudo().browse(int(id))
            data = {
                'title': notice.title,
                'content': convert_static_link(request, notice.content),
            }

            return self.res_ok(data)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))
