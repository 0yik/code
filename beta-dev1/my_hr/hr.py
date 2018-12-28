# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

from odoo import SUPERUSER_ID
from odoo.modules.module import get_module_resource
from odoo import fields, models, api, exceptions, tools
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class hr_employee_category(models.Model):

    def name_get(self):
        if not self._ids:
            return []
        reads = self.read(['name','parent_id'])
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self):
        res = self.name_get()
        return dict(res)

    _name = "hr.employee.category"
    _description = "Employee Category"

    name = fields.Char("Employee Tag", required=True)
    complete_name = fields.Char(compute=_name_get_fnc, string='Name')
    parent_id = fields.Many2one('hr.employee.category', 'Parent Employee Tag', select=True)
    child_ids = fields.One2many('hr.employee.category', 'parent_id', 'Child Categories')
    employee_ids = fields.Many2many('hr.employee', 'employee_category_rel', 'category_id', 'emp_id', 'Employees')

    def _check_recursion(self):
        level = 100
        cr = self._cr
        ids = self._ids
        while len(ids):
            cr.execute('select distinct parent_id from hr_employee_category where id IN %s', (tuple(ids), ))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error! You cannot create recursive Categories.', ['parent_id'])
    ]


class hr_job(models.Model):
    _name = "hr.job"
    _description = "Job Position"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.multi
    def _get_nbr_employees(self):
        res = {}
        for job in self:
            nb_employees = len(job.employee_ids or [])
            res[job.id] = {
                'no_of_employee': nb_employees,
                'expected_employees': nb_employees + job.no_of_recruitment,
            }
        return res

    @api.multi
    def _get_job_position(self):
        res = []
        for employee in self:
            if employee.job_id:
                res.append(employee.job_id.id)
        return res

    name = fields.Char('Job Name', required=True, select=True,
                       translate=True)
    expected_employees = fields.Integer(compute=_get_nbr_employees, string='Total Forecasted Employees',
                                        help='Expected number of employees for this job position after new recruitment.',
                                        store={
                                            'hr.job': (
                                            lambda self, cr, uid, ids, c=None: ids, ['no_of_recruitment'], 10),
                                            'hr.employee': (_get_job_position, ['job_id'], 10),
                                        },
                                        multi='_get_nbr_employees')
    no_of_employee = fields.Integer(compute=_get_nbr_employees, string="Current Number of Employees",
                                    help='Number of employees currently occupying this job position.',
                                    store={
                                        'hr.employee': (_get_job_position, ['job_id'], 10),
                                    },
                                    multi='_get_nbr_employees')
    no_of_recruitment = fields.Integer('Expected New Employees', copy=False,
                                       help='Number of new employees you expect to recruit.')
    no_of_hired_employee = fields.Integer('Hired Employees', copy=False,
                                          help='Number of hired employees for this job position during recruitment phase.')
    employee_ids = fields.One2many('hr.employee', 'job_id', 'Employees', groups='base.group_user')
    description = fields.Text('Job Description')
    requirements = fields.Text('Requirements')
    department_id = fields.Many2one('hr.department', 'Department')
    company_id = fields.Many2one('res.company', 'Company')
    state = fields.Selection([('open', 'Recruitment Closed'), ('recruit', 'Recruitment in Progress')],
                             string='Status', readonly=True, required=True,
                             track_visibility='always', copy=False,
                             help="By default 'Closed', set it to 'In Recruitment' if recruitment process is going on for this job position.")
    write_date = fields.Datetime('Update Date', readonly=True)

    _defaults = {
        'company_id': lambda self: self.env['res.company']._company_default_get('hr.job'),
        'state': 'open',
    }

    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id, department_id)', 'The name of the job position must be unique per department in company!'),
        ('hired_employee_check', "CHECK ( no_of_hired_employee <= no_of_recruitment )", "Number of hired employee must be less than expected number of employee in recruitment."),
    ]

    @api.multi
    def set_recruit(self):
        for job in self:
            no_of_recruitment = job.no_of_recruitment == 0 and 1 or job.no_of_recruitment
            job.write({'state': 'recruit', 'no_of_recruitment': no_of_recruitment})
        return True

    @api.model
    def set_open(self):
        self.write({
            'state': 'open',
            'no_of_recruitment': 0,
            'no_of_hired_employee': 0
        })
        return True

    @api.model
    def copy(self):
        default = {}
        if 'name' not in default:
            default['name'] = _("%s (copy)") % (self.name)
        return super(hr_job, self).copy()

    # ----------------------------------------
    # Compatibility methods
    # ----------------------------------------
    _no_of_employee = _get_nbr_employees  # v7 compatibility
    job_open = set_open  # v7 compatibility
    job_recruitment = set_recruit  # v7 compatibility


