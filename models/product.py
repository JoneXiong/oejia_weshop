# coding=utf-8

from openerp import models, fields, api


class ProductTemplate(models.Model):

    _inherit = "product.template"

    wxpp_category_id = fields.Many2one('wxapp.product.category', string='小程序商城分类', ondelete='set null')
    characteristic = fields.Text('商品特色')
    recommend_status = fields.Boolean('是否推荐')
    wxapp_published = fields.Boolean('是否上架', default=True)
    description_wxapp = fields.Html('小程序描述')
    original_price = fields.Float('原始价格', default=0)
    qty_public_tpl = fields.Integer('库存', default=0)

    number_good_reputation = fields.Integer('好评数', default=0)
    number_fav = fields.Integer('收藏数', default=0)
    views = fields.Integer('浏览量', default=0)


    def get_main_image(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return '%s/web/image/product.template/%s/image/300x300'%(base_url, self.id)

    def get_images(self):
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        _list = []
        if hasattr(self, 'product_image_ids'):
            for obj in self.product_image_ids:
                _dict = {
                    "id": obj.id,
                    "goodsId": self.id,
                    "pic": '%s/web/image/product.image/%s/image/'%(base_url, obj.id)
                }
                _list.append(_dict)
        _list.append({
            'id': self.id,
            'goodsId': self.id,
            'pic': '%s/web/image/product.template/%s/image/'%(base_url, self.id)
        })
        return _list

    def get_present_qty(self):
        return self.qty_public_tpl

    def change_qty(self, val):
        self.write({'qty_public_tpl': self.qty_public_tpl + val})


class ProductProduct(models.Model):

    _inherit = "product.product"

    present_price = fields.Float('现价', default=0, required=True) #暂未用,目前取Odoo的价格
    qty_public = fields.Integer('库存', default=0, required=True)
    attr_val_str = fields.Char('规格', compute='_compute_attr_val_str', store=True)

    @api.multi
    @api.depends('attribute_value_ids')
    def _compute_attr_val_str(self):
        for obj in self:
            obj.attr_val_str = ''


    def get_property_str(self):
        return ''

    def get_present_price(self):
        return self.lst_price or self.product_tmpl_id.list_price

    def get_present_qty(self):
        return self.qty_public

    def change_qty(self, val):
        self.write({'qty_public': self.qty_public + val})
