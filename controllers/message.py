# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request

from .. import defs
from .base import BaseController

import logging

_logger = logging.getLogger(__name__)


class WxappMessage(http.Controller, BaseController):

    @http.route('/wxa/<string:sub_domain>/template-msg/wxa/formId', auth='public', method=['POST'], csrf=False)
    def save_formid(self, sub_domain, token, formId=None, type=None, **kwargs):
        return self.res_ok()

    @http.route('/wxa/<string:sub_domain>/template-msg/put', auth='public', methods=['POST'], csrf=False, type='http')
    def send_template_msg(self, sub_domain, **kwargs):
        return self.res_ok()

