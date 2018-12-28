# -*- coding: utf-8 -*-


from openerp import api, exceptions, fields, models, _


class change_notice_period(models.TransientModel):
    _name = 'change.notice.period'
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
        employee_ids = self._context.get('active_ids')
        employee_objs = False
        if employee_ids:
            employee_objs = self.env['hr.employee'].browse(employee_ids)
        if not employee_objs:
            return {'type': 'ir.actions.act_window_close'}
        for self_obj in self:
            employee_objs.write({'notice_period_id': self_obj.new_notice_id.id })
        return {'type': 'ir.actions.act_window_close'}



change_notice_period()
