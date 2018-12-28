# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang

import odoo.addons.decimal_precision as dp

class Loyalty(models.Model):
    _name = 'loyalty.loyalty'

    date = fields.Date('Date')
    points_earned = fields.Integer('Points earned')
    activity = fields.Char('Activity')
    partner_id = fields.Many2one('res.partner', string="Partner")

class Redeem(models.Model):
    _name = 'redeem.redeem'

    date = fields.Date('Date')
    redeemed_points = fields.Integer('Redeemed Points')
    redeemed_for = fields.Char('Redeemed For')
    partner_id = fields.Many2one('res.partner', string="Partner")