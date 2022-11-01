# -*- coding: utf-8 -*-
import logging

from types import MethodType
from odoo import release

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

_logger = logging.getLogger(__name__)

if release.version_info[0]>=16:
    from odoo.http import Request
    origin_default_lang = Request.default_lang
    def default_lang(self):
        httprequest = self.httprequest
        if 'Referer' in httprequest.headers and 'servicewechat.com' in httprequest.headers['Referer']:
            _logger.info('>>> default_lang %s', httprequest.accept_languages.best)
            if not httprequest.accept_languages.best:
                return 'zh_CN'
        return origin_default_lang(self)
    Request.default_lang = default_lang
else:
    from odoo.http import root, JsonRequest, HttpRequest
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

