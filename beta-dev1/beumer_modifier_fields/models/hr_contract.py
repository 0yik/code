from odoo import api,models,fields

class hr_contract(models.Model):
    _inherit = 'hr.contract'

    other_input_ids = fields.One2many('other.input','contract_id')

    @api.model
    def default_get(self, fields):
        res = super(hr_contract, self).default_get(fields)
        if self._context.get('active_id'):
            employee_id = self.env['hr.employee'].browse(self._context.get('active_id'))
            res.update({
                'date_start' : employee_id.join_date,
            })
        return res