from odoo import models, fields, api,_
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from odoo.exceptions import ValidationError

class consignment_notes(models.Model):
    _inherit = 'consignment.notes'

    @api.multi
    def create_delivery_order(self):

        action = self.env.ref('stock.action_picking_tree_all')
        result = action.read()[0]

        # override the context to get rid of the default filtering
        delivery_order = {
            'partner_id': self.partner_id.id,
            'min_date': self.agreement_deadline,
            # 'location_dest_id': self.env.ref('stock.stock_location_stock', raise_if_not_found=False).id,
            'location_dest_id': self.env.ref('stock.stock_location_suppliers', raise_if_not_found=False).id,
            # 'location_id': self.partner_id.property_stock_supplier.id,
            # 'location_id': self.env.ref('stock.stock_location_stock', raise_if_not_found=False).id,
            'location_id': self.env.ref('stock.stock_location_suppliers', raise_if_not_found=False).id,
            'picking_type_id': self.picking_type_id.id,
            # 'move_lines': move,
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
                # 'product_uom_qty': recode.quantity,
                # 'product_uom': recode.uom_id.id,
                # 'name': recode.product_id.name,
                # 'scrapped': False,
                'product_uom_qty': recode.quantity,
                'product_uom': recode.uom_id.id,
                'name': recode.product_id.name,
                'date_expected': '2018-06-09 07:36:14',
                'state': 'draft',
                'location_dest_id': self.env.ref('stock.stock_location_suppliers', raise_if_not_found=False).id,
                'location_id': self.env.ref('stock.stock_location_stock', raise_if_not_found=False).id,
                'picking_id': delivery_obj.id,
            })

        # delivery = self.env['stock.picking'].create(delivery_order)
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

    @api.multi
    def create_invoice(self):
        for rec in self:
            invoice_line = []
            for recode in rec.order_line_ids:
                invoice_line.append([0, 0, {
                    'product_id': recode.product_id.id,
                    'product_uom_qty': recode.quantity,
                    # 'quantity': recode.quantity_sold - recode.quantity_invoiced,
                    # 'quantity': recode.quantity_sold - recode.quantity_invoiced,
                    'quantity': recode.quantity,
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
                # ('currency_id', '=', self.currency_id.id),
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
                 'type': 'in_invoice', 'journal_id': default_journal_id.id, }).create(invoices)
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
