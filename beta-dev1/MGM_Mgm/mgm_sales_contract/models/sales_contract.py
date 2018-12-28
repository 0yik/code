from odoo import models, fields, api, _
from odoo.exceptions import UserError

class res_partner(models.Model):
    _inherit = 'res.partner'

    company_type = fields.Selection(selection_add=[('subcon', 'Sub Contractor')])

class business_unit(models.Model):
    _name = 'business.unit'

    name = fields.Char('Business Name')
    unit = fields.Selection([('ferry','Ferry'), ('tug_barge','Tug & Barge'), ('stevedoring','Stevedoring'), ('fls','FLF'), ('others','Others')], string="Units")

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.name or ''))
        return result


class sale_contract(models.Model):
    _inherit = 'sale.requisition'

    business_unit_text = fields.Char('Business Unit')
    business_unit = fields.Many2one('business.unit','Business Unit')

    state = fields.Selection([('draft1', 'Draft'), ('inprogress', 'Confirmed'), ('dailynote', 'Done'), ('drafts', 'Quotation'),  ('in_progress', 'Quotation Sent'),
                              ('done', 'Fixture Note'), ('cancel', 'Cancelled')],
                              'Status', track_visibility='onchange', required=False, copy=True)
    laycan_ids = fields.One2many('sale.laycan.lines', 'requisition_id', string="Laycan")
    dock_id = fields.Many2one('ferry.dock', string="Dock")
    port_id = fields.Many2one('ferry.port', string="Port")
    rit_type_id = fields.Many2one('ferry.rit.type', string="Rit Type")
    asset_id = fields.Many2one('account.asset.asset', string="Asset")
    mother_vessel = fields.Char(string='Mother Vessel')
    vessel_type_id = fields.Many2one('mother.vessel.type', string="Vessel Type")
    unit = fields.Selection(related="business_unit.unit", string="Unit")

    ordering_date = fields.Date(string="Ordering Date", default=fields.Datetime.now, store=True)

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')

    currency_id = fields.Many2one("res.currency", related='pricelist_id.currency_id', string="Currency", readonly=True,
                                  required=True)

    @api.model
    def create(self, vals):
        # Makes sure 'pricelist_id' are defined
        if any(f not in vals for f in ['pricelist_id']):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            vals['pricelist_id'] = vals.setdefault('pricelist_id',
                                                   partner.property_product_pricelist and partner.property_product_pricelist.id)
        result = super(sale_contract, self).create(vals)
        return result


    @api.onchange('partner_id')
    def onchange_partner(self):
        values = {
            'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
        }
        self.update(values)


    @api.onchange('business_unit_text')
    def onchange_business_unit_tex(self):
        if self.business_unit_text:
            business_unit = self.env['business.unit'].search([('unit', '=', self.business_unit_text)], limit=1)
            self.business_unit = business_unit.id

    @api.multi
    def analytic_account(self):
        ir_model_data = self.env['ir.model.data']
        try:
            compose_form_id = ir_model_data.get_object_reference('mgm_multi_assign_analytics', 'mgm_multi_assign_analytics_form')[1]
        except ValueError:
            compose_form_id = False
        res = {
            'type': 'ir.actions.act_window',
            'name': 'Analytics Accounting',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mgm.multi.assign.analytics',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': {'default_name': self.id}
        }
        return res

    @api.one
    def action_cancel(self):
        self.write({'state':'cancel'})

    @api.one
    def action_draft1(self):
        self.write({'state':'draft1'})

    @api.one
    def action_drafts(self):
        self.write({'state':'drafts'})

    @api.multi
    def action_in_progress1(self):
        if not all(obj.line_ids for obj in self):
            raise UserError(_('You cannot confirm call because there is no product line.'))
        self.write({'state': 'inprogress'})

    @api.multi
    def action_done_dailynote(self):
        self.write({'state': 'dailynote'})

    @api.multi
    def action_in_progress(self):
        if not all(obj.line_ids for obj in self):
            raise UserError(_('You cannot confirm call because there is no product line.'))
        self.write({'state': 'done'})

    @api.multi
    def action_quotation_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('mgm_sales_contract', 'email_template_edi_requisition')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'sale.requisition',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_fixture_as_sent': True,
            
#             'custom_layout': "sale.mail_template_data_notification_email_sale_order"
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

