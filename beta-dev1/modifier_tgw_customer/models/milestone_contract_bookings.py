# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from openerp import models, fields, api, _, tools
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp

class MilestoneContractBookings(models.Model):
    _inherit = 'milestone.contract.bookings'

    partner_id = fields.Many2one('res.partner', string="Partner")
    staff_ids = fields.Many2many('hr.employee', string='Staff')