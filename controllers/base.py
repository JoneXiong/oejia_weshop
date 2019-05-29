# -*- coding: utf-8 -*-

import json
from datetime import date, datetime, time
import pytz

from odoo import http, exceptions
from odoo.http import request
from odoo.loglevels import ustr

from .. import defs

import logging

_logger = logging.getLogger(__name__)


error_code = {
    -99: '', # 其他异常
    -2: u'用户名或密码不正确',
    -1: u'服务器内部错误',
    0: u'接口调用成功',
    403: u'禁止访问',
    405: u'错误的请求类型',
    501: u'数据库错误',
    502: u'并发异常，请重试',
    600: u'缺少参数',
    601: u'无权操作:缺少 token',
    602: u'签名错误',
    700: u'暂无数据',
    701: u'该功能暂未开通',
    702: u'资源余额不足',
    901: u'登录超时',
    300: u'缺少参数',
    400: u'域名错误',
    401: u'该域名已删除',
    402: u'该域名已禁用',
    404: u'暂无数据',
    10000: u'微信用户未注册'
}


def json_default(obj):
    """
    Properly serializes date and datetime objects.
    """
    from odoo import fields
    if isinstance(obj, date):
        if isinstance(obj, datetime):
            return fields.Datetime.to_string(obj)
        return fields.Date.to_string(obj)
    return ustr(obj)


class BaseController(object):

    def _check_domain(self, sub_domain):
        wxapp_entry = request.env['wxapp.config'].sudo().search([('sub_domain', '=', sub_domain)])
        if not wxapp_entry:
            return self.res_err(404), None
        return None, wxapp_entry[0]

    def _check_user(self, sub_domain, token):
        wxapp_entry = request.env['wxapp.config'].sudo().search([('sub_domain', '=', sub_domain)])
        if not wxapp_entry:
            return self.res_err(404), None, wxapp_entry

        wxapp_entry =wxapp_entry[0]
        if not token:
            return self.res_err(300), None, wxapp_entry

        access_token = request.env['wxapp.access_token'].sudo().search([
            ('token', '=', token),
            #('create_uid', '=', user.id)
        ])

        if not access_token:
            return self.res_err(901), None, wxapp_entry

        wechat_user = request.env['wxapp.user'].sudo().search([
            ('open_id', '=', access_token.open_id),
            #('create_uid', '=', user.id)
        ])

        if not wechat_user:
            return self.res_err(10000), None, wxapp_entry

        request.wechat_user = wechat_user
        return None, wechat_user, wxapp_entry

    def check_userid(self, token, userid):
        if token and userid:
            _logger.info('>>> check_userid: %s %s', userid, token)
            access_token = request.env(user=1)['wxapp.access_token'].search([
                ('token', '=', token),
            ])
            if not access_token:
                return
            wechat_user = request.env(user=1)['wxapp.user'].search([
                ('open_id', '=', access_token.open_id),
            ])
            if not wechat_user:
                return

            if hasattr(wechat_user, 'user_id') and str(wechat_user.user_id.id)==str(userid):
                request.wechat_user = wechat_user


    def res_ok(self, data=None):
        ret = {'code': 0, 'msg': 'success'}
        if data!=None:
            ret['data'] = data
        return request.make_response(
            headers={'Content-Type': 'json'},
            data=json.dumps(ret, default=json_default)
        )

    def res_err(self, code, data=None):
        ret = {'code': code, 'msg': error_code.get(code) or data}
        if data:
            ret['data'] = data
        return request.make_response(json.dumps(ret))


def convert_static_link(request, html):
    base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
    html = html.replace('<p>', '').replace('</p>', '')
    return html.replace('src="', 'src="{base_url}'.format(base_url=base_url))


def dt_convert(value, return_format='%Y-%m-%d %H:%M:%S'):
    """
    时间的时区转换
    """
    if not value:
        return value
    if not isinstance(value, str):
        value = value.strftime(return_format)
    dt = datetime.strptime(value, return_format)
    pytz_timezone = pytz.timezone('Etc/GMT-8')
    dt = dt.replace(tzinfo=pytz.timezone('UTC'))
    return dt.astimezone(pytz_timezone).strftime(return_format)
