# -*- encoding: utf-8 -*-
{
    "name": "Indonesia Payroll Account",
    "version": "1.0",
    "depends": ['l10n_id', 'sg_payroll_account'],
    "author" :"Hashmicro/Kannan",
    "website" : "www.hashmicro.com",
    "category": "Human Resources",
    "description":"""
Indonesia Accounting payroll data
============================
    - This module will assign account in each salary rules to make payroll accounting entries.
    """,
    "data": [
       "data/salary_rule.xml"
    ],
    "installable": True,
    "auto_install":False,
    "application":True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
