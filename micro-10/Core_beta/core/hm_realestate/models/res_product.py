# coding: utf-8

from odoo import api, fields, models
from odoo import api, fields, models, tools, _

class product_template(models.Model):
    _inherit = 'product.template'

    property_ok = fields.Boolean('Is a Property')
    floor_num = fields.Char('Floor No.')
    unit_num = fields.Char('Unit No.')
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    type = fields.Selection([
        ('consu', _('Consumable')),
        ('service', _('Service')),
        ('product',_('Stockable Product'))], string='Product Type', default='service', required=True)


class account_analytic_acc_line(models.Model):
    _name = 'account.analytic.acc.line'

    analy_id = fields.Many2one('account.analytic.account')
    product_id = fields.Many2one('product.product','Unit Number' ,domain="[('property_ok','=', True)]")
    categ_id = fields.Many2one('product.category', 'Property', change_default=True, domain="[('type','=','normal')]",required=True)
    description_prod = fields.Text('Description')
    remarks_prod = fields.Text('Remarks')

    @api.onchange('categ_id')
    def onchange_categ(self):
        res = {}
        if self.categ_id:
            prod = self.env['product.product'].search([('categ_id','=',self.categ_id.id),('property_ok','=', True)])
            if prod:
                res['domain'] = {'product_id': [('id','in',prod.ids)]}
            else:
                res['domain'] = {'product_id': [('id','in',[])]}
        return res

    @api.multi
    @api.onchange('product_id')
    def on_changeunit_product_id(self):
        for ob in self.product_id:
            self.description_prod = ob.description_sale

class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    date_end = fields.Date('Expiration Date')
    line_analytic = fields.One2many('account.analytic.acc.line','analy_id',string="Property Line")
    product_id = fields.Many2one('product.product','Product' ,domain="[('property_ok','=', False)]")
    inv_contra = fields.Integer("Invoice", compute='_compute_inv_contra_count')

    @api.multi
    def _compute_inv_contra_count(self):
        for partner in self:
            partner.inv_contra = self.env['account.invoice'].search_count([('origin', '=',partner.code )])

    @api.multi    
    def action_invoice_tree1_call(self):        
        invoice_ids = self.env['account.invoice'].search([('origin','=',self.code)])                     
        view_id = self.env.ref('account.invoice_tree').id        
        form_view_id = self.env.ref('account.invoice_form').id        
        context = self._context.copy()        
        return {            
            'name':'form_name',            
            'view_type':'form',            
            'view_mode':'tree',            
            'res_model':'account.invoice',            
            'view_id':view_id,            
            'views':[(view_id,'tree'),(form_view_id,'form')],            
            'type':'ir.actions.act_window',            
            'domain':[('id','in',invoice_ids.ids)],            
            'target':'current',            
            'context':context,        
            }