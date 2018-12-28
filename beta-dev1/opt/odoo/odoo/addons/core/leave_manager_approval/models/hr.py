from odoo import api, fields, models, _

class Hr_Employee(models.Model):
    _inherit = 'hr.employee'

    no_of_approval = fields.Selection([(1,'1'),(2,'2'),(3,'3'),(4,'4'),(5,'5')],string='Number Of Approvals Needed')

Hr_Employee()