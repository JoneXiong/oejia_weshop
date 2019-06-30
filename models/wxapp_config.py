# -*- coding: utf-8 -*-

from odoo import models, fields, api


class WxappConfig(models.Model):

    _name = 'wxapp.config'
    _description = u'对接设置'
    _rec_name = 'mall_name'

    sub_domain = fields.Char('小程序接口前缀', help='小程序访问的接口url前缀', index=True, required=True)

    mall_name = fields.Char('商城名称', help='显示在小程序顶部')

    app_id = fields.Char('appid')
    secret = fields.Char('secret')

    wechat_pay_id = fields.Char('微信支付商户号')
    wechat_pay_secret = fields.Char('微信支付商户秘钥')

    kdniao_app_id = fields.Char('快递鸟APP ID')
    kdniao_app_key = fields.Char('快递鸟APP key')

    team_id = fields.Many2one('crm.team', string='所属销售渠道', required=True)

    @api.model
    def get_config(self, key, sub_domain, obj=False):
        config = self.search([('sub_domain', '=', sub_domain)])
        if config:
            config = config[0]
            config.ensure_one()
            if obj:
                return config

            if key=='mallName':
                key = 'mall_name'
            return config.__getattribute__(key)
        else:
            return False

    @api.model
    def get_from_team(self, team_id):
        config = self.search([('team_id', '=', team_id)])
        if config:
            config.ensure_one()
            return config
        else:
            return False

    @api.multi
    def clean_all_token(self):
        self.env['wxapp.access_token'].search([]).unlink()

    @api.multi
    def clean_all_token_window(self):
        new_context = dict(self._context) or {}
        new_context['default_info'] = "确认将所有小程序会话 token 清除？"
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
