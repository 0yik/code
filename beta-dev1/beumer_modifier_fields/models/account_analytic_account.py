# -*- coding: utf-8 -*-

from odoo import models, fields, api

class account_team_member(models.Model):
    _inherit = 'account.team.member'

    status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], string='Status', default='active')

# class project_cost_element(models.Model):
#     _inherit = 'project.cost_element'
#
#     level               = fields.Selection([('1', '1'), ('2', '2'), ('3', '3')])

class account_analytic_account_cost_element(models.Model):
    _inherit ='account.analytic.account.cost.element'

    @api.onchange('cost_element_id1','cost_element_id2','cost_element_id3')
    @api.multi
    def _compute_cost_element_code(self):
        result = ''
        if self.cost_element_id1:
            result += self.cost_element_id1.cost_element_code + "-"
        if self.cost_element_id2:
            result += self.cost_element_id2.cost_element_code + "-"
        if self.cost_element_id3:
            result += self.cost_element_id3.cost_element_code
        self.cost_element_code = result
        self.cost_element_code_sub = result

    @api.model
    def write(self, vals):
        if vals is None:
            vals = {}
        if vals.get('cost_element_code_sub', False):
            vals.update({'cost_element_code': vals.get('cost_element_code_sub')})
        res = super(account_analytic_account_cost_element,self).write(vals)
        return res

    @api.model
    def create(self,vals):
        if vals is None:
            vals = {}
        if vals.get('cost_element_code_sub', False):
            vals.update({'cost_element_code': vals.get('cost_element_code_sub')})
        res = super(account_analytic_account_cost_element,self).create(vals)
        return res

    # level = fields.Selection([('1', '1'), ('2', '2'), ('3', '3')],string="Level")
    cost_element_code = fields.Char(string='Cost Element Code',readonly=True)
    cost_element_code_sub = fields.Char(string='Cost Element Code',readonly=False)
    cost_element_id1  = fields.Many2one('project.cost_element',domain=[('level','=','1')], string='Cost Element 1', required =True)
    cost_element_id2  = fields.Many2one('project.cost_element',domain=[('level','=','2')], string='Cost Element 2', required = True)
    cost_element_id3  = fields.Many2one('project.cost_element',domain=[('level','=','3')], string='Cost Element 3', required = True)

class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    vo_log_change_ids       = fields.One2many('vo.log.change','project_id','VO Log Change')
    delivery_address        = fields.Char('Delivery Address')
    delivery_address_sub    = fields.One2many('purchase.request.delivery.address','project_id','Delivery Address')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.project_number:
                if record.name:
                    name = "%s - %s"%(record.project_number,record.name)
                else:
                    name = record.project_number
            else:
                name = record.name
            if name:
                result.append((record.id, name))
        return result

class volog_change(models.Model):
    _name = 'vo.log.change'

    project_id      = fields.Many2one('account.analytic.account')
    old_value       = fields.Float('Old Value',readonly=True)
    new_value       = fields.Float('New Value',readonly=True)
    remark          = fields.Text('Remarks',readonly=True)
    date            = fields.Date('Date',readonly=True)
    user_id         = fields.Many2one('res.users',readonly=True)
    vo_change_number = fields.Char('VO Change Reference')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = ''
            if record.vo_change_number:
                name = record.vo_change_number
            result.append((record.id, name))
        return result

class account_analytic_account(models.Model):
    _name = 'account.analytic.account.change.contract.amount'

    remark = fields.Text('Remark')
    current_contract_amount = fields.Float('Contract Amount',readonly=True)
    new_contract_amount = fields.Float('New Contract Amount')

    @api.model
    def default_get(self, fields):
        if self.env.context.get('active_model', False) == 'account.analytic.account':
            active_id =  self.env.context.get('active_id',False)
            # self.contract_amount = self.env['account.analytic.account'].browse(active_id).contract_amount
            res = super(account_analytic_account, self).default_get(fields)
            res['current_contract_amount'] = self.env['account.analytic.account'].browse(active_id).contract_amount
            # res['name']         = self.env['account.analytic.account'].browse(active_id).name
            # res['company_id']   = self.env['account.analytic.account'].browse(active_id).company_id.id
            return res
        res = super(account_analytic_account, self).default_get(fields)
        return res

    @api.multi
    def confirm_vo_change(self):
        if self.env.context.get('active_model', False) == 'account.analytic.account':
            active_id = self.env.context.get('active_id', False)

            volog_change_obj = self.env['vo.log.change']
            volog_change_ids = volog_change_obj.search([('project_id', '=', active_id)])
            count = len(volog_change_ids) + 1
            volog_change_number = "VO%s" % ('{0:02}'.format(count))
            if active_id:
                vo_log_change_data = {
                    'vo_change_number': volog_change_number,
                    'project_id': active_id,
                    'old_value': self.current_contract_amount,
                    'new_value': self.new_contract_amount,
                    'remark': self.remark,
                    'date': fields.Date.today(),
                    'user_id': self.env.uid,
                }

                self.env['account.analytic.account'].browse(active_id).contract_amount = self.new_contract_amount

                volog_change_obj.create(vo_log_change_data)
        # self.contract_amount = float(self.new_contract_amount)
        return

