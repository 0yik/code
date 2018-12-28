# -*- coding: utf-8 -*-

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountAgedTrialBalance(models.TransientModel):

    _inherit = 'account.aged.trial.balance'

    currency_id = fields.Many2one('res.currency', string='Currency')
