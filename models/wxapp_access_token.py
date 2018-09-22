# -*- coding: utf-8 -*-

import time

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from odoo import models, fields, api, exceptions


class AccessToken(models.TransientModel):

    _name = 'wxapp.access_token'
    _description = u'assess token'

    # allow session to survive for 30min in case user is slow
    _transient_max_hours = 2

    token = fields.Char('token', index=True)
    session_key = fields.Char('session_key', required=True)
    open_id = fields.Char('open_id', required=True)

    @api.model
    def create(self, vals):
        record = super(AccessToken, self).create(vals)
        record.write({'token': record.generate_token(vals['sub_domain'])})
        return record

    def generate_token(self, sub_domain):
        config = self.env['wxapp.config']
        secret_key = config.get_config('secret', sub_domain)
        app_id = config.get_config('app_id', sub_domain)
        if not secret_key or not app_id:
            raise exceptions.ValidationError('未设置 secret_key 或 appId')

        s = Serializer(secret_key=secret_key, salt=app_id, expires_in=AccessToken._transient_max_hours * 3600)
        timestamp = time.time()
        return s.dumps({'session_key': self.session_key, 'open_id': self.open_id, 'iat': timestamp})