class project_bann_number(models.Model):
    _name = 'account.analytic.account.baan.number'
    _rec_name = 'baan'


    @api.model
    def _compute_project_number(self):
        result = []
        projects = self.env['account.analytic.account'].search([])
        for project in projects:
            if (project.project_number, project.project_number) not in result:
                result.append((project.project_number, project.project_number))
        return result

    # @api.onchange('project_number')
    # def onchange_project_number(self):
    #     if self.project_name:
    #         project = self.env['account.analytic.account'].search([('name', '=', self.project_name)])
    #         self.project_number = (project.project_number, project.project_number)
    #
    # @api.onchange('project_number')
    # def onchange_project_number(self):
    #     if self.project_name:
    #         project = self.env['account.analytic.account'].search([('project_number','=',self.project_number)])
    #         self.project_name = (project.name, project.name)

    # @api.onchange('project_number')
    # def onchange_project_number(self):
    #     domain = []
    #     if self.project_number:
    #         domain.append(('project_number', '=', self.project_number.project_number))
    #     return {'domain': {'project_name': domain}}
    @api.onchange('project_number')
    def onchange_project_number(self):
        domain1 = []
        if self.project_number:
            domain1.append(('project_number', '=', self.project_number))
            project_ids = self.env['account.analytic.account'].search(domain1)
            if len(project_ids) >= 2:
                domain2 = []
                for project in project_ids:
                    domain2.append(('project_name','=',project.name))
                return {'domain': {'project_name': domain2}}
            else: self.project_name = project_ids.name

    @api.onchange('project_name')
    def onchange_project_name(self):
        domain1 = []
        if self.project_name:
            domain1.append(('name', '=', self.project_name))
            project_ids = self.env['account.analytic.account'].search(domain1)
            if len(project_ids) >= 2:
                domain2 = []
                for project in project_ids:
                    domain2.append(('project_number', '=', project.project_number))
                return {'domain': {'project_number': domain2}}
            else: self.project_number = project_ids.project_number
        # return {'domain': {'project_name': domain2,'project_number':domain1}}

    # #
    # @api.onchange('project_name')
    # def onchange_project_name(self):
    #     domain = []
    #     if self.project_name:
    #         domain.append(('name', '=', self.project_name.name))
    #     return {'domain': {'project_number': domain}}

    @api.model
    def _compute_project_name(self):
        result = []
        projects = self.env['account.analytic.account'].search([])
        for project in projects:
            if (project.name, project.name) not in result:
                result.append((project.name, project.name))
        return result



    @api.onchange('project_number','product','phase')
    @api.model
    def _compute_baan_number(self):
        result= ''
        if self.project_number:
            result += self.project_number + '-'
        if self.product:
            result += self.product.cost_element_code + '-'
        if self.phase:
            result += self.phase.cost_element_code
        self.baan = result

    project_number      = fields.Selection('_compute_project_number',string='Project Number')
    # project_number      = fields.Many2one('account.analytic.account',string='Project Number')
    project_name        = fields.Selection('_compute_project_name',string='Project Name')
    # project_name        = fields.Many2one('account.analytic.account',string='Project Name')

    product             = fields.Many2one('project.cost_element',domain=[('level','=','3')],string='Product')
    phase               = fields.Many2one('project.cost_element',domain=[('level','=','2')],string='Phase')
    baan                = fields.Char(string='Baan')
    invoice_type        = fields.Char('Invoice Type')

class AnalyticAccountBudgetLog(models.Model):
    _inherit = 'account.analytic.account.budget.log'

    volog_change_id = fields.Many2one('vo.log.change', 'VO Change Reference')
