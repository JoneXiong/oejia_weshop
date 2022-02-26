# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Category(models.Model):

    _name = 'wxapp.product.category'
    _description = u'商品分类'
    _order = 'level,sort'
    _rec_name = 'complete_name'

    name = fields.Char(string='名称', required=True, translate=True)
    complete_name = fields.Char(string='全名', compute='_compute_complete_name', store=True, recursive=True)
    category_type = fields.Char(string='类型')
    pid = fields.Many2one('wxapp.product.category', string='上级分类', ondelete='cascade')
    child_ids = fields.One2many('wxapp.product.category', 'pid', string='子分类')
    key = fields.Char(string='编号')
    icon = fields.Binary(string='图标/图片')
    level = fields.Integer(string='分类级别', compute='_compute_level', store=True)
    is_use = fields.Boolean(string='是否启用', default=True)
    index_display = fields.Boolean(string='首页导航展示', default=True)
    sort = fields.Integer(string='排序')
    product_template_ids = fields.One2many('product.template', 'wxpp_category_id', string='商品')

    @api.depends('pid')
    def _compute_level(self):
        for cate in self:
            level = 0
            pid = cate.pid
            while True:
                if not pid:
                    break

                pid = pid.pid

                level += 1

            cate.level = level
            for child in cate.child_ids:
                child._compute_level()

    @api.depends('name','pid.complete_name')
    def _compute_complete_name(self):
        for cate in self:
            if cate.pid:
                cate.complete_name = '%s / %s'%(cate.pid.complete_name, cate.name)
            else:
                cate.complete_name = cate.name

    def get_icon_image(self):
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return '%s/web/image/wxapp.product.category/%s/icon/'%(base_url, self.id)
