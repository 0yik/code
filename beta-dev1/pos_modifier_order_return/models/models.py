# -*- coding: utf-8 -*-
from odoo import models, fields, api

class res_users(models.Model):
    _inherit = 'res.users'

    pin_number = fields.Integer(string="PIN Number")

    _sql_constraints = [
        ('unique_pin', 'unique (pin_number)', 'The PIN NUmber must be unique!')
    ]

    @api.model
    def check_pos_security_pin_number(self,pin):
        group_supervisor = self.env.ref('point_of_sale.group_pos_manager')
        supervisors = self.search([('groups_id', 'in', group_supervisor.id)])
        for user in supervisors:
            if str(user.pin_number) == pin:
                return True
        return False