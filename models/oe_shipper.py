# -*- coding: utf-8 -*-

from odoo import models, fields, api

from .. import defs


class Shipper(models.Model):

    _name = 'oe.shipper'
    _description = u'物流商'

    name = fields.Char('名称')
    code = fields.Char('编码')


    @api.model_cr
    def init(self):
        from ..data.oe_shipper_datas import init_sql
        self.env.cr.execute(init_sql)
        self.env.cr.execute("select setval('oe_shipper_id_seq', max(id)) from oe_shipper;")

