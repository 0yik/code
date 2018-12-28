from odoo import api, fields, models


class allocate_overtime_multiplier(models.TransientModel):

    _name = "allocate.overtime.multiplier"
    
    overtime_multiplier_id = fields.Many2one('overtime.multiplier', 'Code')
    name = fields.Char(related="overtime_multiplier_id.overtime_name")
    apply_to = fields.Selection([('normal_work_days', 'Normal Work Days'), ('off_days', 'Off Days'), ('public_holiday', 'Public Holiday')])
    employee_ids = fields.Many2many('hr.employee', string='Employee')

    @api.multi
    def apply(self):
        for rec in self:
            for employee in rec.employee_ids:
                overtime_multiplier_employee_id = self.env['overtime.multiplier.employee'].search([('employee_id', '=', employee.id)])
                vals = {}
                if rec.apply_to == 'normal_work_days':
                    vals.update({
                        'workdays_id': rec.overtime_multiplier_id.id
                    })
                elif rec.apply_to == 'off_days':
                    vals.update({
                        'offdays_id': rec.overtime_multiplier_id.id
                    })
                elif rec.apply_to == 'public_holiday':
                    vals.update({
                        'public_holidays_id': rec.overtime_multiplier_id.id
                    })
                
                if overtime_multiplier_employee_id:
                    overtime_multiplier_employee_id.write(vals)
                else:
                    vals.update({
                        'employee_id': employee.id
                    })
                    self.env['overtime.multiplier.employee'].create(vals)
        return True