class sale_contract_line(models.Model):
    _inherit = 'sale.requisition.line'

    product_code = fields.Char('Product Code')
    description = fields.Char('Description')
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(sale_contract_line, self)._onchange_product_id()
        self.product_code = self.product_id.default_code
        self.description = self.product_id.name

        if not self.product_id:
            return {'domain': {'product_uom_id': []}}

        vals = {}
        product = self.product_id.with_context(
            lang=self.requisition_id.partner_id.lang,
            partner=self.requisition_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.requisition_id.ordering_date,
            pricelist=self.requisition_id.pricelist_id.id,
            uom=self.product_uom_id.id
        )

        if self.requisition_id.pricelist_id and self.requisition_id.partner_id:
            # vals['price_unit'] = self.env['account.tax']._fix_tax_included_price(self._get_display_price(product),
            #                                                                      product.taxes_id,False)
            vals['price_unit'] = self._get_display_price(product)
        self.update(vals)
        return res

    @api.onchange('product_uom_id', 'product_uom_qty')
    def product_uom_change(self):

        if not self.product_uom_id or not self.product_id:
            self.price_unit = 0.0
            return

        if self.requisition_id.pricelist_id and self.requisition_id.partner_id:
            product = self.product_id.with_context(
                lang=self.requisition_id.partner_id.lang,
                partner=self.requisition_id.partner_id.id,
                quantity=self.product_uom_qty,
                date=self.requisition_id.ordering_date,
                pricelist=self.requisition_id.pricelist_id.id,
                uom=self.product_uom_id.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            # self.price_unit = self.env['account.tax']._fix_tax_included_price(self._get_display_price(product),
            #                                                                   product.taxes_id, False)
            self.price_unit = self._get_display_price(product)

    @api.multi
    def _get_display_price(self, product):
        if self.requisition_id.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=self.requisition_id.pricelist_id.id).price
        price, rule_id = self.requisition_id.pricelist_id.get_product_price_rule(self.product_id, self.product_uom_qty or 1.0,
                                                                           self.requisition_id.partner_id)
        pricelist_item = self.env['product.pricelist.item'].browse(rule_id)
        if (pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id.discount_policy == 'with_discount'):
            price, rule_id = pricelist_item.base_pricelist_id.get_product_price_rule(
                self.product_id,self.product_uom_qty or 1.0,self.requisition_id.partner_id)
            return price
        else:
            from_currency = self.requisition_id.company_id.currency_id
            return from_currency.compute(product.lst_price, self.requisition_id.pricelist_id.currency_id)


class LaycanLines(models.Model):
    _name = 'sale.laycan.lines'

    laycan_in = fields.Date('Laycan in')
    laycan_out = fields.Date('Laycan out')
    subcon = fields.Many2one('res.partner', string='Subcon')
    late_fee = fields.Float('Late Fee')
    requisition_id = fields.Many2one('sale.requisition', string="Requisition")
    commence_date = fields.Datetime('Commence Date')
    complete_date = fields.Datetime('Complete Date')

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    sale_contract_id = fields.Many2one('sale.requisition', string='Sales Requisition', copy=False)

    @api.model
    def create(self,vals):
        res = super(account_invoice, self).create(vals)
        if self.env.context.get('active_model',False) == 'sale.requisition' and self.env.context.get('active_id',False):
            self.env['sale.requisition'].browse(self.env.context.get('active_id',False)).write({'invoice_ids':[(4,res.id)]})
        return res

class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def create(self, vals):
        res = super(account_analytic_account, self).create(vals)
        if self.env.context.get('active_model', False) == 'sale.requisition' and self.env.context.get('active_id', False):
            self.env['sale.requisition'].browse(self.env.context.get('active_id', False)).write({'analytic_account_id': res.id})
        return res

class account_analytic_line(models.Model):
    _inherit = 'account.analytic.line'

    @api.model
    def create(self, vals):
        if self._context.has_key('is_created') and self._context.get('is_created') != True:
            if self.env.context.get('active_model', False) == 'sale.requisition' and self.env.context.get('active_id', False):
                vals.update({'account_id': self.env['sale.requisition'].browse(self.env.context.get('active_id', False)).analytic_account_id.id})
            res = super(account_analytic_line, self).create(vals)
            return res
        else:
            res = super(account_analytic_line, self).create(vals)
            return res

class FerryDock(models.Model):
    _name = 'ferry.dock'

    name = fields.Char('Dock Name')

class FerryPort(models.Model):
    _name = 'ferry.port'

    name = fields.Char('Port Name')

class FerryRitType(models.Model):
    _name = 'ferry.rit.type'

    name = fields.Char('Rit Name')

# class MotherVessel(models.Model):
#     _name = 'mother.vessel'
#
#     name = fields.Char('Mother Vessel Name')

class MotherVesselType(models.Model):
    _name = 'mother.vessel.type'

    name = fields.Char('Vessel Type')
