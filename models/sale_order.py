# coding=utf-8

from openerp import models, fields, api

from .. import defs


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    customer_status = fields.Selection(defs.OrderStatus.attrs.items(), default=defs.OrderStatus.unpaid,
                              required=True, string='状态', track_visibility='onchange')

    number_goods = fields.Integer('商品数量')
    goods_price = fields.Float('商品总金额', requried=True, default=0, compute='_compute_pay_total', store=True)
    logistics_price = fields.Float('物流费用', requried=True, default=0)
    total = fields.Float('实际支付', requried=True, default=0, track_visibility='onchange', compute='_compute_pay_total', store=True)

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
    shipper_traces = fields.Text('物流信息')



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

    def get_traces(self, refresh=False):
        return self.shipper_traces

    @api.one
    @api.depends('logistics_price', 'amount_total')
    def _compute_pay_total(self):
        self.total = self.amount_total
        self.goods_price = self.amount_total - self.logistics_price


    @api.multi
    def write(self, vals):
        result = super(SaleOrder, self).write(vals)
        if 'shipper_id' in vals:
            self.delivery()
        return result

    @api.multi
    def delivery(self):
        self.write({'customer_status': 'unconfirmed'})

    @api.multi
    def close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}

    def delivery_window(self):
        self.ensure_one()
        return {
            'name': '送货',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': self.id,
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('oejia_weshop.sale_order_view_form_1029').id,
            'target': 'new',
            'domain': [],
            'context': {
                'default_customer_status': 'unconfirmed'
            }
        }

    @api.multi
    def check_paid(self):
        self.write({'customer_status': 'pending'})

    @api.multi
    def check_pay_window(self):
        new_context = dict(self._context) or {}
        new_context['default_info'] = "此订单客户尚未在线支付，确认将其变为已支付状态？"
        new_context['default_model'] = 'sale.order'
        new_context['default_method'] = 'check_paid'
        new_context['record_ids'] = [obj.id for obj in self]
        return {
            'name': u'确认订单已支付',
            'type': 'ir.actions.act_window',
            'res_model': 'wxapp.confirm',
            'res_id': None,
            'view_mode': 'form',
            'view_type': 'form',
            'context': new_context,
            'view_id': self.env.ref('oejia_weshop.confirm_view_form').id,
            'target': 'new'
        }


    @api.multi
    def action_cancel(self):
        result = super(SaleOrder, self).action_cancel()
        self.write({'customer_status': 'closed'})
        return result

    @api.multi
    def action_draft(self):
        result = super(SaleOrder, self).action_draft()
        self.write({'customer_status': 'unpaid'})
        return result
