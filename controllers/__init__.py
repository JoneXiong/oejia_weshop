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
        lang = httprequest.session.context.get('lang','')
        if lang!='zh-CN':
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


from odoo.http import session_gc

WXAPP_SID = None

def setup_session(self, httprequest):
    # recover or create session
    session_gc(self.session_store)

    sid = httprequest.args.get('session_id')
    explicit_session = True
    if not sid:
        sid = httprequest.headers.get("X-Openerp-Session-Id")
    if not sid:
        sid = httprequest.cookies.get('session_id')
        explicit_session = False
    wxapp_flag = 'Referer' in httprequest.headers and 'servicewechat.com' in httprequest.headers['Referer']
    global WXAPP_SID
    if wxapp_flag and WXAPP_SID:
        sid = WXAPP_SID
    if sid is None:
        httprequest.session = self.session_store.new()
        if wxapp_flag:
            WXAPP_SID = httprequest.session.sid
    else:
        httprequest.session = self.session_store.get(sid)
    return explicit_session
root.setup_session = MethodType(setup_session, root)
