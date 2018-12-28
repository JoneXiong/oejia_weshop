# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request

from .. import defs
from .base import BaseController
from .base import convert_static_link

import logging

_logger = logging.getLogger(__name__)


class WxappProduct(http.Controller, BaseController):


    def _product_basic_dict(self, each_goods):
        _dict = {
            "categoryId": each_goods.wxpp_category_id.id,
            "characteristic": each_goods.characteristic,
            "dateAdd": each_goods.create_date,
            "dateUpdate": each_goods.write_date,
            "id": each_goods.id,
            "logisticsId": 1,
            "minPrice": each_goods.list_price,
            "minScore": 0,
            "name": each_goods.name,
            "numberFav": each_goods.number_fav,
            "numberGoodReputation": 0,
            "numberOrders": each_goods.sales_count,
            "originalPrice": each_goods.original_price,
            "paixu": each_goods.sequence or 0,
            "pic": each_goods.get_main_image(),
            "recommendStatus": 0 if not each_goods.recommend_status else 1,
            "recommendStatusStr": defs.GoodsRecommendStatus.attrs[each_goods.recommend_status],
            "shopId": 0,
            "status": 0 if each_goods.wxapp_published else 1,
            "statusStr": '上架' if each_goods.wxapp_published else '下架',
            "stores": each_goods.get_present_qty(),
            "userId": each_goods.create_uid.id,
            "views": each_goods.views,
            "weight": each_goods.weight
        }
        return _dict

    def _product_category_dict(self, category_id):
        _dict = {
            "dateAdd": category_id.create_date,
            "dateUpdate": category_id.write_date,
            "icon": '',
            "id": category_id.id,
            "isUse": category_id.is_use,
            "key": category_id.key,
            "name": category_id.name,
            "paixu": category_id.sort or 0,
            "pid": category_id.pid.id if category_id.pid else 0,
            "type": category_id.category_type,
            "userId": category_id.create_uid.id
        }
        return _dict

    @http.route('/<string:sub_domain>/shop/goods/list', auth='public', methods=['GET'])
    def list(self, sub_domain, categoryId=False, nameLike=False, page=1, pageSize=20, **kwargs):
        page = int(page)
        pageSize = int(pageSize)
        category_id = categoryId
        try:
            ret, entry = self._check_domain(sub_domain)
            if ret:return ret

            domain = [('wxapp_published', '=', True)]
            if category_id:
                cate_ids = [int(category_id)] + request.env['wxapp.product.category'].sudo().browse(int(category_id)).child_ids.ids
                domain.append(('wxpp_category_id', 'in', cate_ids))
            if nameLike:
                domain.append(('name', 'ilike', nameLike))

            goods_list = request.env['product.template'].sudo().search(domain, offset=(page-1)*pageSize, limit=pageSize)

            if not goods_list:
                return self.res_err(404)

            return self.res_ok([ self._product_basic_dict(each_goods) for each_goods in goods_list])

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e.name)


    @http.route('/<string:sub_domain>/shop/goods/detail', auth='public', methods=['GET'])
    def detail(self, sub_domain, id=False, code=False, **kwargs):
        goods_id = id
        try:
            ret, entry = self._check_domain(sub_domain)
            if ret:return ret

            if not goods_id and not code:
                return self.res_err(300)

            if goods_id:
                product = None
                goods = request.env['product.template'].sudo().browse(int(goods_id))
            else:
                product = request.env['product.product'].sudo().search([('barcode', '=', code)])
                goods = product.product_tmpl_id

            if not goods:
                return self.res_err(404)

            if not goods.wxapp_published:
                return self.res_err(404)

            data = {
                "code": 0,
                "data": {
                    "category": self._product_category_dict(goods.wxpp_category_id),
                    "pics": goods.get_images(),
                    "content": convert_static_link(request, goods.description_wxapp) if goods.description_wxapp else '',
                    "basicInfo": self._product_basic_dict(goods)
                },
                "msg": "success"
            }
            self.product_info_ext(data, goods, product)

            goods.sudo().write({'views': goods.views + 1})
            return self.res_ok(data['data'])

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e.name)

    def product_info_ext(self, data, goods, product):
        data["data"]["logistics"] = {
                "logisticsBySelf": False,
                "isFree": False,
                "by_self": False,
                "feeType": 0,
                "feeTypeStr": '按件',
                "details": []
            }

