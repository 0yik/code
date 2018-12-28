# -*- coding: utf-8 -*-

import bcrypt
import odoo
from datetime import datetime
from odoo.tools.translate import _
from odoo.exceptions import UserError
from odoo import api, fields, models, tools
from odoo.addons.base.ir.ir_mail_server import MailDeliveryException
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_TIME_FORMAT


class ResUsers(models.Model):
    _inherit = 'res.users'

    login_attempt = fields.Integer(default=0)
    user_oldpassword_ids = fields.One2many('user.oldpassword', 'user_id')
    password_change_date = fields.Date()
    
    @api.multi
    def _change_password_reminder(self):
        if self.env["ir.config_parameter"].get_param("activate_password_validation"):
            for user in self.search([]):
                if (user.password_change_date and user.email):
                    days_to_remind = int(self.env["ir.config_parameter"].get_param("change_reminder_days") or 0)
                    if (days_to_remind + 1) == (datetime.now() - datetime.strptime(user.password_change_date, DEFAULT_SERVER_DATE_FORMAT)).days:
                        template = self.env.ref('password_validation_security.mail_template_account_block_maximum_login_attempt')
                        template.with_context(lang=user.lang,days=days_to_remind).send_mail(user.id, force_send=True)
        return True

    
    @api.multi
    def reset_login_attempt(self):
        for rec in self:
            rec.login_attempt = 0
        return True
    
    @api.model
    def check_credentials(self, password):
        self.env.cr.execute('SELECT password, password_crypt FROM res_users WHERE id=%s AND active', (self.env.uid,))
        encrypted = None
        user = self.env.user
        if self.env.cr.rowcount:
            stored, encrypted = self.env.cr.fetchone()
        try:
            return super(ResUsers, self).check_credentials(password)
        except ValueError:
            try:
                if encrypted:
                    if bcrypt.checkpw(password.encode('utf8'), bytes(encrypted)):
                        return
                    else:
                        raise odoo.exceptions.AccessDenied
            except ValueError:
                raise odoo.exceptions.AccessDenied
        except odoo.exceptions.AccessDenied:
            try:
                if encrypted:
                    if bcrypt.checkpw(password.encode('utf8'), bytes(encrypted)):
                        return
                    else:
                        raise
            except ValueError:
                raise odoo.exceptions.AccessDenied
    
    
    def _set_password(self, password):
        self.ensure_one()
        self.password_change_date = datetime.now()
        encrypted = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(rounds=12))
        self.env.cr.execute("INSERT INTO user_oldpassword (name, user_id) VALUES (%s, %s)",(encrypted, self.id))
        self._set_encrypted_password(encrypted)
        

class UserOldPassword(models.Model):
    
    _name = 'user.oldpassword'
    _order = 'id DESC'
    
    name = fields.Char()
    user_id = fields.Many2one()
