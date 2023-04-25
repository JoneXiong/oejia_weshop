# -*- coding: utf-8 -*-
import logging
import json

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class District(models.Model):

    _name = 'oe.district'
    _description = u'区'

    pid = fields.Many2one('oe.city', string='城市')
    name = fields.Char('名称', requried=True)

    @api.model_cr
    def _register_hook(self):
        """ stuff to do right after the registry is built """
        _logger.info('>>> registry hook...')
        #from ..data import province_city_district_data
        #self.env.cr.execute(province_city_district_data)

    @api.model_cr
    def init(self):
        _logger.info('>>> init...')
        from ..data.oe_district_full_datas import init_json
        objs = json.loads(init_json)
        district_sql = city_sql = province_sql = ''
        name_key = 'value'
        children_key = 'children'
        for province in objs:
            province_sql += """INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (%s, '%s', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;\n"""%(province['code'], province[name_key])
            city0code = province[children_key][0]['code']
            if city0code[-2:]=='00':
                for city in province[children_key]:
                    city_sql += """INSERT INTO oe_city (id, pid, name, create_uid, create_date, write_uid, write_date) VALUES (%s, %s, '%s', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;\n"""%(city['code'], province['code'], city[name_key])
                    # _logger.info('>>> load city %s', city)
                    for district in city[children_key]:
                        district_sql += """INSERT INTO oe_district (id, pid, name, create_uid, create_date, write_uid, write_date) VALUES (%s, %s, '%s', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;"""%(district['code'], city['code'], district[name_key])
            else:
                # province 为直辖市
                city_code = '%s0100'%province['code'][:2]
                city_sql += """INSERT INTO oe_city (id, pid, name, create_uid, create_date, write_uid, write_date) VALUES (%s, %s, '%s', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;\n"""%(city_code, province['code'], province[name_key])
                for district in province[children_key]:
                    district_sql += """INSERT INTO oe_district (id, pid, name, create_uid, create_date, write_uid, write_date) VALUES (%s, %s, '%s', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;"""%(district['code'], city_code, district[name_key])
                
        self.env.cr.execute(province_sql)
        self.env.cr.execute("select setval('oe_province_id_seq', max(id)) from oe_province;")
        self.env.cr.execute(city_sql)
        self.env.cr.execute("select setval('oe_city_id_seq', max(id)) from oe_city;")
        self.env.cr.execute(district_sql)
        self.env.cr.execute("select setval('oe_district_id_seq', max(id)) from oe_district;")
