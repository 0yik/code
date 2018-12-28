# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)

class ProductCategory(models.Model):
    _inherit = 'product.category'

    property_valuation = fields.Selection(selection_add=[('vendor_bill', 'Vendor Bill (automated)')])


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    property_valuation = fields.Selection(selection_add=[('vendor_bill', 'Vendor Bill (automated)')])


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    inventory_value = fields.Float('Inventory Value', compute='_compute_inventory_value', readonly=True, store=True)

    def _account_entry_move(self, move):
        """ Accounting Valuation Entries """
        if move.product_id.type != 'product' or move.product_id.valuation == 'manual_periodic':
            # no stock valuation for consumable products
            return False
        if any(quant.owner_id or quant.qty <= 0 for quant in self):
            # if the quant isn't owned by the company, we don't make any valuation en
            # we don't make any stock valuation for negative quants because the valuation is already made for the counterpart.
            # At that time the valuation will be made at the product cost price and afterward there will be new accounting entries
            # to make the adjustments when we know the real cost price.
            return False

        location_from = move.location_id
        location_to = self[0].location_id  # TDE FIXME: as the accounting is based on this value, should probably check all location_to to be the same
        company_from = location_from.usage == 'internal' and location_from.company_id or False
        company_to = location_to and (location_to.usage == 'internal') and location_to.company_id or False

        # Create Journal Entry for products arriving in the company; in case of routes making the link between several
        # warehouse of the same company, the transit location belongs to this company, so we don't need to create accounting entries
        if company_to and (move.location_id.usage not in ('internal', 'transit') and move.location_dest_id.usage == 'internal' or company_from != company_to):
            journal_id, acc_src, acc_dest, acc_valuation = move._get_accounting_data_for_valuation()
            if location_from and location_from.usage == 'customer':  # goods returned from customer
                self.with_context(force_company=company_to.id)._create_account_move_line(move, acc_dest, acc_valuation, journal_id)
            else:
                self.with_context(force_company=company_to.id)._create_account_move_line(move, acc_src, acc_valuation, journal_id)

        # Create Journal Entry for products leaving the company
        if company_from and (move.location_id.usage == 'internal' and move.location_dest_id.usage not in ('internal', 'transit') or company_from != company_to):
            journal_id, acc_src, acc_dest, acc_valuation = move._get_accounting_data_for_valuation()
            if location_to and location_to.usage == 'supplier':  # goods returned to supplier
                self.with_context(force_company=company_from.id)._create_account_move_line(move, acc_valuation, acc_src, journal_id)
            else:
                self.with_context(force_company=company_from.id)._create_account_move_line(move, acc_valuation, acc_dest, journal_id)

        if move.company_id.anglo_saxon_accounting and move.location_id.usage == 'supplier' and move.location_dest_id.usage == 'customer':
            # Creates an account entry from stock_input to stock_output on a dropship move. https://github.com/odoo/odoo/issues/12687
            journal_id, acc_src, acc_dest, acc_valuation = move._get_accounting_data_for_valuation()
            self.with_context(force_company=move.company_id.id)._create_account_move_line(move, acc_src, acc_dest, journal_id)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        for invoice in self.filtered(lambda x: x.type == 'in_invoice'):
            for invoice_line in invoice.invoice_line_ids:
                if invoice_line.purchase_line_id and invoice_line.product_id.categ_id.property_valuation == "vendor_bill":

                    valuation_stock_moves = self.env['stock.move'].search([('purchase_line_id','=',invoice_line.purchase_line_id.id),('state', '=', 'done')])
                    for quant_id in valuation_stock_moves[0].quant_ids.filtered(lambda x: x.product_id.id == invoice_line.product_id.id):

                        if quant_id.qty == invoice_line.quantity:
                            avg_new_cost = invoice_line.price_subtotal / invoice_line.quantity

                            quant_id.sudo().write({'cost': avg_new_cost, 'inventory_value':avg_new_cost * quant_id.qty})

                        elif quant_id.qty > invoice_line.quantity:
                            invoice_qty_cost = invoice_line.price_subtotal
                            quant_cost = (quant_id.qty - invoice_line.quantity) * quant_id.cost
                            avg_new_cost = (quant_cost + invoice_qty_cost) / quant_id.qty
                            quant_id.sudo().write({'cost': avg_new_cost, 'inventory_value':avg_new_cost * quant_id.qty})

                        elif quant_id.qty < invoice_line.quantity:
                            avg_new_cost = invoice_line.price_subtotal / invoice_line.quantity
                            quant_id.sudo().write({'cost': avg_new_cost, 'qty': invoice_line.quantity,
                                                   'inventory_value':avg_new_cost * quant_id.qty})
            return res
