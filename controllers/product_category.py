# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request
from odoo import release

from .. import defs
from .base import BaseController


import logging

_logger = logging.getLogger(__name__)

DEFAULT_IMG_URL = '/web/static/src/img/placeholder.png'
odoo_ver = release.version_info[0]
if odoo_ver>=15:
    DEFAULT_IMG_URL = '/web/static/img/placeholder.png'

class WxappCategory(http.Controller, BaseController):

    def get_categorys(self, entry):
        all_category = request.env['wxapp.product.category'].sudo().search([
            ('is_use', '=', True)
        ])
        return all_category

    @http.route('/wxa/<string:sub_domain>/shop/goods/category/all', auth='public', methods=['GET'])
    def all(self, sub_domain):
        ret, entry = self._check_domain(sub_domain)
        if ret:return ret

        try:
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            all_category = self.get_categorys(entry)
            if not all_category:
                return self.res_err(404)

            parent_cate = [e.pid.id for e in all_category]
            parent_cate = set(parent_cate)

            data = [
                {
                    "dateAdd": each_category.create_date,
                    "dateUpdate": each_category.write_date,
                    "icon": each_category.get_icon_image() if each_category.icon else '%s%s'%(base_url,DEFAULT_IMG_URL),
                    "id": each_category.id,
                    "isUse": each_category.is_use,
                    "key": each_category.key,
                    "level": each_category.level,
                    "index_display": each_category.index_display,
                    "name": each_category.name,
                    "paixu": each_category.sort or 0,
                    "pid": each_category.pid.id if each_category.pid else 0,
                    "hasChild": each_category.id in parent_cate,
                    "type": each_category.category_type,
                    "tag_id": hasattr(each_category, 'tag_id') and each_category.tag_id.id or '',
                    "userId": each_category.create_uid.id
                } for each_category in all_category
            ]
            return self.res_ok(data)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))
