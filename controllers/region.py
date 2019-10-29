# coding=utf-8 

import json

from odoo import http
from odoo.http import request

from .base import BaseController

import logging

_logger = logging.getLogger(__name__)


class Region(http.Controller, BaseController):

    @http.route('/wxa/common/region/v2/province', auth='public', methods=['GET'])
    def province(self, **kwargs):
        provinces = request.env['oe.province'].sudo().search([])
        data = [{'id': e.id, 'name': e.name, 'level': 1} for e in provinces]
        return self.res_ok(data)

    @http.route('/wxa/common/region/v2/child', auth='public', methods=['GET'])
    def child(self, pid, **kwargs):
        model = None
        if pid[-4:]=='0000':
            model = 'oe.city'
        elif pid[-2:]=='00':
            model = 'oe.district'

        if model:
            objs = request.env[model].sudo().search([('pid', '=', int(pid))])
            data = [{'id': e.id, 'name': e.name, 'level': 2, 'pid': e.pid} for e in objs]
            return self.res_ok(data)
        else:
            return self.res_ok([{'id': 0, 'name':' ', 'pid': pid}])
