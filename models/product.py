# coding=utf-8
import logging
import json

from openerp import models, fields, api

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):

    _inherit = "product.template"

    wxpp_category_id = fields.Many2one('wxapp.product.category', string='电商分类', ondelete='set null')
    characteristic = fields.Text('商品特色')
    recommend_status = fields.Boolean('是否推荐')
    wxapp_published = fields.Boolean('是否上架', default=True)
    description_wxapp = fields.Html('商品描述', translate=True)
    original_price = fields.Float('原始价格', default=0)
    qty_public_tpl = fields.Integer('库存', default=0)
    qty_show = fields.Integer('库存数量', compute='_compute_qty_show')

    number_good_reputation = fields.Integer('好评数', default=0)
    number_fav = fields.Integer('收藏数', default=0)
    views = fields.Integer('浏览量', default=0)
    main_img = fields.Char('主图', compute='_get_main_image')
    images_data = fields.Char('图片', compute='_get_multi_images')


    def _get_main_image(self):
        _logger.info('>>> _get_main_image')
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for obj in self:
            obj.main_img = '%s/web/image/product.template/%s/image/300x300'%(base_url, obj.id)

    def _get_multi_images(self):
        _logger.info('>>> _get_multi_images')
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for product in self:
            _list = []
            if hasattr(product, 'product_image_ids'):
                for obj in product.product_image_ids:
                    _dict = {
                        "id": obj.id,
                        "goodsId": product.id,
                        "pic": '%s/web/image/product.image/%s/image/'%(base_url, obj.id)
                    }
                    _list.append(_dict)
            _list.append({
                'id': product.id,
                'goodsId': product.id,
                'pic': '%s/web/image/product.template/%s/image/'%(base_url, product.id)
            })
            product.images_data =  json.dumps(_list)

    def batch_get_main_image(self):
        self._get_main_image()

    def get_present_qty(self):
        return self.qty_public_tpl

    def _compute_qty_show(self):
        for obj in self:
            obj.qty_show = obj.get_present_qty()

    def change_qty(self, val):
        self.write({'qty_public_tpl': self.qty_public_tpl + val})

    def get_present_price(self, quantity=1):
        return self.list_price

    @api.model
    def cli_price(self, price):
        return round(price, 2)

class ProductProduct(models.Model):

    _inherit = "product.product"

    present_price = fields.Float('现价', default=0, required=True) #暂未用,目前取Odoo的价格
    qty_public = fields.Integer('库存', default=0, required=True)
    attr_val_str = fields.Char('规格', compute='_compute_attr_val_str', store=True, default='')

    @api.multi
    @api.depends('attribute_value_ids')
    def _compute_attr_val_str(self):
        for obj in self:
            obj.attr_val_str = ''


    def get_property_str(self):
        return ''

    def get_present_price(self, quantity=1):
        return self.lst_price or self.product_tmpl_id.list_price

    def get_present_qty(self):
        return self.qty_public

    def change_qty(self, val):
        self.write({'qty_public': self.qty_public + val})
