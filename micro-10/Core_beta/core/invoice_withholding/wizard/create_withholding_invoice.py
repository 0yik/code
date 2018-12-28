# -*- coding: utf-8 -*-

import time

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class WithholdingLine(models.Model):
    _inherit = "withholding.line"

    payment_wiz_id = fields.Many2one('res.partner', 'Customer')


class WithholdingPayment(models.TransientModel):
    _name = "withholding.payment.inv"
    _description = "Withholding Payment Invoice"

    line_ids = fields.One2many('withholding.line', 'payment_wiz_id', string='Withholding Lines')
    partner_id = fields.Many2one('res.partner', 'Customer', readonly=True)

    @api.model
    def default_get(self, fields):
        res = super(WithholdingPayment, self).default_get(fields)
        vals = []
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        if active_model == 'res.partner':
            domain = [('partner_id', '=', active_id), ('state','=','to_invoice')]
            res.update({'partner_id': active_id})
        if active_model == 'project.project':
            proj = self.env[active_model].browse(active_id)
            domain = [('project_id', '=', active_id), ('state','=','to_invoice')]
            res.update({'partner_id': proj.partner_id.id})
        lines = self.env['withholding.line'].search(domain)
        res.update({'line_ids': [(6, 0, lines.ids)]})
        return res

    @api.multi
    def create_invoice(self):
        inv_obj = self.env['account.invoice']
        inv_line_obj = self.env['account.invoice.line']
        invoice = inv_obj.create({
            'account_id': self.partner_id.property_account_receivable_id.id,
            'partner_id': self.partner_id.id,
            'type': 'out_invoice',
            'name': '-',
            'currency_id': self.env.user.company_id.currency_id.id,
        })
        for line in self.line_ids:
            account_id = False
            if line.product_id:
                account_id = line.product_id.property_account_income_id.id
            if not account_id:
                prop = self.env['ir.property'].get('property_account_income_categ_id', 'product.category')
                account_id = prop and prop.id or False
            inv_line_obj.create({
                'name': line.name,
                'price_unit': line.amount,
                'account_id': account_id,
                'quantity': 1.0,
                'discount': 0.0,
                'uom_id': line.product_id.uom_id.id,
                'product_id': line.product_id.id,
                'account_analytic_id': False,
                'invoice_id': invoice.id,
            })
            line.state = 'invoiced'
            line.payment_invoice_id = invoice.id

        return invoice

    
    @api.multi
    def create_and_view_invoice(self):
        invoice = self.create_invoice()
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('account.action_invoice_tree1')
        list_view_id = imd.xmlid_to_res_id('account.invoice_tree')
        form_view_id = imd.xmlid_to_res_id('account.invoice_form')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[form_view_id, 'form'], [list_view_id, 'tree'], [False, 'graph'], [False, 'kanban'], [False, 'calendar'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
            'res_id': invoice.id,
        }
        return result