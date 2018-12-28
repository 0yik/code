from odoo import api, fields, models, _
import  re

class Partner(models.Model):
    _inherit = "res.partner"

    customer = fields.Boolean(string="Is a Customer", default=False)
    type = fields.Selection(selection_add=[('delivery', 'HR contact')])
    user_id = fields.Many2one('res.users', string='Salesperson',help='The internal user that is in charge of communicating with this contact if any.', default=lambda self: self.env.uid)
    industry_type = fields.Many2one('industry.type', 'Industry Type')
    # lead_sources_id = fields.Many2one('lead.source', string='Sources')
    source = fields.Many2one('lead.source', 'Source')

    @api.multi
    @api.onchange('email')
    def  ValidateEmail(self):
        if self.email:
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", self.email) == None:
                self.email = False
                warning = {'title': 'Warning!', 'message': 'Invalid Email ID!'}
                return {'warning': warning}

class LeadSource(models.Model):
    _name = "lead.source"
    _description = "Lead Source"

    name = fields.Char('Source', required=True)

class ResUsers(models.Model):
    _inherit = "res.users"

    services = fields.Many2one('product.template', string='Services', domain=[('type', '=', 'service')])

class PartnerTitle(models.Model):
    _inherit = 'res.partner.title'

    @api.multi
    def name_get(self):
        result = []
        for ticket in self.search([]):
            if ticket.shortcut:
                result.append((ticket.id , ticket.shortcut))
        return result