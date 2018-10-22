# -*- coding: utf-8 -*-

from types import MethodType

from . import base
from . import config
from . import banner
from . import product_category
from . import product
from . import user
from . import address
from . import order


from odoo.http import root, JsonRequest, HttpRequest


def get_request(self, httprequest):
    if 'User-Agent' in httprequest.headers and 'MicroMessenger' in httprequest.headers['User-Agent']:
        return HttpRequest(httprequest)
    if httprequest.args.get('jsonp'):
        return JsonRequest(httprequest)
    if httprequest.mimetype in ("application/json", "application/json-rpc"):
        return JsonRequest(httprequest)
    else:
        return HttpRequest(httprequest)

root.get_request = MethodType(get_request, root)
