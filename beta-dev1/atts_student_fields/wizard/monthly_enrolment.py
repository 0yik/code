# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class MonthlyEnrolmentWizard(models.TransientModel):
    _name = "monthly.enrolment.wizard"

    date_selection = fields.Date('Select Date', required='True')

    @api.multi
    def _print_report(self, data):
        return self.env['report'].get_action(self, 'atts_student_fields.report_studentdetail', data=data)
   
   
    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['date_selection'] = self.date_selection
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_selection'])[0]
        return self._print_report(data)

class NationalityEnrolmentWizard(models.TransientModel):
    _name = "nationality.enrolment.wizard"

    date_selection = fields.Date('Select Date')

    @api.multi
    def _print_report(self, data):
        return self.env['report'].get_action(self, 'atts_student_fields.report_student_nationality_enrolment', data=data)
   
   
    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['date_selection'] = self.date_selection
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_selection'])[0]
        return self._print_report(data)
    
    
class religionEnrolmentWizard(models.TransientModel):
    _name = "religion.enrolment.wizard"

    @api.multi
    def _print_report(self, data):
        return self.env['report'].get_action(self, 'atts_student_fields.report_student_religion_enrolment', data=data)
   
   
    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        return self._print_report(data)
    
class raceEnrolmentWizard(models.TransientModel):
    _name = "race.enrolment.wizard"

    @api.multi
    def _print_report(self, data):
        return self.env['report'].get_action(self, 'atts_student_fields.report_student_race_enrolment', data=data)
   
   
    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        return self._print_report(data)
    
class MonthlyWithdrawlWizard(models.TransientModel):
    _name = "monthly.withdrawl.wizard"
    
    date_selection = fields.Date('Select Date', required=True)

    @api.multi
    def _print_report(self, data):
        return self.env['report'].get_action(self, 'atts_student_fields.report_monthly_withdrawl', data=data)
   
   
    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['date_selection'] = self.date_selection
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_selection'])[0]
        return self._print_report(data)

