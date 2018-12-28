# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountFollowupLine(models.Model):
    _inherit = 'account_followup.followup.line'

    invoice_type = fields.Selection(selection=[('in_invoice', 'Payable'), ('out_invoice', 'Receivable')], string="Type")
    has_todo_list = fields.Boolean(string="To-Do List")
