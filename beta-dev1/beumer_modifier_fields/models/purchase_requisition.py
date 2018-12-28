from odoo import fields, models, api, exceptions,_
from datetime import datetime
from odoo.exceptions import Warning

class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    # def _get_creation_date(self):
    #     return datetime.today().date()

    project_id       = fields.Many2one('account.analytic.account', ondelete='set null', string='Project',domain=[('is_project','=',True)])
    cost_element_id1 = fields.Many2one('project.cost_element', domain=[('level', '=', '1')], string='Cost Element 1')
    cost_element_id2 = fields.Many2one('project.cost_element', domain=[('level', '=', '2')], string='Cost Element 2')
    cost_element_id3 = fields.Many2one('project.cost_element', domain=[('level', '=', '3')], string='Cost Element 3')
    # cost_element_code= fields.Char(string = 'Cost Element Code', readonly=True)
    cost_element_code_sub = fields.Char(string='Cost Element Code',compute='_onchange_element_code',store=True)

    product_ctg      = fields.Many2one('pr.approving.matrix',string='Product DOA',required=True)
    vendor_ids       = fields.Many2many('res.partner',domain=[('supplier','=',True)],required=True)
    analytic_distribution_id = fields.Many2one('account.analytic.distribution', string='Analytic Distribution')
    ordering_date = fields.Date(string="Ordering Date",default=lambda *a: datetime.today().date())

    # @api.model
    # def create(self,vals):
    #     res = super(PurchaseRequisition, self).create(vals)
    #     if not self.analytic_distribution_id:
    #         self.create_analytic()
    #     return res

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
        # domain1 = []
        # domain2 = []
        # domain3 = []
        # if self.project_id.id:
        #     domain1.append(('id', 'in', [line.cost_element_id1.id for line in self.project_id.cost_element_ids]))
        #     domain2.append(('id', 'in', [line.cost_element_id2.id for line in self.project_id.cost_element_ids]))
        #     domain3.append(('id', 'in', [line.cost_element_id3.id for line in self.project_id.cost_element_ids]))
        #     return {'domain': {'cost_element_id1': domain1, 'cost_element_id2': domain2, 'cost_element_id3': domain3}}

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
            domain1 = ['|', ('id', 'in', [line.cost_element_id1.id for line in self.project_id.cost_element_ids]),
                       ('write_uid', 'in', user_ids),('level', '=', '1')]
            domain2 = ['|', ('id', 'in', [line.cost_element_id2.id for line in self.project_id.cost_element_ids]),
                       ('write_uid', 'in', user_ids),('level', '=', '2')]
            domain3 = ['|', ('id', 'in', [line.cost_element_id3.id for line in self.project_id.cost_element_ids]),
                       ('write_uid', 'in', user_ids),('level', '=', '3')]
            return {'domain': {'cost_element_id1': domain1, 'cost_element_id2': domain2, 'cost_element_id3': domain3}}

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

        # result = ''
        # if self.cost_element_id1:
        #     result += self.cost_element_id1.cost_element_code + "-"
        # if self.cost_element_id2:
        #     result += self.cost_element_id2.cost_element_code + "-"
        # if self.cost_element_id3:
        #     result += self.cost_element_id3.cost_element_code
        # self.cost_element_code = result

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
        # if self.cost_element_id1.id:
        #     domain2.append(('id', 'in', [line.cost_element_id2.id for line in self.project_id.cost_element_ids.search(
        #         [('cost_element_id1.id', '=', self.cost_element_id1.id)])]))
        #     domain3.append(('id', 'in', [line.cost_element_id3.id for line in self.project_id.cost_element_ids.search(
        #         [('cost_element_id1.id', '=', self.cost_element_id1.id)])]))
        #     return {'domain': {'cost_element_id2': domain2, 'cost_element_id3': domain3}}
        # if self.cost_element_id2.id:
        #     domain1.append(('id', 'in', [line.cost_element_id1.id for line in self.project_id.cost_element_ids.search(
        #         [('cost_element_id2.id', '=', self.cost_element_id2.id)])]))
        #     domain3.append(('id', 'in', [line.cost_element_id3.id for line in self.project_id.cost_element_ids.search(
        #         [('cost_element_id2.id', '=', self.cost_element_id2.id)])]))
        #     return {'domain': {'cost_element_id1': domain1, 'cost_element_id3': domain3}}
        # if self.cost_element_id3.id:
        #     domain2.append(('id', 'in', [line.cost_element_id2.id for line in self.project_id.cost_element_ids.search(
        #         [('cost_element_id3.id', '=', self.cost_element_id3.id)])]))
        #     domain1.append(('id', 'in', [line.cost_element_id1.id for line in self.project_id.cost_element_ids.search(
        #         [('cost_element_id3.id', '=', self.cost_element_id3.id)])]))
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
            'name': 'Create Analytic Distribution',
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.distribution',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id'   :  self.analytic_distribution_id.id,
            'target'   : 'new',
        }

    @api.multi
    def action_create_po(self):
        for record in self:
            for vendor in record.vendor_ids:
                po_data = {
                    'partner_ref'   : record.name,
                    'origin     '   : record.origin or record.name,
                    'date_order'    : record.ordering_date or fields.Date.today(),
                    'company_id'    : record.company_id.id,
                    'currency_id'   : record.company_id.currency_id.id,
                    'requisition_id': record.id,
                    'picking_type_id': record.picking_type_id.id,
                    'product_ctg'   : record.product_ctg.id,
                    'partner_id'    : vendor.id,
                    'date_planned'  : record.schedule_date,
                    'project_id'    : record.project_id.id,
                    'cost_element_id1': record.cost_element_id1.id,
                    'cost_element_id2': record.cost_element_id2.id,
                    'cost_element_id3': record.cost_element_id3.id,
                    # 'analytic_distribution_id': record.analytic_distribution_id.id,
                }
                po = record.env['purchase.order'].create(po_data)
                record.is_purchase_ids = True

                order_line = po.order_line.browse([])
                for requisition_line in record.line_ids:
                    line_data = {
                        'product_id': requisition_line.product_id.id,
                        'name': requisition_line.description or requisition_line.product_id.display_name,
                        'date_planned': requisition_line.schedule_date or fields.Date.today(),
                        'order_id': po.id,
                        'price_unit': requisition_line.price_unit,
                        'product_qty': requisition_line.product_qty,
                        'product_uom': requisition_line.product_uom_id,
                    }
                    order_line += po.order_line.new(line_data)
                po.order_line = order_line
        return

