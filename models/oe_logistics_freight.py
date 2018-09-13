# -*- coding: utf-8 -*-

from odoo import models, fields, api

from .. import defs


class Transportation(models.Model):
    _name = 'oe.logistics.freight'
    _description = u'运输费'

    logistics_id = fields.Many2one('oe.logistics', string='物流', required=True, ondelete='cascade')
    transport_type = fields.Selection(defs.TransportType.attrs.items(), string='运输方式', default='express', required=True)
    unit = fields.Selection(defs.TransportationUnit.attrs.items(), string='单位', compute='_compute_unit')
    less_amount = fields.Integer('数量', required=True, default=0)
    less_price = fields.Float('数量内价格', required=True, default=0)
    increase_amount = fields.Integer('超过数量', required=True, default=0)
    increase_price = fields.Float('递增价格', required=True, default=0)

    district_transportation_ids = fields.One2many('oe.district.freight', 'default_transportation_id',
                                                  string='区域运输费')

    _sql_constraints = [(
        'wechat_mall_transportation_logistics_transport_type_unique',
        'UNIQUE (logistics_id, transport_type)',
        '已存在相同类型的运输方式！'
    )]

    @api.multi
    @api.depends('logistics_id')
    def _compute_unit(self):
        for each_record in self:
            if each_record.logistics_id:
                each_record.unit = each_record.logistics_id.valuation_type


class DistrictTransportation(models.Model):
    _name = 'oe.district.freight'
    _description = u'区域运输费'
    logistics_id = fields.Many2one('oe.logistics', string='物流',
                                   compute='_compute_logistics_id', store=True)

    default_transportation_id = fields.Many2one('oe.logistics.freight', string='默认运输费'
                                                , required=True, ondelete='cascade')

    transport_type = fields.Selection(defs.TransportType.attrs.items(), string='运输方式', compute='_compute_transport_type', store=True)
    unit = fields.Selection(defs.TransportationUnit.attrs.items(), string='单位',
                            related='default_transportation_id.unit')
    area = fields.Char('地区', compute='_compute_area')
    province_id = fields.Many2one('oe.province', string='省', required=True)
    city_id = fields.Many2one('oe.city', string='市')
    district_id = fields.Many2one('oe.district', string='区')
    less_amount = fields.Integer('数量', required=True, default=0)
    less_price = fields.Float('数量内价格', required=True, default=0)
    increase_amount = fields.Integer('递增数量', required=True, default=0)
    increase_price = fields.Float('递增价格', required=True, default=0)

    city_domain_ids = fields.One2many('oe.city', compute='_compute_city_domain_ids')
    district_domain_ids = fields.One2many('oe.district', compute='_compute_district_domain_ids')

    @api.depends('default_transportation_id')
    def _compute_logistics_id(self):
        for each_record in self:
            each_record.logistics_id = each_record.default_transportation_id.logistics_id

    @api.depends('default_transportation_id')
    def _compute_transport_type(self):
        for each_record in self:
            each_record.transport_type = each_record.default_transportation_id.transport_type

    @api.multi
    @api.depends('province_id', 'city_id', 'district_id')
    def _compute_area(self):
        for each_record in self:
            if each_record.district_id:
                each_record.area = each_record.district_id.name

            if not each_record.area and each_record.city_id:
                each_record.area = each_record.city_id.name

            if not each_record.area:
                each_record.area = each_record.province_id.name

    @api.onchange('province_id')
    def _onchange_province_id(self):
        self.city_domain_ids = self.province_id.child_ids if self.province_id else False
        self.city_id = False
        self.district_id = False
        return {
            'domain': {
                'city_id': [('id', 'in', self.city_domain_ids.ids if self.city_domain_ids else [0])]
            }
        }

    @api.onchange('city_id')
    def _onchange_city_id(self):
        self.district_domain_ids = self.city_id.child_ids if self.city_id else False
        self.district_id = False
        return {
            'domain': {
                'district_id': [('id', 'in', self.district_domain_ids.ids if self.district_domain_ids else [0])]
            }
        }

    @api.depends('province_id')
    def _compute_city_domain_ids(self):
        self.city_domain_ids = self.province_id.child_ids if self.province_id else False

    @api.depends('city_id')
    def _compute_district_domain_ids(self):
        self.district_domain_ids = self.city_id.child_ids if self.city_id else False
