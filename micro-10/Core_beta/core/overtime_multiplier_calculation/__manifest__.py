# -*- coding: utf-8 -*-
{
    "name": "Overtime Multiplier Calculation",
    "author": "HashMicro/ Mustufa Kantawala",
    "version": "10.0.1.0",
    "website": "www.hashmicro.com",
    "category": "",
    "depends": ["overtime_rounding"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/allocate_overtime_multiplier.xml",
        "views/overtime_multiplier.xml",
        "views/overtime_multiplier_employee.xml",
    ],
    'description':'''
    The purpose of this module is to allow user to create a multiplier.
    ''',
    'demo': [],
    "installable": True,
    "auto_install": False,
    "application": True,
}