class purchase_requisition_line(models.Model):
    _inherit = 'purchase.requisition.line'

    product_id  = fields.Many2one('product.product',required=False)
    description = fields.Text(string='Description',required=True)
    product_uom = fields.Many2one('product.uom', required=False)

    @api.onchange('product_id')
    def price_unit_onchange(self):
        self.price_unit = self.product_id.standard_price
        self.description = self.product_id.description or self.product_id.display_name

class account_analytic_distribution(models.Model):
    _inherit='account.analytic.distribution'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        res= super(account_analytic_distribution, self).search_read(domain=domain,fields=fields, offset=offset, limit=limit,order=order)
        if self.env.context.get('active_model',False) == 'purchase.requisition':
            active_id = self.env.context.get('active_id')
            self.env['purchase.requisition'].browse(active_id).analytic_distribution_id = res[0]['id']
        return res

    @api.model
    def create(self, vals):
        res = super(account_analytic_distribution, self).create(vals)
        if self.env.context.get('active_id', False) and self.env.context.get('active_model', False) == 'sale.order.line':
            active_id = self.env.context.get('active_id', False)
            sale_order_line_id = self.env['sale.order.line'].search([('id', '=', active_id)])
            if sale_order_line_id:
                sale_order_line_id.analytic_distribution_id = res.id
        if self.env.context.get('active_id', False) and self.env.context.get('active_model', False) == 'purchase.order.line':
            active_id = self.env.context.get('active_id', False)
            purchase_order_line_id = self.env['purchase.order.line'].search([('id', '=', active_id)])
            if purchase_order_line_id:
                purchase_order_line_id.analytic_distribution_id = res.id
        if self.env.context.get('active_id', False) and self.env.context.get('active_model', False) == 'purchase.request':
            active_id = self.env.context.get('active_id', False)
            purchase_request_id = self.env['purchase.request'].search([('id', '=', active_id)])
            if purchase_request_id:
                purchase_request_id.analytic_distribution_id = res.id

        return res