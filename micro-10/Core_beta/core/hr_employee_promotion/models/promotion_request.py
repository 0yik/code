# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class promotion_request(models.Model):
    _name = 'promotion.request'

    @api.multi
    @api.depends('employee_id')
    def get_emp_details(self):
        for rec in self:
            if rec.employee_id:
                rec.job_id = rec.employee_id.job_id.id
                rec.join_date = rec.employee_id.join_date
                rec.department_id = rec.employee_id.department_id.id
                rec.next_approver_ids = False
                next_approver = rec.department_id.manager_id.user_id.id or False
                if next_approver:
                    rec.next_approver_ids = [(6, 0, [next_approver])]
            else:
                rec.job_id = False
                rec.join_date = False
                rec.department_id = False
                rec.next_approver_ids = False

    name = fields.Char("Promotion Request", default="Promotion Request")
    employee_id = fields.Many2one("hr.employee", string="Employee")
    job_id = fields.Many2one("hr.job", string="Job", compute="get_emp_details", store=True)
    join_date = fields.Date("Date joined", compute="get_emp_details",store=True)
    req_date = fields.Date("Requested Date", default=fields.Datetime.now)
    department_id = fields.Many2one("hr.department", string="Department",compute="get_emp_details",store=True)
    promo_date = fields.Date("Promotion Date")
    promoted_to = fields.Many2one("hr.job", string="Promoted To")
    create_uid = fields.Many2one("res.users", default=lambda self: self.env.user)

    status = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_dept_approval', 'Waiting for Department Approval'),
        ('waiting_hr_approval', 'Waiting for HR Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancel', 'Cancel')
    ], string='Status', default='draft', copy=False, index=True, help="Status of the Promotion Request.")

    goal_promo_ids = fields.One2many("goals.promotion","promotion_req_id", string="Goals for promotion", )
    next_approver_ids = fields.Many2many("res.users", string="Next Approvers", compute="get_emp_details", store=True)
    cmt_by_mng = fields.Text("Comment by Manager")

    transfer_company_id = fields.Many2one('res.company', string='Transfer To Company', default=lambda self: self.env.user.company_id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)


    def get_email_to_name(self):
        email_to = ''
        for user in self.next_approver_ids:
            email_to = email_to + user.name + ','
        return email_to

    def send_mail_to_internal_user(self):
        email_template = self.env.ref('hr_employee_promotion.approve_promotion_request')
        email_to = ''
        for user in self.next_approver_ids:
            if user.login:
                email_to = email_to + user.login + ','
        email_template.sudo().write({'email_to': email_to})
        email_template.sudo().send_mail(self.id, force_send=False)

    @api.multi
    def submit_request(self):
        for rec in self:
            rec.status = 'waiting_dept_approval'
            self.send_mail_to_internal_user()
        return True

    @api.multi
    def approved_request(self):
        for rec in self:
            if rec.status == "waiting_dept_approval":
                if self.env.user.id in rec.next_approver_ids.ids:

                    if not self.promo_date:
                        raise ValidationError(_("Please insert promotion date..!!"))

                    rec.next_approver_ids = False
                    hr_manager_users = self.env['res.users'].search([])
                    hr_managers = hr_manager_users.filtered(lambda x: x.has_group('hr.group_hr_manager'))
                    self.next_approver_ids = [(6, 0, hr_managers.ids)]
                    rec.status = 'waiting_hr_approval'
                    self.send_mail_to_internal_user()
                else:
                    raise ValidationError(_("You don't have access to approve this promotion request...!!"))

            elif rec.status == "waiting_hr_approval":
                if self.env.user.id in rec.next_approver_ids.ids:
                    if not self.promo_date:
                        raise ValidationError(_("Please insert promotion date..!!"))
                    rec.status = 'approved'
                else:
                    raise ValidationError(_("You don't have access to approve this promotion request...!!"))
        return True

    @api.multi
    def reject_request(self):
        for rec in self:
            if self.env.user.id in rec.next_approver_ids.ids:
                rec.status = 'rejected'
            else:
                raise ValidationError(_("You don't have access to reject this promotion request...!!"))
        return True

    @api.onchange('job_id')
    def onchabge_job_id(self):
        if self.job_id:
            goal_promotion_lines = []
            for goal_promo_id in self.job_id.goal_promo_ids:

                # goal_performance = ''
                # if goal_promo_id.goal_performance == 'higher':
                #     goal_performance = 'The higher the better'
                # elif goal_promo_id.goal_performance == 'lower':
                #     goal_performance = 'The lower the better'

                vals = {
                    'goal_defination': goal_promo_id.goal_defination.id or False,
                    #'goal_performance': goal_performance or False,
                    'target_value_reach':goal_promo_id.target_value_reach or False,
                    'goal_description': goal_promo_id.goal_description or False,
                }
                goal_promotion_lines.append((0, 0, vals))
            self.goal_promo_ids = goal_promotion_lines

    def get_action_approve_promotion_request(self):
        return self.env['ir.model.data'].sudo().get_object('hr_employee_promotion',
                                                           'action_promotion_request_submited').id


    @api.multi
    def manage_employee_promotion(self):
        """ this method is called form schedule action"""
        today_date = datetime.now().date()
        approved_promotions = self.env['promotion.request'].sudo().search([('status','=','approved'),('promo_date','=',today_date)])
        for approved_promotion in approved_promotions:
            approved_promotion.employee_id.sudo().write({'job_id':approved_promotion.promoted_to.id,
                                                        'address_id':approved_promotion.transfer_company_id.partner_id.id})