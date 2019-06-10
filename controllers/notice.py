# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request

from .. import defs
from .base import BaseController

import logging

_logger = logging.getLogger(__name__)


class WxappNotice(http.Controller, BaseController):

    @http.route('/<string:sub_domain>/notice/list', auth='public', methods=['GET', 'POST'], csrf=False)
    def list(self, sub_domain, pageSize=5, **kwargs):
        try:
            ret, entry = self._check_domain(sub_domain)
            if ret:return ret

            data = []

            return self.res_ok(data)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))
