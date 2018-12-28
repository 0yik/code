# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, date

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import calendar
from time import strftime

class ResPartner(models.Model):
    _inherit = 'res.partner'

    followup_days = fields.Selection([
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday')], string="Followup days")


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    @api.depends('partner_id', 'followup_days')
    def get_week_days(self):
        print ">>>>>>>>>>>>>>. "
        for rec in self:
            if rec.followup_days == datetime.today().strftime('%A'):
                rec.today_weekday = True
            else:
                rec.today_weekday = False
            print "rec.followup_days == datetime.datetime.today().strftime('%A') ",rec.followup_days , datetime.today().strftime('%A'), rec.today_weekday

    followup_days = fields.Selection([
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday')], string="Followup days")

    today_weekday = fields.Boolean(string="Today Week day?", compute='get_week_days', store=True)

    @api.onchange('partner_id')
    def get_followup_days(self):
        if self and self.partner_id:
            self.followup_days = self.partner_id.followup_days
