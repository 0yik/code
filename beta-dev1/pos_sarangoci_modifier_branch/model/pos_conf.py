from odoo import api, fields, models

class pos_conf(models.Model):
    _inherit='pos.config'

    branch_status = fields.Boolean(default=True)

    @api.multi
    def toggle_branch_status(self):
        if self.branch_status:
            self.branch_status = False
            self.active = False
        else:
            self.branch_status = True
            self.active = True