# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime



class purchase_order(models.Model):
    _inherit = 'purchase.order'


    project_id       = fields.Many2one('account.analytic.account', ondelete='set null', string='Project', domain=[('is_project','=',True)])
    remarks          = fields.Char('Remarks')
    pricing          = fields.Text('Pricing')
    attachments      = fields.Text('Attachments')
    packing          = fields.Text('Packing')
    shipping_documents = fields.Text('Shipping Conditions')
    purchasing       = fields.Char('Purchasing')
    warranty         = fields.Char('Warranty')
    cost_element_id1 = fields.Many2one('project.cost_element', domain=[('level', '=', '1')], string='Cost Element 1')
    cost_element_id2 = fields.Many2one('project.cost_element', domain=[('level', '=', '2')], string='Cost Element 2')
    cost_element_id3 = fields.Many2one('project.cost_element', domain=[('level', '=', '3')], string='Cost Element 3')
    product_ctg = fields.Many2one('pr.approving.matrix', string='Product DOA', required=True)
    delivery_address = fields.Many2one('purchase.request.delivery.address', string="Delivery Address")
    # related = 'requisition_id.product_ctg'
    contact_name = fields.Many2one('res.partner', string="Contact Name")
    # analytic_distribution_id = fields.Many2one('account.analytic.distribution', string='Analytic Distribution')
    date_planned = fields.Datetime(string='Delivery Date', compute='_compute_date_planned', store=True, index=True,
                                   oldname='minimum_planned_date')
    get_employee = fields.Many2one('hr.employee',compute='_get_employee')

    def _get_employee(self):
        for record in self:
            employee_id = record.env['hr.employee'].search([('user_id','=',record._uid)],limit=1)
            record.get_employee = employee_id.id

    def _get_value_product_ctg(self):
        if self.requisition_id and self.requisition_id.product_ctg:
            self.product_ctg = self.requisition_id.product_ctg

    @api.onchange('requisition_id')
    def onchange_requisition_id(self):
        if self.requisition_id and self.requisition_id.product_ctg:
            self.product_ctg = self.requisition_id.product_ctg

    @api.onchange('partner_id')
    def onchane_partner(self):
        if self.partner_id:
            return {'domain': {'contact_name' : [('parent_id','=',self.partner_id.id)]}}

    @api.model
    def create(self,vals):
        res = super(purchase_order, self).create(vals)
        name_rfq = "RFQ%s" % ('{0:05}'.format(res.id))
        res.name = name_rfq
        return res

    @api.multi
    def button_confirm(self):
        super(purchase_order, self).button_confirm()
        current_year = datetime.now().strftime('%y')
        name_po = "%s-%s" % (current_year,'{0:04}'.format(self.id))
        self.name = name_po

    @api.onchange('project_id')
    def costelement_in_project(self):
        user_ids = []
        administrator_group = self.env['res.groups'].search([('name','in',('Procurement Executive','Procurement Manager'))])
        for admin in administrator_group:
            if admin.users:
                for user in admin.users:
                    user_ids.append(user.id)
        domain1 = []
        domain2 = []
        domain3 = []
        if self.project_id.id:
            domain_address = [('id','in',self.project_id.delivery_address_sub.ids)]

            domain1 = ['|',('id', 'in', [line.cost_element_id1.id for line in self.project_id.cost_element_ids]),('write_uid','in',user_ids)]
            domain2 = ['|',('id', 'in', [line.cost_element_id2.id for line in self.project_id.cost_element_ids]),('write_uid','in',user_ids)]
            domain3 = ['|',('id', 'in', [line.cost_element_id3.id for line in self.project_id.cost_element_ids]),('write_uid','in',user_ids)]
            return {'domain': {'cost_element_id1': domain1, 'cost_element_id2': domain2, 'cost_element_id3': domain3, 'delivery_address' : domain_address}}

    # @api.onchange('cost_element_id1', 'cost_element_id2', 'cost_element_id3')
    # def onchange_costelement(self):
        # user_ids = []
        # administrator_group = self.env['res.groups'].search(
        #     [('name', 'in', ('Procurement Executive', 'Procurement Manager'))])
        # for admin in administrator_group:
        #     if admin.users:
        #         for user in admin.users:
        #             user_ids.append(user.id)
        # domain1 = []
        # domain2 = []
        # domain3 = []
        # if self.cost_element_id1.id:
        #     domain2 = ['|',('id', 'in', [line.cost_element_id2.id for line in self.project_id.cost_element_ids.search(
        #         [('cost_element_id1.id', '=', self.cost_element_id1.id)])]),('write_uid','in',user_ids),('level', '=', '2')]
        #     domain3 = ['|',('id', 'in', [line.cost_element_id3.id for line in self.project_id.cost_element_ids.search(
        #         [('cost_element_id1.id', '=', self.cost_element_id1.id)])]),('write_uid','in',user_ids),('level', '=', '3')]
        #     return {'domain': {'cost_element_id2': domain2, 'cost_element_id3': domain3}}
        # if self.cost_element_id2.id:
        #     domain1 = ['|',('id', 'in', [line.cost_element_id1.id for line in self.project_id.cost_element_ids.search(
        #         [('cost_element_id2.id', '=', self.cost_element_id2.id)])]),('write_uid','in',user_ids),('level', '=', '1')]
        #     domain3 = ['|',('id', 'in', [line.cost_element_id3.id for line in self.project_id.cost_element_ids.search(
        #         [('cost_element_id2.id', '=', self.cost_element_id2.id)])]),('write_uid','in',user_ids),('level', '=', '3')]
        #     return {'domain': {'cost_element_id1': domain1, 'cost_element_id3': domain3}}
        # if self.cost_element_id3.id:
        #     domain2 = ['|',('id', 'in', [line.cost_element_id2.id for line in self.project_id.cost_element_ids.search(
        #         [('cost_element_id3.id', '=', self.cost_element_id3.id)])]),('write_uid','in',user_ids),('level', '=', '2')]
        #     domain1 = ['|',('id', 'in', [line.cost_element_id1.id for line in self.project_id.cost_element_ids.search(
        #         [('cost_element_id3.id', '=', self.cost_element_id3.id)])]),('write_uid','in',user_ids),('level', '=', '1')]
        #     return {'domain': {'cost_element_id2': domain2, 'cost_element_id1': domain1}}

    @api.onchange('cost_element_id1')
    def onchanger_cost_element_id1(self):
        domain2 = []
        domain3 = []

        if self.cost_element_id1.id:
            domain2.append(('id', 'in', [line.id for line in self.env['project.cost_element'].search(
                [('parent_cost_element', '=', self.cost_element_id1.id)])]))
            domain3.append(('level', '=', '3'))
            return {'domain': {'cost_element_id2': domain2, 'cost_element_id3': domain3}}

    @api.onchange('cost_element_id2')
    def onchanger_cost_element_id2(self):
        domain1 = []
        domain3 = []

        if self.cost_element_id2.id:
            domain1.append(('id', 'in', [line.id for line in self.env['project.cost_element'].search(
                [('id', '=', self.cost_element_id2.parent_cost_element.id)])]))
            domain3.append(('id', 'in', [line.id for line in self.env['project.cost_element'].search(
                [('parent_cost_element', '=', self.cost_element_id2.id)])]))
            return {'domain': {'cost_element_id1': domain1, 'cost_element_id3': domain3}}

    @api.onchange('cost_element_id3')
    def onchanger_cost_element_id3(self):
        domain2 = []
        domain1 = []

        if self.cost_element_id3.id:
            domain2.append(('id', 'in', [line.id for line in self.env['project.cost_element'].search(
                [('id', '=', self.cost_element_id3.parent_cost_element.id)])]))
            domain1.append(('level', '=', '1'))
            return {'domain': {'cost_element_id2': domain2, 'cost_element_id1': domain1}}

    @api.multi
    def create_analytic(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.distribution',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_id' : self.requisition_id.analytic_distribution_id.id,
        }

    # def update_product_ctg(self):
    #     purchase_order_ids = self.search([])
    #     for purchase_order_id in purchase_order_ids:
    #         if purchase_order_id.requisition_id and purchase_order_id.requisition_id.product_ctg:
    #             purchase_order_id.product_ctg = purchase_order_id.requisition_id.product_ctg

    @api.multi
    @api.model
    def create_purchase_request(self):
        context = self.env.context
        purchase_ids = context.get('active_ids', [])
        request_obj = self.env['purchase.request']
        if context.get('active_model', False) == 'purchase.order':
            purchase_request = False
            lines = []
            for purchase in self.browse(purchase_ids):

                if purchase_request is False:
                    requisition = purchase.requisition_id
                    if requisition:
                        department = requisition.env['hr.employee'].search(
                                [('user_id', '=', requisition.user_id.id)]).department_id
                        if not department:
                            raise ValidationError('Responsible person of Purchase Agreements %s need join any department')%(requisition.name)
                        request_data = {
                            'company_id': requisition.company_id.id,
                            'department_id': requisition.env['hr.employee'].search(
                                [('user_id', '=', requisition.user_id.id)]).department_id.id,
                            'picking_type_id': requisition.picking_type_id.id,
                            'product_ctg': requisition.product_ctg.id,
                            'requested_by': requisition.user_id.id,
                            'project_id': requisition.project_id.id,
                            'cost_element_id1': requisition.cost_element_id1.id,
                            'cost_element_id2': requisition.cost_element_id2.id,
                            'cost_element_id3': requisition.cost_element_id3.id,
                            'analytic_distribution_id': requisition.analytic_distribution_id.id,
                            'delivery_address'  : purchase.delivery_address.id,
                            'approve_sub' : request_obj.setup_approver(requisition.product_ctg.line_ids),
                            'origin': requisition.name,
                        }
                    else:
                        department = requisition.env['hr.employee'].search(
                            [('user_id', '=',  self._uid)]).department_id
                        if not department:
                            raise ValidationError('You need join any department')
                        request_data = {
                            'company_id': purchase.company_id.id,
                            'department_id': requisition.env['hr.employee'].search(
                                [('user_id', '=', self._uid)]).department_id.id,
                            'picking_type_id': purchase.picking_type_id.id,
                            'product_ctg': purchase.product_ctg.id,
                            'requested_by': self._uid,
                            'project_id': purchase.project_id.id,
                            'cost_element_id1': purchase.cost_element_id1.id,
                            'cost_element_id2': purchase.cost_element_id2.id,
                            'cost_element_id3': purchase.cost_element_id3.id,
                            'origin': requisition.name,
                        }
                    purchase_request = request_obj.create(request_data)
                    purchase.purchase_request_id = purchase_request.id
                    lines = purchase_request.line_ids.browse([])
                if purchase_request:
                    line_data = {
                        'rfq_number': purchase.id,
                        'vendor': purchase.partner_id.id,
                        'total_amount': purchase.amount_total,
                        'amount_untaxed': purchase.amount_untaxed,
                    }
                    lines += purchase_request.line_ids.new(line_data)
            if purchase_request and lines:
                purchase_request.line_ids = lines
            return {
                'name': 'Purchase Request',
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.request',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.env.ref('purchase_request.view_purchase_request_form').id,
                'res_id': self.purchase_request_id.id,
            }

        return True

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #
    #     purchase_order_action_id = self.env.ref('purchase.purchase_form_action').id
    #     purchase_order_requisition_id = self.env.ref('purchase_requisition.action_purchase_requisition_list').id
    #     rfq_action_id = self.env.ref('purchase.purchase_rfq').id
    #     if self._context and 'params' in self._context and self._context['params']['action']:
    #         if view_type == 'tree' and purchase_order_action_id == self._context['params']['action']:
    #             self.env.ref('beumer_modifer_printout.picking_purchase_order').write({'multi': False})
    #         if view_type == 'tree' and purchase_order_requisition_id == self._context['params']['action']:
    #             self.env.ref('beumer_modifer_printout.picking_purchase_order').write({'multi': True})
    #         if view_type == 'tree' and rfq_action_id == self._context['params']['action']:
    #             self.env.ref('beumer_modifer_printout.picking_purchase_order').write({'multi': True})
    #
    #     result = super(purchase_order, self).fields_view_get(view_id=view_id, view_type=view_type,
    #                                                       toolbar=toolbar, submenu=submenu)
    #     return result

    # @api.model
    # def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
    #     purchase_order_action_id = self.env.ref('purchase.purchase_form_action').id
    #     purchase_order_requisition_id = self.env.ref('purchase_requisition.action_purchase_requisition_list').id
    #     rfq_action_id = self.env.ref('purchase.purchase_rfq').id
    #     if self._context and 'params' in self._context and self._context['params']['action']:
    #         if purchase_order_action_id == self._context['params']['action']:
    #             self.env.ref('beumer_modifer_printout.picking_purchase_order').write({'ir_values_id' : True})
    #         if purchase_order_requisition_id == self._context['params']['action']:
    #             self.env.ref('beumer_modifer_printout.picking_purchase_order').write({'ir_values_id' : False})
    #         if rfq_action_id == self._context['params']['action']:
    #             self.env.ref('beumer_modifer_printout.picking_purchase_order').write({'ir_values_id' : False})
    #     res = super(purchase_order, self).search_read(domain=domain, fields=fields, offset=offset,
    #                                                limit=limit, order=order)
    #     return res

