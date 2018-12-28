from odoo import models, api, fields

class res_partner(models.Model):
    _inherit = 'res.partner'

    supplier_id = fields.Char(string="Supplier ID")
    contractor_check = fields.Boolean(default=False, string="")
    contractor = fields.Many2one('res.partner')

    @api.model
    def default_get(self, fields):
        res = super(res_partner, self).default_get(fields)
        country_id = self.env['res.country'].search([('code','=','SG')],limit=1)
        if country_id:
            res['country_id'] = country_id.id
        return res

    @api.multi
    def name_get(self):
        res = super(res_partner, self).name_get()
        if self._context.get('contact_name'):
            val = []
            for partner in self:
                name = partner.name or ''
                if not partner.is_company:
                    name = "%s" % (name)
                    val.append((partner.id, name))
            return val
        return res
