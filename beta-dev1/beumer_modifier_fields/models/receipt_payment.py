from odoo import api, fields, models

class account_payments(models.Model):
    _inherit = 'receipt.payment'

    cheque_number = fields.Char(string='Cheque Number')

class account_model_line_inherit(models.Model):
    _inherit = 'account.model.line'

    cost_element_id1 = fields.Many2one('project.cost_element', domain=[('level', '=', '1')], string='Cost Element 1')
    cost_element_id2 = fields.Many2one('project.cost_element', domain=[('level', '=', '2')], string='Cost Element 2')
    cost_element_id3 = fields.Many2one('project.cost_element', domain=[('level', '=', '3')], string='Cost Element 3')