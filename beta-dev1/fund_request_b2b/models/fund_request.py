from odoo import api, fields, models

class FundRequest(models.Model):
    _name = 'fund.request'

    company_id = fields.Many2one('res.company', string='Company', readonly=True, copy=False,
                                 default=lambda self: self.env['res.company']._company_default_get())

    name = fields.Char('Name')
    docuemnt = fields.Date('Document Date',default=fields.Datetime.now)
    request_date = fields.Date('Request Date')
    approver = fields.Many2one('res.users','Approver')
    so_id = fields.Many2one('sale.order','Project Number')
    contract_id = fields.Many2one('sale.requisition', 'Contract Number')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('tobe_approved', 'To be approved'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', copy=False, store=True, default='draft')

    fun_req_line = fields.One2many('fund.request.line','fun_req_id','Fund Request Line')
    emp_id = fields.Many2one('hr.employee', 'Employee')
    designation = fields.Many2one('hr.job')
    department_id = fields.Many2one('hr.department', 'Department')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('fund.request')
        result = super(FundRequest, self).create(vals)
        return result

    @api.multi
    def request_approval(self):
        for rec in self:
            rec.state = 'tobe_approved'

    @api.multi
    def request_approved(self):
        for rec in self:
            rec.state = 'approved'

    @api.multi
    def request_rejected(self):
        for rec in self:
            rec.state = 'rejected'

class FundRequestLine(models.Model):
    _name = 'fund.request.line'

    fun_req_id = fields.Many2one('fund.request','Fund Request')

    type_of_expense = fields.Char('Type Of Expense')
    currency = fields.Many2one('res.currency')
    amount = fields.Float('Amount')
    status = fields.Selection([
        ('orignal', 'Orignal'),
        ('revised', 'Revised'),
    ], string='Status',copy=False, store=True, default='orignal')

    @api.onchange('emp_id')
    def onchange_employee(self):
        for rec in self:
            if rec.emp_id:
                rec.designation = rec.emp_id.job_id.id
                rec.department_id = rec.emp_id.department_id.id



