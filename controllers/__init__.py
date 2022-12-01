# -*- coding: utf-8 -*-
import logging

from types import MethodType

from . import base
from . import config
from . import banner
from . import product_category
from . import product
from . import user
from . import address
from . import order
from . import notice
from . import score
from . import region
from . import message


from odoo.http import root, JsonRequest, HttpRequest

_logger = logging.getLogger(__name__)

def get_request(self, httprequest):
    if 'Referer' in httprequest.headers and 'servicewechat.com' in httprequest.headers['Referer']:
        if not httprequest.accept_languages.best:
            httprequest.session.context["lang"] = 'zh_CN'
        if httprequest.mimetype=="application/json":
            return HttpRequest(httprequest)
    if httprequest.args.get('jsonp'):
        return JsonRequest(httprequest)
    if httprequest.mimetype in ("application/json", "application/json-rpc"):
        return JsonRequest(httprequest)
    else:
        return HttpRequest(httprequest)
root.get_request = MethodType(get_request, root)

origin_get_response = root.get_response
def get_response(self, httprequest, result, explicit_session):
    response = origin_get_response(httprequest, result, explicit_session)
    if hasattr(response, 'headers') and response.headers.get('set-sid'):
        response.headers.set('set-sid', httprequest.session.sid)
    return response
root.get_response = MethodType(get_response, root)

