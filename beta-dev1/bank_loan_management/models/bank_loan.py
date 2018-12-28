# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date, time, timedelta
from odoo.exceptions import Warning, UserError

class MailActivity(models.Model):
    _inherit = "mail.activity"

    user_id = fields.Many2one('res.users', string="Created by")
    active = fields.Boolean(compute="_get_active_value", string="Active", default=True, store=True)
    invoice_id = fields.Many2one('account.invoice', string="Invocie ID")


    @api.depends('invoice_id.state')
    def _get_active_value(self):
        print "---self ", self

        for rec in self:
            rec.active = True
            if rec.res_model == 'account.invoice' and rec.invoice_id and rec.invoice_id.state == 'paid':
                mail_act_id = self.env['mail.activity'].sudo().search([('res_id', '=', rec.invoice_id.id), ('res_model', '=','account.invoice')])
                if mail_act_id:
                    rec.active = False

class BankLoanType(models.Model):
    _name = "bank.loan.type"
    # _rec_name = 'disburse_journal_id'

    name = fields.Char(string="Loan Name")
    disburse_journal_id = fields.Many2one("account.journal", string="Disburse Journal")
    payable_account_id = fields.Many2one('account.account', string="Payable Account")
    interest_account_id = fields.Many2one('account.account', string="Interest Account")

