# -*- encoding: utf-8 -*-
from odoo import fields, models


class hr_employee_configuration_inherit(models.TransientModel):
    _inherit = 'hr.employee.config.settings'

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    ot1_monday = fields.Boolean(related='company_id.ot1_monday', string="Monday")
    ot1_tuesday = fields.Boolean(related='company_id.ot1_tuesday', string="Tuesday")
    ot1_wednesday = fields.Boolean(related='company_id.ot1_wednesday', string="Wednesday")
    ot1_thursday = fields.Boolean(related='company_id.ot1_thursday', string="Thursday")
    ot1_friday = fields.Boolean(related='company_id.ot1_friday', string="Friday")
    ot1_saturday = fields.Boolean(related='company_id.ot1_saturday', string="Saturday")
    ot1_sunday = fields.Boolean(related='company_id.ot1_sunday', string="Sunday")

    ot1_5_monday = fields.Boolean(related='company_id.ot1_5_monday', string="Monday")
    ot1_5_tuesday = fields.Boolean(related='company_id.ot1_5_tuesday', string="Tuesday")
    ot1_5_wednesday = fields.Boolean(related='company_id.ot1_5_wednesday', string="Wednesday")
    ot1_5_thursday = fields.Boolean(related='company_id.ot1_5_thursday', string="Thursday")
    ot1_5_friday = fields.Boolean(related='company_id.ot1_5_friday', string="Friday")
    ot1_5_saturday = fields.Boolean(related='company_id.ot1_5_saturday', string="Saturday")
    ot1_5_sunday = fields.Boolean(related='company_id.ot1_5_sunday', string="Sunday")

    ot2_saturday = fields.Boolean(related='company_id.ot2_saturday', string="Saturday")
    ot2_sunday = fields.Boolean(related='company_id.ot2_sunday', string="Sunday")


