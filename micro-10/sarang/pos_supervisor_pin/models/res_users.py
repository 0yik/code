from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def compare_pin_number(self, pin_number):
        supervisor = self.env.ref('pos_supervisor_pin.group_hr_supervisor')
        all_pins = [user.pin_number for user in supervisor.users if user.branch_id.id==self.env.user.branch_id.id]
        if int(pin_number) in all_pins:
            return True
        elif not all_pins and self.env.user.pin_number == int(pin_number):
            return True
        return False
