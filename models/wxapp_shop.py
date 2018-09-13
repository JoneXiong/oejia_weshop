# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SubShop(models.Model):

    _name = 'wxapp.shop'
    _description = u'商铺'
    _order = 'sort'

    shop_type = fields.Char('店铺类型')
    province_id = fields.Many2one('oe.province', string='省', required=True)
    city_id = fields.Many2one('oe.city', string='市', required=True)
    district_id = fields.Many2one('oe.district', string='区', required=True)
    name = fields.Char('店铺名称', required=True)
    address = fields.Char('地址')
    phone = fields.Char('联系电话')
    introduce = fields.Text('店铺介绍')
    characteristic = fields.Text('店铺特色')
    sort = fields.Integer('排序')
    pic = fields.Many2one('ir.attachment', string='图片')
    activity = fields.Char('打折优惠信息')
    latitude = fields.Float('纬度')
    longitude = fields.Float('经度')
    number_good_reputation = fields.Integer('好评数')
    number_order = fields.Integer('订单数')
