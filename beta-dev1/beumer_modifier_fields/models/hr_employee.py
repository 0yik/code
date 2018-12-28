from odoo import fields, models, api, exceptions

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    known_as        = fields.Char('Known As')
    employee_id     = fields.Char('Employee ID')
    service_date    = fields.Date('Service Date')
    cessation_date  = fields.Date('Cessation Date')
    cessation_reason= fields.Many2one('cessation.reason','cessation_reason')
    division        = fields.Many2one('division','division')
    job_family      = fields.Many2one('job.family','job_family')
    expiry_date     = fields.Date('MSOC Expiry Date')
    bank_name       = fields.Many2one('res.bank','name')
    bank_code       = fields.Many2one('res.bank','bic')
    branch_code     = fields.Many2one('res.partner.bank','sequence')
    child_detail_ids= fields.One2many('child.detail','user_id')
    remark_ids      = fields.One2many('remark','user_id')
    other_input_ids = fields.One2many('other.input','user_id')
    employee_race_id = fields.Many2one('hr.employee.race')
    employee_religion_id = fields.Many2one('hr.employee.religion')
    employee_qualification_id = fields.Many2one('hr.employee.qualification')

class other_input(models.Model):
    _name= 'other.input'

    user_id     = fields.Many2one('hr.employee')
    salary_name = fields.Many2one('hr.salary.rule','Salary Name')
    salary_code = fields.Char('Salary Code',readonly=True)
    start_date  = fields.Date('Start Date')
    end_date    = fields.Date('End Date')
    amount      = fields.Integer('Amount')
    salary_code_sub = fields.Char()

    @api.onchange('salary_name')
    def update_salary_code(self):
        if self.salary_name:
            self.salary_code = self.salary_name.code
            self.salary_code_sub = self.salary_name.code

    @api.model
    def create(self,vals):
        if 'salary_code_sub' in vals:
            vals.update({'salary_code':vals['salary_code_sub']})
        res = super(other_input, self).create(vals)
        return res

    @api.model
    def write(self,vals):
        if 'salary_code_sub' in vals:
            vals.update({'salary_code':vals['salary_code_sub']})
        res = super(other_input, self).write(vals)
        return res

class remark(models.Model):
    _name='remark'

    user_id = fields.Many2one('hr.employee')
    remark  = fields.Text('Remark')
    date    = fields.Date('Date')

class child_detail(models.Model):
    _name = 'child.detail'

    user_id = fields.Many2one('hr.employee')
    child_full_name = fields.Char('Child Full Name')
    child_nationality = fields.Many2one('res.country')
    child_birth_cert_no = fields.Char('Birth Cert No')
    child_date_of_birth = fields.Date('Date of Birth')
    child_place_of_birth = fields.Char('Place of Birth')
    child_detail    = fields.Many2one('hr.employee')
class cessation_reason(models.Model):
    _name=  'cessation.reason'

    cessation_reason = fields.Char('Cessation Reason')

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            if record.cessation_reason:
                res.append((record.id, str(record.cessation_reason)))
        return res

class division(models.Model):
    _name=  'division'

    division = fields.Char('Division')

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            if record.division:
                res.append((record.id, str(record.division)))
        return res

class job_family(models.Model):
    _name=  'job.family'

    job_family = fields.Char('Job Family')

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            if record.job_family:
                res.append((record.id, str(record.job_family)))
        return res