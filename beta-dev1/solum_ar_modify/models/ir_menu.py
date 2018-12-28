# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID

class ir_ui_menu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        menus_for_solum = [
        'solum_sale.led_idesign_quote_menu',
        'solum_sale.led_idesign_so_menu',
        'solum_invoice.led_idesign_invoice_menu',
        ]
        menus_for_idesign = [
        'solum_sale.led_attach_so_menu',
        'solum_sale.led_attach_quote_menu',
        'solum_sale.led_strip_quote_menu',
        'solum_sale.led_strip_so_menu',
        'solum_invoice.led_strip_invoice_menu',
        'solum_invoice.led_attach_invoice_menu'
        ]
        if 'design' in self.env.user.company_id.name.lower():
            menu_ids = []
            for menu_item in menus_for_idesign:
                menu = self.env.ref(menu_item)
                if menu and menu.id:
                    menu_ids.append(menu.id)
            if menu_ids and len(menu_ids) > 0:
                args.append('!')
                args.append(('id', 'in', menu_ids))
        if 'sol' in self.env.user.company_id.name.lower():
            menu_ids = []
            for menu_item in menus_for_solum:
                menu = self.env.ref(menu_item)
                if menu and menu.id:
                    menu_ids.append(menu.id)
            if menu_ids and len(menu_ids) > 0:
                args.append('!')
                args.append(('id', 'in', menu_ids))
        
        #Hide a menu for the Sales Manager
        sales_manager_hide_menu = [
            'account.menu_finance', #Invoicing top menu
            'purchase.menu_procurement_management_supplier_name' # Vendor from Purchase menu
        ]
        #Hide a menu for the Sales Person
        sales_person_hide_menu = [
            'account.menu_board_journal_1', #Dashboard menu
            'account.menu_finance_payables', #Purchase menu from Invoicing
            'account.menu_finance_reports', #Reports menu from Invoicing
            'account.menu_finance_entries', #Adviser menu from Invoicing
            'account.menu_finance_configuration', #Configuration menu from Invoicing
            'account.menu_product_template_action', #Sellable Products menu from Invoicing
            'account.menu_account_customer', #Customers menu from Invoicing
            'account.menu_action_account_payments_receivable', #Payments menu from Invoicing
            'purchase.menu_procurement_management_supplier_name', #Vendors menu from Purchase menu
            'account.menu_account_supplier', #Vendors menu from Invoicing menu
        ]
        
        accountant_hide_menu = [
        	'account.menu_finance_receivables', # Sales menu under the Invoicing
        	'account.menu_finance_payables', # Purchase menu under the Invoicing
        	'account.menu_board_journal_1', # Dashboard menu under the Invoicing
        	'account.menu_finance_entries', # Adviser menu under the Invoicing
        	'solum_invoice.led_strip_invoice_menu', # LED Strip Invoice menu
        	'solum_invoice.led_attach_invoice_menu', # LED Attachment Invoice menu
        	'solum_invoice.led_idesign_invoice_menu', # iDesign Invoice menu
        	'account.menu_action_invoice_tree2', # Vendor Bills Menu
        	'sales_team.menu_base_partner', # Main Top Sales Menu
        	'calendar.mail_menu_calendar', # Main Top Calendar menu
        	'purchase.menu_purchase_root', # Main Top Purchases menu
        	'stock.menu_stock_root', # Main Top Inventory menu
        	'mail.mail_channel_menu_root_chat',#Discuss,
        	'muk_dms.main_menu_muk_dms' # Document menu
        ]
        sm_user_id = self.env['ir.model.data'].get_object_reference('solum_ar_modify', 'group_sales_manager_sl')[1]
        sp_user_id = self.env['ir.model.data'].get_object_reference('solum_ar_modify', 'group_sale_person_sl')[1]
        accountant_user_id = self.env['ir.model.data'].get_object_reference('solum_ar_modify', 'group_accountant_sl')[1]
        for group in self.env['res.users'].browse(self.env.uid).groups_id:
    	    if group.id == sm_user_id:
    	        menu_ids = []
    	        for menu_item in sales_manager_hide_menu:
                    menu = self.env.ref(menu_item)
                    if menu and menu.id:
                        menu_ids.append(menu.id)
                if menu_ids and len(menu_ids) > 0:
                    args.append('!')
                    args.append(('id', 'in', menu_ids))
            if group.id == sp_user_id:
    	        menu_ids = []
    	        for menu_item in sales_person_hide_menu:
                    menu = self.env.ref(menu_item)
                    if menu and menu.id:
                        menu_ids.append(menu.id)
                if menu_ids and len(menu_ids) > 0:
                    args.append('!')
                    args.append(('id', 'in', menu_ids))
            if group.id == accountant_user_id:
    	        menu_ids = []
    	        for menu_item in accountant_hide_menu:
                    menu = self.env.ref(menu_item)
                    if menu and menu.id:
                        menu_ids.append(menu.id)
                if menu_ids and len(menu_ids) > 0:
                    args.append('!')
                    args.append(('id', 'in', menu_ids))
        return super(ir_ui_menu, self).search(args, offset, limit, order, count=count)
