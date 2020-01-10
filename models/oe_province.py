# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Province(models.Model):

    _name = 'oe.province'
    _description = u'省份'

    name = fields.Char('名称')
    child_ids = fields.One2many('oe.city', 'pid', string='市')


    @api.model_cr
    def init(self):
        from ..data.oe_province_datas import init_sql
        self.env.cr.execute(init_sql)
        self.env.cr.execute("select setval('oe_province_id_seq', max(id)) from oe_province;")
