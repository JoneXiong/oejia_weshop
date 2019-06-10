# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request

from .. import defs
from .base import BaseController

import logging

_logger = logging.getLogger(__name__)


class WxappAddress(http.Controller, BaseController):

    @http.route('/<string:sub_domain>/user/amount', auth='public', methods=['GET'])
    def user_amount(self, sub_domain, token=None):
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res
            _data = {
                'balance': hasattr(wechat_user, 'balance') and wechat_user.balance or 0,
                'freeze': 0,
                'score': 0,
                'totleConsumed': 0,
            }
            return self.res_ok(_data)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))

    def _get_address_dict(self, each_address, wxapp_user_id):
        _dict = {
            "address": each_address.street,
            "areaStr": each_address.district_id.name or '',
            "cityId": each_address.city_id.id,
            "cityStr": each_address.city_id.name,
            "code": each_address.zip,
            "dateAdd": each_address.create_date,
            "dateUpdate": each_address.write_date,
            "districtId": each_address.district_id.id or False,
            "id": each_address.id,
            "isDefault": each_address.is_default,
            "linkMan": each_address.name,
            "mobile": each_address.mobile,
            "provinceId": each_address.province_id.id,
            "provinceStr": each_address.province_id.name,
            "status": 0 if each_address.active else 1,
            "statusStr": '正常' if each_address.active else '禁用',
            "uid": each_address.create_uid.id,
            "userId": wxapp_user_id
        }
        return _dict

    @http.route('/<string:sub_domain>/user/shipping-address/list', auth='public', methods=['GET'])
    def list(self, sub_domain, token=None):
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res

            if not wechat_user.address_ids:
                return self.res_err(700)

            data = [self._get_address_dict(each_address, wechat_user.id) for each_address in wechat_user.address_ids.filtered(lambda r: r.active)]
            return self.res_ok(data)

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))


    @http.route('/<string:sub_domain>/user/shipping-address/add', auth='public', methods=['GET','POST'], csrf=False, type='http')
    def add(self, sub_domain, **kwargs):
        try:
            token = kwargs.get('token', None)

            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res

            new_address = request.env(user=1)['res.partner'].create({
                'parent_id': wechat_user.partner_id.id,
                'name': kwargs['linkMan'],
                'mobile': kwargs['mobile'],
                'province_id': int(kwargs['provinceId']),
                'city_id': int(kwargs['cityId']),
                'district_id': int(kwargs['districtId']) if kwargs.get('districtId') else False,
                'street': kwargs['address'],
                'zip': kwargs['code'],
                'type': 'delivery',
                'is_default': json.loads(kwargs['isDefault'])
            })

            address_ids = wechat_user.address_ids.filtered(lambda r: r.id != new_address.id)
            if address_ids:
                address_ids.write({'is_default': False})

            return self.res_ok()

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))


    @http.route('/<string:sub_domain>/user/shipping-address/update', auth='public', methods=['GET','POST'], csrf=False, type='http')
    def update(self, sub_domain, **kwargs):
        try:
            token = kwargs.get('token', None)

            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res

            address = request.env(user=1)['res.partner'].browse(int(kwargs['id']))

            if not address:
                return self.res_err(404)

            address.write({
                'name': kwargs['linkMan'] if kwargs.get('linkMan') else address.name,
                'mobile': kwargs['mobile'] if kwargs.get('mobile') else address.mobile,
                'province_id': int(kwargs['provinceId']) if kwargs.get('provinceId') else address.province_id.id,
                'city_id': int(kwargs['cityId']) if kwargs.get('cityId') else address.city_id.id,
                'district_id': int(kwargs['districtId']) if kwargs.get('districtId') else address.district_id.id,
                'street': kwargs['address'] if kwargs.get('address') else address.street,
                'zip': kwargs['code'] if kwargs.get('code') else address.zip,
                'is_default': json.loads(kwargs['isDefault'])
            })

            address_ids = wechat_user.address_ids.filtered(lambda r: r.id != address.id)
            if address_ids:
                address_ids.write({'is_default': False})

            return self.res_ok()

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))


    @http.route('/<string:sub_domain>/user/shipping-address/delete', auth='public', methods=['GET'])
    def delete(self, sub_domain, token=None, id=None, **kwargs):
        address_id = id
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res

            if not address_id:
                return self.res_err(300)

            address = request.env(user=1)['res.partner'].browse(int(address_id))

            if not address:
                return self.res_err(404)

            address.unlink()

            if wechat_user.address_ids:
                wechat_user.address_ids[0].write({'is_default': True})

            return self.res_ok()

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))


    @http.route('/<string:sub_domain>/user/shipping-address/default', auth='public', methods=['GET'])
    def default(self, sub_domain, token=None, **kwargs):
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res

            address = request.env(user=1)['res.partner'].search([
                ('parent_id', '=', wechat_user.partner_id.id),
                ('type', '=', 'delivery'),
                ('is_default', '=', True)
            ], limit=1)

            if not address:
                return self.res_err(404)

            return self.res_ok(self._get_address_dict(address, wechat_user.id))

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))


    @http.route('/<string:sub_domain>/user/shipping-address/detail', auth='public', methods=['GET'])
    def detail(self, sub_domain, token=None, id=None, **kwargs):
        address_id = id
        try:
            res, wechat_user, entry = self._check_user(sub_domain, token)
            if res:return res

            if not address_id:
                return self.res_err(300)

            address = request.env(user=1)['res.partner'].browse(int(address_id))

            if not address:
                return self.res_err(404)

            return self.res_ok(self._get_address_dict(address, wechat_user.id))

        except Exception as e:
            _logger.exception(e)
            return self.res_err(-1, str(e))
