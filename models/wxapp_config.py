# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class Platform(object):

    def __init__(self, val):
        self.val = val

    def __get__(self, obj, objtype):
        return self.val

    def __set__(self, obj, val):
        self.val = val


class WxappConfig(models.Model):

    _name = 'wxapp.config'
    _description = u'对接设置'
    _rec_name = 'mall_name'
    _platform = Platform('wxapp')

    sub_domain = fields.Char('接口前缀', help='商城访问的接口url前缀', index=True, required=True, default='oejia')

    mall_name = fields.Char('商城名称', help='显示在顶部')

    app_id = fields.Char('AppId')
    secret = fields.Char('Secret')

    team_id = fields.Many2one('crm.team', string='所属销售渠道', required=True)

    def need_login(self):
        return False

    def get_config(self, key):
        if key=='mallName':
            key = 'mall_name'
        if hasattr(self, key):
            return self.__getattribute__(key)
        else:
            return None

    @api.model
    def get_entry(self, sub_domain):
        # mirror 默认使用平台的配置
        if sub_domain in ['mirror']:
            entry = self.env.ref('oejia_weshop.wxapp_config_data_1')
            entry._platform = sub_domain
            return entry
        config = self.search([('sub_domain', '=', sub_domain)])
        if config:
            config.ensure_one()
            config._platform = 'wxapp|%s' % config.id
            return config
        else:
            return False

    def get_id(self):
        if self._platform in ['mirror']:
            return self.id
        else:
            return int(self._platform.replace('wxapp|', ''))

    @api.model
    def get_from_team(self, team_id):
        config = self.search([('team_id', '=', team_id)])
        if config:
            config.ensure_one()
            return config
        else:
            return False

    @api.model
    def get_from_id(self, id):
        return self.browse(id)

    @api.multi
    def clean_all_token(self):
        self.env['wxapp.access_token'].search([]).unlink()

    @api.multi
    def clean_all_token_window(self):
        new_context = dict(self._context) or {}
        new_context['default_info'] = "确认将所有会话 token 清除？"
        new_context['default_model'] = 'wxapp.config'
        new_context['default_method'] = 'clean_all_token'
        new_context['record_ids'] = [obj.id for obj in self]
        return {
            'name': u'确认清除',
            'type': 'ir.actions.act_window',
            'res_model': 'wxapp.confirm',
            'res_id': None,
            'view_mode': 'form',
            'view_type': 'form',
            'context': new_context,
            'view_id': self.env.ref('oejia_weshop.confirm_view_form').id,
            'target': 'new'
        }

    def get_level(self):
        return 0

    def get_ext_config(self):
        return {}
