# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Indonesia's Taxform",
    "version": "8.0.1.0.0",
    "category": "localization",
    "website": "https://hashmicro.com",
    "author": "Hashmicro / MpTechnolabs - Parikshit Vaghasiya",
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "depends": [
        "base","mail","account","hr_payroll",'hr_contract',"base_amount_to_text",
    ],
    "data": [
        "security/taxform_groups.xml",
        "security/ir.model.access.csv",
        "data/data_decimal_precision.xml", 
        "data/l10n_id_bukti_potong_type.xml",
        "data/ptkp_category_data.xml",
        "data/hr_salary_rule_category_data.xml",
        "data/hr_salary_rule_data.xml",
        "views/menu.xml",
        "views/l10n_id_taxform_bukti_potong_pph_type_views.xml",
        "views/bukti_potong_pph_views.xml",
        "views/bukti_potong_pph_f113301_out_views.xml",
        "views/hr_employee_views.xml",
        "views/tax_period_views.xml",
        "views/ptkp_views.xml",
        "views/pph_21_biaya_jabatan_views.xml",
        "views/pph_21_npwp_rate_modifier_views.xml",
        "views/pph_21_rate_views.xml",
        "views/res_partner_views.xml",
        "views/hr_payslip_views.xml",
    ],
    "demo": [
        "demo/pph_21_biaya_jabatan_demo.xml",
        "demo/pph_21_npwp_rate_modifier_demo.xml",
        "demo/pph_21_rate_demo.xml",
        "demo/ptkp_demo.xml",
        "demo/tax_period_demo.xml",
    ]
}
