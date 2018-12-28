# -*- coding: utf-8 -*-
from odoo import fields, models, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    address = fields.Text('Working Address')
    address_home = fields.Text('Home Address')
    birthday = fields.Date('Date of Birth', groups='hr.group_hr_user',default=lambda *a: (datetime.today() - relativedelta(years=30)).strftime('%Y-%m-%d'))
    coach_id = fields.Many2one('hr.employee', string='Mentor')
    # employee_type_id = fields.Selection([('employment_pass','Employement Pass'),('skilled_pass','Skilled S Pass'),('unskilled_pass','Unskilled S Pass'),('skilled_work_permit','Skilled Work Permit'),('unskilled_work_permit','Unskilled Work Permit'),('dependant_pass','Dependant Pass (LOC)'),('traning_pass','Training Pass'),('work_holiday_pass','Work Holiday Pass'),('others','Others')], string='Type Of Work Pass')
    emp_status = fields.Selection(selection=[('active','Active'),('probation', 'Probation'), ('full_time', 'Full Time'),
                                             ('part_time','Part Time'), ('contract_based','Contract Based'),
                                             ('in_notice', 'In Notice'), ('internship','Internship'),
                                             ('terminated', 'Terminated'), ('outsourced','Outsourced'),
                                             ('others', 'Others')], string='Employment Status', default='full_time')
    other_document_ids = fields.One2many('employee.other.document', 'other_document_id', string='Other Documents')
    expiry_document_ids = fields.One2many('expiring.document', 'employee_id', string='Expiring Documents')

    # @api.one
    # @api.constrains('age')
    # def _check_name(self):
    #     if len(self.search([('age', '=', self.age)])) <= 0:
    #         raise ValidationError("Date of birth should be lesser than date of joined!")

hr_employee()

class dependents(models.Model):

    _inherit = 'dependents'

    nationality = fields.Many2one('res.country', 'Nationality')

class hr_education_information(models.Model):
    _inherit = 'hr.education.information'

    institution = fields.Text('Institution')
    country_id =fields.Many2one('res.country','Country')
    date_start = fields.Date('Date Start')
    date_end = fields.Date('Date End')
    language_of_instruction = fields.Text('Language Of Instruction')
    qualification_obtained = fields.Text('Qualification Obtained')
    attachments = fields.Binary('Attachments')
    remarks = fields.Text('Remarks')

hr_education_information()

class employee_history(models.Model):
    _inherit = 'employee.history'

    emp_status = fields.Selection(selection=[('active', 'Active'),('probation', 'Probation'), ('full_time', 'Full Time'),
                                             ('part_time', 'Part Time'), ('contract_based', 'Contract Based'),
                                             ('in_notice', 'In Notice'), ('internship', 'Internship'),
                                             ('terminated', 'Terminated'), ('outsourced', 'Outsourced'),
                                             ('others', 'Others')], string='Employment Status', default='full_time')

employee_history()

class employee_other_document(models.Model):
    _name = 'employee.other.document'

    document_name = fields.Char('Name')
    document_attachment = fields.Binary('Attachment')
    other_document_id = fields.Many2one('hr.employee', string='Other Document')

employee_other_document()

class expiry_document(models.Model):
    _name = 'expiring.document'

    expiry_name = fields.Char("Documents", size=256)
    expiry_number = fields.Char('Number', size=256)
    employee_id = fields.Many2one('hr.employee', 'Employee Name')
    exp_date = fields.Date('Expiry Date')
    issue_date = fields.Date('Issue Date')
    eligible_status = fields.Char('Eligible Status', size=256)
    issue_by = fields.Many2one('res.country', 'Issue By')
    eligible_review_date = fields.Date('Eligible Review Date')
    doc_type_id = fields.Many2one('document.type', 'Document Type')
    comments = fields.Text("Comments")
    expiry_attachment = fields.Binary('Attach Document')
    immigration_id = fields.Many2one('employee.immigration', string='Immigration')

    @api.multi
    def expiring_document_scheduler(self):
        after_90days = str(datetime.now() + relativedelta(days=90))[:10]
        expiring_vals = {}
        for immigration_line in self.env['employee.immigration'].search([('exp_date', '>=', after_90days)]):
            expiring_vals['expiry_name'] = immigration_line.documents
            expiring_vals['expiry_number'] = immigration_line.number
            expiring_vals['employee_id'] = immigration_line.employee_id.id
            expiring_vals['exp_date'] = immigration_line.exp_date
            expiring_vals['issue_date'] = immigration_line.issue_date
            expiring_vals['eligible_status'] = immigration_line.eligible_status
            expiring_vals['issue_by'] = immigration_line.issue_by.id
            expiring_vals['eligible_review_date'] = immigration_line.eligible_review_date
            expiring_vals['doc_type_id'] = immigration_line.doc_type_id.id
            expiring_vals['comments'] = immigration_line.comments
            expiring_vals['immigration_id'] = immigration_line.id
            expiring_vals['expiry_attachment'] = immigration_line.attach_document
            self.create(expiring_vals)
        return True

expiry_document()

class employee_immigration(models.Model):
    _inherit = 'employee.immigration'

    @api.multi
    def write(self,vals):
        for record in self:
            if vals.get('exp_date'):
                expiring_ids = self.env['expiring.document'].search([('exp_date','=',str(record.exp_date))])
                for expiring_id in expiring_ids:
                    if expiring_id.exp_date != vals.get('exp_date') and expiring_id.immigration_id.id == record.id:
                        expiring_id.unlink()
        return super(employee_immigration, self).write(vals)

employee_immigration()