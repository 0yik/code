from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    current_leave_state = fields.Selection(compute='_compute_leave_status', string="Current Leave Status",
        selection=[
            ('draft', 'New'),
            ('pm_approval', 'Waiting for Project Manager approval'),
            ('sup_approval', 'Waiting for Supervisor approval'),
            ('eng_approval', 'Waiting for Engineer approval'),
            ('confirm', 'Waiting for SIC/Manager approval'),
            ('tic_approval', 'Waiting for TIC/OIC approval'),
            ('hod_approval', 'Waiting for HOD approval'),
            ('gm_approval', 'Waiting for GM approval'),
            ('ed_approval', 'Waiting for ED approval'),
            ('md_approval', 'Waiting for MD approval'),
            ('next_approval', 'Waiting for Next Manager approval'),
            ('refuse', 'Refused'), ('validate1', 'Waiting Final Approval'),
            ('validate', 'Approved'), ('cancel', 'Cancelled')
        ])


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    state = fields.Selection([('draft', 'New'), ('confirm', 'Waiting for SIC/Manager approval'),
                              ('pm_approval', 'Waiting for Project Manager approval'),
                              ('sup_approval', 'Waiting for Supervisor approval'),
                              ('eng_approval', 'Waiting for Engineer approval'),
                              ('tic_approval', 'Waiting for TIC/OIC approval'),
                              ('hod_approval', 'Waiting for HOD approval'),
                              ('gm_approval', 'Waiting for GM approval'),
                              ('ed_approval', 'Waiting for ED approval'),
                              ('md_approval', 'Waiting for MD approval'),
                              ('next_approval', 'Waiting for Next Manager approval'),
                              ('refuse', 'Refused'), ('validate1', 'Waiting Final Approval'),
                              ('validate', 'Approved'), ('cancel', 'Cancelled')],
        'State', readonly=True, help='The state is set to \'Draft\', when a holiday request is created.\
        \nThe state is \'Waiting Approval\', when holiday request is confirmed by user.\
        \nThe state is \'Refused\', when holiday request is refused by manager.\
        \nThe state is \'Approved\', when holiday request is approved by manager.', track_visibility='onchange')

    def approve_pm(self):
        team_member_ids = self.env['project.teammember'].sudo().search([('team_member', 'in', [self.employee_id.user_id.id])])
        project_ids = self.env['project.project'].sudo().search([('supervisor_id', 'in', [self.employee_id.user_id.id])])

        pm_ids = []
        for team in team_member_ids:
            for user in team.project_id.user_id:
                pm_ids.append(user.id)

        for team_member_id in team_member_ids:
            if not team_member_id.project_id.user_id:
                raise UserError(_('Manager is not set for this %s project.') % (team_member_id.project_id.name))
            if team_member_id.project_id:
                if self._uid not in pm_ids and self._uid != 1:
                    raise UserError(_('Only Project Manager can approve this Leave.'))

#         pm1_ids = [project.user_id.id for project in project_ids]
        pm1_ids = []
        for project in project_ids:
            for user in project.user_id:
                pm1_ids.append(user.id)

        if pm1_ids and self._uid not in pm1_ids and self._uid != 1:
            raise UserError(_('Only Project Manager can approve this Leave.'))

#         NOTE : set status
        site_mgr_id = self.env.ref('hr_employee_hierarchy.group_leave_sic')
        assis_hod_id = self.env.ref('hr_employee_hierarchy.group_leave_tic')
        hod_id = self.env.ref('hr_employee_hierarchy.group_leave_hod')
        gm_id = self.env.ref('hr_employee_hierarchy.group_leave_gm')
        ed_id = self.env.ref('hr_employee_hierarchy.group_leave_ed')
        md_id = self.env.ref('hr_employee_hierarchy.group_leave_md')
        if not self.employee_id.hierarchy_id:
            if self.employee_id.user_id.id in site_mgr_id.users.ids:
                self.state = 'tic_approval'
            elif self.employee_id.user_id.id in assis_hod_id.users.ids:
                self.state = 'hod_approval'
            elif self.employee_id.user_id.id in hod_id.users.ids:
                self.state = 'gm_approval'
            elif self.employee_id.user_id.id in gm_id.users.ids:
                self.state = 'ed_approval'
            elif self.employee_id.user_id.id in ed_id.users.ids:
                self.state = 'md_approval'
            else:
                self.state = 'confirm'
        else:
            if self.employee_id.hierarchy_id:
                state = self.leave_approve_hierarchy()
                if state =='confirm':
                    self.notify_email_manager(site_mgr_id)
                if state =='tic_approval':
                    self.notify_email_manager(assis_hod_id)
                if state =='hod_approval':
                    self.notify_email_manager(hod_id)
                if state =='gm_approval':
                    self.notify_email_manager(gm_id)
                if state == 'ed_approval':
                    self.notify_email_manager(ed_id)
                if state == 'md_approval':
                    self.notify_email_manager(md_id)
            else:
                self.state = 'confirm'
                self.notify_email_manager(site_mgr_id)
        return

    def approve_sup(self):
        team_member_ids = self.env['project.teammember'].sudo().search([('team_member', 'in', [self.employee_id.user_id.id])])
        flag = False
        team = []
        for team_member_id in team_member_ids:
            if team_member_id.project_id and team_member_id.project_id.user_id:
                if not flag:
                    if self._uid not in team_member_id.project_id.supervisor_id.ids and self._uid != 1:
                        team.append(team_member_id.project_id.name)
                        continue
                    self.state = 'pm_approval'
                    flag = True
                self.notify_email(team_member_id.project_id.user_id)
        if not flag:
            raise UserError(_('Only supervisor of %s project can approve this Leave.') % (' '.join(team)))        

        return

    def approve_eng(self):
        team_member_ids = self.env['project.teammember'].sudo().search([('team_member', 'in', [self.employee_id.user_id.id])])
        flag = False

        allow_approve = False
        for team_member_id in team_member_ids:
            if team_member_id.project_id.engineer_ids:
                if (team_member_id.project_id.allow_eng and self._uid in team_member_id.project_id.engineer_ids.ids) or self._uid == 1:
                    allow_approve = True
                    break
        if not allow_approve:
            raise UserError(_('Only Engineer from The project, in which Include Engineer in Leave Hierarchy is Ticked can approve this Leave.'))

        for team_member_id in team_member_ids:
            if team_member_id.project_id.supervisor_id:
                if not flag:
                    self.state = 'sup_approval'
                    flag = True
                self.notify_email(team_member_id.project_id.supervisor_id)

            if team_member_id.project_id.user_id and not team_member_id.project_id.supervisor_id:
                if not flag:
                    self.state = 'pm_approval'
                    flag = True
                self.notify_email(team_member_id.project_id.user_id)
        if flag:
            return True

        return

    @api.model
    def create(self, vals):
        if vals.get('type') == 'remove' and vals.get('employee_id'):
            vals.update({'from_project': True})
        res = super(HrHolidays, self).create(vals)
        return res
