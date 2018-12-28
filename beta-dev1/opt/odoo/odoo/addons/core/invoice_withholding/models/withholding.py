# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class WithHoldingLine(models.Model):
    _name = 'withholding.line'

    name = fields.Char()
    partner_id = fields.Many2one('res.partner', 'Customer', required=True)
    project_id = fields.Many2one('project.project', 'Project')
    invoice_id = fields.Many2one('account.invoice', 'Invoice')
    payment_invoice_id = fields.Many2one('account.invoice', 'Payment Invoice')
    product_id = fields.Many2one('product.product', 'Product', required=True)
    amount = fields.Float(required=True)
    state = fields.Selection([
        ('to_invoice', 'To Invoiced'),
        ('invoiced', 'Invoiced')], index=True, default='to_invoice')

    @api.multi
    def unlink(self):
        for line in self:
            if line.state == 'invoiced':
                raise UserError(_('You can not delete a invoiced Withholding Line.'))
        return super(WithHoldingLine, self).unlink()

class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def _withholding_count(self):
        for rec in self:
            rec.witholding_count = self.env['withholding.line'].search_count([('partner_id','=',rec.id)])

    witholding_count = fields.Integer(compute="_withholding_count", readonly=True, string="Withlodings")
    withholding_ids = fields.One2many('withholding.line', 'partner_id', string='Withholding Lines', copy=False)

    @api.multi
    def partner_withholding_action(self):
        return {
            'name': _('Withholdings'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'withholding.line',
            'type': 'ir.actions.act_window',
            'domain': [('id','in', self.withholding_ids.ids)],
            'context': {
                'default_partner_id': self.id,
            }
        }

class ProjectProject(models.Model):
    _inherit = "project.project"

    @api.multi
    def _withholding_count(self):
        for rec in self:
            rec.witholding_count = self.env['withholding.line'].search_count([('project_id','=',rec.id)])

    witholding_count = fields.Integer(compute="_withholding_count", readonly=True, string="Withlodings")
    withholding_ids = fields.One2many('withholding.line', 'project_id', string='Withholding Lines', copy=False)
    holding_percent = fields.Float('Withholding Percentage')

    @api.multi
    def project_withholding_action(self):
        return {
            'name': _('Withholdings'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'withholding.line',
            'type': 'ir.actions.act_window',
            'domain': [('id','in', self.withholding_ids.ids)],
            'context': {
                'default_project_id': self.id,
            }
        }


class InvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    withholding_id = fields.Many2one('withholding.line', string='Withholding Line', copy=False)


class Invoice(models.Model):
    _inherit = "account.invoice"

    withholding_ids = fields.One2many('withholding.line', 'invoice_id', string='Withholding Lines', copy=False)
    withholding_amount = fields.Boolean("Add withholding Amount", readonly=True, states={'draft': [('readonly', False)]},)

    @api.multi
    def action_invoice_open(self):
        res = super(Invoice, self).action_invoice_open()
        lines = self.env['withholding.line'].search([('invoice_id', 'in', self.ids)])
        for line in lines:
            line.name = line.name + ' ' + line.invoice_id.number
        return res

    @api.multi
    def _withholding_unset(self):
        if self.env.user.company_id.withholding_product_id:
            self.env['account.invoice.line'].search([('invoice_id', 'in', self.ids), ('product_id', '=', self.env.user.company_id.withholding_product_id.id)]).unlink()
            self.env['withholding.line'].search([('invoice_id', 'in', self.ids)]).unlink()

    @api.multi
    def create_withholding(self):
        InvoiceLine = self.env['account.invoice.line']
        

        product_id = self.env.user.company_id.withholding_product_id
        withholding_percentage = self.env.user.company_id.withholding_percentage
        if not product_id:
            raise UserError(_('Please set Withholding product in General Settings first.'))

        # Remove Witholding line first
        self._withholding_unset()

        account_id = product_id.property_account_income_id.id
        if not account_id:
            prop = self.env['ir.property'].get('property_account_income_categ_id', 'product.category')
            account_id = prop and prop.id or False

        for invoice in self:
            
            # Apply fiscal position
            taxes = product_id.taxes_id.filtered(lambda t: t.company_id.id == invoice.company_id.id)
            taxes_ids = taxes.ids
            if invoice.partner_id and self.fiscal_position_id:
                taxes_ids = self.fiscal_position_id.map_tax(taxes, product_id, invoice.partner_id).ids

            amount = -(invoice.amount_total * withholding_percentage)/100

            # Create the Invoice line
            InvoiceLine.create({
                'name':  str(withholding_percentage) + '% Withholding of Invoice',
                'price_unit': amount,
                'account_id': account_id,
                'quantity': 1.0,
                'discount': 0.0,
                'uom_id': product_id.uom_id.id,
                'product_id': product_id.id,
                'invoice_id': invoice.id,
                'invoice_line_tax_ids': [(6, 0, taxes_ids)],
            })
        return True


    @api.multi
    def invoice_validate(self):
        res = super(Invoice, self).invoice_validate()
        WithholdingLine = self.env['withholding.line']

        for inv in self:
            if inv.withholding_amount:
                for line in inv.invoice_line_ids:
                    if self.env.user.company_id.withholding_product_id and (line.product_id.id == self.env.user.company_id.withholding_product_id.id):
                        #Create witholding line
                        wh_line = WithholdingLine.create({
                            'name': line.name,
                            'product_id': line.product_id.id,
                            'partner_id': inv.partner_id.id,
                            'amount': -line.price_subtotal,
                            'invoice_id': inv.id,
                        })
                        line.withholding_id = wh_line.id
        return res