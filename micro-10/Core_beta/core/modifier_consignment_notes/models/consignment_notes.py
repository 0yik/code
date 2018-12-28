# -*- coding: utf-8 -*-
from openerp import api, fields, models, _

class ConsignmentNotes(models.Model):
    _inherit = 'consignment.notes'

    stock_picking_ids = fields.One2many("stock.picking",'consignment_id', string="Delivery Orders")


    @api.multi
    def confirm(self):
        for rec in self :
            rec.write({'state':'confirmed'})
        return True

    @api.multi
    def create_delivery_order(self):
        action = self.env.ref('stock.action_picking_tree_all')
        result = action.read()[0]

        # override the context to get rid of the default filtering
        move = []
        for recode in self.order_line_ids:
            move.append([0, 0, {
                'product_id': recode.product_id.id,
                #'product_uom_qty': recode.quantity,
                #'product_uom': recode.uom_id.id,
                #'name': recode.product_id.name,
                #'scrapped': False,
            }
        ])

        result['context'] = {'default_picking_type_id': self.picking_type_id.id,
                             'default_consignment_id': self.id,
                             'default_partner_id':self.partner_id.id,
                             'default_min_date': self.agreement_deadline,
                             #'default_location_id' : self.partner_id.property_stock_supplier.id,
                             'default_origin': self.source_document,
                             #'default_move_lines': move,
                             'default_owner_id':self.partner_id.id,
                    }

        # choose the view_mode accordingly
        if len(self.stock_picking_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(self.stock_picking_ids.ids) + ")]"

        elif len(self.stock_picking_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.stock_picking_ids.id

        return result


    @api.multi
    def create_invoice(self):
        for rec in self:
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
                    'consignment_note_line_ids': [(6, 0, [recode.id])],
                }
            ])

            invoices = {
                'partner_id': rec.partner_id.id,
                'date_invoice': rec.agreement_deadline,
                'invoice_line_ids': invoice_line,
                'account_id': rec.account_id.id,
                'user_id': rec.users_id.id,
                'consignment_id': rec.id,
                'is_consignment': True,
                'type': 'in_invoice',
            }

            self.env['account.invoice'].create(invoices)
            #rec.write({'state': 'done'})

        return True


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    consignment_note_line_ids = fields.Many2many(
        'order.lines','consignment_notes_line_invoice_rel','invoice_line_id', 'order_line_id',
        string='Consignment Notes Order Lines', readonly=True, copy=False)


class order_line(models.Model):
    _inherit = 'order.lines'

    @api.depends('invoice_lines.invoice_id.state', 'invoice_lines.quantity','consignment_id.state')
    def get_quantity_invoiced(self):
        paid = True
        for line in self:
            qty_invoiced = 0.0
            for invoice_line in line.invoice_lines:
                if invoice_line.invoice_id.state != 'cancel':
                    if invoice_line.invoice_id.type == 'in_invoice':
                        qty_invoiced += invoice_line.quantity

                    elif invoice_line.invoice_id.type == 'in_refund':
                        qty_invoiced -= invoice_line.quantity

            line.quantity_invoiced = qty_invoiced
            if line.quantity_invoiced < line.quantity:
                paid = False

        if paid:
            self.env.cr.execute(""" update consignment_notes set state = 'done' where id = %s 
            """ % ( self.consignment_id.id) )


    invoice_lines = fields.Many2many('account.invoice.line', 'consignment_notes_line_invoice_rel', 'order_line_id',
                                     'invoice_line_id', string='Invoice Lines', copy=False)

    quantity_invoiced = fields.Integer('Quantity Invoiced',compute="get_quantity_invoiced", store=True)




