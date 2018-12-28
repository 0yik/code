# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date

class helpdesk_ticket(models.Model):
    _inherit = 'helpdesk.ticket'

    name = fields.Char(string='Name')
    employer_name = fields.Char(string='Employer Name')
    company_name  = fields.Char(string='Company Name')
    contract_person = fields.Char(string='Contact Person')
    contract_mobile = fields.Char(string='Contact No (Mobile)')
    contract_hom     = fields.Char(string='Contact No (Hom)')
    contract_work    = fields.Char(string='Contact No (Work)')
    email  = fields.Char(string='Char')
    nature_of_business = fields.Char(string='Nature of Business')
    mailling = fields.Char(string='Mailling Address')
    postal_code = fields.Char(string='Postal Code')
    nature_of_call=fields.Many2one('helpdesk.ticket.notes',string="Nature Of Call")
    nric_fin    = fields.Char(string='NRIC FIN')
    passpost_no = fields.Char(string='Passport No')
    roc_no      = fields.Char(string='ROC No')
    nationality = fields.Many2one('res.country', string='nationality')
    date_birth  = fields.Date(string='Date of Birth')
    age  = fields.Integer(string='Age')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string='Gender')
    marital_status = fields.Selection([('marital', 'Marital'), ('unmarital', 'Unmarital')], string='Marital Status')
    occupation = fields.Char(string='Occupation:')
    license_pass_date = fields.Date(string='License Pass Date')
    driving_experience = fields.Float(string='Driving Experience')
    years_arf = fields.Integer(string='Years with ARF')
    dnc = fields.Boolean(string='DNC')
    pdpa_opt_out = fields.Boolean(string='PDPA Opt Out')
    completely   = fields.Boolean(string='Completely')
    sms          = fields.Boolean(string='SMS')
    fax          = fields.Boolean(string='FAX')
    call         = fields.Boolean(string='CALL')
    no_form      = fields.Boolean(string='No Form')

    history_ids      = fields.One2many('helpdesk.ticket.email', 'ticket_id', readonly=False, string='Email History')
    completed_ids    = fields.One2many('helpdesk.ticket.completed','completed_id',string='Completed Form')
    renewal_ids      = fields.One2many('helpdesk.ticket.renewal','renewal_id',string='Renewal Notice')
    cover_ids        = fields.One2many('helpdesk.ticket.cover','cover_id',string='Cover Note')
    policy_ids       = fields.One2many('helpdesk.ticket.policy', 'policy_id', string='Policy')
    notes_ids        = fields.One2many('helpdesk.ticket.notes', 'notes_id', string='Notes History')
    # customer_name=fields.Many2one('res.partner', string="Customer Name:")
    date_time_created=fields.Datetime(string='Date and time',readonly=True, index=True, default=fields.Datetime.now)
    ticket_number = fields.Char('Ticket Number')
    date_create = fields.Date('Date')
    @api.model
    def create(self, vals):
        res = super(helpdesk_ticket, self).create(vals)
        res.update({
            'ticket_number': res.id,
            'date_create': date.today()
        })
        return res


    @api.multi
    def action_reply(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail.inbox',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'email_to': True,
                'default_model': 'helpdesk.ticket',
                'default_res_id': self.id,
            }

        }
    @api.multi
    def action_forward(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail.inbox',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'email_to': True,
                'default_model': 'helpdesk.ticket',
                'default_res_id': self.id,
            }
        }
