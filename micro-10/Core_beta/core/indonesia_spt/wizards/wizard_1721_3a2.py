from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError

class wizard_1721_3a2_report(models.TransientModel):
    _name = 'wizard.1721.3a2.report'

    employee_ids = fields.Many2many('hr.employee', string='Employees')
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    @api.multi
    def print_report(self):
        emp_dict = []
        if not self.employee_ids:
            raise ValidationError(_('Please select employee.'))

        if self.start_date > self.end_date:
            raise ValidationError(_("You must be enter start date less than end date !"))

        sequence = 1
        for one_emp in self.employee_ids:
            emp_country = ''
            if not one_emp.singaporean:
                emp_country = one_emp.country_id and one_emp.country_id.name or ''

            contract_ids = self.env['hr.contract'].search(
                [('employee_id', '=', one_emp.id), ('date_start', '<=', self.start_date),
                 '|', ('date_end', '>=', self.start_date), ('date_end', '=', None)
                 ], limit=1, order='id desc')
            contract_start_month = ''
            contract_end_month = ''
            basic_salary = 0
            if contract_ids:
                basic_salary = contract_ids.wage
                strat_datee = datetime.strptime(contract_ids.date_start, "%Y-%m-%d")
                contract_start_month = str('{:02d}'.format(strat_datee.month))
                if contract_ids.date_end:
                    end_datee = datetime.strptime(contract_ids.date_end, "%Y-%m-%d")
                    contract_end_month = str('{:02d}'.format(end_datee.month))

            last_display_date = '31/12/' + str(datetime.strptime(self.end_date, "%Y-%m-%d").year)
            ptkp_status = 'K/_____TK/_____HB/_____'
            if one_emp.ptkp_status and one_emp.ptkp_status.name:
                ptkp_status_split = one_emp.ptkp_status.name.split('/')
                if ptkp_status_split and len(ptkp_status_split) == 2 and str(ptkp_status_split[0]) == 'k':
                    ptkp_status = 'K/__' + str(ptkp_status_split[1]) + '__TK/_____HB/_____'
                if ptkp_status_split and len(ptkp_status_split) == 2 and str(ptkp_status_split[0]) == 'TK':
                    ptkp_status = 'K/_____TK/__' + str(ptkp_status_split[1]) + '__HB/_____'
                if ptkp_status_split and len(ptkp_status_split) == 2 and str(ptkp_status_split[0]) == 'HB':
                    ptkp_status = 'K/_____TK/_____HB/__' + str(ptkp_status_split[1]) + '__'
            emp_dict.append({
                'print_current_month': str('{:02d}'.format(datetime.now().date().month)),
                'print_sequence': str('{:07d}'.format(sequence)),
                'print_current_year': str(datetime.now().year)[-2:],
                'company_npwp': one_emp.company_id and one_emp.company_id.company_npwp or '',
                'company_name': one_emp.company_id and one_emp.company_id.name or '',
                'emp_name': one_emp.name or '',
                'emp_tax_calculation_method': one_emp.tax_calculation_method or False,
                'emp_address': one_emp.address or '',
                'emp_npwp_number': one_emp.npwp_number or '',
                'emp_identification_id': one_emp.identification_id or one_emp.passport_id or '',
                # 'emp_ptkp_status': one_emp.ptkp_status and one_emp.ptkp_status.name or 'K/_____TK/_____HB/_____',
                'emp_ptkp_status': ptkp_status,
                'emp_job': one_emp.job_id and one_emp.job_id.name or '',
                'emp_indonatian': one_emp.singaporean,
                'emp_gender': one_emp.gender,
                'emp_country': emp_country,
                'emp_contract_start_month': contract_start_month,
                'emp_contract_end_month': contract_end_month,
                'emp_contract_basic_salary': basic_salary,
                'company_taxcutter_name': one_emp.company_id and one_emp.company_id.taxcutter_name or '',
                'company_taxcutter_npwp': one_emp.company_id and one_emp.company_id.taxcutter_npwp or '',
                'last_display_date': last_display_date,
            })
            sequence = sequence + 1
        datas = {
            'start_date': self.start_date,
            'emp_ids': self.employee_ids.ids,
            'emp_dict': emp_dict,
        }
        print "--------datas--------",datas
        return self.env['report'].get_action(self, 'indonesia_spt.report_1721_3a2',data=datas)
