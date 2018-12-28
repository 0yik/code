from odoo import api, fields, models


class FundRealization(models.Model):
    _name = 'fund.relization'

    @api.depends('fun_relization_line.remaning_amount')
    def _compute_fund_transfer(self):
        for order in self:
            my_amount_remaning = 0.0
            for line in order.fun_relization_line:
                my_amount_remaning += line.remaning_amount
            order.update({
                'amount_transfer': my_amount_remaning,
            })

    company_id = fields.Many2one('res.company', string='Company', readonly=True, copy=False,
                                 default=lambda self: self.env['res.company']._company_default_get())
    docuemnt = fields.Date('Document Date',default=fields.Datetime.now)
    fr_number = fields.Many2one('fund.request','FR Number')
    fun_relization_line = fields.One2many('fund.relization.line','fun_relization_id','Fund Relization Line')
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
            ir_model_data.get_object_reference('fund_request_b2b', 'relization_journal_adjustment_form')[1]
        except ValueError:
            compose_form_id = False
        res = {
            'type': 'ir.actions.act_window',
            'name': 'Accounting Adjustment',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'relization.journal.adjustment',
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
    def onchange_relization_fr_number(self):
        for rec in self:
            if rec.fr_number:
                line_to_create = []
                for request_line in self.fr_number.fun_req_line:
                    line_to_create.append((0, 0, {'emp_id': self.fr_number.emp_id.id,
                                                  'designation': self.fr_number.designation.id,
                                                  'department_id': self.fr_number.department_id.id,
                                                  'currency': request_line.currency.id,
                                                  'total_amount': request_line.amount,
                                                  }))

                rec.update({'fun_relization_line': line_to_create})


class FundRequestLine(models.Model):
    _name = 'fund.relization.line'

    fun_relization_id = fields.Many2one('fund.relization','Fund Transfer')
    emp_id = fields.Many2one('hr.employee','Employee')
    designation = fields.Many2one('hr.job')
    department_id = fields.Many2one('hr.department','Department')
    currency = fields.Many2one('res.currency')
    remaning_amount = fields.Float('Amount Used')
    total_amount = fields.Float('Fund Transfered')
    bank_account = fields.Many2one('account.account', 'Account')