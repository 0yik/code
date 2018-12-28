from odoo import models, fields, api,_
from datetime import datetime, timedelta
from odoo import tools
from odoo.exceptions import Warning, ValidationError
from odoo import SUPERUSER_ID


HOURS_PER_DAY = 8

class hr_holidays_multiple(models.Model):
    _inherit = 'hr.holidays.multiple'

    check_access_group_manager = fields.Boolean('Check rule',
                                                default=False)

    @api.model
    def default_get(self, fields):
        res = super(hr_holidays_multiple, self).default_get(fields)
        res.update({
            'state' : 'draft'
        })
        user_obj = self.env['res.groups'].search([('name', '=', 'HR Manager')]).users.ids
        if self._uid in user_obj:
            res.update({
                'check_access_group_manager': True
            })
        return res

    @api.model
    def create(self, vals):
        res = super(hr_holidays, self).create(vals)
        return res


class hr_holidays(models.Model):
    _inherit = 'hr.holidays'

    state       = fields.Selection([
                                    ('draft', 'To Submit'),
                                    ('cancel', 'Cancelled'),
                                    ('confirm', 'To Approve'),
                                    ('refuse', 'Rejected'),
                                    ('validate1', 'Second Approval'),
                                    ('validate', 'Approved')],default='draft')

    @api.model
    def default_get(self,fields):
        res = super(hr_holidays, self).default_get(fields)
        res.update({
            'state': 'draft'
        })
        return res

    @api.model
    def create(self,vals):
        res = super(hr_holidays, self).create(vals)
        res.state = 'draft'
        return res

    @api.onchange('date_from')
    def _onchange_date_from(self):
        """ If there are no date set for date_to, automatically set one 8 hours later than
            the date_from. Also update the number_of_days.
        """
        date_from = self.date_from
        date_to = self.date_to

        # No date_to set so far: automatically compute one 8 hours later
        if date_from:
            if not date_to or date_to and date_from > date_to:
                date_to_with_delta = fields.Datetime.from_string(date_from) + timedelta(hours=HOURS_PER_DAY)
                self.date_to = str(date_to_with_delta)
                date_to = self.date_to

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            self.number_of_days_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
        else:
            self.number_of_days_temp = 0

    def _check_user_is_hr_manager(self):
        user_ids = []
        user_ids.append(SUPERUSER_ID)
        group_ids = self.env['res.groups'].search([('name','in',('CFO','HR Manager','HR Executive'))])
        for group_id in group_ids:
            if group_id.users:
                for user in group_id.users:
                    user_ids.append(user.id)
        if self._uid in user_ids:
            return False
        else:
            return True

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(hr_holidays, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=False)
        action_id = self.env.ref('hr_holidays.open_company_allocation').id
        if self._context.get('params') and self._context.get('params').get('action') and action_id == self._context.get('params').get('action'):
            if view_type != 'form':
                if view_type == 'tree':
                    check_user = self._check_user_is_hr_manager()
                    if check_user == True:
                        if 'arch' in res:
                            data = res.get('arch').split('\n')
                            modify_edit_str = 'create="0" delete="0"'

                            arch_data = '<tree decoration-danger="state == \'refuse\'" decoration-info="state == \'draft\'" string="Leaves Summary" %s>' % (
                            modify_edit_str)
                            for n in range(1, len(data)):
                                arch_data += '\n%s' % (data[n])
                            res['arch'] = arch_data
                    return res
                else:
                    return res
            if view_type == 'form':
                check_user = self._check_user_is_hr_manager()
                if check_user == True:
                    if 'arch' in res:
                        data = res.get('arch').split('\n')
                        modify_edit_str = 'edit="0" create="0" copy="0" delete="0"'

                        arch_data = '<form string="Leave Request" %s>' % (modify_edit_str)
                        for n in range(1, len(data)):
                            arch_data += '\n%s' % (data[n])
                        res['arch'] = arch_data
                return res
        else:
            return res

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        action_id = self.env.ref('hr_holidays.open_company_allocation').id
        if self._context.get('params') and self._context.get('params').get('action') and action_id == self._context.get(
                'params').get('action'):
            cfo_group_id = self.env.ref('beumer_modifier_access_right.cfo_group')
            hr_manager_group_id = self.env.ref('beumer_modifier_access_right.hr_manager_group')
            hr_executive_group_id = self.env.ref('beumer_modifier_access_right.hr_executive_group')
            if self._uid not in cfo_group_id.users.ids and self._uid not in hr_manager_group_id.users.ids and self._uid not in hr_executive_group_id.users.ids:
                if domain:
                    domain.append(('user_id', '=', self._uid))
                else:
                    domain = [('user_id', '=', self._uid)]
        res = super(hr_holidays, self).read_group(domain, fields, groupby, offset=offset, limit=limit,
                                                     orderby=orderby, lazy=lazy)
        return res

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        action_id = self.env.ref('hr_holidays.open_company_allocation').id
        if self._context.get('params') and self._context.get('params').get('action') and action_id == self._context.get('params').get('action'):
            cfo_group_id = self.env.ref('beumer_modifier_access_right.cfo_group')
            hr_manager_group_id = self.env.ref('beumer_modifier_access_right.hr_manager_group')
            hr_executive_group_id = self.env.ref('beumer_modifier_access_right.hr_executive_group')
            if self._uid not in cfo_group_id.users.ids and self._uid not in hr_manager_group_id.users.ids and self._uid not in hr_executive_group_id.users.ids:
                if domain:
                    domain.append(('user_id', '=', self._uid))
                else:
                    domain = [('user_id', '=', self._uid)]
        res = super(hr_holidays, self).search_read(domain=domain, fields=fields, offset=offset,
                                                            limit=limit, order=order)
        return res


