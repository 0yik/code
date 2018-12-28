# -*- coding: utf-8 -*-

import json

from collections import OrderedDict
from openerp import http  # @UnresolvedImport
from openerp.addons.website.controllers.main import Website
from openerp.http import request  # @UnresolvedImport

FIELDS = ['id', 'parent_id', 'name', 'job_id', 'work_location',
          'work_email', 'work_phone', 'mobile_phone','department_id', 'manager_id', "total_employees", "no_of_employee","no_of_recruitment","expected_employees","no_of_hired_employee"]
JOB_MATCH={
    'no_of_employee' : 'Existing',
    'no_of_recruitment' : 'Recruiting',
    'expected_employees' : 'Forecasted',
    'no_of_hired_employee' : 'Recruited',
}

DEPT_MATCH={
    'manager_id' : 'Manager: ',
    'total_employees' : 'Total Employees: ',
}
ADDITION = {
    'work_phone': "Phone: %s",
    'mobile_phone': "Mobile: %s"
}


class Main(Website):
    @http.route(['/hr_employee/get_full_org_chart_employee'],
                type='http', auth="public", website=True)
    def get_full_org_chart_emloyee(self):

        Model = request.env['hr.employee'].sudo()
        employee_ids = Model.search([])
        data_source = self.get_chart_data_source(employee_ids)

        data = {'dataSource': data_source,
                }

        return json.dumps(data)

    @http.route(['/hr_employee/get_full_org_chart_dept'],
                type='http', auth="public", website=True)
    def get_full_org_chart_dept(self):

        Model = request.env['hr.department'].sudo()
        departments = Model.search([])
        data_source = self.get_chart_data_source(departments)

        data = {'dataSource': data_source,
                }

        return json.dumps(data)

    @http.route(['/hr_employee/get_full_org_chart_job'],
                type='http', auth="public", website=True)
    def get_full_org_chart_job(self):

        Model = request.env['hr.job'].sudo()
        jobs = Model.search([])
        data_source = self.get_chart_data_source(jobs)

        data = {'dataSource': data_source,
                }

        return json.dumps(data)
    @http.route(['/hr_employee/get_org_chart/<int:employee_id>'],
                type='http', auth="public", website=True)
    def get_org_chart(self, employee_id=0):

        Model = request.env['hr.employee'].sudo()
        employee_ids = Model.browse(employee_id)
        manager = employee_ids.parent_id
        employee_ids |= manager
        employee_ids |= Model.search([('parent_id', 'child_of', employee_id)])
        data_source = self.get_chart_data_source(employee_ids)

        data = {'dataSource': data_source,
                'customize': {manager.id: {"color": "darkred"},
                              employee_id: {"color": "teal"}},
                'expandToLevel': manager and 3 or 2
                }

        return json.dumps(data)

    def get_chart_data_source(self, employee_ids):
        baseUri = '/web/image/' + 'hr.employee/'
        res = []
        for employee in employee_ids:
            employee_dict = OrderedDict()
            for field in FIELDS:
                field_value = None
                if field == "parent_id":
                    field_value = getattr(employee, field, None)
                    field_value = field_value and field_value.id or None
                elif field.endswith("id") and field != 'id':
                    field_value = getattr(employee, field, None)
                    field_value = field_value and field_value.name or ''
                    if field  == 'manager_id' and field_value:
                        field_value = DEPT_MATCH[field] + str(field_value)
                elif field in ["no_of_employee","no_of_recruitment","expected_employees","no_of_hired_employee"]:
                    field_value = getattr(employee, field, None)
                    if field_value:
                        field_value = JOB_MATCH[field] + ": " + str(field_value)
                elif field in ['manager_id', "total_employees",]:
                    field_value = getattr(employee, field, None)
                    if field_value:
                        field_value = DEPT_MATCH[field]  + str(field_value)
                else:
                    field_value = getattr(employee, field, None)
                field_value = field in ADDITION and field_value and (
                    ADDITION[field] % field_value) or field_value
                employee_dict[field] = field_value
            employee_dict['image'] = baseUri + str(employee.id) + '/image'
            res.append(employee_dict)
        return res
