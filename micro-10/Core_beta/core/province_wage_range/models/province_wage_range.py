from odoo import api, models, fields, _

class ProvinceWageRange(models.Model):
    _name = 'province.wage.range'
    _rec_name = "country_id"
    
    state_id = fields.Many2one('res.country.state', string="State", required=True)
    country_id = fields.Many2one('res.country', string="Country", required=True)
    code = fields.Char('State Code')
    min_wage = fields.Float('Min Wage', required=True)
    max_wage = fields.Float('Max Wage')

    @api.onchange('state_id')
    def onchange_state(self):
        self.code = self.state_id.code