# -*- coding: utf-8 -*-

from odoo import models, fields, api

from .. import defs


class WxappUser(models.Model):

    _name = 'wxapp.user'
    _description = u'小程序用户'
    _inherits = {'res.partner': 'partner_id'}

    name = fields.Char(related='partner_id.name',string='名称', inherited=True)
    nickname = fields.Char('昵称')

    open_id = fields.Char('OpenId', required=True, index=True, readonly=True)
    union_id = fields.Char('UnionId', readonly=True)
    gender = fields.Integer('gender')
    language = fields.Char('语言')
    phone = fields.Char('手机号码')
    country = fields.Char('国家')
    province = fields.Char('省份')
    city = fields.Char('城市')
    avatar = fields.Html('头像', compute='_compute_avatar')
    avatar_url = fields.Char('头像链接')
    register_ip = fields.Char('注册IP')
    last_login = fields.Datetime('登陆时间')
    ip = fields.Char('登陆IP')
    status = fields.Selection(defs.WechatUserStatus.attrs.items(), string='状态', default=defs.WechatUserStatus.default)
    register_type = fields.Selection(defs.WechatUserRegisterType.attrs.items(), string='注册来源', default=defs.WechatUserRegisterType.app)

    partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict', string='关联联系人', auto_join=True) #
    address_ids = fields.One2many('res.partner', compute='_compute_address_ids', string='收货地址')

    _sql_constraints = [(
        'wxapp_user_union_id_unique',
        'UNIQUE (union_id, create_uid)',
        'wechat user union_id with create_uid is existed！'
    ),
        (
            'wxapp_user_open_id_unique',
            'UNIQUE (open_id, create_uid)',
            'wechat user open_id with create_uid is existed！'
        ),
    ]

    @api.multi
    @api.depends('avatar_url')
    def _compute_avatar(self):
        for each_record in self:
            if each_record.avatar_url:
                each_record.avatar = """
                <img src="{avatar_url}" style="max-width:100px;">
                """.format(avatar_url=each_record.avatar_url)
            else:
                each_record.avatar = False

    @api.depends('partner_id')
    def _compute_address_ids(self):
        for obj in self:
            obj.address_ids = obj.partner_id.child_ids.filtered(lambda r: r.type == 'delivery')
