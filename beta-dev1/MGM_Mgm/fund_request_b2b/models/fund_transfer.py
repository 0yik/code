from odoo import api, fields, models


class FundTransfer(models.Model):
    _name = 'fund.transfer'

    @api.depends('fun_trans_line.amount_transfer')
    def _compute_fund_transfer(self):
        for order in self:
            my_amount_transfer = 0.0
            for line in order.fun_trans_line:
                my_amount_transfer += line.amount_transfer
            order.update({
                'amount_transfer': my_amount_transfer,
            })

    docuemnt = fields.Date('Document Date',default=fields.Datetime.now)
    request_date = fields.Date('Transfer Date')
    fr_number = fields.Many2one('fund.request','FR Number')
    bank_account = fields.Many2one('account.account','Account')
    fun_trans_line = fields.One2many('fund.transfer.line','fun_trans_id','Fund Transfer Line')
    state = fields.Selection([
        ('unposted', 'Unposted'),
        ('posted', 'Posted'),
    ], string='Status', copy=False, store=True, default='unposted')
    amount_transfer = fields.Float(string='Total', store=True, readonly=True, compute='_compute_fund_transfer', track_visibility='always')
    move_id = fields.Many2one('account.move','Move')

    @api.multi
    def fund_post(self):
        ir_model_data = self.env['ir.model.data']
        try:
            compose_form_id = \
            ir_model_data.get_object_reference('fund_request_b2b', 'journal_adjustment_form')[1]
        except ValueError:
            compose_form_id = False
        res = {
            'type': 'ir.actions.act_window',
            'name': 'Accounting Adjustment',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'journal.adjustment',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': {}
        }
        return res

    @api.multi
    def open_journal_entry(self):
        invoices = self.mapped('move_id')
        action = self.env.ref('account.action_move_journal_line').read()[0]
        if invoices:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.onchange('fr_number')
    def onchange_fr_number(self):
        for rec in self:
            if rec.fr_number:
                line_to_create = []
                for line in rec.fr_number.fun_req_line:
                    line_to_create.append((0, 0, {
                        'emp_id': line.emp_id.id,
                        'designation': line.designation.id,
                        'department_id': line.department_id.id,
                        'currency': line.currency.id,
                        'amount': line.amount
                    }))
                rec.update({'fun_trans_line': line_to_create})


class FundRequestLine(models.Model):
    _name = 'fund.transfer.line'

    fun_trans_id = fields.Many2one('fund.transfer','Fund Transfer')
    emp_id = fields.Many2one('hr.employee','Employee')
    designation = fields.Many2one('hr.job')
    department_id = fields.Many2one('hr.department','Department')
    currency = fields.Many2one('res.currency')
    amount = fields.Float('Amount')
    amount_transfer = fields.Float('Amount Transfered')