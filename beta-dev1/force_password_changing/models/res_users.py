# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
import re

from openerp import api, fields, models, _

def delta_now(**kwargs):
    dt = datetime.now() + timedelta(**kwargs)
    return fields.Datetime.to_string(dt)

    
class Password(models.Model):
    _inherit = 'res.password'
    
    lock_after = fields.Integer('Lock account after')
    change_before = fields.Integer('Force changing password every')
    
class ResUsers(models.Model):
    _inherit = 'res.users'
    
    password_write_date = fields.Datetime(
        'Latest password update', readonly=True
    )

    @api.model
    def create(self, vals, ):
        vals['password_write_date'] = fields.Datetime.now()
        return super(ResUsers, self).create(vals)

    @api.multi
    def write(self, vals, ):
        if vals.get('password'):
            vals['password_write_date'] = fields.Datetime.now()
        return super(ResUsers, self).write(vals)
    
    @api.multi
    def _password_has_expired(self, ):
        if not self.password_write_date:
            return True
        write_date = fields.Datetime.from_string(self.password_write_date)
        today = fields.Datetime.from_string(fields.Datetime.now())
        days = (today - write_date).days
        month= self.env['res.password'].search([]).change_before
        return (days > month*30)

    @api.multi
    def action_expire_password(self):
        expiration = delta_now(days=+1)
        for rec_id in self:
            rec_id.mapped('partner_id').signup_prepare(
                signup_type="reset", expiration=expiration
            )
    