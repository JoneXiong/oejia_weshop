# -*- coding: utf-8 -*-

import json
import re

from odoo import http
from odoo.http import request
from odoo import release

from .. import defs
from .base import BaseController, dt_convert, UserException, WechatUser

import logging

_logger = logging.getLogger(__name__)


class WxappOrder(http.Controller, BaseController):

    cur_gmt_diff = 8

    def _get_user(self):
        user = None
        if hasattr(request, 'wechat_user') and request.wechat_user:
            user = request.wechat_user.user_id
        return user

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

            province_id = int(kwargs.pop('provinceId')) if kwargs.get('provinceId', 'false')!='false' else False
            city_id = int(kwargs.pop('cityId')) if kwargs.get('cityId', 'false')!='false' else False
            district_id = int(kwargs.pop('districtId')) if kwargs.get('districtId', 'false')!='false' else False
            addr_id = int(kwargs.pop('addrid')) if 'addrid' in kwargs else False
            zipcode = kwargs.pop('code') if 'code' in kwargs else False
            link_man = kwargs.pop('linkMan') if 'linkMan' in kwargs else False

            calculate = kwargs.pop('calculate', False)
            if calculate=='false':
                calculate = False
            remark = kwargs.pop('remark', '')

            goods_price, logistics_price, order_lines, isNeedLogistics = self.parse_goods_json(
                goods_json, province_id, city_id, district_id, calculate
            )
            if not addr_id:
                address = request.env(user=1)['res.partner'].search([
                    ('parent_id', '=', wechat_user.partner_id.id),
                    ('type', '=', 'delivery'),
                    ('is_default', '=', True)
                ], limit=1)
                if address:
                    addr_id = address.id

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
                'partner_shipping_id': addr_id or wechat_user.partner_id.id,
                'user_id': wechat_user.partner_id.user_id.id,
                'goods_price': goods_price,
                'extra': {},
                'entry': entry,
            }
            order_dict.update(kwargs)
            if kwargs.get('extraInfo'):
                try:
                    extraInfo = json.loads(kwargs.get('extraInfo'))
                    order_dict.update(extraInfo)
                except:
                    import traceback;traceback.print_exc()
            order_dict['_params'] = {'calculate': calculate, 'isNeedLogistics': isNeedLogistics}
            order_dict['_params'].update(kwargs)
            _logger.info('>>> order_dict %s', order_dict)
            order_logistics = self.calculate_order_logistics(wechat_user, order_dict, order_lines)
            if order_logistics!=None:
                order_dict['logistics_price'] = order_logistics
            self.after_calculate(wechat_user, order_dict, order_lines)

            if calculate:
                _data = {
                    'score': order_dict.get('need_score', 0),
                    'isNeedLogistics': isNeedLogistics,
                    'amountTotle': round(order_dict['goods_price'], 2),
                    'amountLogistics': order_dict['logistics_price'],
                    'amountTax': order_dict.get('amount_tax', 0),
                    'extra': order_dict['extra']
                }
                _data['amountReal'] = _data['amountTotle'] + _data['amountLogistics'] + _data['amountTax']
                _data.update(self.calculate_ext_info(wechat_user, order_dict, order_lines, _data))
                for line in order_lines:
                    line['price_unit'] = round(line['price_unit'], 2)
                _data['orderLines'] = order_lines
                _data['amountReal'] = round(_data['amountReal'], 2)
            else:
                OrderModel = request.env(user=1)['sale.order']
                user = self._get_user()
                if user:
                    if release.version_info[0]>=14:
                        OrderModel = OrderModel.with_company(user.company_id.id)
                    else:
                        OrderModel = OrderModel.with_context(force_company=user.company_id.id)
                order_dict.pop('goods_price')
                order_dict.pop('extra')
                order_dict.pop('_params')
                line_value_list = []
                for line in order_lines:
                    if 'goods_id' in line:
                        line.pop('goods_id')
                    line_value_list.append((0, 0, line))
                if order_dict['logistics_price']>0:
                    line_value_list.append((0, 0, {
                        'product_id': request.env.ref('oejia_weshop.product_product_delivery_weshop').id,
                        'price_unit': order_dict['logistics_price'],
                        'product_uom_qty': 1,
                    }))
                order_dict['order_line'] = line_value_list
                _logger.info('>>> create order_line %s', order_dict['order_line'])
                vals = order_dict.copy()
                vals.pop('entry', None)
                order = OrderModel.create(vals)

                #mail_template = request.env.ref('wechat_mall_order_create')
                #mail_template.sudo().send_mail(order.id, force_send=True, raise_exception=False)
                if hasattr(order, 'action_accounted'):
                    order.action_accounted(order_dict)
                order.action_created(order_dict)
                _data = {
                    "amountReal": round(order.amount_total, 2),
                    "dateAdd": dt_convert(order.create_date, gmt_diff=entry.gmt_diff),
                    "id": order.id,
                    "orderNumber": order.name,
                    "customer": order.partner_id.name,
                    "status": defs.OrderResponseStatus.attrs[order.customer_status],
                    "statusStr": self.get_statusStr(order),
                }

            return self.res_ok(_data)

        except UserException as e:
            return self.res_err(-99, e.args[0])
        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, '%s'%e)

    def calculate_order_logistics(self, wechat_user, order_dict, order_lines):
        pass

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
            _ids = goods_id_set - set(template_dict.keys())
            _logger.info('>>> _ids %s', _ids)
            _name_list = [e.name for e in request.env['product.template'].sudo().search([('id', 'in', list(_ids))])]
            raise UserException(u'订单中包含已下架的商品: %s' % ','.join(_name_list))

        isNeedLogistics = 0
        for each_goods in goods_json:
            property_child_ids = each_goods.get('propertyChildIds')
            amount = each_goods['number']
            transport_type = each_goods['logisticsType']
            template = template_dict[each_goods['goodsId']]
            if template.type=='product':
                isNeedLogistics = 1

            each_goods_total, line_dict = self.calculate_goods_fee(template, amount, property_child_ids, calculate)
            order_lines.append(line_dict)
            goods_fee += each_goods_total
            each_logistics_price = self.calculate_logistics_fee(template, amount, transport_type, province_id, city_id, district_id)
            logistics_fee += each_logistics_price

        return goods_fee, logistics_fee, order_lines, isNeedLogistics

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
                raise UserException(u'商品不存在！')

            price = product.get_present_price(amount)
            total = price * amount
            property_str = product.name

            stores = product.get_present_qty() - amount
            if not property_child_ids:
                stores = goods.get_present_qty() - amount

            if stores < 0:
                raise UserException(u'%s 库存不足！'%goods.name)
            if stores == 0:
                # todo 发送库存空预警
                pass
            if not calculate:
                product.sudo().change_qty(-amount)
                if not property_child_ids:
                    goods.sudo().change_qty(-amount)

        line_dict = {
            'product_id': product.id,
            'goods_id': goods.id,
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

            domain = self.get_orders_domain(None, **kwargs)
            orders = request.env['sale.order'].sudo().search(domain)
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

    def clean_html(self, content):
        pattern = re.compile(r'<[^>]+>',re.S)
        result = pattern.sub('', content)
        return result

    def _order_basic_dict(self, each_order):
        ret = {
            "amountReal": round(each_order.amount_total, 2),
            "dateAdd": dt_convert(each_order.create_date, gmt_diff=self.cur_gmt_diff),
            "id": each_order.id,
            "remark": self.clean_html(each_order.note),
            "orderNumber": each_order.name,
            "goodsNumber": each_order.number_goods,
            "status": defs.OrderResponseStatus.attrs[each_order.customer_status],
            "statusStr": self.get_statusStr(each_order),
            "score": 0,
        }
        return ret

    def get_statusStr(self, order):
        return defs.OrderStatus.attrs[order.customer_status]

    def get_orders_domain(self, status, **kwargs):
        domain = [('partner_id', '=', request.wechat_user.partner_id.id), ('number_goods', '>', 0)]
        if status and status!='9' and status.isdigit():
            domain.append(('customer_status', '=', defs.OrderRequestStatus.attrs[int(status)]))
        return domain

    @http.route('/wxa/<string:sub_domain>/order/list', auth='public', method=['GET', 'POST'], csrf=False)
    def list(self, sub_domain, token=None, status=None, **kwargs):
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res

            kwargs['entry'] = entry
            domain = self.get_orders_domain(status, **kwargs)
            orders = request.env['sale.order'].sudo().search(domain, order='id desc', limit=30)
            delivery_product_id = request.env.ref('oejia_weshop.product_product_delivery_weshop').id
            self.cur_gmt_diff = entry.gmt_diff
            data = {
                "logisticsMap": {},
                "orderList": [self._order_basic_dict(each_order) for each_order in orders],
                "goodsMap": {
                    each_order.id: [
                        {
                            "pic": each_goods.product_id.product_tmpl_id.main_img,
                            "number": each_goods.product_uom_qty,
                            "name": each_goods.name,
                            "price": each_goods.price_unit,
                            "sku": each_goods.product_id.get_property_str(),
                            "product_uom": each_goods.product_uom.name,
                            "prodId": each_goods.product_id.product_tmpl_id.id,
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
            if res:
                if entry and kwargs.get('access_token'):
                    pass
                else:
                    return res

            if not order_id:
                return self.res_err(300)

            if kwargs.get('access_token'):
                order = request.env['sale.order'].sudo().search([
                    ('access_token', '=', kwargs.get('access_token')),
                    ('id', '=', int(order_id))
                ])
                if order:
                    wechat_user = WechatUser(order.partner_id, request.env.user)
            else:
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
                        "amountTax": round(order.amount_tax, 2),
                        "amountReal": round(order.amount_total, 2),
                        "dateAdd": dt_convert(order.create_date, gmt_diff=entry.gmt_diff),
                        "dateUpdate": dt_convert(order.write_date, gmt_diff=entry.gmt_diff),
                        "goodsNumber": order.number_goods,
                        "id": order.id,
                        "orderNumber": order.name,
                        "remark": self.clean_html(order.note),
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
                            "product_uom": each_goods.product_uom.name,
                            "orderId": order.id,
                            "pic": each_goods.product_id.product_tmpl_id.main_img,
                            "property": each_goods.product_id.get_property_str(),
                            "propertyChildIds": each_goods.product_id.attr_val_str,
                        } for each_goods in order.order_line if each_goods.product_id.id!=delivery_product_id
                    ],
                    "logistics": {
                        "address": order.address,
                        "provinceId": order.province_id.id,
                        "cityId": order.city_id.id,
                        "districtId": order.district_id.id or 0,
                        "provinceStr": order.province_id.name,
                        "cityStr": order.city_id.name,
                        "areaStr": order.district_id.name,
                        "linkMan": order.linkman,
                        "mobile": order.mobile,
                        "code": order.zipcode,
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
            order.get_detail_ext(data)

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

            order.action_receive()

            #mail_template = request.env.ref('wechat_mall_order_confirmed')
            #mail_template.sudo().send_mail(order.id, force_send=True, raise_exception=False)

            return self.res_ok()

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))


