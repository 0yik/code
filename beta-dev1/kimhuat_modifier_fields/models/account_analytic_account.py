from odoo import models, api, fields

class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    customer_id = fields.Char('Customer ID')
    customer_contact = fields.Char('Customer Contact')
    warranty_start = fields.Date('Warranty Start Date')
    warranty_end = fields.Date('Warranty End Date')
    product_line_ids = fields.One2many('account.analytic.account.product.line', 'account_id', 'Product Lines')
    is_installation = fields.Boolean('Installation')
    is_servicing = fields.Boolean('Servicing')
    contact_name = fields.Many2one('res.partner', 'Contact Name')
    mobile = fields.Char('Mobile')
    contract_amount = fields.Char('Contract Amount')
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    no_of_routines = fields.Selection(
    [('monthly', 'Monthly'),
     ('bi-monthly', 'Bi-Monthly'),
     ('quaterly', 'Quaterly')],
    string='No. of Routines',)

    @api.onchange('partner_id')
    def onchange_customer_contact_id(self):
        if self.partner_id:
            self.customer_id = self.partner_id.customer_id or ''
            self.customer_contact = self.partner_id.phone or ''
            self.mobile = self.partner_id.mobile or ''
            self.street = self.partner_id.street or ''
            self.street2 = self.partner_id.street2 or ''
            self.zip = self.partner_id.zip or ''
            self.city = self.partner_id.city or ''
            self.state_id = self.partner_id.state_id.id or ''
            self.country_id = self.partner_id.country_id.id or ''
            return {'domain': {
                'contact_name': [('id', 'in', self.partner_id.child_ids.ids)],
            }}

    @api.onchange('contact_name')
    def onchange_customer_phone(self):
        if self.contact_name:
            self.mobile = self.contact_name.mobile

class account_analytic_account_product_line(models.Model):
    _name = 'account.analytic.account.product.line'

    name = fields.Char('Name')
    product_id = fields.Many2one('product.product', string='Product')
    account_id = fields.Many2one('account.analytic.account', 'Account ID', required=True, ondelete='cascade')
    brand = fields.Many2one('product.brand', 'Brand')
    type = fields.Many2one('product.type', 'Type')
    description = fields.Text('Description')
    ordered_qty = fields.Float('Ordered Quantity')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.description

    @api.onchange('brand', 'type')
    def onchange_brand_type(self):
        domain  = []
        if self.brand:
            domain.append(('product_brand','=',self.brand.id))
        if self.type:
            domain.append(('product_type','=',self.type.id))
        return {
            'domain': {
                'product_id' : domain
            }
        }
