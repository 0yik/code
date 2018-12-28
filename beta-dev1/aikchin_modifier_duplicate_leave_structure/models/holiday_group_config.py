# -*- coding: utf-8 -*-

from odoo import models, fields, api

class holiday_group_config(models.Model):
    _inherit = 'holiday.group.config'

    @api.multi
    def copy(self, default={}):
        res = super(holiday_group_config, self).copy(default)

        if self.holiday_group_config_line_ids:
            holiday_group_config_line_ids = []
            for holiday_group_config_line_id in self.holiday_group_config_line_ids :
                vals = {
                    'leave_type_id' : holiday_group_config_line_id.leave_type_id.id,
                    'default_leave_allocation' :holiday_group_config_line_id.default_leave_allocation,
                    'incr_leave_per_year':holiday_group_config_line_id.incr_leave_per_year,
                    'max_leave_kept':holiday_group_config_line_id.max_leave_kept,
                    'carryover' :holiday_group_config_line_id.carryover,
                    'carry_no_of_days':holiday_group_config_line_id.carry_no_of_days
                }
                temp = self.env['holiday.group.config.line'].create(vals)
                holiday_group_config_line_ids += [temp.id]
            res.write({'holiday_group_config_line_ids': [(6, 0, holiday_group_config_line_ids)]})
        return res

class holiday_group_config_line(models.Model):
    _inherit = 'holiday.group.config.line'

    @api.constrains('leave_type_id')
    def _check_multiple_leaves_configured(self):
        return True
        # for holiday in self:
        #     domain = [
        #         ('leave_type_id', '=',holiday.leave_type_id.id),
        #         ('holiday_group_config_id', '=', holiday.holiday_group_config_id.id),
        #         ('id', '!=', holiday.id),
        #         ]
        #     nholidays = self.search_count(domain)
        #     if nholidays:
        #         raise ValidationError('You can not add multiple configurations for leave type "%s".'%(holiday.leave_type_id.name2))