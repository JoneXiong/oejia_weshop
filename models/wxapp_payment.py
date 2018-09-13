# -*- coding: utf-8 -*-

from odoo import models, fields, api

from .. import defs


class Payment(models.Model):

    _name = 'wxapp.payment'
    _description = u'支付记录'

    wechat_user_id = fields.Many2one('wxapp.user', string='微信用户')
    order_id = fields.Many2one('sale.order', string='订单')
    payment_number = fields.Char('支付单号', index=True)
    price = fields.Float('支付金额(元)')
    status = fields.Selection(defs.PaymentStatus.attrs.items(), string='状态', default=defs.PaymentStatus.unpaid)

    # notify返回参数
    openid = fields.Char('openid')
    result_code = fields.Char('业务结果')
    err_code = fields.Char('错误代码')
    err_code_des = fields.Char('错误代码描述')
    transaction_id = fields.Char('微信订单号')
    bank_type = fields.Char('付款银行')
    fee_type = fields.Char('货币种类')
    total_fee = fields.Integer('订单金额(分)')
    settlement_total_fee = fields.Integer('应结订单金额(分)')
    cash_fee = fields.Integer('现金支付金额')
    cash_fee_type = fields.Char('货币类型')
    coupon_fee = fields.Integer('代金券金额(分)')
    coupon_count = fields.Integer('代金券使用数量')

    _sql_constraints = [(
        'wxapp_payment_payment_number_unique',
        'UNIQUE (payment_number)',
        'wechat payment payment_number is existed！'
    )]

    @api.model
    def create(self, vals):
        vals['payment_number'] = self.env['ir.sequence'].next_by_code('wxapp.payment_num')
        return super(Payment, self).create(vals)