class BankLoan(models.Model):
    _name = "bank.loan"
    _description = 'Bank Loan'
    # _inherit = ['mail.thread']
    
    @api.multi
    def _get_residual_amount(self):
        tota_paid_amount    = 0.0
        residual_amount     = 0.0
        
        for o in self:
            principal_amount = o.principal_amount
            for installment in o.computation_line_ids:
                tota_paid_amount += installment.principal_amount if installment.status=='paid'else 0.0
            
            residual_amount = principal_amount - tota_paid_amount
            
            o.principal_residual_amount = residual_amount
            
        
    name = fields.Char(string="Name", copy=False)
    account_id = fields.Many2one('account.account', string="Account")
    # payable_account_id = fields.Many2one('account.account', string="Payable Account")
    # interest_account_id = fields.Many2one('account.account', string="Interest Account")
    state = fields.Selection([('draft', 'Draft'), ('applied', 'Applied'), ('approved', 'Approved'), ('cancel', 'Cancel'), ('locked', 'Locked'),('posted','Posted')], default="draft", track_visibility='onchange')
    # loan_type = fields.Many2one('loan.type', string="Loan Type")
    bank_loan_type = fields.Many2one('bank.loan.type', string="Bank Loan Type")
    principal_amount = fields.Float(string="Principal Amount")
    principal_residual_amount = fields.Float(compute="_get_residual_amount", string="Residual")
    interest = fields.Float(string="Interest")
    period = fields.Integer(string="Period")
    period_type = fields.Selection([('month', 'Month(s)'), ('year', 'Year(s)')], default="month")
    payment_term = fields.Selection([('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('semiannualy', 'Semiannualy'),('annualy', 'Annualy')], default="monthly")
    applied_date = fields.Date(string="Applied Date", default=fields.Date.context_today)
    approved_date = fields.Date(string="Approved Date")
    disbursement_date = fields.Date(string="Disbursement Date")
    note = fields.Text(string="Note")
    vendor_id = fields.Many2one("res.partner", string="Vendor")

    # disburse_journal_id = fields.Many2one("account.journal", string="Disburse Journal")
    board_journal_id = fields.Many2one("account.journal", string="Repayment Board Journal")
    interest_journal_id = fields.Many2one("account.journal", string="Interest Journal")
    company_account_id = fields.Many2one("account.account", string="Company Account")
    move_id = fields.Many2one('account.move', string="Accounting Entry")
    computation_line_ids = fields.One2many('loan.computation', 'loan_id', string="Computation")
    branch_id = fields.Many2one('res.branch', string="Branch")
    method_type = fields.Selection([('flat','Flat'),('annuity','Annuity'),('effective','Effective')], string='Method')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('bank.loan')
        if vals.has_key('principal_amount') and vals.get('principal_amount') <= 0:
            raise UserError(_('Principal Amount must be more than 0.'))
        if vals.has_key('interest') and vals.get('interest') <= 0:
            raise UserError(_('Interest Rate must be more than 0.'))
        if vals.has_key('period') and vals.get('period') <= 1:
            raise UserError(_('Period must be more than 1 month.'))
        return super(BankLoan, self).create(vals)
        
    
    @api.multi
    def set_locked(self):
        if self:
            if not self.disbursement_date:
                raise Warning(_('You must fill the disbursement date first!'))
            move_obj = self.env['account.move']
            move_line_obj = self.env['account.move.line']
            
            move_line_ids = []
            for o in self:
                journal_id = o.bank_loan_type.disburse_journal_id.id or False
                liquidity_account_id = o.account_id.id or False
                payable_account_id = o.bank_loan_type.payable_account_id.id or False
                
                if not journal_id or not liquidity_account_id or not payable_account_id:
                    raise Warning(_('Please Insert Journal, Bank Account & Payable Account !'))
                
                
                vals_line = {'name'         : 'Bank Loan',
                             'account_id'   : liquidity_account_id,
                             'debit'        : o.principal_amount,
                             'credit'       : 0.0}
                move_line_ids.append((0,0, vals_line))
                
                vals_line = {'name'         : 'Bank Loan',
                             'account_id'   : payable_account_id,
                             'debit'        : 0.0,
                             'credit'       : o.principal_amount}
                move_line_ids.append((0,0, vals_line))
                vals = {'journal_id'    : journal_id,
                        'date'          : o.disbursement_date,
                        'line_ids'      : move_line_ids,
                        'branch_id': o.branch_id.id}
                
                move = move_obj.create(vals)
                move.post()
                # o.write({'state' : 'posted'})
                
                o.move_id = move.id
                o.compute_installment()
                o.state = 'locked'
            for line_id in self.computation_line_ids:
                one_week_ago_date =  (date.today() + relativedelta(days=7)).strftime('%Y-%m-%d') or False
                if not line_id.is_bill and line_id.date and one_week_ago_date > line_id.date:
                    inv_id = line_id.create_supplier_invoice(line_id)
                    if inv_id:
                        line_id.create_to_do_list(line_id, inv_id)


    ###Compute Installment after Locked
    @api.multi
    def compute_installment_locked(self):
        loan_comp_obj = self.env['loan.computation']
        installment_change_rate = self._context.get('installment_change_rate_id', False)
        remain_installment_duration = 0
        installment_to_remove = []
        for o in self:
#             for installment in o.computation_line_ids:
#                 if installment.status=='paid':
#                     last_installment_sequence   = int(installment.name)
#                     last_installment_date       = installment.date
#                 elif installment.status and installment.status != 'paid':
#                     remain_installment_duration += 1
#                     installment_to_remove.append(installment.id)
                    
            last_installment_sequence   = int(installment_change_rate.name) - 1
            last_installment            = loan_comp_obj.search([('name','=',last_installment_sequence),('loan_id','=',o.id)])
            last_installment_date       = last_installment.date
                
            for installment in loan_comp_obj.search([('date','>',last_installment_date),('loan_id','=',o.id)]):
                remain_installment_duration += 1
                installment_to_remove.append(installment.id) 
                
                    
            ##Check
            if o.payment_term=='monthly':
                term = 1
            elif o.payment_term=='quarterly':
                term = 4
            elif o.payment_term=='semiannualy':
                term = 6
            elif o.payment_term=='annualy':    
                term = 12
            
            installment_duration = remain_installment_duration
            balance = last_installment.balance
            
            principal_amount = last_installment.balance / installment_duration
            
            if o.interest:
                rate = o.interest / 100
            else:
                rate = 0.0

            start_installment_date = last_installment_date
            #Remove Status not Paid
            installment_loan_remove = loan_comp_obj.browse(installment_to_remove)
            installment_loan_remove.unlink()
            #raise UserError(_('Please check Your Period and Terms'))
            
            
            prev_installment_date = start_installment_date
 
            count = last_installment_sequence
            curbalance = 0
            first_loop = 0
            for l in range(0, installment_duration):
                first_loop += 1
                # next_installment_date = None
                # prev_installment_date = None
                count += 1
                if count <=1:
                    next_installment_date = start_installment_date and (datetime.strptime(start_installment_date, '%Y-%m-%d') + relativedelta(months=term)).strftime('%Y-%m-%d') or False
                    #o.write({'disbursement_date' : next_installment_date})
                else:
                    next_installment_date = start_installment_date and (datetime.strptime(prev_installment_date, '%Y-%m-%d') + relativedelta(months=term)).strftime('%Y-%m-%d') or False
                prev_installment_date = next_installment_date
                 
                temp2 = (1 - 1 / (1 + rate / (12/term)) ** (installment_duration - count))
                angsuran = (last_installment.balance * (rate / (12/term))) / (1 - 1 / (1 + rate / (12/term)) ** installment_duration)
                balance = balance if first_loop==1 else balance - principal_amount
                 
                if o.method_type=='annuity':
                    bunga = balance * (rate / (12/term))
                    interest_amount = bunga
                    principal_amount = angsuran - interest_amount
                     
                    curbalance = balance - principal_amount
                    emi_installment = (temp2 <> 0.0 and interest_amount / temp2) or 0.0
                     
                elif o.method_type=='flat':
                    interest_amount = ((installment_duration/12.0) * (last_installment.balance * rate)) / installment_duration 
                    emi_installment = principal_amount + interest_amount
                    curbalance = balance - principal_amount
                 
                elif o.method_type=='effective':
                    interest_amount = (last_installment.balance - (count-1.0)*principal_amount) * (rate/12.0)
                    emi_installment = principal_amount + interest_amount
                     
                    curbalance = balance - principal_amount
                     
                #curbalance = balance
                week_ago_installment_date = None
                status = None
                if next_installment_date:
                    week_ago_installment_date = datetime.strptime(next_installment_date, "%Y-%m-%d") - timedelta(days=7)
                    if datetime.strftime(date.today(), '%Y-%m-%d') > next_installment_date:
                        status = 'late'
                    elif datetime.strftime(date.today(), '%Y-%m-%d') == next_installment_date:
                        status = 'due'
                    elif datetime.strftime(date.today(), '%Y-%m-%d') < next_installment_date:
                        status = 'not_due'
 
                vals = {
                    'loan_id': o.id,
                    'date': next_installment_date,
                    'name': count,
                    'principal_amount': principal_amount,
                    'interest': interest_amount,
                    'payment_amount': principal_amount + interest_amount,
                    'balance': curbalance,
                    'bill_date': week_ago_installment_date,
                    'status': status,
                    'interest_rate': o.interest,
                }
 
                loan_id = self.env['loan.computation'].create(vals)
    
    @api.multi
    def compute_installment(self):
        for o in self:
            if o.state == 'locked':
                #self._context.get('installment_change_rate_id', False)
                #print "###context--->>", context
                o.with_context().compute_installment_locked()
                return True
            
            print "####Dont Enter####"
            ##Check
            if o.payment_term=='monthly':
                term = 1
            elif o.payment_term=='quarterly':
                term = 4
            elif o.payment_term=='semiannualy':
                term = 6
            elif o.payment_term=='annualy':    
                term = 12
                
            installment_duration = ((o.period_type=='year' and o.period*12) or o.period) / term
            
#             for i in range(term):
#                 print "i--->>", i
#                 print "installment_duration##", installment_duration
#                 installment_duration -= term
#                 
#                 if installment_duration > 1:
#                     continue
#                 elif installment_duration==0:
#                     pass
#                 elif installment_duration < 0:
#                     raise UserError(_('Please check Your Period and Terms'))
            
            if o.principal_amount:
                principal_amount = o.principal_amount / installment_duration
            else:
                principal_amount = 0.0
            
            if o.interest:
                rate = o.interest / 100
            else:
                rate = 0.0

            start_installment_date = o.disbursement_date
            o.computation_line_ids.unlink()
            prev_installment_date = start_installment_date

            count = 0
            curbalance = 0
            
            ##Installment 0
            vals = {
                'loan_id': o.id,
                'date': False,
                'name': '0',
                'principal_amount': 0.0,
                'interest': 0.0,
                'payment_amount': 0.0,
                'balance': o.principal_amount}

            self.env['loan.computation'].create(vals)
            #
            
            for l in range(0, installment_duration):
                # next_installment_date = None
                # prev_installment_date = None
                count += 1
                if count <=1:
                    next_installment_date = start_installment_date and (datetime.strptime(start_installment_date, '%Y-%m-%d') + relativedelta(months=term)).strftime('%Y-%m-%d') or False
                    #o.write({'disbursement_date' : next_installment_date})
                else:
                    next_installment_date = start_installment_date and (datetime.strptime(prev_installment_date, '%Y-%m-%d') + relativedelta(months=term)).strftime('%Y-%m-%d') or False
                prev_installment_date = next_installment_date
                
                temp2 = (1 - 1 / (1 + rate / (12/term)) ** (installment_duration - count))
                angsuran = (o.principal_amount * (rate / (12/term))) / (1 - 1 / (1 + rate / (12/term)) ** installment_duration)
                if count <= 1:
                    balance = o.principal_amount
                else:
                    balance = balance - principal_amount

                
                if o.method_type=='annuity':
                    bunga = balance * (rate / (12/term))
                    interest_amount = bunga
                    principal_amount = angsuran - interest_amount
                    
                    curbalance = balance - principal_amount
                    emi_installment = (temp2 <> 0.0 and interest_amount / temp2) or 0.0
                    
                elif o.method_type=='flat':
                    interest_amount = ((installment_duration/12.0) * (o.principal_amount * rate)) / installment_duration 
                    emi_installment = principal_amount + interest_amount
                    curbalance = balance - principal_amount
                
                elif o.method_type=='effective':
                    interest_amount = (o.principal_amount - (count-1.0)*principal_amount) * (rate/12.0)
                    emi_installment = principal_amount + interest_amount
                    
                    
                    
                    curbalance = balance - principal_amount
                    
                #curbalance = balance
                week_ago_installment_date = None
                status = None
                if next_installment_date:
                    week_ago_installment_date = datetime.strptime(next_installment_date, "%Y-%m-%d") - timedelta(days=7)
                    if datetime.strftime(date.today(), '%Y-%m-%d') > next_installment_date:
                        status = 'late'
                    elif datetime.strftime(date.today(), '%Y-%m-%d') == next_installment_date:
                        status = 'due'
                    elif datetime.strftime(date.today(), '%Y-%m-%d') < next_installment_date:
                        status = 'not_due'

                vals = {
                    'loan_id': o.id,
                    'date': next_installment_date,
                    'name': count,
                    'principal_amount': principal_amount,
                    'interest': interest_amount,
                    'payment_amount': principal_amount + interest_amount,
                    'balance': curbalance,
                    'bill_date': week_ago_installment_date,
                    'status': status,
                    'interest_rate': o.interest , 
                }

                loan_id = self.env['loan.computation'].create(vals)


                    # loan_installment_id
                    # invoice.compute_taxes()
            #self.date_start = o.installment_date
            #self.date_end   = next_installment_date

    @api.multi
    def apply_loan(self):
        self.state = 'applied'

    @api.multi
    def approve_loan(self):
        self.state = 'approved'
        self.approved_date = datetime.today()

    @api.multi
    def cancel(self):
        self.state = 'cancel'

    @api.multi
    def set_draft(self):
        self.state = 'draft'
        
    @api.multi
    def compute_sheet(self):
#         self.state = 'approved'
        print""

class LoanComputation(models.Model):
    _name = "loan.computation"
    # _inherit = ['mail.activity.mixin']

    name = fields.Char(string="Installment")
    number = fields.Integer(string="Payment Number")
    date = fields.Date(string="Due Date")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    payment_amount = fields.Float(string="Payment")
    principal_amount = fields.Float(string="Principal Amount")
    interest = fields.Float(string="Interest")
    interest_rate = fields.Float(string="Interest Rate")
    emi = fields.Integer(string="EMI (Installment)")
    state = fields.Selection([('draft', 'Draft'), ('applied', 'Applied'), ('approved', 'Approved'), ('cancel', 'Cancel')], default="draft")
    loan_id = fields.Many2one("bank.loan", string="Bank Loan")
    balance = fields.Float(string="Balance")
    is_bill = fields.Boolean(string="Is Bill created?", default=False)
    invoice_id = fields.Many2one('account.invoice', string="Invocie ID")
    bill_date = fields.Date('Bill Invoice Date')
    status = fields.Selection(compute="_get_state_value", selection=[('late', 'Late'), ('not_due', 'Not Due'), ('due', 'Due'), ('paid', 'Paid')], string="Status")
    commulative_principal = fields.Float(compute="_get_commulative_value", store=True, string="Cumulative Principal")
    commulative_interest = fields.Float(compute="_get_commulative_value", store=True, string="Cumulative Interest")
    # commulative_int = fields.Float(compute="_get_commulative_value", store=True,string="Cumulative Interest")
    
    @api.multi  
    def _get_state_value(self):
        for rec in self:
            if rec.date and datetime.strftime(date.today(), '%Y-%m-%d') > rec.date:
                rec.status = 'late'
            elif rec.date and datetime.strftime(date.today(), '%Y-%m-%d') == rec.date:
                rec.status = 'due'
            elif rec.date and datetime.strftime(date.today(), '%Y-%m-%d') < rec.date:
                rec.status = 'not_due'
            if rec.date and rec.commulative_principal:
                rec.status = 'paid'


    @api.depends('invoice_id.state')
    def _get_commulative_value(self):
        for rec in self:
            rec.commulative_interest = 0.0
            rec.commulative_principal = 0.0
            if rec.invoice_id and rec.invoice_id.state == 'paid':
                if self.invoice_id.loan_installment_id.loan_id and self.invoice_id.id == self.invoice_id.loan_installment_id.invoice_id.id:
                    comp_ids = self.search([('loan_id', '=', self.invoice_id.loan_installment_id.loan_id.id)])
                    interest = self.invoice_id.loan_installment_id.interest
                    principal_amount = self.invoice_id.loan_installment_id.principal_amount
                    for comp_id in comp_ids:
                        if comp_id.commulative_interest and comp_id.commulative_principal:
                            interest += comp_id.interest
                            principal_amount += comp_id.principal_amount
                    rec.status = 'paid'
                    rec.commulative_principal = principal_amount
                    rec.commulative_interest = interest
                # mail_act_id = self.env['mail.activity'].sudo().search([('res_id', '=', rec.invoice_id.id), ('res_model', '=','account.invoice')])
                # if mail_act_id:
                #     mail_act_id.active = False
                #     # mail_act_id.unlink()

    @api.multi
    def create_supplier_invoice(self, loan_id):
        #bank_id = self.env.ref('bank_loan_management.bank_supplier')

        # currency_id =  loan_id.loan_id.account_id and loan_id.loan_id.account_id.company_id and loan_id.loan_id.account_id.company_id.currency_id and loan_id.loan_id.account_id.company_id.currency_id.id or False
        currency_id = self.env.ref('base.IDR').id
        invoice_account = self.env['account.account'].search([('user_type_id', '=', self.env.ref('account.data_account_type_payable').id)], limit=1).id
        # Non-current Liabilities
        #principal_loan_account =  self.env['account.account'].search([('user_type_id', '=', self.env.ref('account.data_account_type_non_current_liabilities').id)], limit=1).id
        principal_loan_account =  loan_id.loan_id.bank_loan_type.payable_account_id.id
        if not principal_loan_account:
            raise Warning(_('Non-current Liabilities account not found. Please check.'))
        #cost_of_interest_account = self.env.ref('bank_loan_management.cost_of_interest_account').id
        cost_of_interest_account = loan_id.loan_id.bank_loan_type.interest_account_id.id

        week_ago = datetime.strptime(loan_id.date, "%Y-%m-%d") - timedelta(days=7)
        journal = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
        
        inv_vals = {
            'partner_id': loan_id.loan_id.vendor_id and loan_id.loan_id.vendor_id.id or False,
            'account_id': invoice_account,
            'date_invoice': week_ago,
            'branch_id': loan_id.loan_id.branch_id and loan_id.loan_id.branch_id.id,
            'date_due': loan_id.date, 
            'currency_id': currency_id,
            'type': 'in_invoice',
            'loan_installment_id': loan_id.id,
            'user_id': loan_id.create_uid.id,
            'origin': loan_id.loan_id.name,
            }
        if journal:
            inv_vals.update({'journal_id':journal.id})
        inv_id = self.env['account.invoice'].create(inv_vals)
        invoice_line = self.env['account.invoice.line'].create({
            'product_id': self.env.ref('bank_loan_management.product_principal_loan').id,
            'quantity': 1,
            'price_unit': loan_id.principal_amount,
            'invoice_id': inv_id.id,
            'name': self.env.ref('bank_loan_management.product_principal_loan').name,
            'account_id': principal_loan_account,
            # 'account_analytic_id': analytic_account.id,
        })
        invoice_line = self.env['account.invoice.line'].create({
            'product_id': self.env.ref('bank_loan_management.product_interest_loan').id,
            'quantity': 1,
            'price_unit': loan_id.interest,
            'invoice_id': inv_id.id,
            'name': self.env.ref('bank_loan_management.product_interest_loan').name,
            'account_id': cost_of_interest_account,
            # 'account_analytic_id': analytic_account.id,
        })
        loan_id.is_bill = True
        loan_id.invoice_id = inv_id.id
        return inv_id

    @api.multi
    def create_to_do_list(self, loan_id, inv_id):
        mail_vals = {}
        mail_type = self.env['mail.activity.type'].sudo().create({
            'name': str(inv_id.origin) + ' - Installment No ' + str(inv_id.loan_installment_id.name)
            })
        model_id = self.env['ir.model'].sudo().search([('model', '=','account.invoice')])
        activity_id = self.env['mail.activity'].sudo().create({
            'activity_type_id' : mail_type.id,
            'res_model_id': model_id.id,
            'res_model': 'account.invoice',
            'res_id': inv_id.id,
            'summary': "Please process the loan payment.",
            'user_id': inv_id.create_uid.id,
            'invoice_id': inv_id.id,
            })
        if activity_id:
            admin_user = self.env['res.users'].search([('id', '=', SUPERUSER_ID)])
            subject = """Loan Payment - %s (Instalment no - %s)""" % (inv_id.origin, inv_id.loan_installment_id.name)
            message = """
                            <p>Hello %s,</p>
                            <p>Please process the loan payment no %s on instalment no. %s </p>
                            <p>Regards,</p>
                            <p>%s</p>""" % (inv_id.create_uid.name, inv_id.origin, inv_id.loan_installment_id.name, admin_user.name)
            mail_vals['email_from'] = admin_user.login
            mail_vals['email_to'] = inv_id.create_uid.partner_id.email
            mail_vals['subject'] = subject
            mail_vals['body_html'] = message
            mail_id = self.env['mail.mail'].create(mail_vals)
            if mail_id:
                mail_id.send()
        return activity_id

    @api.model
    def _cron_generate_vendor_bill(self):
        for loan_id in self.search([('bill_date', '=', date.today()), ('is_bill', '=', False)]):
            inv_id = self.create_supplier_invoice(loan_id)
            if inv_id:
                self.create_to_do_list(loan_id, inv_id)

    # @api.model
    # def _loan_computation_status(self):
    #     for bank_loan_id in self.env['bank.loan'].search([]):
    #         cum_principal = 0.0
    #         cum_interest = 0.0
    #         computation_line_ids = self.search([('id', 'in', bank_loan_id.computation_line_ids.ids)], order="name")
    #         print "----bank_loan_id.computation_line_ids.ids ",bank_loan_id, bank_loan_id.computation_line_ids
    #         # print ">>>>... computation_id ",computation_id
    #         print ">>>>>>>computation_line_ids ",computation_line_ids
    #         for computation_id in computation_line_ids:
    #             cum_principal += computation_id.principal_amount
    #             cum_interest += computation_id.interest
    #             if computation_id.invoice_id and computation_id.invoice_id.state == 'paid':
    #                 computation_id.status = 'paid'
    #                 computation_id.commulative_principal = cum_principal
    #                 computation_id.commulative_interest = cum_interest
    #                 continue
    #             if computation_id.date:
    #                 due_date = datetime.strptime(computation_id.date, "%Y-%m-%d").date()
    #                 if date.today() > due_date:
    #                     computation_id.status = 'not_due'
    #                 if date.today() < due_date:
    #                     computation_id.status = 'late'
    #                 if date.today() == due_date:
    #                     computation_id.status = 'due'

class AccountInvocie(models.Model):
    _inherit = "account.invoice"

    loan_installment_id = fields.Many2one('loan.computation', string="Loan Installment")

