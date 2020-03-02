# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request

from .. import defs
from .base import BaseController, dt_convert, UserException

import logging

_logger = logging.getLogger(__name__)


class WxappOrder(http.Controller, BaseController):

    @http.route('/wxa/<string:sub_domain>/order/create',
                auth='public', methods=['POST'], csrf=False, type='http')
    def create(self, sub_domain, **kwargs):
        token = kwargs.pop('token', None)
        team_id = kwargs.pop('team', None)
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res

            res = self.pre_check(entry, wechat_user, kwargs)
            if res:return res

            # [{"goodsId":1,"number":3,"propertyChildIds":"1:1,2:4,","logisticsType":0, "inviter_id":0}]
            goods_json = json.loads(kwargs.pop('goodsJsonStr'))

            province_id = int(kwargs.pop('provinceId')) if 'provinceId' in kwargs else False
            city_id = int(kwargs.pop('cityId')) if 'cityId' in kwargs else False
            district_id = int(kwargs.pop('districtId')) if 'districtId' in kwargs else False
            zipcode = kwargs.pop('code') if 'code' in kwargs else False
            link_man = kwargs.pop('linkMan') if 'linkMan' in kwargs else False

            calculate = kwargs.pop('calculate', False)
            remark = kwargs.pop('remark', '')

            goods_price, logistics_price, order_lines = self.parse_goods_json(
                goods_json, province_id, city_id, district_id, calculate
            )

            address = request.env(user=1)['res.partner'].search([
                ('parent_id', '=', wechat_user.partner_id.id),
                ('type', '=', 'delivery'),
                ('is_default', '=', True)
            ], limit=1)
            order_dict = {
                'zipcode': zipcode,
                'partner_id': wechat_user.partner_id.id,
                'number_goods': sum(map(lambda r: r['product_uom_qty'], order_lines)),
                'logistics_price': logistics_price,
                'province_id': province_id,
                'city_id': city_id,
                'district_id': district_id,
                'team_id': team_id and int(team_id) or entry.team_id.id,
                'note': remark,
                'linkman': link_man,
                'partner_shipping_id': address and address.id or None,
                'user_id': wechat_user.partner_id.user_id.id,
                'goods_price': goods_price,
                'extra': {},
            }
            order_dict.update(kwargs)
            _logger.info('>>> order_dict %s', order_dict)
            self.after_calculate(wechat_user, order_dict, order_lines)

            if calculate:
                _data = {
                    'score': 0,
                    'isNeedLogistics': 1,
                    'amountTotle': round(order_dict['goods_price'], 2),
                    'amountLogistics': order_dict['logistics_price'],
                    'extra': order_dict['extra']
                }
                _data.update(self.calculate_ext_info(wechat_user, order_dict, order_lines, _data))
                for line in order_lines:
                    line['price_unit'] = round(line['price_unit'], 2)
                _data['orderLines'] = order_lines
            else:
                order_dict.pop('goods_price')
                order_dict.pop('extra')
                order = request.env(user=1)['sale.order'].create(order_dict)
                for line in order_lines:
                    line['order_id'] = order.id
                    request.env(user=1)['sale.order.line'].create(line)
                if logistics_price>0:
                    request.env(user=1)['sale.order.line'].create({
                        'order_id': order.id,
                        'product_id': request.env.ref('oejia_weshop.product_product_delivery_weshop').id,
                        'price_unit': logistics_price,
                        'product_uom_qty': 1,
                    })

                #mail_template = request.env.ref('wechat_mall_order_create')
                #mail_template.sudo().send_mail(order.id, force_send=True, raise_exception=False)
                order.action_created(kwargs)
                _data = {
                    "amountReal": round(order.amount_total, 2),
                    "dateAdd": dt_convert(order.create_date),
                    "id": order.id,
                    "orderNumber": order.name,
                    "status": defs.OrderResponseStatus.attrs[order.customer_status],
                    "statusStr": defs.OrderStatus.attrs[order.customer_status],
                }

            return self.res_ok(_data)

        except UserException as e:
            return self.res_err(-99, str(e))
        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))

    def after_calculate(self, wechat_user, order_dict, order_lines):
        pass

    def calculate_ext_info(self, wechat_user, order_dict, goods_list, init_info):
        return {}

    def parse_goods_json(self, goods_json, province_id, city_id, district_id, calculate):
        """
        :param goods_json: dict
        :param province_id: 省
        :param city_id: 市
        :param district_id: 区
        :return: goods_fee, logistics_fee, order_lines
        """
        # [{"goodsId":1,"number":3,"propertyChildIds":"1:1,2:4,","logisticsType":0, "inviter_id":0}]
        goods_fee, logistics_fee = 0.0, 0.0
        order_lines = []

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

        if goods_id_set - set(template_dict.keys()):
            raise UserException('订单中包含已下架的商品')

        for each_goods in goods_json:
            property_child_ids = each_goods.get('propertyChildIds')
            amount = each_goods['number']
            transport_type = each_goods['logisticsType']
            template = template_dict[each_goods['goodsId']]

            each_goods_total, line_dict = self.calculate_goods_fee(template, amount, property_child_ids, calculate)
            each_logistics_price = self.calculate_logistics_fee(template, amount, transport_type, province_id, city_id, district_id)
            order_lines.append(line_dict)
            goods_fee += each_goods_total
            logistics_fee += each_logistics_price

        return goods_fee, logistics_fee, order_lines

    def calculate_goods_fee(self, goods, amount, property_child_ids, calculate):
        _logger.info('>>> calculate_goods_fee %s %s %s', goods, amount, property_child_ids)
        property_str = ''

        if 1:#property_child_ids:
            property_child_ids = property_child_ids or ''
            product = request.env['product.product'].sudo().search([
                ('product_tmpl_id', '=', goods.id),
                ('attr_val_str', '=', property_child_ids)
            ])
            if not property_child_ids and not product:
                product = request.env['product.product'].sudo().search([
                    ('product_tmpl_id', '=', goods.id),
                    ('attr_val_str', '=', False)
                ])
            if not product:
                raise UserException('商品不存在！')

            price = product.get_present_price(amount)
            total = price * amount
            property_str = product.name

            stores = product.get_present_qty() - amount
            if not property_child_ids:
                stores = goods.get_present_qty() - amount

            if stores < 0:
                raise UserException('库存不足！')
            if stores == 0:
                # todo 发送库存空预警
                pass
            if not calculate:
                product.sudo().change_qty(-amount)
                if not property_child_ids:
                    goods.sudo().change_qty(-amount)

        line_dict = {
            'product_id': product.id,
            'price_unit': price,
            'product_uom_qty': amount,
        }
        return total, line_dict

    def calculate_logistics_fee(self, goods, amount, transport_type, province_id, city_id, district_id):
        return 0

    def pre_check(self, entry, wechat_user, post_data):
        return


    @http.route('/wxa/<string:sub_domain>/order/statistics', auth='public', method=['GET', 'POST'], csrf=False)
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

            orders = request.env['sale.order'].sudo().search([('partner_id', '=', wechat_user.partner_id.id), ('number_goods', '>', 0)])
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
            return self.res_err(-1, str(e))

    def _order_basic_dict(self, each_order):
        ret = {
            "amountReal": round(each_order.amount_total, 2),
            "dateAdd": dt_convert(each_order.create_date),
            "id": each_order.id,
            "remark": each_order.note,
            "orderNumber": each_order.name,
            "status": defs.OrderResponseStatus.attrs[each_order.customer_status],
            "statusStr": defs.OrderStatus.attrs[each_order.customer_status],
            "score": 0,
        }
        return ret

    def get_orders_domain(self, status, **kwargs):
        domain = [('partner_id', '=', request.wechat_user.partner_id.id), ('number_goods', '>', 0)]
        if status:
            domain.append(('customer_status', '=', defs.OrderRequestStatus.attrs[int(status)]))
        return domain

    @http.route('/wxa/<string:sub_domain>/order/list', auth='public', method=['GET', 'POST'], csrf=False)
    def list(self, sub_domain, token=None, status=None, **kwargs):
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res

            domain = self.get_orders_domain(status, **kwargs)
            orders = request.env['sale.order'].sudo().search(domain, order='id desc', limit=30)
            delivery_product_id = request.env.ref('oejia_weshop.product_product_delivery_weshop').id
            data = {
                "logisticsMap": {},
                "orderList": [self._order_basic_dict(each_order) for each_order in orders],
                "goodsMap": {
                    each_order.id: [
                        {
                            "pic": each_goods.product_id.product_tmpl_id.main_img,
                        } for each_goods in each_order.order_line if each_goods.product_id.id!=delivery_product_id]
                    for each_order in orders}
            }
            if not data['orderList']:
                return self.res_err(700)
            return self.res_ok(data)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))


    @http.route('/wxa/<string:sub_domain>/order/detail', auth='public', method=['GET'])
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
                        "amountReal": round(order.amount_total, 2),
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
                            "id": each_goods.product_id.id,
                            "number": each_goods.product_uom_qty,
                            "orderId": order.id,
                            "pic": each_goods.product_id.product_tmpl_id.main_img,
                            "property": each_goods.product_id.get_property_str(),
                            "propertyChildIds": each_goods.product_id.attr_val_str,
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
            self.build_ext(order, data)

            return self.res_ok(data["data"])

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))

    def build_traces(self, order, data):
        pass

    def build_ext(self, order, data):
        pass

    @http.route('/wxa/<string:sub_domain>/order/close', auth='public', method=['GET', 'POST'], csrf=False)
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
            return self.res_err(-1, str(e))


    @http.route('/wxa/<string:sub_domain>/order/delivery', auth='public', method=['GET', 'POST'], csrf=False)
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
            return self.res_err(-1, str(e))