class purchase_order_line(models.Model):
    _inherit ="purchase.order.line"

    product_id  = fields.Many2one('product.product',required=False)
    product_uom = fields.Many2one('product.uom',required=False)
    product_ids = fields.Char(string="Product id")

class purchase_request_line(models.Model):
    _inherit = 'purchase.request.line'

    amount_untaxed = fields.Float(string="Untaxed")

class purchase_request(models.Model):
    _inherit = 'purchase.request'

    delivery_address    = fields.Many2one('purchase.request.delivery.address', string = 'Delivery Address')
    sales_quotation     = fields.Char('Sales Quotation')
    customer_po_no      = fields.Char('Customer PO No')
    customer_po_date    = fields.Date('Sales Quotation/Customer PO Date')
    customer_id         = fields.Many2one('res.partner','Customer')



    @api.model
    def _compute_balance_budget(self):
        if self.project_id.id and (self.cost_element_id1.id or self.cost_element_id2.id or self.cost_element_id3.id):
            budget_obj = self.project_id.cost_element_ids.search([('account_analytic_account_id','=',self.project_id.id),
                                                                           ('cost_element_id1','=',self.cost_element_id1.id),
                                                                            ('cost_element_id2','=',self.cost_element_id2.id),
                                                                            ('cost_element_id3','=',self.cost_element_id3.id)])
            if len(budget_obj) ==1:
                self.balance_budget = budget_obj.total_budget

    bipo_no         = fields.Char('BIPO No')
    balance_budget  = fields.Float('Budget Balance Prior to Purchase',compute=_compute_balance_budget,readonly=True)
    sale_price      = fields.Char('Sales Price to Customer')
    project_id      = fields.Many2one('account.analytic.account', ondelete='set null', string='Project',
                                      domain=[('is_project', '=', True)])
    cost_element_id1 = fields.Many2one('project.cost_element', domain=[('level', '=', '1')], string='Cost Element 1')
    cost_element_id2 = fields.Many2one('project.cost_element', domain=[('level', '=', '2')], string='Cost Element 2')
    cost_element_id3 = fields.Many2one('project.cost_element', domain=[('level', '=', '3')], string='Cost Element 3')
    # cost_element_code = fields.Char(string='Cost Element Code', readonly=True)
    cost_element_code_sub = fields.Char(string='Cost Element Code',compute='_onchange_element_code',store=True)
    product_ctg      = fields.Many2one('pr.approving.matrix',string='Product DOA',required=True)
    analytic_distribution_id = fields.Many2one('account.analytic.distribution', string='Analytic Distribution')
    delivery_date    = fields.Date('Delivery Date')

    @api.multi
    @api.depends('cost_element_id1', 'cost_element_id2', 'cost_element_id3')
    def _onchange_element_code(self):
        for record in self:
            result = ''
            if record.cost_element_id1 and record.cost_element_id1.cost_element_code:
                result += record.cost_element_id1.cost_element_code + "-"
            if record.cost_element_id2 and record.cost_element_id2.cost_element_code:
                result += record.cost_element_id2.cost_element_code + "-"
            if record.cost_element_id3 and record.cost_element_id3.cost_element_code:
                result += record.cost_element_id3.cost_element_code
            record.cost_element_code_sub = result


    @api.onchange('project_id')
    def costelement_in_project(self):

        # domain1=[]
        # domain2=[]
        # domain3=[]
        # if self.project_id.id:
        #     domain1.append(('id','in',[line.cost_element_id1.id for line in self.project_id.cost_element_ids]))
        #     domain2.append(('id','in',[line.cost_element_id2.id for line in self.project_id.cost_element_ids]))
        #     domain3.append(('id','in',[line.cost_element_id3.id for line in self.project_id.cost_element_ids]))
        #     return {'domain' : {'cost_element_id1':domain1,'cost_element_id2':domain2,'cost_element_id3':domain3}}
        #
        # user_ids = []
        # administrator_group = self.env['res.groups'].search(
        #     [('name', 'in', ('Procurement Executive', 'Procurement Manager'))])
        # for admin in administrator_group:
        #     if admin.users:
        #         for user in admin.users:
        #             user_ids.append(user.id)

        user_ids = []
        administrator_group = self.env['res.groups'].search(
            [('name', 'in', ('Procurement Executive', 'Procurement Manager'))])
        for admin in administrator_group:
            if admin.users:
                for user in admin.users:
                    user_ids.append(user.id)

        domain1 = []
        domain2 = []
        domain3 = []
        if self.project_id.id:
            domain_address = [('id', 'in', self.project_id.delivery_address_sub.ids)]

            domain1 = ['|', ('id', 'in', [line.cost_element_id1.id for line in self.project_id.cost_element_ids]),
                       ('write_uid', 'in', user_ids),('level', '=', '1')]
            domain2 = ['|', ('id', 'in', [line.cost_element_id2.id for line in self.project_id.cost_element_ids]),
                       ('write_uid', 'in', user_ids),('level', '=', '2')]
            domain3 = ['|', ('id', 'in', [line.cost_element_id3.id for line in self.project_id.cost_element_ids]),
                       ('write_uid', 'in', user_ids),('level', '=', '3')]
            return {'domain': {'cost_element_id1': domain1, 'cost_element_id2': domain2, 'cost_element_id3': domain3, 'delivery_address' : domain_address}}

    # @api.onchange('cost_element_id1','cost_element_id2','cost_element_id3')
    # def onchange_costelement(self):

        # user_ids = []
        # administrator_group = self.env['res.groups'].search(
        #     [('name', 'in', ('Procurement Executive', 'Procurement Manager'))])
        # for admin in administrator_group:
        #     if admin.users:
        #         for user in admin.users:
        #             user_ids.append(user.id)

        # domain1 = []
        # domain2 = []
        # domain3 = []

        #
        # result = ''
        # if self.cost_element_id1:
        #     result += self.cost_element_id1.cost_element_code + "-"
        # if self.cost_element_id2:
        #     result += self.cost_element_id2.cost_element_code + "-"
        # if self.cost_element_id3:
        #     result += self.cost_element_id3.cost_element_code
        # self.cost_element_code = result

        # if self.cost_element_id1.id:
        #     domain2.append(('id','in',[line.id for line in self.env['project.cost_element'].search([('parent_cost_element','=',self.cost_element_id1.id)])]))
        #     # domain3.append(('level', '=', '3'))
        #     return {'domain' : {'cost_element_id2':domain2}}
        # if self.cost_element_id2.id:
        #     domain1.append(('id','in',[line.id for line in self.env['project.cost_element'].search([('id','=',self.cost_element_id2.parent_cost_element.id)])]))
        #     domain3.append(('id','in',[line.id for line in self.env['project.cost_element'].search([('parent_cost_element','=',self.cost_element_id2.id)])]))
        #     return {'domain' : {'cost_element_id1':domain1,'cost_element_id3':domain3}}
        # if self.cost_element_id3.id:
        #     domain2.append(('id','in',[line.id for line in self.env['project.cost_element'].search([('id','=',self.cost_element_id3.parent_cost_element.id)])]))
        #     domain1.append(('level', '=', '1'))
        #     return {'domain' : {'cost_element_id2':domain2,'cost_element_id1':domain1}}

        # if self.cost_element_id1.id:
        #     domain2.append(('id','in',[line.cost_element_id2.id for line in self.project_id.cost_element_ids.search([('cost_element_id1.id','=',self.cost_element_id1.id)])]))
        #     domain3.append(('id','in',[line.cost_element_id3.id for line in self.project_id.cost_element_ids.search([('cost_element_id1.id','=',self.cost_element_id1.id)])]))
        #     return {'domain' : {'cost_element_id2':domain2,'cost_element_id3':domain3}}
        # if self.cost_element_id2.id:
        #     domain1.append(('id','in',[line.cost_element_id1.id for line in self.project_id.cost_element_ids.search([('cost_element_id2.id','=',self.cost_element_id2.id)])]))
        #     domain3.append(('id','in',[line.cost_element_id3.id for line in self.project_id.cost_element_ids.search([('cost_element_id2.id','=',self.cost_element_id2.id)])]))
        #     return {'domain' : {'cost_element_id1':domain1,'cost_element_id3':domain3}}
        # if self.cost_element_id3.id:
        #     domain2.append(('id','in',[line.cost_element_id2.id for line in self.project_id.cost_element_ids.search([('cost_element_id3.id','=',self.cost_element_id3.id)])]))
        #     domain1.append(('id','in',[line.cost_element_id1.id for line in self.project_id.cost_element_ids.search([('cost_element_id3.id','=',self.cost_element_id3.id)])]))
        #     return {'domain' : {'cost_element_id2':domain2,'cost_element_id1':domain1}}

    @api.onchange('cost_element_id1')
    def onchanger_cost_element_id1(self):
        domain2 = []
        domain3 = []

        if self.cost_element_id1.id:
            domain2.append(('id','in',[line.id for line in self.env['project.cost_element'].search([('parent_cost_element','=',self.cost_element_id1.id)])]))
            domain3.append(('level', '=', '3'))
            return {'domain' : {'cost_element_id2':domain2,'cost_element_id3':domain3}}

    @api.onchange('cost_element_id2')
    def onchanger_cost_element_id2(self):
        domain1 = []
        domain3 = []

        if self.cost_element_id2.id:
            domain1.append(('id','in',[line.id for line in self.env['project.cost_element'].search([('id','=',self.cost_element_id2.parent_cost_element.id)])]))
            domain3.append(('id','in',[line.id for line in self.env['project.cost_element'].search([('parent_cost_element','=',self.cost_element_id2.id)])]))
            return {'domain' : {'cost_element_id1':domain1,'cost_element_id3':domain3}}

    @api.onchange('cost_element_id3')
    def onchanger_cost_element_id3(self):
        domain2 = []
        domain1 = []

        if self.cost_element_id3.id:
            domain2.append(('id','in',[line.id for line in self.env['project.cost_element'].search([('id','=',self.cost_element_id3.parent_cost_element.id)])]))
            domain1.append(('level', '=', '1'))
            return {'domain' : {'cost_element_id2':domain2,'cost_element_id1':domain1}}


    @api.multi
    def create_analytic(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.distribution',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_id' : self.analytic_distribution_id.id,
        }

    @api.model
    def get_matrix_id(self):
        matrix_obj = self.env['pr.approving.matrix']
        matrix_id = self.product_ctg
        return matrix_id