class hr_public_holiday(models.Model):
    _inherit = 'hr.holiday.public'

    # fields_view = fields.Boolean(compute='_load_view')
    #
    # def _load_view(self):
    #     self._context['params'].update({
    #         'view_type' : 'form',
    #         '_push_me' : False ,
    #         'model'  : 'hr.holiday.public',
    #         'id'     : self.id
    #     })
    #     self.fields_view_get(view_id=None,view_type='form', toolbar=True, submenu=False)
    #     self.open_new_view()
    #     return True
    #
    # def open_new_view(self):
    #     return {
    #         'name': ('Load Form Again'),
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'hr.holiday.public',
    #         'type': 'ir.actions.act_window',
    #         'res_id' : self.id ,
    #         'view_id': self.env.ref('sg_hr_holiday.hr_holiday_public_form').id,
    #     }
    #
    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(hr_public_holiday, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=False)
    #     if view_type == 'form':
    #         if 'params' in self._context and 'id' in self._context.get('params') or self.id:
    #             holiday_public_id = self._context.get('params').get('id')
    #             holiday_public_id = self.browse(holiday_public_id) or self
    #             if holiday_public_id.state == 'confirmed':
    #                 if 'arch' in res:
    #                     data = res.get('arch').split('\n')
    #                     modify_edit_str = 'edit="0" delete="0"'
    #
    #                     arch_data = '<form string="Public Holiday detail" %s>' % (modify_edit_str)
    #                     for n in range(1, len(data)):
    #                         arch_data += '\n%s' % (data[n])
    #                     res['arch'] = arch_data
    #     return res

    @api.multi
    def setstate_validate(self):
        '''
            Sets state to validated
        '''
        file_name = 'HolidayList'  # Name of report file
        attachments = []
        email_body = ''  # To store email body text specified for each employee
        mail_obj = self.env["ir.mail_server"]
        data_obj = self.env['ir.model.data']
        for self_rec in self:
            mail_server_ids = self.env['ir.mail_server'].search([])
            if mail_server_ids and mail_server_ids.ids:
                mail_server_id = mail_server_ids[0]
                if not self_rec.email_body:
                    raise ValidationError(_('Please specify email body!'))
                result_data = data_obj._get_id('hr', 'group_hr_manager')
                model_data = data_obj.browse(result_data)
                group_data = self.env['res.groups'].browse(model_data.res_id)
                work_email = []
                user_ids = [user.id for user in group_data.users]
                if 1 in user_ids:
                    user_ids.remove(1)
                emp_ids = self.env['hr.employee'
                ].search([('user_id', 'in', user_ids)])
                for emp in emp_ids:
                    if not emp.work_email:
                        if emp.user_id.email and \
                                        emp.user_id.email not in work_email:
                            work_email.append(str(user.email))
                        else:
                            raise ValidationError(_('Email must be configured \
                                        in %s HR manager !') % (emp.name))
                    elif emp.work_email not in work_email:
                        work_email.append(str(emp.work_email))
                if not work_email:
                    raise ValidationError(_('No Hr Manager found!'))
                # Create report. Returns tuple (True,filename) if successfuly
                # executed otherwise (False,exception)
                report_name = 'sg_hr_holiday.employee_public_holiday_report'
                report = self.create_report(report_name, file_name)
                if report[0]:
                    # Inserting file_data into dictionary with file_name as a key
                    attachments.append((file_name, report[1]))
                    email_body = self_rec.email_body
                    specific_email_body = email_body
                    message_app = mail_obj.build_email(
                        email_from=mail_server_id.smtp_user,
                        email_to=work_email,
                        subject='Holiday list',
                        body=specific_email_body or '',
                        body_alternative=specific_email_body or '',
                        email_cc=None,
                        email_bcc=None,
                        reply_to=None,
                        attachments=attachments,
                        references=None,
                        object_id=None,
                        subtype='html',
                        subtype_alternative=None,
                        headers=None)
                    mail_obj.send_email(message=message_app,
                                        mail_server_id=mail_server_id.id)
            self_rec.write({'state': 'validated'})
        return True


