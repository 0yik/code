from odoo import api, fields, models

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    def _bank_type_get(self):
        bank_type_obj = self.env['res.partner.bank.type']
        result = []
        for bank_type in bank_type_obj.search([]):
            result.append((bank_type.code, bank_type.name))
        return result
        
    name = fields.Char()
    street = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one('res.country.state', 'Fed. State', domain="[('country_id', '=', country)]")
    country = fields.Many2one('res.country')
    bank_name = fields.Char(string="Bank Name")
    bank_bic = fields.Char(string='Bank Identifier Code', size=16)
    branch_code = fields.Char(string='Branch Code')
    branch_id = fields.Char(string='Branch ID')
    state = fields.Selection(_bank_type_get, string='Bank Account Type', required=True,
            change_default=True)
    journal_id = fields.Many2one('account.journal',string='Account Journal')
            
    @api.multi
    @api.onchange('partner_id')
    def onchange_partner(self):
        print "self",self.partner_id.id
        if not self.partner_id:
            return {}
        self.name = self.partner_id.name
        self.street = self.partner_id.street
        self.zip = self.partner_id.zip
        self.city = self.partner_id.city
        self.state = self.partner_id.state_id and self.partner_id.state_id.id or False
        self.country = self.partner_id.country_id and self.partner_id.country_id.id or False
    
class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    bank_account_ids = fields.One2many('res.partner.bank','partner_id',string="Bank Account Details")
    
class ResPartnerBankType(models.Model):
    _name = 'res.partner.bank.type'
    
    name = fields.Char(string='Name', required=True, translate=True)
    code = fields.Char(string='Code', size=64, required=True)
    field_ids = fields.One2many('res.partner.bank.type.field', 'bank_type_id', string='Type Fields')
    format_layout = fields.Text(string='Format Layout', translate=True)
    

class ResPartnerBankTypeField(models.Model):
    _name = 'res.partner.bank.type.field'

    name = fields.Char(string='Field Name', required=True, translate=True)
    bank_type_id = fields.Many2one('res.partner.bank.type', string='Bank Type', required=True, ondelete='cascade')
    required = fields.Boolean(string='Required')
    readonly = fields.Boolean(string='Readonly')
    size = fields.Integer(string='Max. Size')
