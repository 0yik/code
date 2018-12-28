from odoo import fields,models,api,_
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class consignment_notes(models.Model):
    _name = 'consignment.notes'
    _rec_sequence = 'name'

    def _compute_invoice_count(self):
        for inv in self:
            invoice = self.env['account.invoice'].search([('consignment_id','=', inv.id)])
            inv.invoice_count = len(invoice)

    def _compute_delivery_order_count(self):
        for delivery in self:
            order = self.env['stock.picking'].search([('consignment_id','=', delivery.id)])
            delivery.delivery_order_count = len(order)


    name = fields.Char('Consignment Reference' ,readonly="True")
    users_id = fields.Many2one('res.users', string = "Responsible")
    partner_id = fields.Many2one('res.partner',string = "Owner")
    account_analytic_id = fields.Many2one('account.analytic.account',
                                          string='Analytic Account')
    agreement_deadline = fields.Datetime(string="Agreement Deadline")
    source_document = fields.Text(string="Source Document")
    state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('done','Done')], string='State', default='draft')
    delivery_order_count = fields.Integer('Delivery Order', compute='_compute_delivery_order_count')
    invoice_count = fields.Integer('Invoice', compute='_compute_invoice_count')
    order_line_ids = fields.One2many('order.lines','consignment_id')
    picking_type_id = fields.Many2one('stock.picking.type' , string="Picking Type")
    account_id = fields.Many2one('account.account','Account')

    @api.multi
    def action_view_delivery(self):
        for rec in self:
            delivery = self.env['stock.picking'].search([('consignment_id', '=', rec.id)])
            # for rec in invoice:
            #     for recode in rec.
            action = self.env.ref('stock.action_picking_tree_all').read()[0]
            if len(delivery) > 1:
                action['domain'] = [('id', 'in', delivery.ids)]
            elif len(delivery) == 1 :
                action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
                action['res_id'] = delivery.ids[0]
            else:
                action = {'type':'ir.actions.act_window_close'}
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
            elif len(invoice) == 1 :
                action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
                action['res_id'] = invoice.ids[0]
            else:
                action = {'type':'ir.actions.act_window_close'}
            return action

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('consignment.notes')
        result = super(consignment_notes, self).create(vals)
        return result


    @api.multi
    def create_invoice(self):
        for rec in self :

            invoice_line = []
            for recode in rec.order_line_ids:
                invoice_line.append([0, 0, {
                        'product_id': recode.product_id.id,
                        'product_uom_qty': recode.quantity,
                        'quantity': recode.quantity_sold - recode.quantity_invoiced,
                        'product_uom': recode.uom_id.id,
                        'name': recode.product_id.name,
                        'price_unit': recode.price_unit,
                        'account_id': recode.account_id.id,
                    }
                    ])
            invoices = {
                'partner_id': rec.partner_id.id,
                'date_invoice': rec.agreement_deadline,
                'invoice_line_ids': invoice_line,
                'account_id': rec.account_id.id,
                'user_id' : rec.users_id.id,
                'consignment_id': rec.id,
                'is_consignment': True,
                'type': 'in_invoice',

            }
            create_invoice = self.env['account.invoice'].create(invoices)
            rec.write({'state': 'done'})
        return True



    @api.multi
    def confirm(self):
        for rec in self :

            move = []
            for recode in rec.order_line_ids:

                    move.append([0, 0, {
                        'product_id': recode.product_id.id,
                        'product_uom_qty': recode.quantity,
                        'product_uom': recode.uom_id.id,
                        'name': recode.product_id.name,
                    }
                    ])
            delivery_order = {
                'partner_id': rec.partner_id.id,
                'min_date': rec.agreement_deadline,
                'location_dest_id': self.env.ref('stock.stock_location_stock', raise_if_not_found=False).id,
                'location_id': rec.partner_id.property_stock_supplier.id,
                'picking_type_id': rec.picking_type_id.id,
                'move_lines': move,
                'consignment_id': rec.id,
                'origin': rec.source_document,
            }
            delivery = self.env['stock.picking'].create(delivery_order)
            rec.write({'state':'confirmed'})
        return True
class order_line(models.Model):
    _name = 'order.lines'

    @api.multi
    @api.depends('product_id')
    def _compute_delivery_quantity(self):
        for delivery in self:
            picking_id = self.env['stock.picking'].search([('partner_id','=', delivery.consignment_id.partner_id.id),('state','=','done')])
            if picking_id.picking_type_id.name == 'Receipts':
                for rec in picking_id.move_lines:
                    if rec.product_id.id == delivery.product_id.id:
                        delivery.delivered_quantities = rec.product_uom_qty

    @api.multi
    @api.depends('product_id')
    def _compute_quantity_sold(self):
        for delivery in self:
            picking_id = self.env['stock.picking'].search([('partner_id','=', delivery.consignment_id.partner_id.id),('state','=','done')])
            if picking_id.picking_type_id.name == 'Delivery Orders':
                for rec in picking_id.move_lines:
                    if rec.product_id.id == delivery.product_id.id:
                        delivery.quantity_sold = rec.product_uom_qty


    consignment_id = fields.Many2one('consignment.notes')
    product_id = fields.Many2one('product.product' ,'Product' ,required=True)
    quantity = fields.Float(string = 'Quantity' ,required=True)
    account_analytic_id = fields.Many2one('account.analytic.account',
                                          string='Analytic Account')
    delivered_quantities = fields.Integer('Delivered Quantities', compute='_compute_delivery_quantity')
    quantity_sold = fields.Integer('Quantity Sold', compute='_compute_quantity_sold')
    quantity_invoiced = fields.Integer('Quantity Invoiced')

    uom_id = fields.Many2one('product.uom', string='Unit of Measure',
                              index=True ,required=True)
    price_unit = fields.Float(string='Unit Price' ,required=True)
    account_id = fields.Many2one('account.account', 'Account' ,required=True)

class account_account(models.Model):
    _inherit = 'account.invoice'

    consignment_id = fields.Many2one('consignment.notes', string="Consignment Notes")
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
                    if one_line.product_id:
                        for one_consignment_line in self.env['order.lines'].sudo().search([('product_id', '=', one_line.product_id.id),('consignment_id', '=', rec.consignment_id.id)]):
                            one_consignment_line.sudo().write({
                                'quantity_invoiced': one_consignment_line.quantity_invoiced + one_line.quantity
                            })
        return to_open_invoices.invoice_validate()


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    consignment_id = fields.Many2one('consignment.notes', string="Consignment Notes")
