from odoo import fields, models, api, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class consignment_notes(models.Model):
    _name = 'consignment.notes'
    _rec_sequence = 'name'

    def _compute_invoice_count(self):
        for inv in self:
            invoice = self.env['account.invoice'].search(
                [('consignment_id', '=', inv.id)])
            inv.invoice_count = len(invoice)

    def _compute_delivery_order_count(self):
        for delivery in self:
            order = self.env['stock.picking'].search(
                [('consignment_id', '=', delivery.id)])
            delivery.delivery_order_count = len(order)


    name = fields.Char('Consignment Reference', readonly="True")
    users_id = fields.Many2one('res.users', string="Responsible")
    partner_id = fields.Many2one('res.partner', string="Owner")
    account_analytic_id = fields.Many2one('account.analytic.account',
                                          string='Analytic Account')
    agreement_deadline = fields.Datetime(string="Agreement Deadline")
    source_document = fields.Text(string="Source Document")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done')], string='State', default='draft')
    delivery_order_count = fields.Integer(
        'Delivery Order', compute='_compute_delivery_order_count')
    invoice_count = fields.Integer('Invoice', compute='_compute_invoice_count')
    order_line_ids = fields.One2many('order.lines', 'consignment_id', copy=True)
    picking_type_id = fields.Many2one(
        'stock.picking.type', string="Picking Type")
    account_id = fields.Many2one('account.account', 'Account')
    stock_picking_ids = fields.One2many(
        "stock.picking", 'consignment_id', string="Delivery Orders")
    
    # technical field for invoice and delivery order create
    invoice_create = fields.Boolean("Is invoice created?", help="technical field to hide button.", copy=False)
    delivery_create = fields.Boolean("Delivery Created?", help="technical field to hide button.", copy=False)
    

    @api.multi
    def action_view_delivery(self):
        for rec in self:
            delivery = self.env['stock.picking'].search(
                [('consignment_id', '=', rec.id)])
            # for rec in invoice:
            #     for recode in rec.
            action = self.env.ref('stock.action_picking_tree_all').read()[0]
            if len(delivery) > 1:
                action['domain'] = [('id', 'in', delivery.ids)]
            elif len(delivery) == 1:
                action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
                action['res_id'] = delivery.ids[0]
            else:
                action = {'type': 'ir.actions.act_window_close'}
            return action

    @api.multi
    def action_view_invoice(self):
        for inv in self:
            invoice = self.env['account.invoice'].search([('consignment_id', '=', inv.id)])
            # for rec in invoice:
            #     for recode in rec.
            action = self.env.ref('account.action_invoice_tree1').read()[0]
            if len(invoice) > 1:
                action['domain'] = [('id', 'in', invoice.ids)]
            elif len(invoice) == 1:
                action['views'] = [(self.env.ref('account.invoice_supplier_form').id, 'form')]
                action['res_id'] = invoice.ids[0]
            else:
                action = {'type': 'ir.actions.act_window_close'}
            return action

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('consignment.notes')
        result = super(consignment_notes, self).create(vals)
        return result

    @api.multi
    def create_invoice(self):
        for rec in self:
            invoice_line = []
            for recode in rec.order_line_ids:
                invoice_line.append([0, 0, {
                    'product_id': recode.product_id.id,
                    'product_uom_qty': recode.quantity,
                    # 'quantity': recode.quantity_sold - recode.quantity_invoiced,
                    'quantity': recode.quantity_sold - recode.quantity_invoiced,
                    'product_uom': recode.uom_id.id,
                    'name': recode.product_id.name,
                    'price_unit': recode.price_unit,
                    'account_id': recode.account_id.id,
                    'consignment_note_line_ids': [(6, 0, [recode.id])],
                    }
                    ])
            journal_domain = [
                ('type', '=', 'purchase'),
                ('company_id', '=', rec.partner_id.company_id.id),
                #('currency_id', '=', self.currency_id.id),
            ]
            default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)
                
            invoices = {
                'partner_id': rec.partner_id.id,
                'date_invoice': rec.agreement_deadline,
                'invoice_line_ids': invoice_line,
                'account_id': rec.account_id.id,
                'user_id': rec.users_id.id,
                'consignment_id': rec.id,
                'is_consignment': True,
                'type': 'in_invoice',
                'journal_id': default_journal_id.id

            }
            create_invoice = self.env['account.invoice'].with_context(
                {'default_type': 'in_invoice', 'default_journal_id': default_journal_id.id,
                'type': 'in_invoice', 'journal_id': default_journal_id.id,}).create(invoices)
            self.write({'invoice_create': True})
        invoice = self.env['account.invoice'].search([('consignment_id', '=', self.ids)])
        action = self.env.ref('account.action_invoice_tree2').read()[0]
        if len(invoice) > 1:
            action['domain'] = [('id', 'in', invoice.ids)]
        elif len(invoice) == 1:
            action['views'] = [(self.env.ref('account.invoice_supplier_form').id, 'form')]
            action['res_id'] = invoice.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def confirm(self):
        for rec in self:
            move = []
            '''
            for recode in rec.order_line_ids:
                    move.append([0, 0, {
                        'product_id': recode.product_id.id,
                        'product_uom_qty': recode.quantity,
                        'product_uom': recode.uom_id.id,
                        'name': recode.product_id.name,
                    }])
            delivery_order = {
                'partner_id': rec.partner_id.id,
                'min_date': rec.agreement_deadline,
                'location_dest_id': self.env.ref('stock.stock_location_stock', raise_if_not_found=False).id,
                'location_id': rec.partner_id.property_stock_supplier.id,
                'picking_type_id': rec.picking_type_id.id,
                'move_lines': move,
                'owner_id': rec.partner_id.id,
                'consignment_id': rec.id,
                'origin': rec.source_document,
            }
            delivery = self.env['stock.picking'].create(delivery_order)
            '''
            rec.write({'state': 'confirmed'})
        return True

    @api.multi
    def create_delivery_order(self):
        
        action = self.env.ref('stock.action_picking_tree_all')
        result = action.read()[0]
        location_source_id = self.picking_type_id.default_location_src_id.id
        location_dest_id = self.picking_type_id.default_location_dest_id.id
        # override the context to get rid of the default filtering
        delivery_order = {
                'partner_id': self.partner_id.id,
                'min_date': self.agreement_deadline,
               # 'location_dest_id': self.env.ref('stock.stock_location_stock', raise_if_not_found=False).id,
                #'location_dest_id': self.env.ref('stock.stock_location_suppliers', raise_if_not_found=False).id,
                'location_dest_id':location_dest_id or self.env.ref('stock.stock_location_suppliers', raise_if_not_found=False).id,
                #'location_id': self.partner_id.property_stock_supplier.id,
                'location_id': location_source_id or self.env.ref('stock.stock_location_stock', raise_if_not_found=False).id,
                'picking_type_id': self.picking_type_id.id,
                #'move_lines': move,
                'owner_id': self.partner_id.id,
                'consignment_id': self.id,
                'origin': self.source_document,
                
            }
        delivery_obj = self.env['stock.picking'].create(delivery_order)
        move = []
        for recode in self.order_line_ids:
            '''
            move.append((0, 0, {
                'product_id': recode.product_id.id,
                #'product_uom_qty': recode.quantity,
                #'product_uom': recode.uom_id.id,
                #'name': recode.product_id.name,
                #'scrapped': False,
                'product_uom_qty': recode.quantity,
                'product_uom': recode.uom_id.id,
                'name': recode.product_id.name,
                'date_expected': '2018-06-09 07:36:14',
                'location_dest_id': self.env.ref('stock.stock_location_suppliers', raise_if_not_found=False).id,
                'location_id': self.env.ref('stock.stock_location_stock', raise_if_not_found=False).id,
                
            }))
            '''
            delivery = self.env['stock.move'].create({
                'product_id': recode.product_id.id,
                #'product_uom_qty': recode.quantity,
                #'product_uom': recode.uom_id.id,
                #'name': recode.product_id.name,
                #'scrapped': False,
                'product_uom_qty': recode.quantity,
                'product_uom': recode.uom_id.id,
                'name': recode.product_id.name,
                'date_expected': '2018-06-09 07:36:14',
                'state': 'draft',
                'location_dest_id': location_dest_id or self.env.ref('stock.stock_location_suppliers', raise_if_not_found=False).id,
                'location_id': location_source_id or self.env.ref('stock.stock_location_stock', raise_if_not_found=False).id,
                'picking_id': delivery_obj.id,
                })
            

        #delivery = self.env['stock.picking'].create(delivery_order)
        '''
        result['context'] = {'default_picking_type_id': self.picking_type_id.id,
                             'default_consignment_id': self.id,
                             'default_partner_id': self.partner_id.id,
                             'default_min_date': self.agreement_deadline,
                             #'default_location_id' : self.partner_id.property_stock_supplier.id,
                             'default_origin': self.source_document,
                             #'default_move_lines': move,
                             'default_owner_id': self.partner_id.id,
                              }
        '''
        delivery_obj.action_assign_owner()
        if self.env.ref('stock.picking_type_in').id == self.picking_type_id.id:
            delivery_obj.action_confirm()
            delivery_obj.force_assign()
        self.write({'delivery_create': True})
        # choose the view_mode accordingly
        if len(self.stock_picking_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(self.stock_picking_ids.ids) + ")]"

        elif len(self.stock_picking_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.stock_picking_ids.id
        return result


consignment_notes()


class order_line(models.Model):
    _name = 'order.lines'

    @api.multi
    @api.depends('product_id')
    def _compute_delivery_quantity(self):
        delivery_qty = 0.0
        for delivery in self:
            picking_ids = self.env['stock.picking'].search(
                [('owner_id', '=', delivery.consignment_id.partner_id.id),
                 ('state', '=', 'done')])
            for picking_id in picking_ids:
                if picking_id.picking_type_id.name == 'Receipts':
                    for rec in picking_id.move_lines:
                        if rec.product_id.id == delivery.product_id.id:
                            delivery_qty += rec.product_uom_qty
        delivery.delivered_quantities = delivery_qty
    @api.multi
    @api.depends('product_id')
    def _compute_quantity_sold(self):
        qty_sold = 0.0
        for delivery in self:
            picking_ids = self.env['stock.picking'].search(
                [('owner_id', '=', delivery.consignment_id.partner_id.id),
                 ('state', '=', 'done')])
            for picking_id in picking_ids:
                if picking_id.picking_type_id.name == 'Delivery Orders':
                    for rec in picking_id.move_lines:
                        if rec.product_id.id == delivery.product_id.id:
                            qty_sold += rec.product_uom_qty
        delivery.quantity_sold = qty_sold
    @api.depends('invoice_lines.invoice_id.state', 'invoice_lines.quantity','consignment_id.state')
    def get_quantity_invoiced(self):
        paid = True
        for line in self:
            qty_invoiced = 0.0
            for invoice_line in line.invoice_lines:
                if invoice_line.invoice_id.state == 'paid':
                    if invoice_line.invoice_id.type == 'in_invoice':
                        qty_invoiced += invoice_line.quantity

                    elif invoice_line.invoice_id.type == 'in_refund':
                        qty_invoiced -= invoice_line.quantity

            line.quantity_invoiced = qty_invoiced
            if line.quantity_invoiced < line.quantity:
                paid = False
        # if paid:
        #     self.env.cr.execute(""" update consignment_notes set state = 'done' where id = %s
        #     """ % ( self.consignment_id.id) )

    invoice_lines = fields.Many2many(
        'account.invoice.line', 'consignment_notes_line_invoice_rel', 'order_line_id',
        'invoice_line_id', string='Invoice Lines', copy=False)
    quantity_invoiced = fields.Integer(
        'Quantity Invoiced',compute="get_quantity_invoiced", store=True)
    consignment_id = fields.Many2one('consignment.notes')
    product_id = fields.Many2one('product.product' ,'Product' ,required=True)
    quantity = fields.Float(string = 'Quantity' ,required=True,default=1.0)
    account_analytic_id = fields.Many2one('account.analytic.account',
                                          string='Analytic Account')
    delivered_quantities = fields.Integer(
        'Delivered Quantities', compute='_compute_delivery_quantity')
    quantity_sold = fields.Integer(
        'Quantity Sold', compute='_compute_quantity_sold')
    uom_id = fields.Many2one('product.uom', string='Unit of Measure',
                              index=True ,required=True)
    price_unit = fields.Float(string='Unit Price' ,required=True)
    account_id = fields.Many2one('account.account', 'Account' ,required=True)
    check_qty = fields.Boolean('Check QTY')

    @api.onchange('product_id')
    def product_onchange(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id
            self.price_unit = self.product_id.lst_price
        else:
            self.uom_id = False

    
order_line()


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    consignment_note_line_ids = fields.Many2many(
        'order.lines','consignment_notes_line_invoice_rel','invoice_line_id', 'order_line_id',
        string='Consignment Notes Order Lines', readonly=True, copy=False)


AccountInvoiceLine()


class account_account(models.Model):
    _inherit = 'account.invoice'

    consignment_id = fields.Many2one(
        'consignment.notes', string="Consignment Notes")
    is_consignment = fields.Boolean('Is Consignment')

    @api.multi
    def action_invoice_open(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: inv.state not in ['proforma2', 'draft']):
            raise UserError(_("Invoice must be in draft or Pro-forma state in order to validate it."))
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        for rec in self:
            if rec.consignment_id:
                for one_line in rec.invoice_line_ids:
                    paid = True
                    if one_line.product_id:
                        for one_consignment_line in self.env['order.lines'].sudo().search(
                                [('product_id', '=', one_line.product_id.id),
                                 ('consignment_id', '=', rec.consignment_id.id)]):
                            one_consignment_line.sudo().write({
                                'quantity_invoiced': one_consignment_line.quantity_invoiced + one_line.quantity
                            })
                            if one_consignment_line.quantity_invoiced < one_consignment_line.quantity:
                                paid = False
                        if paid:
                            self.env.cr.execute(""" update consignment_notes set state = 'done' where id = %s
                            """ % ( rec.consignment_id.id) )
        return to_open_invoices.invoice_validate()


account_account()

class stock_picking(models.Model):
    _inherit = 'stock.picking'

    consignment_id = fields.Many2one(
        'consignment.notes', string="Consignment Notes")

    @api.onchange('owner_id')
    def _on_change_owner(self):
        if self.owner_id:
            for pack_operation in self.pack_operation_product_ids:
                pack_operation['owner_id'] = self.owner_id.id

stock_picking()
