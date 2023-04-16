# -*- coding: utf-8 -*-

from odoo import models, fields, api


class City(models.Model):

    _name = 'oe.city'
    _description = u'城市'

    pid = fields.Many2one('oe.province', string='省份')
    name = fields.Char('名称', requried=True)
    child_ids = fields.One2many('oe.district', 'pid', string='区')
