# -*- coding: utf-8 -*-
import json
import logging
import re

from operator import attrgetter, add
from lxml import etree

from odoo import api, models, fields, registry, SUPERUSER_ID, _
from odoo.exceptions import AccessError, RedirectWarning, UserError
from odoo.tools import ustr

_logger = logging.getLogger(__name__)

class ModuleBoardConfig(models.TransientModel):
    _name = 'module.board.config'
    _inherit = 'res.config.settings'

    module_stock_barcode = fields.Boolean('Allow barcode scanning in Warehouse (stock_barcode)')
    module_simple_stock2 = fields.Boolean('Simple stock scanning, stock in and stock out using barcode (simple_stock2)')
    module_quotation_opportunities = fields.Boolean('Allow users to create quotations for opportunities, located in opportunties form view (quotation_opportunities)')
    module_crm_phonecall = fields.Boolean('Track and schedule calls with customers, leads & opportunities (crm_phonecall)')
    module_crm_profiling = fields.Boolean('Manage profiling of each customer through a seres of questionnaires (crm_profiling)')
    module_dusal_sale = fields.Boolean('Show images in quotation & sales order form view (dusal_sale, dusal_web_tree_image)')
    module_dusal_web_tree_image = fields.Boolean('Show images in quotation & sales order form view (dusal_web_tree_image)')
    module_auto_stock_refund = fields.Boolean('Allow invoice refunds upon delivery returns (auto_stock_refund)')
    module_barcodes_generator_abstract = fields.Boolean('Generate UPC / EAN Barcodes for every product created, simply go to Settings > Technical > Sequence > Barcode Nomenclatures to set the barcode rules, and then go to products, set the barcode rule and barcode base, then generate barcodes (barcodes_generator_abstract, barcodes_generator_product)')
    module_barcodes_generator_product = fields.Boolean('Generate UPC / EAN Barcodes for every product created, simply go to Settings > Technical > Sequence > Barcode Nomenclatures to set the barcode rules, and then go to products, set the barcode rule and barcode base, then generate barcodes (barcodes_generator_abstract, barcodes_generator_product)')
    module_account_balance_reporting = fields.Boolean('Create PDF report comparing accounting codes between certain periods of time / Fiscal Year Go to Invoicing > Reports > Financial Reports, create the template and Print (account_balance_reporting)')
    module_account_followup = fields.Boolean('Manage payment follow ups & set payment reminders, in Accounting / Invoicing > Payment Follow Ups (account_followup)')
    module_currency_rate_update = fields.Boolean('Synchronize rate currency updates with Statutory boards like MAS (currency_rate_update)')
    module_accounting_auditor = fields.Boolean('Create an Auditor type access which only has access to read-only Accounting which will show in user form view (accounting_auditor)')
    module_budget_management_extension = fields.Boolean('Manage budgets per group of products in Accounting > Configuration > Analytic Accounts Form View (budget_management_extension)')
    module_bom_components_image = fields.Boolean('Show images in Bill of Material Components form view (bom_components_image)')
    module_board_frontdesk = fields.Boolean('Frontdesk Dashboard with view of room resevation, restaurants, etc (board_frontdesk)')
    module_cab_booking_management = fields.Boolean('Cab booking, cab logs, with notifications & activity tracker (cab_booking_management)')
    module_auditlog = fields.Boolean('Allow generation of audit log trails per object per user (auditlog)')
    module_company_bank_details = fields.Boolean('Manage multiple bank details for each customer & supplier (company_bank_details)')
    module_access_rights_group = fields.Boolean('Use only one group for all the access rights instead of one group per module (access_rights_group)')
    module_sale = fields.Boolean('Base Sales Module (sale)')
    module_sale_discount_total = fields.Boolean('Manage discount on the total sales order rather than per line (sale_discount_total)')
    module_sale_order_revision = fields.Boolean('Manage versions of quotations (sale_order_revision)')
    module_sale_subscription = fields.Boolean('Manage recurring sales orders (sale_subscription)')
    module_sale_sourced_by_line = fields.Boolean('Set so multiple warehouse can be set per quotation line (sale_sourced_by_line)')
    module_pipeline_activity_history = fields.Boolean('Show the activity history for each opportuntty ( pipeline_activity_history)')
    module_pipeline_won = fields.Boolean('Allow pipeline to convert to customer once won (pipeline_won)')
    module_crm = fields.Boolean('Base CRM module - Leads Management (crm)')
    module_partner_credit_limit = fields.Boolean('Manage customer credit limit, where you can set their credit and no further sales order can be done if it is over the credit (partner_credit_limit)')
    module_helpdesk = fields.Boolean('Manage incoming emails as tickets for helpdesk teams, manage SLA, and generate reports (helpdesk,helpdesk_extension)')
    module_helpdesk_extension = fields.Boolean('Manage incoming emails as tickets for helpdesk teams, manage SLA, and generate reports (helpdesk,helpdesk_extension)')
    module_helpdesk_email_routing = fields.Boolean('Manage email routing based on sender and email subject (helpdesk_email_routing)')
    module_helpdesk_default_access = fields.Boolean('Use sample helpdesk default access (helpdesk_default_access)')
    module_website_helpdesk_livechat = fields.Boolean('Allow live chat embedding and live chat to ticket conversion (website_helpdesk_livechat,livechat_ext)')
    module_livechat_ext = fields.Boolean('Allow live chat embedding and live chat to ticket conversion (website_helpdesk_livechat,livechat_ext)')
    module_so_analytic = fields.Boolean('Set Up Analytic in SO (so_analytic)')
    module_purchase = fields.Boolean('Base purchase Module (purchase)')
    module_purchase_request = fields.Boolean('Manage purchase requests (purchase_request)')
    module_purchase_request_procurement = fields.Boolean('Manage purchase requests (purchase_request_procurement)')
    module_purchase_request_to_requisition = fields.Boolean('Manage purchase requests (purchase_request, purchase_request_procurement, purchase_request_to_requisition, purchase_request_to_rfq, purchase_requisition)')
    module_purchase_request_to_rfq = fields.Boolean('Manage purchase requests (purchase_request_to_rfq)')
    module_purchase_requisition = fields.Boolean('Manage purchase requests (purchase_requisition)')
    module_stock = fields.Boolean('Base Inventory module (stock)')
    module_mrp_repair = fields.Boolean('Manage product repairs (mrp_repair)')
    module_barcodes = fields.Boolean('Manage barcode scannings (barcodes)')
    module_inventory_age_report = fields.Boolean('Generate inventory aging report in Reporting (inventory_age_report)')
    module_quality_control = fields.Boolean('Manage quality controls for incoming products (quality_control)')
    module_quality_control_hr = fields.Boolean('Manage quality controls for incoming products (quality_control,quality_control_hr)')
    module_account = fields.Boolean('Base Invoicing Module (account)')
    module_account_accountant = fields.Boolean('Base Accounting Module (account_accountant)')
    module_payment_receipt_invoice = fields.Boolean('Generate payment receipts for customer payments (payment_receipt_invoice)')
    module_payment_tab_invoices = fields.Boolean('Show the payment tab in invoices (payment_tab_invoices)')
    module_currecny_rate_update = fields.Boolean('Synchronize rate currency updates with Statutory boards like MAS (currency_rate_update)')
    module_sg_se_currency = fields.Boolean('Set Up Singapore Currencies (sg_se_currency)')
    module_my_account_analytic_analysis = fields.Boolean('Manage contracts, forecasts, recurinng invoices (my_account_analytic_analysis)')
    module_account_asset = fields.Boolean('Manage assets, value & deprevisation (account_asset)')
    module_sg_accomodation = fields.Boolean('Manage Accomodations (sg_accomodation)')
    module_sg_account_config = fields.Boolean('Set Up Accounting Reports & Config (sg_account_config,sg_account_report, sg_cashflow_report)')
    module_sg_account_report = fields.Boolean('Set Up Accounting Reports & Config (sg_account_config,sg_account_report, sg_cashflow_report)')
    module_sg_cashflow_report = fields.Boolean('Set Up Accounting Reports & Config (sg_account_config,sg_account_report, sg_cashflow_report)')
    module_sg_bank_reconcile = fields.Boolean('Bank Reconciliation (Sg_bank_reconcile)')
    module_report_xlsx = fields.Boolean('Generate reports in excel (report_xlsx)')
    module_hr = fields.Boolean('Base HR module(hr)')
    module_user_creation_from_employee = fields.Boolean('Auto create user from employee (user_creation_from_employee)')
    module_hr_dashboard = fields.Boolean('Generate your own custom HR dashboard (hr_dashboard)')
    module_hr_payslip_monthly_report = fields.Boolean('Generate monthly payslip report in Reporting (hr_payslip_monthly_report)')
    module_hr_leave_balance = fields.Boolean('View the leave balance for each leave type per employee in employee form view (hr_leave_balance)')
    module_sg_allocate_leave = fields.Boolean('Easy leave allocations (sg_allocate_leave)')
    module_urgent_leave_function = fields.Boolean('Set Up urgent leaves (urgent_leave_function)')
    module_leave_manager_approval = fields.Boolean('Set Up multiple manager approval (leave_manager_approval)')
    module_sg_expense_maxcap = fields.Boolean('Manage expenses cap (sg_expense_maxcap)')
    module_sg_expense_payroll = fields.Boolean('Expenses to go to payroll (sg_expense_payroll)')
    module_hr_timesheet = fields.Boolean('Base Timesheet module (hr_timesheet)')
    module_sg_appendix8a_report = fields.Boolean('Singapore HR Reports (sg_appendix8a_report, sg_cimb_report,sg_cpf_extended, sg_dbs_giro, sg_document_expiry, sg_income_tax_report, sg_ir21, sg_hr_report, sg_ocbc_report, sg_report_letter_undertaking)')
    module_sg_cimb_report = fields.Boolean('Singapore HR Reports (sg_appendix8a_report, sg_cimb_report,sg_cpf_extended, sg_dbs_giro, sg_document_expiry, sg_income_tax_report, sg_ir21, sg_hr_report, sg_ocbc_report, sg_report_letter_undertaking)')
    module_sg_cpf_extended = fields.Boolean('Singapore HR Reports (sg_appendix8a_report, sg_cimb_report,sg_cpf_extended, sg_dbs_giro, sg_document_expiry, sg_income_tax_report, sg_ir21, sg_hr_report, sg_ocbc_report, sg_report_letter_undertaking)')
    module_sg_dbs_giro = fields.Boolean('Singapore HR Reports (sg_appendix8a_report, sg_cimb_report,sg_cpf_extended, sg_dbs_giro, sg_document_expiry, sg_income_tax_report, sg_ir21, sg_hr_report, sg_ocbc_report, sg_report_letter_undertaking)')
    module_sg_document_expiry = fields.Boolean('Singapore HR Reports (sg_appendix8a_report, sg_cimb_report,sg_cpf_extended, sg_dbs_giro, sg_document_expiry, sg_income_tax_report, sg_ir21, sg_hr_report, sg_ocbc_report, sg_report_letter_undertaking)')
    module_sg_income_tax_report = fields.Boolean('Singapore HR Reports (sg_appendix8a_report, sg_cimb_report,sg_cpf_extended, sg_dbs_giro, sg_document_expiry, sg_income_tax_report, sg_ir21, sg_hr_report, sg_ocbc_report, sg_report_letter_undertaking)')
    module_sg_ir21 = fields.Boolean('Singapore HR Reports (sg_appendix8a_report, sg_cimb_report,sg_cpf_extended, sg_dbs_giro, sg_document_expiry, sg_income_tax_report, sg_ir21, sg_hr_report, sg_ocbc_report, sg_report_letter_undertaking)')
    module_sg_hr_report = fields.Boolean('Singapore HR Reports (sg_appendix8a_report, sg_cimb_report,sg_cpf_extended, sg_dbs_giro, sg_document_expiry, sg_income_tax_report, sg_ir21, sg_hr_report, sg_ocbc_report, sg_report_letter_undertaking)')
    module_sg_ocbc_report = fields.Boolean('Singapore HR Reports (sg_appendix8a_report, sg_cimb_report,sg_cpf_extended, sg_dbs_giro, sg_document_expiry, sg_income_tax_report, sg_ir21, sg_hr_report, sg_ocbc_report, sg_report_letter_undertaking)')
    module_sg_report_letter_undertaking = fields.Boolean('Singapore HR Reports (sg_appendix8a_report, sg_cimb_report,sg_cpf_extended, sg_dbs_giro, sg_document_expiry, sg_income_tax_report, sg_ir21, sg_hr_report, sg_ocbc_report, sg_report_letter_undertaking)')
    module_sg_expire_leave = fields.Boolean('SG Leave Setup (sg_expire_leave, sg_hr_holiday, sg_leave_constraints, sg_leave_extended)')
    module_sg_hr_holiday = fields.Boolean('SG Leave Setup (sg_expire_leave, sg_hr_holiday, sg_leave_constraints, sg_leave_extended)')
    module_sg_leave_constraints = fields.Boolean('SG Leave Setup (sg_expire_leave, sg_hr_holiday, sg_leave_constraints, sg_leave_extended)')
    module_sg_leave_extended = fields.Boolean('SG Leave Setup (sg_expire_leave, sg_hr_holiday, sg_leave_constraints, sg_leave_extended)')
    module_sg_hr_config = fields.Boolean('SG Employee Setup (sg_hr_config, sg_hr_employee, sg_hr_holiday, sg_nric_verification, sg_payroll_account, sg_payroll_constraints, hm_hr_sg_standardization)')
    module_sg_hr_employee = fields.Boolean('SG Employee Setup (sg_hr_config, sg_hr_employee, sg_hr_holiday, sg_nric_verification, sg_payroll_account, sg_payroll_constraints, hm_hr_sg_standardization)')
    module_nric_verification = fields.Boolean('SG Employee Setup (sg_hr_config, sg_hr_employee, sg_hr_holiday, sg_nric_verification, sg_payroll_account, sg_payroll_constraints, hm_hr_sg_standardization)')
    module_sg_payroll_account = fields.Boolean('SG Employee Setup (sg_hr_config, sg_hr_employee, sg_hr_holiday, sg_nric_verification, sg_payroll_account, sg_payroll_constraints, hm_hr_sg_standardization)')
    module_sg_payroll_constraints = fields.Boolean('SG Employee Setup (sg_hr_config, sg_hr_employee, sg_hr_holiday, sg_nric_verification, sg_payroll_account, sg_payroll_constraints, hm_hr_sg_standardization)')
    module_hm_hr_sg_standardization = fields.Boolean('SG Employee Setup (sg_hr_config, sg_hr_employee, sg_hr_holiday, sg_nric_verification, sg_payroll_account, sg_payroll_constraints, hm_hr_sg_standardization)')
    module_mass_mailing = fields.Boolean('Mass Mailing Functionalities with its extensions (mass_mailing, mass_mailing_delimiter, mass_mailing_extension,mail_addin_style, web_editor_fixer)')
    module_mass_mailing_delimiter = fields.Boolean('Mass Mailing Functionalities with its extensions (mass_mailing, mass_mailing_delimiter, mass_mailing_extension,mail_addin_style, web_editor_fixer)')
    module_mass_mailing_extension = fields.Boolean('Mass Mailing Functionalities with its extensions (mass_mailing, mass_mailing_delimiter, mass_mailing_extension,mail_addin_style, web_editor_fixer)')
    module_mail_addin_style = fields.Boolean('Mass Mailing Functionalities with its extensions (mass_mailing, mass_mailing_delimiter, mass_mailing_extension,mail_addin_style, web_editor_fixer)')
    module_web_editor_fixer = fields.Boolean('Mass Mailing Functionalities with its extensions (mass_mailing, mass_mailing_delimiter, mass_mailing_extension,mail_addin_style, web_editor_fixer)')
    module_website_event = fields.Boolean('Manage events (website_event)')
    module_point_of_sale = fields.Boolean('Base POS Module (point_of_sale)')
    module_pos_analytic_by_config = fields.Boolean('Allow setting analytic accounts to each POS (pos_analytic_by_config)')
    module_pos_stock_avail = fields.Boolean('Show the stocks available on the product screen (pos_stock_avail)')
    module_pos_ticket = fields.Boolean('Show the company logo in receipts (pos_ticket)')
    module_muk_dms = fields.Boolean('Manage Documents using GUI (muk_dms,muk_web_preview,muk_web_preview_attachment, muk_web_preview_msoffice)')
    module_muk_web_preview = fields.Boolean('Manage Documents using GUI (muk_dms,muk_web_preview,muk_web_preview_attachment, muk_web_preview_msoffice)')
    module_muk_web_preview_attachment = fields.Boolean('Manage Documents using GUI (muk_dms,muk_web_preview,muk_web_preview_attachment, muk_web_preview_msoffice)')
    module_muk_web_preview_msoffice = fields.Boolean('Manage Documents using GUI (muk_dms,muk_web_preview,muk_web_preview_attachment, muk_web_preview_msoffice)')
    module_project = fields.Boolean('Base project management (project)')
    module_project_forecast = fields.Boolean('Manage project forecasting and ganttchart (project_forecast, project_lifeline)')
    module_project_lifeline = fields.Boolean('Manage project forecasting and ganttchart (project_forecast, project_lifeline)')
    module_project_subtask = fields.Boolean('Manage project subtasks (project_subtask)')
    module_workload_in_project = fields.Boolean('Manage project workload and resources needed (workload_in_project)')
    module_fleet_rental = fields.Boolean('Manage your fleet assets, track fuels, repairs and maintenance (fleet_rental)')
    module_fleet_repair_request_management = fields.Boolean('Manage fleet repair requestss (fleet_repair_request_management)')
    module_muk_theme_nav_transparent = fields.Boolean('Manage transparent navigation bar (muk_theme_nav_transparent)')
    module_website_forum = fields.Boolean('Manage forums (website_forum)')
    module_website_slides = fields.Boolean('Manage slides in website (website_slides)')
    module_website_blog = fields.Boolean('Manage blogs in website (website_blog)')
    module_survey = fields.Boolean('Manage surveys & online quiz (survey)')
    module_website_sale = fields.Boolean('Manage ecommerce (website_sale)')
    module_maintenance = fields.Boolean('Manage assets and equipments (maintenance)')
    module_lunch = fields.Boolean('Manage Lunch meals (lunch)')
    module_hotel = fields.Boolean('Manage your hotel rooms and details (hotel)')
    module_hotel_pos_restaurant = fields.Boolean('Manage your hotel restaurant POS (hotel_pos_restaurant, report_hotel_restaurant)')
    module_report_hotel_restaurant = fields.Boolean('Manage your hotel restaurant POS (hotel_pos_restaurant, report_hotel_restaurant)')
    module_hotel_reservation = fields.Boolean('Manage your hotel reservation & bookings (hotel_reservation,report_hotel_reservation)')
    module_report_hotel_reservation = fields.Boolean('Manage your hotel reservation & bookings (hotel_reservation,report_hotel_reservation)')
    module_car_booking_management = fields.Boolean('Cab booking, cab logs, with notifications & activity tracker (car_booking_management)')
    module_mrp = fields.Boolean('Base Manufacturing Module (mrp)')
    module_gym_management = fields.Boolean('Add exercises, schedules, equipments, ingredients, etc (gym_management)')
    module_insurance_management_cybro = fields.Boolean('Manage insurances, start and expiry, etc (insurance_management_cybro)')
    module_medical = fields.Boolean('Track clinics, patients, prescriptions, etc (medical)')
    module_salon_management = fields.Boolean('Manage salon and spa chair booking, packages and invoices (salon_management)')
    module_email_management = fields.Boolean('Manage individual user emails - inbox, draft, outbox, sent (email_management)')
    module_mail_auto_reply = fields.Boolean('Set auto reply for incoming mail server (mail_auto_reply)')
    module_partner_contact_birthdate = fields.Boolean('Manage partner birthdate (partner_contact_birthdate)')
    module_partner_contact_gender = fields.Boolean('Manage partner gender (partner_contact_gender)')
    module_partner_firstname = fields.Boolean('Separate partner first and last name (partner_firstname)')
    module_partner_identification = fields.Boolean('Manage partner identification numbers (partner_identification)')
    module_partner_geo_map_location = fields.Boolean('Show the map for customer location (partner_geo_map_location)')
    module_product_pack = fields.Boolean('Manage product packs, like packages or sets of products (product_pack)')
    module_product_warehouse_quantity = fields.Boolean('Show the product quantity in form view and kanban view (product_warehouse_quantity)')
    module_dusal_purchase = fields.Boolean('Show images on PO (dusal_purchase)')
    module_stock_transport_management = fields.Boolean('Manage transportation for delivery orders, and will show in SO (stock_transport_management)')
    module_document = fields.Boolean('Manage attachments for every record (document)')
    module_website_digital_sign = fields.Boolean('Record digital signatures that can be used for digital signing (web_digital_sign)')

    @api.multi
    def copy(self, values):
        raise UserError(_("Cannot duplicate configuration!"), "")

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        ret_val = super(ModuleBoardConfig, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)

        can_install_modules = self.env['ir.module.module'].check_access_rights(
                                    'write', raise_exception=False)

        doc = etree.XML(ret_val['arch'])

        for field in ret_val['fields']:
            if not field.startswith("module_"):
                continue
            for node in doc.xpath("//field[@name='%s']" % field):
                if not can_install_modules:
                    node.set("readonly", "1")
                    modifiers = json.loads(node.get("modifiers"))
                    modifiers['readonly'] = True
                    node.set("modifiers", json.dumps(modifiers))
                if 'on_change' not in node.attrib:
                    node.set("on_change",
                    "onchange_module(%s, '%s')" % (field, field))

        ret_val['arch'] = etree.tostring(doc)
        return ret_val

    @api.multi
    def onchange_module(self, field_value, module_name):
        ModuleSudo = self.env['ir.module.module'].sudo()
        modules = ModuleSudo.search(
            [('name', '=', module_name.replace("module_", '')),
            ('state', 'in', ['to install', 'installed', 'to upgrade'])])

        if modules and not field_value:
            deps = modules.sudo().downstream_dependencies()
            dep_names = (deps | modules).mapped('shortdesc')
            message = '\n'.join(dep_names)
            return {
                'warning': {
                    'title': _('Warning!'),
                    'message': _('Disabling this option will also uninstall the following modules \n%s') % message,
                }
            }
        return {}

    @api.model
    def _get_classified_fields(self):
        IrModule = self.env['ir.module.module']
        ref = self.env.ref

        defaults, groups, modules, others = [], [], [], []
        for name, field in self._fields.iteritems():
            if name.startswith('default_') and hasattr(field, 'default_model'):
                defaults.append((name, field.default_model, name[8:]))
            elif name.startswith('group_') and field.type in ('boolean', 'selection') and \
                    hasattr(field, 'implied_group'):
                field_group_xmlids = getattr(field, 'group', 'base.group_user').split(',')
                field_groups = reduce(add, map(ref, field_group_xmlids))
                groups.append((name, field_groups, ref(field.implied_group)))
            elif name.startswith('module_') and field.type in ('boolean', 'selection'):
                module_list = []
                if name == 'module_website_helpdesk_livechat':
                    module_list = ['module_website_helpdesk_livechat', 'module_livechat_ext']
                elif name == 'module_sg_account_config':
                    module_list = ['module_sg_account_config', 'module_sg_account_report', 'module_sg_cashflow_report']
                elif name == 'module_sg_appendix8a_report':
                    module_list = ['module_sg_appendix8a_report', 'module_sg_cimb_report', 'module_sg_cpf_extended', 'module_sg_dbs_giro', 'module_sg_document_expiry', 'module_sg_income_tax_report', 'module_sg_ir21', 'module_sg_hr_report', 'module_sg_ocbc_report', 'module_sg_report_letter_undertaking']
                elif name == 'module_sg_expire_leave':
                    module_list = ['module_sg_expire_leave', 'module_sg_hr_holiday', 'module_sg_leave_constraints', 'module_sg_leave_extended']
                elif name == 'module_sg_hr_config':
                    module_list = ['module_sg_hr_config', 'module_sg_hr_employee', 'module_sg_hr_holiday', 'module_sg_nric_verification', 'module_sg_payroll_account', 'module_sg_payroll_constraints', 'module_hm_hr_sg_standardization']
                elif name == 'module_mass_mailing':
                    module_list = ['module_mass_mailing', 'module_mass_mailing_delimiter', 'module_mass_mailing_extension', 'module_mail_addin_style', 'module_web_editor_fixer']
                elif name == 'module_muk_dms':
                    module_list = ['module_muk_dms', 'module_muk_web_preview', 'module_muk_web_preview_attachment', 'module_muk_web_preview_msoffice']
                elif name == 'module_project_forecast':
                    module_list = ['module_project_forecast', 'module_project_lifeline']
                elif name == 'module_hotel_pos_restaurant':
                    module_list = ['module_hotel_pos_restaurant', 'module_report_hotel_restaurant']
                if module_list:
                    for m in module_list:
                        module = IrModule.sudo().search([('name', '=', m[7:])], limit=1)
                        modules.append((name, module))
                else:
                    module = IrModule.sudo().search([('name', '=', name[7:])], limit=1)
                    modules.append((name, module))
            else:
                others.append(name)

        return {'default': defaults, 'group': groups, 'module': modules, 'other': others}

    @api.model
    def default_get(self, fields):
        IrValues = self.env['ir.values']
        classified = self._get_classified_fields()

        res = super(ModuleBoardConfig, self).default_get(fields)

        # defaults: take the corresponding default value they set
        for name, model, field in classified['default']:
            value = IrValues.get_default(model, field)
            if value is not None:
                res[name] = value

        # groups: which groups are implied by the group Employee
        for name, groups, implied_group in classified['group']:
            res[name] = all(implied_group in group.implied_ids for group in groups)
            if self._fields[name].type == 'selection':
                res[name] = int(res[name])

        # modules: which modules are installed/to install
        for name, module in classified['module']:
            res[name] = module.state in ('installed', 'to install', 'to upgrade')
            if self._fields[name].type == 'selection':
                res[name] = int(res[name])

        # other fields: call all methods that start with 'get_default_'
        for method in dir(self):
            if method.startswith('get_default_'):
                res.update(getattr(self, method)(fields))

        return res

    @api.multi
    def execute(self):
        self.ensure_one()
        if not self.env.user._is_superuser() and not self.env.user.has_group('base.group_system'):
            raise AccessError(_("Only administrators can change the settings"))

        self = self.with_context(active_test=False)
        classified = self._get_classified_fields()

        # default values fields
        IrValues = self.env['ir.values'].sudo()
        for name, model, field in classified['default']:
            IrValues.set_default(model, field, self[name])

        # group fields: modify group / implied groups
        for name, groups, implied_group in classified['group']:
            if self[name]:
                groups.write({'implied_ids': [(4, implied_group.id)]})
            else:
                groups.write({'implied_ids': [(3, implied_group.id)]})
                implied_group.write({'users': [(3, user.id) for user in groups.mapped('users')]})

        # other fields: execute all methods that start with 'set_'
        for method in dir(self):
            if method.startswith('set_'):
                getattr(self, method)()

        # module fields: install/uninstall the selected modules
        to_install = []
        to_uninstall_modules = self.env['ir.module.module']
        lm = len('module_')
        for name, module in classified['module']:
            if self[name]:
                to_install.append((name[lm:], module))
            else:
                if module and module.state in ('installed', 'to upgrade'):
                    to_uninstall_modules += module

        if to_uninstall_modules:
            to_uninstall_modules.button_immediate_uninstall()

        action = self._install_modules(to_install)
        if action:
            return action

        if to_install or to_uninstall_modules:
            # After the uninstall/install calls, the registry and environments
            # are no longer valid. So we reset the environment.
            self.env.reset()
            self = self.env()[self._name]
        config = self.env['res.config'].next() or {}
        if config.get('type') not in ('ir.actions.act_window_close',):
            return config

        # force client-side reload (update user menu and current view)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @api.multi
    def cancel(self):
        # ignore the current record, and send the action to reopen the view
        actions = self.env['ir.actions.act_window'].search([('res_model', '=', self._name)], limit=1)
        if actions:
            return actions.read()[0]
        return {}

    @api.multi
    def name_get(self):
        action = self.env['ir.actions.act_window'].search([('res_model', '=', self._name)], limit=1)
        name = action.name or self._name
        return [(record.id, name) for record in self]


ModuleBoardConfig()