# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from openerp import models, fields, api, _, tools
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp

class MilestoneContractBookings(models.Model):
    _name = 'milestone.contract.bookings'
    _rec_name = 'milestone_id'

    milestone_id = fields.Many2one('milestone.milestone', string="Appointments")
    date = fields.Date('Date')
    start_time = fields.Float('Start Time', help='24-Hours format (00.00 to 24:00)')
    end_time = fields.Float('End Time', help='24-Hours format (00.00 to 24:00)')
    location = fields.Char('Location')
    vendor_ids = fields.Many2many('res.partner', string='Vendor', domain=[('supplier', '=', True)])
    state = fields.Selection(
        [('draft', 'Pending'), ('approved', 'Approved'), ('reject', 'Rejected'), ('done', 'Completed')], 'Status',
        default='draft', store=True)
    account_analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Contract')