# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class District(models.Model):

    _name = 'oe.district'
    _description = u'区'

    pid = fields.Many2one('oe.city', string='城市')
    name = fields.Char('名称')

    @api.model_cr
    def _register_hook(self):
        """ stuff to do right after the registry is built """
        _logger.info('>>> registry hook...')
        #from ..data import province_city_district_data
        #self.env.cr.execute(province_city_district_data)

    @api.model_cr
    def init(self):
        _logger.info('>>> init...')
        from ..data.oe_district_datas import init_sql
        self.env.cr.execute(init_sql)
