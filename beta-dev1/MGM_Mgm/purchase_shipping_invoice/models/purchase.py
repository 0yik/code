
from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends('service_product_lines.shipping_amount', 'service_product_lines.total')
    def _service_amount_all(self):
        for order in self:
            amount_total = 0.0
            for line in order.service_product_lines:
                amount_total += line.total
            order.update({
                'service_amount_total': amount_total
            })

    def _compute_vendor_bill_count(self):
        for order in self:
            orders = self.env['account.invoice'].search([('purchase_id','=', order.id),('is_shipment_bill', '=', True)])
            order.vendor_bill_count = len(orders)

    vendor_bill_count = fields.Integer('Completed Work Order ', compute='_compute_vendor_bill_count')
    service_product_lines = fields.One2many('purchase.service.product', 'purchase_id', 'Service Products')
    service_amount_total = fields.Float(string='Total', store=True, readonly=True, compute='_service_amount_all')

    @api.multi
    def action_view_vendor_bills(self):
        for rec in self:
            vendor_bills = self.env['account.invoice'].search([('purchase_id', '=', rec.id),('is_shipment_bill', '=', True)])
            action = self.env.ref('account.action_invoice_tree2').read()[0]
            if len(vendor_bills) > 1:
                action['domain'] = [('id', 'in', vendor_bills.ids)]
                action['display_name'] = "Shipment Vendor Bills"
            elif len(vendor_bills) == 1:
                action['views'] = [(self.env.ref('account.invoice_supplier_form').id, 'form')]
                action['res_id'] = vendor_bills.ids[0]
                action['display_name'] = "Shipment Vendor Bills"
            else:
                action = {'type': 'ir.actions.act_window_close'}
            return action


class PurchaseServiceProducts(models.Model):
    _name = 'purchase.service.product'

    purchase_id = fields.Many2one('purchase.order', 'Purchase Reference')
    product_id = fields.Many2one('product.product', 'Shipping Product', required=1)
    name = fields.Text('Description')
    shipping_amount = fields.Float(string='Shipping Amount')
    shipping_vendor = fields.Char('Shipping Vendor')
    shipping_information = fields.Text('Shipping Information')
    total = fields.Float(string='Total', readonly=True, related='shipping_amount')

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result

        product_lang = self.product_id.with_context(
            lang=self.purchase_id.partner_id.lang,
            partner_id=self.purchase_id.partner_id.id,
        )
        self.name = product_lang.display_name
        if product_lang.description_purchase:
            self.name += '\n' + product_lang.description_purchase
        self.shipping_amount = self.product_id.lst_price
        self.shipping_vendor = self.purchase_id.partner_id.name

