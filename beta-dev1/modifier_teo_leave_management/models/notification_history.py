from odoo import fields, models

class HolidayNotification(models.Model):
    _name = "hr.holiday.notification"
    _order = 'id desc'

    mail_id = fields.Many2one('mail.mail', 'Email', required=True)
    name = fields.Char('Name', required=True, related='mail_id.subject')
    date = fields.Datetime('Name', related='mail_id.date')
    email_from = fields.Char('Email From', related="mail_id.email_from")
    state = fields.Selection('Status', related="mail_id.state")
    author_id = fields.Many2one('res.users', 'User')
    email_to = fields.Char('Email To')
    is_businnes_ref = fields.Boolean('Businnes Travel Reference')
    emlpoyee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    boss_id = fields.Many2one('hr.employee', 'Boss', related='emlpoyee_id.boss_id')
    leave_manager = fields.Many2one('hr.employee', 'Leave Manager', related='emlpoyee_id.leave_manager')
    parent_id = fields.Many2one('hr.employee', 'Expense Manager', related='emlpoyee_id.parent_id')
    department_id = fields.Many2one('hr.department', 'Leave Manager', related='emlpoyee_id.department_id')
    dept_manager_id = fields.Many2one('hr.employee', '	Manager', related='department_id.manager_id')
    
