# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request

from .. import defs
from .base import BaseController

import logging

_logger = logging.getLogger(__name__)


class WxappBanner(http.Controller, BaseController):

    @http.route('/<string:sub_domain>/banner/list', auth='public', methods=['GET'])
    def list(self, sub_domain, default_banner=True, **kwargs):
        _logger.info('>>> banner_list %s %s', default_banner, kwargs)
        banner_type = kwargs.get('type')
        try:
            ret, entry = self._check_domain(sub_domain)
            if ret:return ret

            banner_list = request.env['wxapp.banner'].sudo().search([
                ('status', '=', True)
            ])

            data = []
            if banner_list:
                data = [
                    {
                        "businessId": each_banner.business_id.id,
                        "dateAdd": each_banner.create_date,
                        "dateUpdate": each_banner.write_date,
                        "id": each_banner.id,
                        "linkUrl": each_banner.link_url or '',
                        "paixu": each_banner.sort or 0,
                        "picUrl": each_banner.get_main_image(),
                        "remark": each_banner.remark or '',
                        "status": 0 if each_banner.status else 1,
                        "statusStr": defs.BannerStatus.attrs[each_banner.status],
                        "title": each_banner.title,
                        "type": each_banner.type_mark,
                        "userId": each_banner.create_uid.id
                    } for each_banner in banner_list
                ]
                if banner_type=='app':
                    if len(data)>=3:
                        return self.res_ok(data)
                    else:
                        return self.res_err(700)
            else:
                if banner_type=='app':
                    return self.res_err(700)

            recommend_goods = request.env(user=1)['product.template'].search([
                ('recommend_status', '=', True),
                ('wxapp_published', '=', True)
            ], limit=5)

            data += [
                {
                    "goods": True,
                    "businessId": goods.id,
                    "dateAdd": goods.create_date,
                    "dateUpdate": goods.write_date,
                    "id": goods.id,
                    "linkUrl": '',
                    "paixu": goods.sequence or 0,
                    "picUrl": goods.get_main_image(),
                    "remark": '',
                    "status": 0 if goods.wxapp_published else 1,
                    "statusStr": '',
                    "title": goods.name,
                    "type": 0,
                    "userId": goods.create_uid.id
                } for goods in recommend_goods
            ]

            return self.res_ok(data)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))
