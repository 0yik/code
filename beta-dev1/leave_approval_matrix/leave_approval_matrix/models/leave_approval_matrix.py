from odoo import models, fields, api

class leave_approval_matrix_line(models.Model):
    _name = 'leave.approval.matrix.line'

    leave_approval_id       = fields.Many2one('leave.approval.matrix')
    employee_ids            = fields.Many2many('hr.employee',string='Employee')
    job_type_ids            = fields.Many2many('hr.job',string='Job Title')

class leave_approval_matrix(models.Model):
    _name = 'leave.approval.matrix'

    leave_type_ids          = fields.Many2many('hr.holidays.status',string="Leave Type")
    job_type_ids            = fields.Many2many('hr.job',string='Job Title')
    line_ids                = fields.One2many('leave.approval.matrix.line','leave_approval_id')

    def import_job_title(self):
        for record in self:
            if record.job_type_ids and record.job_type_ids.ids:
                self.line_ids = self.line_ids.browse([])
                for job_id in record.job_type_ids:
                    lines = self.line_ids.browse([])
                    line_ids = record.get_line_data(job_id.approving_manager_id,lines)
                    # total_line_ids = line_ids
                    if self.id and line_ids:
                        self.line_ids += line_ids
        return

    def get_line_data(self, job_id,lines):
        if not job_id.approving_manager_id.id:
            if job_id.department_id.manager_id.id:
                line_data = {
                    'leave_approval_id': self.id,
                    'employee_ids': [(6, 0, job_id.department_id.manager_id.ids)] or False,
                    'job_type_ids': [(6, 0, job_id.ids)],
                }
            else:
                line_data = {
                    'leave_approval_id': self.id,
                    'employee_ids': [(6, 0, self.env['hr.employee'].search([('job_id','=',job_id.id)]).ids)] or False,
                    'job_type_ids': [(6, 0, job_id.ids)],
                }
            lines += self.line_ids.new(line_data)
            # if self.id and lines:
            #     self.line_ids += lines
            return lines
        if job_id.id in self.job_type_ids.ids:
            return lines
        if job_id.department_id.manager_id.id:
            line_data = {
                'leave_approval_id': self.id,
                'employee_ids': [(6, 0, job_id.department_id.manager_id.ids)] or False,
                'job_type_ids': [(6, 0, job_id.ids)],
            }
        else:
            line_data = {
                'leave_approval_id': self.id,
                'employee_ids': [(6, 0, self.env['hr.employee'].search([('job_id', '=', job_id.id)]).ids)] or False,
                'job_type_ids': [(6, 0, job_id.ids)],
            }
        lines += self.line_ids.new(line_data)
        # if self.id and lines:
        #     self.line_ids += lines [(6, 0, job_id.department_id.manager_id.ids)] or False
        return self.get_line_data(job_id.approving_manager_id,lines)




