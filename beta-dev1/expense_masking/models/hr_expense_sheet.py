from odoo import api, fields, models

class hr_expense_sheet(models.Model):
    # _name='hr.expense.sheet'
    _inherit = 'hr.expense.sheet'

    @api.one
    @api.depends('expense_line_ids', 'expense_line_ids.total_amount', 'expense_line_ids.currency_id')
    def _compute_amount_expense_sheet(self):
        for record in self:
            record.amount_untaxed = sum(record.expense_line_ids.mapped('untaxed_amount'))
            for expense in record.expense_line_ids:
                record.amount_tax += sum(expense.mapped('tax_ids.amount'))*expense.untaxed_amount/100
                record.amount_total   = record.amount_untaxed + record.amount_tax

    refused_reason  = fields.Char('Refused Reason')
    date            = fields.Date('Date',default=fields.Date.today(),readonly=True,store=True)
    description     = fields.Text('Description')
    note            = fields.Text(string="Note")
    state           = fields.Selection([
                              ('submit', 'To Submit'),
                              ('submited', 'Submitted'),
                              ('approve', 'Approved'),
                              ('post', 'Posted'),
                              ('done', 'Paid'),
                              ('cancel', 'Refused')
                              ], string='Status', index=True, readonly=True, track_visibility='onchange', copy=False,
                             default='submit', required=True,
                             help='Expense Report State')
    payment_mode = fields.Selection([("own_account", "Employee (to reimburse)"), ("company_account", "Company")], store=True,related=False,default='own_account', string="Payment By",readonly=False)
    expense_line_ids    = fields.One2many('hr.expense', 'sheet_id', string='Expense Lines',
                                       states={'done': [('readonly', True)], 'post': [('readonly', True)]})
    amount_untaxed = fields.Monetary(string='Untaxed Amount',
                                     store=True, readonly=True, compute='_compute_amount_expense_sheet', track_visibility='always')
    amount_tax = fields.Monetary(string='Tax',
                                 store=True, readonly=True, compute='_compute_amount_expense_sheet')
    amount_total = fields.Monetary(string='Total',
                                   store=True, readonly=True, compute='_compute_amount_expense_sheet')

    @api.one
    def action_submited(self):
        self.write({'state':'submited'})
        for line in self.expense_line_ids:
        # hr_expense_obj = self.env['hr.expense'].browse(self.expense_line_ids.id)
            line.write({'state':'reported'})

    @api.depends('payment_mode')
    @api.onchange('payment_mode')
    def onchange_payment_mode(self):
        for expense in self.expense_line_ids:
            expense.write({'payment_mode':self.payment_mode})

class hr_expense(models.Model):
    _inherit= 'hr.expense'

    @api.onchange('product_id')
    def update_price(self):
         self.unit_amount = self.product_id.list_price

    @api.onchange('unit_amount','quantity')
    def update_total(self):
        self.total_amount       = self.unit_amount* self.quantity
        self.total_amount_sub   = self.total_amount

    date                 = fields.Date(readonly=False)
    sheet_id             = fields.Many2one('hr.expense.sheet')
    product_id           = fields.Many2one('product.product',domain=[('can_be_expensed', '=', True)],string="Product",copy=True,readonly=False)
    name                 = fields.Text(required=True,default=lambda self: self.product_id.description)
    total_amount_sub     = fields.Float()
    payment_mode         = fields.Selection([("own_account", "Employee (to reimburse)"), ("company_account", "Company")],
                                    default='own_account',
                                    states={'done': [('readonly', True)], 'post': [('readonly', True)]},
                                    string="Payment By")
    currency_id          = fields.Many2one('res.currency', string='Currency', readonly=False)
    unit_amount          = fields.Float(string='Unit Price', readonly=False, required=True)
    quantity             = fields.Float(required=True, readonly=False,default=1)

    @api.model
    def create(self,vals):
        if vals.get('sheet_id',False):
            vals.update({'payment_mode' : self.env['hr.expense.sheet'].browse(vals['sheet_id']).payment_mode})
            res = super(hr_expense, self).create(vals)
            return res
        res = super(hr_expense, self).create(vals)
        return res


    @api.depends('sheet_id', 'sheet_id.account_move_id', 'sheet_id.state')
    def _compute_state(self):
        for expense in self:
            if not expense.sheet_id or expense.sheet_id.state == 'submit':
                expense.state = "draft"
            elif not expense.sheet_id.account_move_id and expense.sheet_id.state == 'cancel':
                expense.state = "reported"
            elif expense.sheet_id.state == "cancel":
                expense.state = "refused"
            else:
                expense.state = "done"

    class HrExpenseRefuseWizard(models.TransientModel):
        _inherit = "hr.expense.refuse.wizard"

        @api.multi
        def expense_refuse_reason(self):
            self.ensure_one()

            context = dict(self._context or {})
            active_ids = context.get('active_ids', [])
            expense_sheet = self.env['hr.expense.sheet'].browse(active_ids)
            expense_sheet.refuse_expenses(self.description)
            expense_sheet.update({'refused_reason': self.description})
            return {'type': 'ir.actions.act_window_close'}