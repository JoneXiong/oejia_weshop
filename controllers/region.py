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
        provinces = request.env['oe.province'].sudo().search([]).sorted(key=lambda o: o.name[0])
        data = [{'id': e.id, 'name': e.name, 'level': 1} for e in provinces]
        return self.res_ok(data)

    @http.route('/wxa/common/region/v2/child', auth='public', methods=['GET'])
    def child(self, pid, **kwargs):
        model = None
        if pid[-4:]=='0000' or int(pid)>820000:
            model = 'oe.city'
        else:
            model = 'oe.district'

        if model:
            objs = request.env[model].sudo().search([('pid', '=', int(pid))]).sorted(key=lambda o: o.name[0])
            data = [{'id': e.id, 'name': e.name, 'level': 2, 'pid': e.pid} for e in objs]
            return self.res_ok(data)
        else:
            return self.res_ok([{'id': 0, 'name':' ', 'pid': pid}])

    @http.route('/wxa/common/region/v2/search', auth='public', methods=['POST'], csrf=False)
    def search(self, nameLike=False, **kwargs):
        if nameLike:
            objs = request.env['oe.district'].sudo().search([('name', 'ilike', nameLike)]).sorted(key=lambda o: o.name[0])
            if not objs:
                citys = request.env['oe.city'].sudo().search([('name', 'ilike', nameLike)]).sorted(key=lambda o: o.name[0])
                objs = []
                for city in citys:
                    objs = objs + [e for e in city.child_ids]
            data = [{'value': {'dObject': {'id': e.id,'name': e.name}, 'cObject': {'id': e.pid.id, 'name': e.pid.name}, 'pObject': {'id': e.pid.pid.id, 'name': e.pid.pid.name}}, 'text': '%s %s %s'%(e.pid.pid.name, e.pid.name, e.name)} for e in objs]
            return self.res_ok(data)
        else:
            return self.res_ok([])