# -*- coding: utf-8 -*-


from openerp import api, exceptions, fields, models, _
from datetime import datetime, timedelta


class change_notice_period(models.TransientModel):
    _name = 'change.notice.period.res'
    _description = 'Change Notice Period'

    @api.model
    def _get_current_notice_id(self):
        """docstring for fname"""
        return self._context.get('default_current_period_id')


    current_notice_id = fields.Many2one(
        comodel_name='employee.notice.period', string='Current Notice', help='',
         )
    new_notice_id = fields.Many2one(
        comodel_name='employee.notice.period', string='New Notice Period', help='')

    @api.multi
    def action_change_period(self):
        """docstring for action_change_period"""
        resignation_ids = self._context.get('active_ids')
        resignation_objs = False
        if resignation_ids:
            resignation_objs = self.env['resignation.request'].browse(resignation_ids)
        if not resignation_objs:
            return {'type': 'ir.actions.act_window_close'}
        for self_obj in self:
            resignation_objs.write({'notice_period_id': self_obj.new_notice_id.id })
            resignation_objs.onchange_get_cessation_date()
            for resignation_obj in resignation_objs:
                resignation_obj.employee_id.write(
                    {'notice_period_id': self_obj.new_notice_id.id,
                     'cessation_date':fields.Date.from_string(
                         resignation_obj.resignation_date) + timedelta(days=self_obj.new_notice_id.duration)
                     })
        return {'type': 'ir.actions.act_window_close'}



change_notice_period()
