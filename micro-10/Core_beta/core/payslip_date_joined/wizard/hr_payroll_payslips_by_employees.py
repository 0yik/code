# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    @api.multi
    def compute_sheet(self):
        res = super(HrPayslipEmployees, self).compute_sheet()
        if res.get('skip_other',False):
            return {'type': 'ir.actions.act_window_close'}
        active_id = self.env.context.get('active_id')
        self.env['hr.payslip.run'].browse(active_id).slip_ids.unlink()
        payslips = self.env['hr.payslip']
        [data] = self.read()
        active_id = self.env.context.get('active_id')
        if active_id:
            [run_data] = self.env['hr.payslip.run'].browse(active_id).read(['date_start', 'date_end', 'credit_note'])
        from_date = run_data.get('date_start')
        to_date = run_data.get('date_end')
        if not data['employee_ids']:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            if employee.join_date >= from_date and employee.join_date <= to_date:
                slip_data = self.env['hr.payslip'].with_context(date_from=employee.join_date, date_to=to_date, employee_id=employee.id, contract_id=False).onchange_employee()
                from_date = employee.join_date
            else:
                slip_data = self.env['hr.payslip'].with_context(date_from=from_date, date_to=to_date, employee_id=employee.id, contract_id=False).onchange_employee()
                from_date = run_data.get('date_start')
            res = {
                'employee_id': employee.id,
                'name': slip_data['value'].get('name'),
                'struct_id': slip_data['value'].get('struct_id'),
                'contract_id': slip_data['value'].get('contract_id'),
                'payslip_run_id': active_id,
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
                'date_from': from_date,
                'date_to': to_date,
                'credit_note': run_data.get('credit_note'),
            }
            payslips += self.env['hr.payslip'].create(res)
        payslips.compute_sheet()
        return {'type': 'ir.actions.act_window_close'}
