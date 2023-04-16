# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Province(models.Model):

    _name = 'oe.province'
    _description = u'省份'

    name = fields.Char('名称', requried=True)
    child_ids = fields.One2many('oe.city', 'pid', string='市')
