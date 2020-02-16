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
            "minPrice": round(each_goods.get_present_price(1), 2),
            "minScore": 0,
            "name": '[%s] %s'%(each_goods.default_code, each_goods.name) if each_goods.default_code else each_goods.name,
            "numberFav": each_goods.number_fav,
            "numberGoodReputation": 0,
            "numberOrders": 0,#each_goods.sales_count,
            "originalPrice": each_goods.original_price,
            "paixu": each_goods.sequence or 0,
            "pic": each_goods.main_img,
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

    def get_goods_domain(self, category_id, nameLike, **kwargs):
        if 'recommendStatus' in kwargs or 'pingtuan' in kwargs:
            return [('id', '=', 0)]
        domain = [('sale_ok', '=', True), ('wxapp_published', '=', True)]
        if category_id:
            cate_ids = [int(category_id)] + request.env['wxapp.product.category'].sudo().browse(int(category_id)).child_ids.ids
            domain.append(('wxpp_category_id', 'in', cate_ids))
        if nameLike:
            domain.append(('name', 'ilike', nameLike))

        return domain

    @http.route('/wxa/<string:sub_domain>/shop/goods/list', auth='public', methods=['GET', 'POST'], csrf=False)
    def list(self, sub_domain, categoryId=False, nameLike=False, page=1, pageSize=20, **kwargs):
        _logger.info('>>> product list %s', kwargs)
        page = int(page)
        pageSize = int(pageSize)
        category_id = categoryId
        token = kwargs.get('token', None)
        try:
            ret, entry = self._check_domain(sub_domain)
            if ret:return ret
            self.check_userid(token)

            domain = self.get_goods_domain(category_id, nameLike, **kwargs)

            goods_list = request.env['product.template'].sudo().search(domain, offset=(page-1)*pageSize, limit=pageSize, order="sequence")
            goods_list.batch_get_main_image()

            if not goods_list:
                return self.res_err(404)

            return self.res_ok([ self._product_basic_dict(each_goods) for each_goods in goods_list])

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))


    @http.route('/wxa/<string:sub_domain>/shop/goods/detail', auth='public', methods=['GET'])
    def detail(self, sub_domain, id=False, code=False, **kwargs):
        goods_id = id
        token = kwargs.get('token', None)
        try:
            ret, entry = self._check_domain(sub_domain)
            if ret:return ret
            self.check_userid(token)

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

            description_value = None
            if goods.description_wxapp:
                _content = goods.description_wxapp.replace('<p>', '').replace('</p>', '').replace('<br>', '').replace('<br/>', '')
                if _content:
                    description_value = goods.description_wxapp
            if not description_value:
                if hasattr(goods, 'website_description'):
                    description_value = goods.website_description

            data = {
                "code": 0,
                "data": {
                    "category": self._product_category_dict(goods.wxpp_category_id),
                    "pics": json.loads(goods.images_data),
                    "content": convert_static_link(request, description_value) if description_value else '',
                    "basicInfo": self._product_basic_dict(goods)
                },
                "msg": "success"
            }
            self.product_info_ext(data, goods, product)

            # goods.sudo().write({'views': goods.views + 1}) #同时同用户多次重复请求的事务问题
            return self.res_ok(data['data'])

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))

    def product_info_ext(self, data, goods, product):
        data["data"]["logistics"] = {
                "logisticsBySelf": False,
                "isFree": False,
                "by_self": False,
                "feeType": 0,
                "feeTypeStr": '按件',
                "details": []
            }

    @http.route('/wxa/<string:sub_domain>/shop/goods/reputation', auth='public', methods=['GET', 'POST'], csrf=False)
    def reputation(self, sub_domain, goodsId=None, **kwargs):
        return self.res_ok([])
