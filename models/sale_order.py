# coding=utf-8

from openerp import models, fields, api

from .. import defs


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    customer_status = fields.Selection(defs.OrderStatus.attrs.items(), default=defs.OrderStatus.unpaid,
                              required=True, string='状态', track_visibility='onchange')

    number_goods = fields.Integer('商品数量')
    goods_price = fields.Float('商品总金额', requried=True, default=0)
    logistics_price = fields.Float('物流费用', requried=True, default=0)
    total = fields.Float('实际支付', requried=True, default=0, track_visibility='onchange')

    province_id = fields.Many2one('oe.province', string='省')
    city_id = fields.Many2one('oe.city', string='市')
    district_id = fields.Many2one('oe.district', string='区')
    address = fields.Char('详细地址')
    full_address = fields.Char('联系人地址', compute='_compute_full_address', store=True)

    linkman = fields.Char('联系人')
    mobile = fields.Char('手机号码')
    zipcode = fields.Char('邮编', requried=True)


    shipper_id = fields.Many2one('oe.shipper', string='承运商', track_visibility='onchange')
    shipper_no = fields.Char('运单号', track_visibility='onchange')
    shipper_traces = fields.Text('物流信息', compute='_compute_traces')



    @api.one
    @api.depends('province_id', 'city_id', 'district_id', 'address')
    def _compute_full_address(self):
        self.full_address = u'{province_name} {city_name} {district_name} {address}'.format(
            province_name=self.province_id.name,
            city_name=self.city_id.name,
            district_name=self.district_id.name or '',
            address=self.address
        )

    @api.one
    @api.depends('shipper_id', 'shipper_no')
    def _compute_traces(self):
        pass
