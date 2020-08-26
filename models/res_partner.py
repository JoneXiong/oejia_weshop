# coding=utf-8

from openerp import models, fields, api


class res_partner(models.Model):

    _inherit = 'res.partner'

    province_id = fields.Many2one('oe.province', string='省')
    city_id = fields.Many2one('oe.city', string='市')
    district_id = fields.Many2one('oe.district', string='区')
    # street 详细地址
    is_default = fields.Boolean('是否为默认地址')
    city_domain_ids = fields.One2many('oe.city', compute='_compute_city_domain_ids')
    district_domain_ids = fields.One2many('oe.district', compute='_compute_district_domain_ids')


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

    def check_account_ok(self):
        return True