class hr_employee(models.Model):
    _name = "hr.employee"
    _description = "Employee"
    _order = 'name'
    _inherit = "mail.thread"
    _inherits = {'resource.resource': "resource_id"}

    _mail_post_access = 'read'

    @api.multi
    def _get_image(self):
        result = dict.fromkeys(self._ids, False)
        for obj in self:
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    @api.model
    def _set_image(self, value):
        return self.write({'image': tools.image_resize_image_big(value)})

    # we need a related field in order to be able to sort the employee by name
    name = fields.Char(related='resource_id.name', string='Name', readonly=True, store=True)
    country_id = fields.Many2one('res.country', 'Nationality')
    birthday = fields.Date("Date of Birth")
    ssnid = fields.Char('SSN No', help='Social Security Number')
    sinid = fields.Char('SIN No', help="Social Insurance Number")
    identification_id = fields.Char('Identification No')
    otherid = fields.Char('Other Id')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], 'Gender')
    marital = fields.Selection(
        [('single', 'Single'), ('married', 'Married'), ('widower', 'Widower'), ('divorced', 'Divorced')],
        'Marital Status')
    department_id = fields.Many2one('hr.department', 'Department')
    address_id = fields.Many2one('res.partner', 'Working Address')
    address_home_id = fields.Many2one('res.partner', 'Home Address')
    bank_account_id = fields.Many2one('res.partner.bank', 'Bank Account Number',
                                      domain="[('partner_id','=',address_home_id)]",
                                      help="Employee bank salary account")
    work_phone = fields.Char('Work Phone', readonly=False)
    mobile_phone = fields.Char('Work Mobile', readonly=False)
    work_email = fields.Char('Work Email', size=240)
    work_location = fields.Char('Office Location')
    notes = fields.Text('Notes')
    parent_id = fields.Many2one('hr.employee', 'Manager')
    category_ids = fields.Many2many('hr.employee.category', 'employee_category_rel', 'emp_id', 'category_id',
                                    'Tags')
    child_ids = fields.One2many('hr.employee', 'parent_id', 'Subordinates')
    coach_id = fields.Many2one('hr.employee', 'Coach')
    job_id = fields.Many2one('hr.job', 'Job Title')
    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary("Photo",
                          help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
    image_medium = fields.Binary(compute=_get_image, fnct_inv=_set_image,
                                 string="Medium-sized photo", multi="_get_image",
                                 # store={
                                 #     'hr.employee': (lambda self: self._ids, ['image'], 10),
                                 # },
                                 help="Medium-sized photo of the employee. It is automatically " \
                                      "resized as a 128x128px image, with aspect ratio preserved. " \
                                      "Use this field in form views or some kanban views.")
    image_small = fields.Binary(compute=_get_image, fnct_inv=_set_image,
                                string="Small-sized photo", multi="_get_image",
                                # store={
                                #     'hr.employee': (lambda self: self._ids, ['image'], 10),
                                # },
                                help="Small-sized photo of the employee. It is automatically " \
                                     "resized as a 64x64px image, with aspect ratio preserved. " \
                                     "Use this field anywhere a small image is required.")
    passport_id = fields.Char('Passport No')
    color = fields.Integer('Color Index')
    city = fields.Char(related='address_id.city', string='City')
    user_id = fields.Many2one('res.users', 'Users')
    active = fields.Integer('Active')
    company_id = fields.Many2one('res.company', 'Company', select=True, required=False)
    login = fields.Char(related='user_id.login', string='Login', readonly=1)
    last_login = fields.Date(related='user_id.date', string='Latest Connection', readonly=1)

    def _get_default_image(self, cr, uid, context=None):
        image_path = get_module_resource('hr', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))

    defaults = {
        'active': 1,
        'image': _get_default_image,
        'color': 0,
    }

    def _broadcast_welcome(self, employee_id):
        """ Broadcast the welcome message to all users in the employee company. """
        employee = self.browse(employee_id)
        cr = self._cr
        uid = self._uid
        partner_ids = []
        _model, group_id = self.env['ir.model.data'].get_object_reference('base', 'group_user')
        if employee.user_id:
            company_id = employee.user_id.company_id.id
        elif employee.company_id:
            company_id = employee.company_id.id
        elif employee.job_id:
            company_id = employee.job_id.company_id.id
        elif employee.department_id:
            company_id = employee.department_id.company_id.id
        else:
            company_id = self.env['res.company']._company_default_get('hr.employee')
        res_users = self.env['res.users']
        user_ids = res_users.search([
                ('company_id', '=', company_id),
                ('groups_id', 'in', group_id)
            ])
        partner_ids = list(set(u.partner_id.id for u in res_users.browse(cr, SUPERUSER_ID, user_ids)))
        self.message_post(
            cr, uid, [employee_id],
            body=_('Welcome to %s! Please help him/her take the first steps with Odoo!') % (employee.name),
            partner_ids=partner_ids,
            subtype='mail.mt_comment')
        return True

    def create(self, data, context=None):
        context = dict(context or {})
        if context.get("mail_broadcast"):
            context['mail_create_nolog'] = True

        employee_id = super(hr_employee, self).create()

        if context.get("mail_broadcast"):
            self._broadcast_welcome(employee_id)
        return employee_id

    def unlink(self):
        resource_ids = []
        for employee in self:
            resource_ids.append(employee.resource_id.id)
        super(hr_employee, self).unlink()
        return self.env['resource.resource'].unlink(resource_ids)

    def onchange_address_id(self, address):
        if address:
            address = self.env['res.partner'].browse(address)
            return {'value': {'work_phone': address.phone, 'mobile_phone': address.mobile}}
        return {'value': {}}

    def onchange_company(self, company):
        address_id = False
        if company:
            company_id = self.env('res.company').browse(company)
            address = self.env('res.partner').address_get(self._cr, self._uid, [company_id.partner_id.id], ['default'])
            address_id = address and address['default'] or False
        return {'value': {'address_id': address_id}}

    def onchange_department_id(self, department_id):
        value = {'parent_id': False}
        if department_id:
            department = self.env['hr.department'].browse(department_id)
            value['parent_id'] = department.manager_id.id
        return {'value': value}

    def onchange_user(self, user_id):
        work_email = False
        if user_id:
            work_email = self.env['res.users'].browse(user_id).email
        return {'value': {'work_email': work_email}}

    def action_follow(self):
        """ Wrapper because message_subscribe_users take a user_ids=None
            that receive the context without the wrapper. """
        return self.message_subscribe_users()

    def action_unfollow(self):
        """ Wrapper because message_unsubscribe_users take a user_ids=None
            that receive the context without the wrapper. """
        return self.message_unsubscribe_users()

    def get_suggested_thread(self, removed_suggested_threads=None):
        """Show the suggestion of employees if display_employees_suggestions if the
        user perference allows it. """
        if not self.display_employees_suggestions:
            return []
        else:
            return super(hr_employee, self).get_suggested_thread(removed_suggested_threads)

    def _message_get_auto_subscribe_fields(self, updated_fields, auto_follow_fields=None):
        """ Overwrite of the original method to always follow user_id field,
        even when not track_visibility so that a user will follow it's employee
        """
        if auto_follow_fields is None:
            auto_follow_fields = ['user_id']
        user_field_lst = []
        for name, field in self._fields.items():
            if name in auto_follow_fields and name in updated_fields and field.comodel_name == 'res.users':
                user_field_lst.append(name)
        return user_field_lst

    def _check_recursion(self):
        level = 100
        ids = self._ids
        cr = self._cr
        while len(ids):
            cr.execute('SELECT DISTINCT parent_id FROM hr_employee WHERE id IN %s AND parent_id!=id',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error! You cannot create recursive hierarchy of Employee(s).', ['parent_id']),
    ]


class hr_department(models.Model):

    def _dept_name_get_fnc(self, prop):
        res = self.name_get()
        return dict(res)

    _name = "hr.department"

    name = fields.Char('Department Name', required=True)
    complete_name = fields.Char(compute=_dept_name_get_fnc, string='Name')
    company_id = fields.Many2one('res.company', 'Company', select=True, required=False)
    parent_id = fields.Many2one('hr.department', 'Parent Department', select=True)
    child_ids = fields.One2many('hr.department', 'parent_id', 'Child Departments')
    manager_id = fields.Many2one('hr.employee', 'Manager')
    member_ids = fields.One2many('hr.employee', 'department_id', 'Members', readonly=True)
    jobs_ids = fields.One2many('hr.job', 'department_id', 'Jobs')
    note = fields.Text('Note')

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.env['res.company']._company_default_get('hr.department'),
    }

    def _check_recursion(self):
        cr = self._cr
        ids = self._ids
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from hr_department where id IN %s',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error! You cannot create recursive departments.', ['parent_id'])
    ]

    def name_get(self):
        if not self._ids:
            return []
        reads = self.read(['name','parent_id'])
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res


class res_users(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    employee_ids = fields.One2many('hr.employee', 'user_id', 'Related employees'),

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
