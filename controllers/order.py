# -*- coding: utf-8 -*-

import json

from odoo import http, exceptions
from odoo.http import request

from .. import defs
from .base import BaseController, dt_convert

import logging

_logger = logging.getLogger(__name__)


class WxappOrder(http.Controller, BaseController):

    @http.route('/<string:sub_domain>/order/create',
                auth='public', methods=['POST'], csrf=False, type='http')
    def create(self, sub_domain, **kwargs):
        token = kwargs.pop('token', None)
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res

            # [{"goodsId":1,"number":3,"propertyChildIds":"1:1,2:4,","logisticsType":0, "inviter_id":0}]
            goods_json = json.loads(kwargs.pop('goodsJsonStr'))
            province_id = int(kwargs.pop('provinceId'))
            city_id = int(kwargs.pop('cityId'))
            district_id = int(kwargs.pop('districtId')) if 'districtId' in kwargs.keys() else False
            zipcode = kwargs.pop('code')
            link_man = kwargs.pop('linkMan')
            calculate = kwargs.pop('calculate', False)
            remark = kwargs.pop('remark', '')

            goods_price, logistics_price, total, goods_list = self.parse_goods_json(
                goods_json, province_id, city_id, district_id, calculate
            )

            order_dict = {
                'zipcode': zipcode,
                'partner_id': wechat_user.partner_id.id,
                'number_goods': sum(map(lambda r: r['product_uom_qty'], goods_list)),
                'logistics_price': logistics_price,
                'province_id': province_id,
                'city_id': city_id,
                'district_id': district_id,
                'team_id': entry.team_id.id,
                'note': remark,
                'linkman': link_man,
            }
            order_dict.update(kwargs)
            _logger.info('>>> order_dict %s', order_dict)

            if calculate:
                _data = {
                    'score': 0,
                    'isNeedLogistics': 1,
                    'amountTotle': goods_price,
                    'amountLogistics': logistics_price,
                }
            else:
                order = request.env(user=1)['sale.order'].create(order_dict)
                for each_goods in goods_list:
                    each_goods['order_id'] = order.id
                    request.env(user=1)['sale.order.line'].create(each_goods)
                if logistics_price>0:
                    request.env(user=1)['sale.order.line'].create({
                        'order_id': order.id,
                        'product_id': request.env.ref('oejia_weshop.product_product_delivery_weshop').id,
                        'price_unit': logistics_price,
                        'product_uom_qty': 1,
                    })

                #mail_template = request.env.ref('wechat_mall_order_create')
                #mail_template.sudo().send_mail(order.id, force_send=True, raise_exception=False)
                _data = {
                    "amountReal": order.amount_total,
                    "dateAdd": dt_convert(order.create_date),
                    "id": order.id,
                    "orderNumber": order.name,
                    "status": defs.OrderResponseStatus.attrs[order.customer_status],
                    "statusStr": defs.OrderStatus.attrs[order.customer_status],
                }

            return self.res_ok(_data)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e.name)

    def parse_goods_json(self, goods_json, province_id, city_id, district_id, calculate):
        """
        :param goods_json: dict
        :param province_id: 省
        :param city_id: 市
        :param district_id: 区
        :return: goods_price, logistics_price, total, goods_list
        """
        # [{"goodsId":1,"number":3,"propertyChildIds":"1:1,2:4,","logisticsType":0, "inviter_id":0}]
        goods_price, logistics_price = 0.0, 0.0
        goods_list = []

        goods_id_set = set(map(lambda r: r['goodsId'], goods_json))
        product_list = []
        for data in goods_json:
            rs = request.env['product.product'].sudo().search([
                ('product_tmpl_id', '=', data['goodsId']),
                ('attr_val_str', '=', data['propertyChildIds'])
            ])
            product_list += [p for p in rs]

        template_list = request.env['product.template'].sudo().search([
            ('id', 'in', list(goods_id_set)),
            ('wxapp_published', '=', True)
        ])
        template_dict = {template.id: template for template in template_list}

        if set(template_dict.keys()) - goods_id_set:
            raise exceptions.ValidationError('订单中包含已下架的商品')

        for each_goods in goods_json:
            property_child_ids = each_goods.get('propertyChildIds')
            amount = each_goods['number']
            transport_type = each_goods['logisticsType']
            template = template_dict[each_goods['goodsId']]

            each_goods_price, each_goods_total, property_str, product = self.calculate_goods_fee(template, amount, property_child_ids, calculate)
            each_logistics_price = self.calculate_logistics_fee(template, amount, transport_type, province_id, city_id, district_id)
            goods_list.append({
                'product_id': product.id,
                'price_unit': each_goods_price,
                'product_uom_qty': amount,
            })
            goods_price += each_goods_total
            logistics_price += each_logistics_price

        return goods_price, logistics_price, goods_price + logistics_price, goods_list

    def calculate_goods_fee(self, goods, amount, property_child_ids, calculate):
        _logger.info('>>> calculate_goods_fee %s %s %s', goods, amount, property_child_ids)
        property_str = ''

        if 1:#property_child_ids:
            property_child_ids = property_child_ids or ''
            product = request.env['product.product'].sudo().search([
                ('product_tmpl_id', '=', goods.id),
                ('attr_val_str', '=', property_child_ids)
            ])
            if not product:
                raise exceptions.ValidationError('商品不存在！')

            price = product.get_present_price()
            total = price * amount
            property_str = product.name

            stores = product.get_present_qty() - amount
            if not property_child_ids:
                stores = goods.get_present_qty() - amount

            if stores < 0:
                raise exceptions.ValidationError('库存不足！')
            if stores == 0:
                # todo 发送库存空预警
                pass
            if not calculate:
                product.sudo().change_qty(-amount)
                if not property_child_ids:
                    goods.sudo().change_qty(-amount)

        return price, total, property_str, product

    def calculate_logistics_fee(self, goods, amount, transport_type, province_id, city_id, district_id):
        return 0


    @http.route('/<string:sub_domain>/order/statistics', auth='public', method=['GET', 'POST'], csrf=False)
    def statistics(self, sub_domain, token=None, **kwargs):
        '''
        closed = ('closed', u'已关闭')
        unpaid = ('unpaid', u'待支付')
        pending = ('pending', u'待发货')
        unconfirmed = ('unconfirmed', u'待收货')
        unevaluated = ('unevaluated', u'待评价')
        completed = ('completed', u'已完成')
        '''
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res

            orders = request.env['sale.order'].sudo().search([('partner_id', '=', wechat_user.partner_id.id)])
            order_statistics_dict = {order_status: 0 for order_status in defs.OrderStatus.attrs.keys()}
            for each_order in orders:
                order_statistics_dict[each_order.customer_status] += 1

            data = {
                "count_id_no_reputation": order_statistics_dict['unevaluated'],
                "count_id_no_transfer": order_statistics_dict['pending'],
                "count_id_close": order_statistics_dict['closed'],
                "count_id_no_pay": order_statistics_dict['unpaid'],
                "count_id_no_confirm": order_statistics_dict['unconfirmed'],
                "count_id_success": order_statistics_dict['completed']
            }
            return self.res_ok(data)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e.name)


    @http.route('/<string:sub_domain>/order/list', auth='public', method=['GET', 'POST'], csrf=False)
    def list(self, sub_domain, token=None, status=None, **kwargs):
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res

            if status is not None:
                orders = request.env['sale.order'].sudo().search([
                    ('partner_id', '=', wechat_user.partner_id.id),
                    ('customer_status', '=', defs.OrderRequestStatus.attrs[int(status)])
                ])
            else:
                orders = request.env['sale.order'].search([
                    ('partner_id', '=', wechat_user.partner_id)
                ])
            delivery_product_id = request.env.ref('oejia_weshop.product_product_delivery_weshop').id
            data = {
                "logisticsMap": {},
                "orderList": [{
                    "amountReal": each_order.amount_total,
                    "dateAdd": dt_convert(each_order.create_date),
                    "id": each_order.id,
                    "remark": each_order.note,
                    "orderNumber": each_order.name,
                    "status": defs.OrderResponseStatus.attrs[each_order.customer_status],
                    "statusStr": defs.OrderStatus.attrs[each_order.customer_status],
                    "score": 0,
                } for each_order in orders],
                "goodsMap": {
                    each_order.id: [
                        {
                            "pic": each_goods.product_id.product_tmpl_id.get_main_image(),
                        } for each_goods in each_order.order_line if each_goods.product_id.id!=delivery_product_id]
                    for each_order in orders}
            }
            if not data['orderList']:
                return self.res_err(700)
            return self.res_ok(data)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e.name)


    @http.route('/<string:sub_domain>/order/detail', auth='public', method=['GET'])
    def detail(self, sub_domain, token=None, id=None, **kwargs):
        order_id = id
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res

            if not order_id:
                return self.res_err(300)

            order = request.env['sale.order'].sudo().search([
                ('partner_id', '=', wechat_user.partner_id.id),
                ('id', '=', int(order_id))
            ])

            if not order:
                return self.res_err(404)

            delivery_product_id = request.env.ref('oejia_weshop.product_product_delivery_weshop').id
            data = {
                "code": 0,
                "data": {
                    "orderInfo": {
                        "amount": order.goods_price,
                        "amountLogistics": order.logistics_price,
                        "amountReal": order.amount_total,
                        "dateAdd": dt_convert(order.create_date),
                        "dateUpdate": dt_convert(order.write_date),
                        "goodsNumber": order.number_goods,
                        "id": order.id,
                        "orderNumber": order.name,
                        "remark": order.note,
                        "status": defs.OrderResponseStatus.attrs[order.customer_status],
                        "statusStr": defs.OrderStatus.attrs[order.customer_status],
                        "type": 0,
                        "uid": 1,#user.id,
                        "userId": wechat_user.id
                    },
                    "goods": [
                        {
                            "amount": each_goods.price_unit,
                            "goodsId": each_goods.product_id.product_tmpl_id.id,
                            "goodsName": each_goods.name,
                            "id": each_goods.id,
                            "number": each_goods.product_uom_qty,
                            "orderId": order.id,
                            "pic": each_goods.product_id.product_tmpl_id.get_main_image(),
                            "property": each_goods.product_id.get_property_str(),
                        } for each_goods in order.order_line if each_goods.product_id.id!=delivery_product_id
                    ],
                    "logistics": {
                        "address": order.address,
                        "cityId": order.city_id.id,
                        "code": order.zipcode,
                        "dateUpdate": dt_convert(order.write_date),
                        "districtId": order.district_id.id or 0,
                        "linkMan": order.linkman,
                        "mobile": order.mobile,
                        "provinceId": order.province_id.id,
                        "shipperCode": order.shipper_id.code if order.shipper_id else '',
                        "shipperName": order.shipper_id.name if order.shipper_id else '',
                        "status": 0 if order.shipper_id else '',
                        "trackingNumber": order.shipper_no if order.shipper_no else ''
                    },
                },
                "msg": "success"
            }
            if order.shipper_no:
                self.build_traces(order, data)

            return self.res_ok(data["data"])

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e.name)

    def build_traces(self, order, data):
        pass

    @http.route('/<string:sub_domain>/order/close', auth='public', method=['GET', 'POST'], csrf=False)
    def close(self, sub_domain, token=None, orderId=None, **kwargs):
        order_id = orderId
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res

            if not order_id:
                return self.res_err(300)

            order = request.env['sale.order'].sudo().search([
                ('partner_id', '=', wechat_user.partner_id.id),
                ('id', '=', int(order_id))
            ])

            if not order:
                return self.res_err(404)

            if order.state=='sale':
                return self.res_err(-99, u'该订单已被确认，无法取消')

            #order.write({'customer_status': 'closed'})
            order.action_cancel()

            #mail_template = request.env.ref('wechat_mall_order_closed')
            #mail_template.sudo().send_mail(order.id, force_send=True, raise_exception=False)

            return self.res_ok()

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e.name)


    @http.route('/<string:sub_domain>/order/delivery', auth='public', method=['GET', 'POST'], csrf=False)
    def delivery(self, sub_domain, token=None, orderId=None, **kwargs):
        '''
        确认收货接口
        '''
        order_id = orderId
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res

            if not order_id:
                return self.res_err(300)

            order = request.env['sale.order'].sudo().search([
                ('partner_id', '=', wechat_user.partner_id.id),
                ('id', '=', int(order_id))
            ])

            if not order:
                return self.res_err(404)

            order.write({'customer_status': 'unevaluated'})

            #mail_template = request.env.ref('wechat_mall_order_confirmed')
            #mail_template.sudo().send_mail(order.id, force_send=True, raise_exception=False)

            return self.res_ok()

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e.name)


    @http.route('/<string:sub_domain>/order/reputation', auth='public', method=['GET'])
    def reputation(self, sub_domain, token=None, order_id=None, reputation=2, **kwargs):
        '''
        评论接口
        {
            "token": "xxx",
            "orderId": "4",
            "reputations": [{
                "id": "4",
                "reputation": "2",
                "remark": "xxx"
            }]
        }
        '''
        try:
            post_json = json.loads(kwargs.pop('postJsonString'))
            token = post_json.get('token',None)
            order_id = post_json.get('orderId',None)
            reputations = post_json.get('reputations',[])

            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res

            if not order_id:
                return self.res_err(300)

            order = request.env['sale.order'].sudo().search([
                ('partner_id', '=', wechat_user.partner_id.id),
                ('id', '=', int(order_id))
            ])

            if not order:
                return self.res_err(404)

            order.write({'customer_status': 'completed'})

            for reputation in reputations:
                # 保存评论
                pass

            return request.make_response(json.dumps({'code': 0, 'msg': 'success'}))

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, e.name)



