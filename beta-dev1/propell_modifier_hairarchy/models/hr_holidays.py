from odoo import api, fields, models
from odoo.exceptions import UserError, AccessError, ValidationError
from openerp.tools import float_compare
from odoo.tools.translate import _

HOURS_PER_DAY = 8

class hr_holidays_modifier(models.Model):
    _inherit = 'hr.holidays'

    # state = fields.Selection(selection_add=[])

    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('supervisor', 'supervisor'),
        ('SIC', 'SIC'),
        ('TIC/OIC', 'TIC/OIC'),
        ('HOD', 'HOD'),
        ('GM', 'GM'),
        ('ED', 'ED'),
        ('MD', 'MD'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')
    ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='confirm',
        help="The status is set to 'To Submit', when a holiday request is created." +
             "\nThe status is 'To Approve', when holiday request is confirmed by user." +
             "\nThe status is 'Refused', when holiday request is refused by manager." +
             "\nThe status is 'Approved', when holiday request is approved by manager.")

    @api.multi
    def action_approve(self):
        # if double_validation: this method is the first approval approval
        # if not double_validation: this method calls action_validate() below
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only an HR Officer or Manager can approve leave requests.'))

        hr_supervisor = \
        self.env['ir.model.data'].get_object_reference('propell_modifier_hairarchy', 'group_hr_holidays_supervisor')[1]

        hr_supervisor_group = self.env['res.groups'].browse(hr_supervisor)

        hr_sic = \
        self.env['ir.model.data'].get_object_reference('propell_modifier_hairarchy', 'group_hr_holidays_SIC')[1]

        hr_sic_group = self.env['res.groups'].browse(hr_sic)

        hr_tic = \
            self.env['ir.model.data'].get_object_reference('propell_modifier_hairarchy', 'group_hr_holidays_TIC')[1]

        hr_tic_group = self.env['res.groups'].browse(hr_tic)

        hr_hod = \
            self.env['ir.model.data'].get_object_reference('propell_modifier_hairarchy', 'group_hr_holidays_HOD')[1]

        hr_hod_group = self.env['res.groups'].browse(hr_hod)

        hr_gm = \
            self.env['ir.model.data'].get_object_reference('propell_modifier_hairarchy', 'group_hr_holidays_GM')[1]

        hr_gm_group = self.env['res.groups'].browse(hr_gm)

        hr_ed = \
            self.env['ir.model.data'].get_object_reference('propell_modifier_hairarchy', 'group_hr_holidays_ED')[1]

        hr_ed_group = self.env['res.groups'].browse(hr_ed)

        hr_md = \
            self.env['ir.model.data'].get_object_reference('propell_modifier_hairarchy', 'group_hr_holidays_MD')[1]

        hr_md_group = self.env['res.groups'].browse(hr_md)



        for user in hr_supervisor_group.users:
            if int(self._context.get('uid')) == int(user.id):
                if self.department_id.name in ['Technician/Worker']:
                    if self.state == 'confirm':
                        return self.write({'state': 'supervisor'})
                    if self.state == 'supervisor':
                        raise UserError(_('You had already sent approval to SIC'))
                else:
                    raise UserError(_('Supervisor can not approval %s Department leave') % (self.department_id.name))

        for user in hr_sic_group.users:
            if int(self._context.get('uid')) == int(user.id):
                if self.department_id.name in ['Technician/Worker','Engineer','Supervisor/Forman']:
                    print "2222222"
                    if self.state == 'confirm':
                        return self.write({'state': 'SIC'})
                    if self.state == 'supervisor':
                        return self.write({'state': 'SIC'})
                    if self.state == 'SIC':
                        raise UserError(_('You had already sent approval to SIC'))
                else:
                    raise UserError(_('SIC/Manager can not approval %s Department leave') % (self.department_id.name))

        for user in hr_tic_group.users:
            if int(self._context.get('uid')) == int(user.id):
                if self.department_id.name in ['Technician/Worker','Engineer','Supervisor/Forman','SIC/Manager/site-manager']:
                    print "2222222"
                    if self.state == 'confirm':
                        return self.write({'state': 'TIC/OIC'})
                    if self.state == 'SIC':
                        return self.write({'state': 'TIC/OIC'})
                    if self.state == 'TIC/OIC':
                        raise UserError(_('You had already sent approval to TIC'))
                else:
                    raise UserError(_('TIC/OIC/Assistent HOD can not approval %s Department leave') % (self.department_id.name))

        for user in hr_hod_group.users:
            if int(self._context.get('uid')) == int(user.id):
                if self.department_id.name in ['Technician/Worker','Engineer','Supervisor/Forman','SIC/Manager/site-manager','TIC/OIC/Assistant HOD']:
                    print "2222222"
                    if self.state == 'confirm':
                        return self.write({'state': 'HOD'})
                    if self.state == 'TIC/OIC':
                        return self.write({'state': 'HOD'})
                    if self.state == 'HOD':
                        raise UserError(_('You had already sent approval to HOD'))
                else:
                    raise UserError(_('HOD can not approval %s Department leave') % (self.department_id.name))

        for user in hr_gm_group.users:
            if int(self._context.get('uid')) == int(user.id):
                if self.department_id.name in ['Technician/Worker','Engineer','Supervisor/Forman','SIC/Manager/site-manager','TIC/OIC/Assistant HOD','HOD']:
                    print "2222222"
                    if self.state == 'confirm':
                        return self.write({'state': 'ED'})
                    if self.state == 'HOD':
                        return self.write({'state': 'ED'})
                    if self.state == 'GM':
                        raise UserError(_('You had already sent approval to ED'))
                else:
                    raise UserError(_('GM can not approval %s Department leave') % (self.department_id.name))

        for user in hr_ed_group.users:
            if int(self._context.get('uid')) == int(user.id):
                if self.department_id.name in ['Technician/Worker','Engineer','Supervisor/Forman','SIC/Manager/site-manager','TIC/OIC/Assistant HOD','HOD','General Manager']:
                    print "2222222"
                    if self.state == 'confirm':
                        return self.write({'state': 'MD'})
                    if self.state == 'ED':
                        return self.write({'state': 'MD'})
                    if self.state == 'MD':
                        raise UserError(_('You had already sent approval to MD'))
                else:
                    raise UserError(_('GM can not approval %s Department leave') % (self.department_id.name))

        for user in hr_md_group.users:
            if int(self._context.get('uid')) == int(user.id):
                if self.department_id.name in ['Technician/Worker','Engineer','Supervisor/Forman','SIC/Manager/site-manager','TIC/OIC/Assistant HOD','HOD','General Manager','Executive Director']:

                    manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
                    for holiday in self:
                        if holiday.state != 'MD':
                            raise UserError(_('Leave request must be confirmed ("To Approve") in order to approve it.'))

                        if holiday.double_validation:
                            return holiday.write({'state': 'validate1', 'manager_id': manager.id if manager else False})
                        else:
                            self.action_validate()
                else:
                    raise UserError(_('MD can not approval %s Department leave') % (self.department_id.name))

    def action_validate(self):
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only an HR Officer or Manager can approve leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm', 'validate1','MD']:
                raise UserError(_('Leave request must be confirmed in order to approve it.'))
            if holiday.state == 'validate1' and not holiday.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
                raise UserError(_('Only an HR Manager can apply the second approval on leave requests.'))

            holiday.write({'state': 'validate'})
            if holiday.double_validation:
                holiday.write({'manager_id2': manager.id})
            else:
                holiday.write({'manager_id': manager.id})
            if holiday.holiday_type == 'employee' and holiday.type == 'remove':
                meeting_values = {
                    'name': holiday.display_name,
                    'categ_ids': [
                        (6, 0, [holiday.holiday_status_id.categ_id.id])] if holiday.holiday_status_id.categ_id else [],
                    'duration': holiday.number_of_days_temp * HOURS_PER_DAY,
                    'description': holiday.notes,
                    'user_id': holiday.user_id.id,
                    'start': holiday.date_from,
                    'stop': holiday.date_to,
                    'allday': False,
                    'state': 'open',  # to block that meeting date in the calendar
                    'privacy': 'confidential'
                }
                # Add the partner_id (if exist) as an attendee
                if holiday.user_id and holiday.user_id.partner_id:
                    meeting_values['partner_ids'] = [(4, holiday.user_id.partner_id.id)]

                meeting = self.env['calendar.event'].with_context(no_mail_to_attendees=True).create(meeting_values)
                holiday._create_resource_leave()
                holiday.write({'meeting_id': meeting.id})
            elif holiday.holiday_type == 'category':
                leaves = self.env['hr.holidays']
                for employee in holiday.category_id.employee_ids:
                    values = holiday._prepare_create_by_category(employee)
                    leaves += self.with_context(mail_notify_force_send=False).create(values)
                # TODO is it necessary to interleave the calls?
                leaves.action_approve()
                if leaves and leaves[0].double_validation:
                    leaves.action_validate()
        return True