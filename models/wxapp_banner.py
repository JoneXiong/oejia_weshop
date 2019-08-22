# -*- coding: utf-8 -*-

from odoo import models, fields, api

from .. import defs


class Banner(models.Model):

    _name = 'wxapp.banner'
    _description = u'横幅图'
    _rec_name = 'title'
    _order = 'sort'

    business_id = fields.Many2one('product.template', string='链接商品(可选)')
    title = fields.Char(string='名称', required=True)
    display_pic = fields.Html('图片', compute='_compute_display_pic')
    image = fields.Binary(string='图片')
    link_url = fields.Char(string='链接地址')
    sort = fields.Integer(string='排序')
    status = fields.Boolean('显示', default=True, required=True)
    remark = fields.Text(string='备注')

    type_mark = fields.Integer(string='类型标记', default=0)
    ptype = fields.Selection([('index', '首页'), ('app', '启动页')], string='位置', default='index')

    @api.depends('image')
    def _compute_display_pic(self):
        for each_record in self:
            if each_record.image:
                each_record.display_pic = """<img src="{pic}" style="max-width:100px;">""".format(pic=each_record.get_main_image())
            else:
                each_record.display_pic = False

    def get_main_image(self):
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return '%s/web/image/wxapp.banner/%s/image/'%(base_url, self.id)
