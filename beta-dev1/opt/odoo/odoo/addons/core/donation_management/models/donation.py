# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.tools.misc import formatLang
from odoo.exceptions import UserError

class Donation(models.Model):
    _name = 'donation'
    _inherit = 'mail.thread'
    _description = 'Donation'
    _order = 'id desc'

    @api.depends('journal_id')
    def compute_currency_id(self):
        for record in self:
            record.currency_id = record.journal_id and record.journal_id.currency_id.id or record.journal_id.company_id.currency_id.id

    partner_id = fields.Many2one('res.partner', 'Donor')
    date = fields.Date('Date')
    amount = fields.Float('Amount', track_visibility='always')
    monetary = fields.Boolean('Monetary', default=True)
    non_monetary = fields.Boolean('Non Monetary')
    journal_id = fields.Many2one('account.journal', 'Payment Method')
    currency_id = fields.Many2one('res.currency', compute='compute_currency_id', string='Currency', store=True)
    account_id = fields.Many2one('account.account', 'Account')
    remark = fields.Text('Remarks')
    move_id = fields.Many2one('account.move', string='Journal Entry', copy=False)
    state = fields.Selection([('draft','Draft'),('confirm','Confirmed'),('cancel','Cancelled')], default='draft', string='Status', track_visibility='always')

    @api.depends('partner_id', 'amount')
    def name_get(self):
        result = []
        for record in self:
            name = record.partner_id.name + ': ' + formatLang(self.env, record.amount, currency_obj=record.currency_id)
            result.append((record.id, name))
        return result

    @api.onchange('monetary')
    def onchange_monetary(self):
        if self.monetary:
            self.non_monetary = False
            self.account_id = False

    @api.onchange('non_monetary')
    def onchange_non_monetary(self):
        if self.non_monetary:
            self.monetary = False
            self.journal_id = False
            self.monetary = False

    @api.multi
    def button_confirm(self):
        for record in self:
            if not record.monetary and not record.non_monetary:
                raise UserError('Monetary or Non Monetary must be selected!')

            if record.monetary:
                journal_id = record.journal_id.id
                debit_account_id = record.journal_id.default_debit_account_id.id
                currency_id = record.journal_id.currency_id.id or record.journal_id.company_id.currency_id.id
            else:
                journal_id = self.env['account.journal'].sudo().search([('code','=','MISC')], limit=1)
                debit_account_id = record.account_id.id
                currency_id = journal_id.currency_id.id or journal_id.company_id.currency_id.id
                journal_id = journal_id.id

            company_currency_id = self.env.user.company_id.currency_id.id
            credit_account_id = self.env['ir.model.data'].xmlid_to_object('donation_management.donation_account').id

            debit_line = {
                'name': 'Donation / %s / %s' % (record.partner_id.name, record.amount),
                'account_id': debit_account_id,
                'debit': record.amount,
                'credit': 0.0,
                'journal_id': journal_id,
                'partner_id': record.partner_id.id,
                'currency_id': company_currency_id != currency_id and currency_id or False,
                'amount_currency': company_currency_id != currency_id and record.amount,
            }
            credit_line = {
                'name': 'Donation / %s / %s' % (record.partner_id.name, record.amount),
                'account_id': credit_account_id,
                'credit': record.amount,
                'debit': 0.0,
                'journal_id': journal_id,
                'partner_id': record.partner_id.id,
                'currency_id': company_currency_id != currency_id and currency_id or False,
                'amount_currency': company_currency_id != currency_id and - 1.0 * record.amount,
            }
            move_vals = {
                'ref': 'Donations',
                'date': fields.Datetime.now(),
                'journal_id': journal_id,
                'line_ids': [(0,0,credit_line),(0,0,debit_line)],
            }

            move = self.env['account.move'].create(move_vals)
            move.post()
            record.write({'move_id': move.id, 'state': 'confirm'})

    @api.multi
    def button_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def open_account_move(self):
        action = self.env.ref('account.action_move_journal_line').read()[0]
        action['views'] = [(False, 'form')]
        action['res_id'] = self.move_id.id
        return action

Donation()
