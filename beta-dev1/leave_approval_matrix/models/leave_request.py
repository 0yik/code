from odoo import models, fields, api

class hr_holidays_multiple(models.Model):
    _inherit = 'hr.holidays.multiple'

    leave_matrix_line       = fields.Many2many('leave.approval.matrix.line')
    check_access_request    = fields.Boolean(compute='_check_access_leave_request',default=True)


    # def _check_leave_matrix_line(self):
    #     if self.state == 'confirm' or not self.leave_matrix_line:
    #         leave_obj = self.env['leave.approval.matrix'].search([])
    #         for leave_id in self.env['leave.approval.matrix'].browse(leave_obj.ids):
    #             if (self.holiday_status_id.id in leave_id.leave_type_ids.ids) and (self.department_id.id in leave_id.job_type_ids.mapped('department_id').ids):
    #                 self.leave_matrix_line += leave_id.line_ids

    def _check_access_leave_request(self):
        if self.leave_matrix_line:
            if self._uid in self.leave_matrix_line.mapped('employee_ids.user_id').ids:
                self.check_access_request = False
            else:
                self.check_access_request = True
        else:
            self.check_access_request = True

    @api.multi
    def action_approve(self):
        if self.leave_matrix_line:
            leave_line_ids = self.leave_matrix_line
            first_leave_matrix = self.env['leave.approval.matrix.line'].search([('id','in',leave_line_ids.ids)],limit=1,order='id asc')
            if self._uid in first_leave_matrix.mapped('employee_ids.user_id').ids:
                self.leave_matrix_line = [(3,first_leave_matrix.id)]
                if not self.leave_matrix_line:
                    return super(hr_holidays_multiple, self).action_approve()
                else:
                    user_ids = self.env['leave.approval.matrix.line'].search([('id', 'in', self.leave_matrix_line.ids)], limit=1,order='id asc').mapped('employee_ids.user_id')
                    if user_ids.ids and user_ids:
                        for user_id in user_ids:
                            self.leave_request_send_mail(user_id)

    @api.model
    def create(self,vals):
        res = super(hr_holidays_multiple, self).create(vals)
        leave_obj = self.env['leave.approval.matrix'].search([])
        for leave_id in self.env['leave.approval.matrix'].browse(leave_obj.ids):
            if (res.holiday_status_id.id in leave_id.leave_type_ids.ids) and (res.department_id.id in leave_id.job_type_ids.mapped('department_id').ids):
                res.leave_matrix_line = leave_id.line_ids
                user_ids = self.env['leave.approval.matrix.line'].search([('id','in',res.leave_matrix_line.ids)],limit=1,order='id asc').mapped('employee_ids.user_id')
                if user_ids.ids and user_ids:
                    for user_id in user_ids:
                        res.leave_request_send_mail(user_id)
        return res

    def write(self,vals):
        res = super(hr_holidays_multiple, self).write(vals)
        if vals.get('department_id',False):
            leave_obj = self.env['leave.approval.matrix'].search([])
            for leave_id in self.env['leave.approval.matrix'].browse(leave_obj.ids):
                if (res.holiday_status_id.id in leave_id.leave_type_ids.ids) and (
                    res.department_id.id in leave_id.job_type_ids.mapped('department_id').ids):
                    res.leave_matrix_line = leave_id.line_ids
                    user_ids = self.env['leave.approval.matrix.line'].search([('id', 'in', res.leave_matrix_line.ids)],
                                                                            limit=1, order='id asc').mapped('employee_ids.user_id')
                    if user_ids.ids and user_ids:
                        for user_id in user_ids:
                            res.leave_request_send_mail(user_id)
        return res

    def leave_request_send_mail(self, user_id):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = base_url + '/web#id=%s&view_type=form&model=hr.holidays.multiple' % (self.id)
        email_from = user_id.company_id.email or 'Administrator <admin@example.com>'
        email_to = user_id.email
        subject = 'You have a Leave Request need approval'
        message = """
                <html>
                    <head>
                        Dear %s,
                    </head>
                    <body>
                        You have a Leave Request *Leave Name %s (<a href="%s" target="_blank">Clickable link</a>)waiting for your approval.<br/><br/>

                        <strong>Thank you</strong>
                    </body>
                <html>""" % (user_id.name, self.display_name, url)

        vals = {
            'state': 'outgoing',
            'subject': subject,
            'body_html': '<pre>%s</pre>' % message,
            'email_to': email_to,
            'email_from': email_from,
        }
        if vals:
            email_id = self.env['mail.mail'].create(vals)
            if email_id:
                email_id.send()