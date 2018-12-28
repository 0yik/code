# -*- encoding: utf-8 -*-
from odoo import models, fields, api, tools
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import time

class AisApiSchedule(models.TransientModel):
    _name = 'ais.api.schedule'
    _description = 'AIS API Schedule'

    @api.multi
    def _get_payroll_user_name(self):
        supervisors_list = []
        data_obj = self.env['ir.model.data']
        result_data = data_obj._get_id('l10n_sg_hr_payroll', 'group_hr_payroll_admin')
        model_data = data_obj.browse(result_data)
        group_data = self.env['res.groups'].browse(model_data.res_id)
        for user in group_data.users:
            supervisors_list.append((tools.ustr(user.id), tools.ustr(user.name)))
        return supervisors_list

    form_type = fields.Selection([('ir8a', 'IR8A'), ('ir8s', 'IR8S'), ('appendix8a', 'APPENDIX8A')], default='ir8a', required=True, string='Form Type')
    next_schedule_date = fields.Date(string='Next Schedule Date', required=True)
    start_date = fields.Date('Start Date', required=True, default=lambda *a: time.strftime('%Y-01-01'))
    end_date = fields.Date('End Date', required=True, default=lambda *a: time.strftime('%Y-12-31'))
    source = fields.Selection(selection=[
        ('1', 'Mindef'),
        ('4', 'Government Department'),
        ('5', 'Statutory Board'),
        ('6', 'Private Sector'),
        ('9', 'Others')], string='Source', default='6', required=True)
    organization_id_type = fields.Selection(selection=[
        ('7', 'UEN – Business Registration number issued by ACRA'),
        ('8', 'UEN – Local Company Registration number issued by ACRA'),
        ('A', 'ASGD – Tax Reference number assigned by IRAS'),
        ('I', 'ITR – Income Tax Reference number assigned by IRAS'),
        ('U', 'UENO – Unique Entity Number Others')], string='Organization ID Type', default='8', required=True)
    organization_id_no = fields.Char('Organization ID No', size=16, required=True)
    batch_indicatior = fields.Selection(selection=[
        ('O', 'Original'),
        ('A', 'Amendment')], string='Batch Indicator', required=True)
    batch_date = fields.Date('Batch Date', required=True, default=fields.Date.today)
    payroll_user = fields.Selection(_get_payroll_user_name, string='Authorised Person', size=128, required=True)
    user_id = fields.Char(string='User ID', required=True)
    user_id_type = fields.Selection([('1', 'NRIC'), ('2', 'FIN'), ('4', 'WP'), ('A', 'ASGD'), ('11', 'MIC')], default='1', required=True, string='User ID Type')
    employee_ids = fields.Many2many('hr.employee', required=True, string='Employees')
    company_id = fields.Many2one('res.company', 'Company', required=True)

    @api.onchange('payroll_user')
    def onchange_payroll_user(self):
        if self.payroll_user:
            try:
                employee_id = self.env['hr.employee'].search([('user_id', '=', int(self.payroll_user))], limit=1)
                if employee_id:
                    self.user_id = employee_id.identification_id
                    if employee_id.identification_no in ['1', '2', '4']:
                        self.user_id_type = employee_id.identification_no
                    elif employee_id.identification_no == '5':
                        self.user_id_type = '11'
                    else:
                        self.user_id_type = False
            except:
                pass

    @api.onchange('batch_date')
    def onchange_batch_date(self):
        today = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        if self.batch_date > today:
            self.batch_date = False
            return {
                'warning': {
                    'title': 'Warning',
                    'message': 'You are not allow to Select Future Date !'
                }
            }

    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.company_id:
            self.organization_id_no = self.company_id.company_registry

    def action_set(self):
        vals = {}
        vals['ais_api_id'] = self._context.get('active_id')
        vals['form_type'] = self.form_type
        vals['next_schedule_date'] = self.next_schedule_date
        vals['start_date'] = self.start_date
        vals['end_date'] = self.end_date
        vals['submission_date'] = fields.datetime.now()
        vals['source'] = self.source
        vals['organization_id_type'] = self.organization_id_type
        vals['organization_id_no'] = self.organization_id_no
        vals['batch_indicatior'] = self.batch_indicatior
        vals['batch_date'] = self.batch_date
        vals['payroll_user'] = self.payroll_user
        vals['company_id'] = self.company_id.id
        vals['user_id'] = self.user_id
        vals['user_id_type'] = self.user_id_type
        vals['employee_ids'] = [(6, 0, self.employee_ids.ids)]
        self.env['ais.api.history'].create(vals)
        return True

AisApiSchedule()