# -*- coding: utf-8 -*-

from odoo import models, fields, api


class WxappNotice(models.Model):

    _name = 'wxapp.notice'
    _description = u'公告'
    _rec_name = 'title'

    title = fields.Char(string='标题', required=True)
    content = fields.Text('内容')
    active = fields.Boolean('是否有效', default=True)
