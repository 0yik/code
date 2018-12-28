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
    'department_id':'',
    'total_employees' : 'Total Employees: ',
}
ADDITION = {
    'work_phone': "Phone: %s",
    'mobile_phone': "Mobile: %s"
}


class Main(Website):

    @http.route(['/hr_employee/get_full_org_chart_branch'], type='http', auth="public", website=True)
    def get_full_org_chart_branch(self):

        Model = request.env['res.branch'].sudo()
        branch = Model.search([])
        data_source = self.get_chart_data_bh(branch)
        data = {'dataSource': data_source}
        return json.dumps(data)

    @http.route(['/hr_employee/get_full_org_chart_deptment'], type='http', auth="public", website=True)
    def get_full_org_chart_deptment(self):

        Model = request.env['hr.department'].sudo()
        departments = Model.search([])
        context = request.env.context.copy()
        context.update({'department':True})
        request.env.context = context
        data_source = self.get_chart_data_sc(departments)
        
        data = {'dataSource': data_source}
        return json.dumps(data)

    def get_chart_data_bh(self, branch_ids):
        baseUri = '/web/image/' + 'hr.employee/'
        res = []
        max_id = max(branch_ids.ids)
        max_number = max_id

        Model = request.env['hr.employee'].sudo()
        emp_ids = Model.search([])

        for branch in branch_ids:
            employee_dict = OrderedDict()
            for field in ["id","name"]:
                field_value = getattr(branch, field, None)
                field_value = field in ADDITION and field_value and (ADDITION[field] % field_value) or field_value
                employee_dict[field] = field_value
                res.append(employee_dict)
        for branch in branch_ids:
            for emp in emp_ids:
                emp_dict = OrderedDict()
                if emp.user_id.branch_id.id == branch.id:
                    for field1 in ['id', 'child_id','name','work_email', 'work_phone', 'mobile_phone']:
                        field1_value = None
                        if field1 in ["id"]:
                            field1_value = max_number + 1
                            max_number = field1_value
                        elif field1 == "child_id":
                            field1_value = branch and branch.id or None
                        elif field1 == "name":
                            field1_value = emp and emp.name or None
                        else:
                            field1_value = getattr(emp, field1, None)
                        field1_value = field1 in ADDITION and field1_value and (ADDITION[field1] % field1_value) or field1_value
                        emp_dict[field1] = field1_value
                    emp_dict['image'] = baseUri + str(emp.id) + '/image'
                    res.append(emp_dict)
        return res

    def get_chart_data_sc(self, department_ids):
        baseUri = '/web/image/' + 'hr.employee/'
        res = []
        Model = request.env['hr.employee'].sudo()
        emp_ids = Model.search([])
        max_id = max(department_ids.ids)
        max_number = max_id
        for department in department_ids:
            department_dict = OrderedDict()
            for field in FIELDS:
                field_value = None
                if field == "parent_id":
                    field_value =  None
                elif field.endswith("id") and field != 'id':
                    field_value = getattr(department, field, None)
                    field_value = field_value and field_value.name or ''
                    if field  == 'manager_id' and field_value:
                        field_value = DEPT_MATCH[field] + str(field_value)
                elif field in ["no_of_employee","no_of_recruitment","expected_employees","no_of_hired_employee"]:
                    field_value = getattr(department, field, None)
                    if field_value:
                        field_value = JOB_MATCH[field] + ": " + str(field_value)
                elif field in ['manager_id', "total_employees",]:
                    field_value = getattr(department, field, None)
                    if field_value:
                        field_value = DEPT_MATCH[field]  + str(field_value)
                else:
                    field_value = getattr(department, field, None)
                field_value = field in ADDITION and field_value and (ADDITION[field] % field_value) or field_value
                department_dict[field] = field_value
                res.append(department_dict)
        for department in department_ids:
            for emp in emp_ids:
                emp_dict = OrderedDict()
                if emp.department_id.id == department.id:
                    for field in ['id', 'child_id','name','work_email', 'work_phone', 'mobile_phone']:
                        field_value = None
                        if field in ["id"]:
                            field_value = max_number + 1
                            max_number = field_value
                        elif field == "child_id":
                            field_value = department and department.id or None
                        elif field == "name":
                            field_value = emp and emp.name or None
                        else:
                            field_value = getattr(emp, field, None)
                        field_value = field in ADDITION and field_value and (
                            ADDITION[field] % field_value) or field_value
                        emp_dict[field] = field_value
                    emp_dict['image'] = baseUri + str(emp.id) + '/image'
                    res.append(emp_dict)
        return res
