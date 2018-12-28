# -*- coding: utf-8 -*-
{
    "name": "Indonesia Expense Payroll",
    "version": "1.1",
    "depends": ['indo_hr_payroll'],
    "author" :"Hashmicro/Kannan",
    "website" : "www.hashmicro.com",
    "category": "Human Resources",
    "description": """
Expense auto calculation.
============================
    This modules will help for expenses auto calculation""",

    'data': [
             'security/ir.model.access.csv',
             'data/salary_rule.xml',
             ],

    'installable': True,
    'auto_install':False,
    'application':True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
