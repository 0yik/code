# -*- coding: utf-8 -*-
#
#
#    TechSpawn Solutions Pvt. Ltd.
#    Copyright (C) 2016-TODAY TechSpawn(<http://www.techspawn.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#


from odoo import models, fields, api

import logging
from odoo.addons.connector.event import on_record_create, on_record_write
from odoo.addons.connector.connector import ConnectorEnvironment
from ..connector import get_environment
from ..backend import quick
from ..unit.backend_adapter import (GenericAdapter)
from ..unit.import_synchronizer import ( DelayedBatchImporter, WooImporter)
from odoo.addons.connector.unit.synchronizer import (Importer, Exporter)
from odoo.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper
                                                  )
from odoo.addons.queue_job.job import job, related_action
import xmlrpclib

from odoo.exceptions import except_orm, Warning, RedirectWarning
from ..related_action import unwrap_binding

_logger = logging.getLogger(__name__)


class quickbook_purchase_order(models.Model):

    _inherit = 'purchase.order'

    backend_id = fields.Many2one(comodel_name='qb.backend',
                                      string='Quick Backend', store=True,
                                      readonly=False, required=False,
                                      )

    quickbook_id = fields.Char(
        string='ID on Quickbook', readonly=False, required=False)
    sync_date = fields.Datetime(string='Last synchronization date')
    location_id = fields.Many2one('stock.location', 'Destination', required=False)
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', required=False)
    
    @api.multi
    def sync_purchase(self):
        """ Export Purchase Order And Details. """

        env = self.backend_id.get_environment(self._name)
        
        # session = ConnectorSession(self.env.cr, self.env.uid,
        #                            context=self.env.context)
        # env = get_environment(session, 'purchase.order', self.backend_id[0].id)
        product_exporter = env.get_connector_unit(PurchaseExporter)
        product_exporter.run_sync(self.quickbook_id or 0, self)

    @api.multi
    @job(default_channel='root.quick')
    def purchases_import_batch(session, model_name, backend_id, filters=None):
        """ Import Purchase Order And Details. """

        env = get_environment(session, model_name, backend_id)
        importer = env.get_connector_unit(PurchaseBatchImporter)
        importer.run(filters=filters)

    @job(default_channel='root.quick')
    @related_action(action=unwrap_binding)
    def export_purchase_details(self, backend_id):
        """ Export Purchase Order And Details. """

        env = backend_id.get_environment(self._name)
        # env = get_environment(session, model_name, backend_id)
        inventory_exporter = env.get_connector_unit(
            PurchaseExporter)

        return inventory_exporter.run(backend_id, fields)
        
@quick
class PurchaseAdapter(GenericAdapter):
    _model_name = 'purchase.order'
    _booking_model = 'purchaseorder'
    url = None

    def _call(self, method, arguments):
        print method
        try:
            return super(PurchaseAdapter, self)._call(method, arguments)
        except xmlrpclib.Fault as err:
            # this is the error in the Quickbook API
            # when the Purchase does not exist
            if err.faultCode == 102:
                raise IDMissingInBackend
            else:
                raise

    def search(self, filters=None, from_date=None, to_date=None):
        """ Search records according to some criteria and return a
        list of ids

        :rtype: list
        """
        
        if filters is None:
            filters = {}
        WOO_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
        dt_fmt = WOO_DATETIME_FORMAT
        if from_date is not None:
            # updated_at include the created records
            filters.setdefault('updated_at', {})
            filters['updated_at']['from'] = from_date
        if to_date is not None:
            filters.setdefault('updated_at', {})
            filters['updated_at']['to'] = to_date
        # the search method is on ol_Purchase instead of Purchase
        # return self._call('staff/list',
        #                   [filters] if filters else [{}])

        if 'url' in filters:
            if filters['url'] is 'purchaseorder':
                return self._call('/query?query=select%20from%20purchaseorder',
                                  [filters] if filters else [{}])

            # elif filters['url'] is 'Purchase':
            #     return self._call('/query?query=select%20ID%20from%20Purchase',
            #                       [filters] if filters else [{}])

    def update_purchase(self, id, data):
        # product_stock.update is too slow

        return self._call_purchase('update_purchase', [int(id), data])


@quick
class PurchaseBatchImporter(DelayedBatchImporter):

    """ Import the Quickbook Partners.

    For every partner in the list, a delayed job is created.
    """
    _model_name = ['purchase.order']
    url = None

    def _import_record(self, quickbook_id, priority=None):
        """ Delay a job for the import """

        super(PurchaseBatchImporter, self)._import_record(
            quickbook_id, priority=priority)

    def run(self, filters=None):
        """ Run the synchronization """
        from_date = filters.pop('from_date', None)
        to_date = filters.pop('to_date', None)
        count = 1
        record_ids = ['start']
        filters['url'] = 'purchaseorder'
        while record_ids:
            filters['count'] = count
            record_ids = self.backend_adapter.search(
                filters,
                from_date=from_date,
                to_date=to_date,
            )
    #         record_ids = self.env['bk.backend'].get_Purchase_ids(record_ids)
            _logger.info('search for purchase %s returned %s',
                         filters, record_ids)
            count += 300
            self.url = 'purchaseorder'
            if 'PurchaseOrder' in record_ids['QueryResponse']:
                record_ids = record_ids['QueryResponse']['PurchaseOrder']
                for record_id in record_ids:

                    self._import_record(int(record_id['Id']), 40)
            else:
                record_ids = record_ids['QueryResponse']



PurchaseBatchImporter = PurchaseBatchImporter  # deprecated


@quick
class PurchaseImporter(WooImporter):
    _model_name = ['purchase.order']
    url = None

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        # record = self.woo_record
        # if 'PurchaseOrder' in record:
        #     if 'VendorRef' in record['PurchaseOrder']:
        #         if record['PurchaseOrder']['VendorRef']:
        #             self._import_dependency(record['PurchaseOrder']['VendorRef']['value'],
        #                             'res.partner')
        return

    def _create(self, data):
        openerp_binding = super(PurchaseImporter, self)._create(data)
        return openerp_binding

    def _after_import(self, binding):
        """ Hook called at the end of the import """
        return

PurchaseImporter = PurchaseImporter  # deprecated


@quick
class PurchaseImportMapper(ImportMapper):
    _model_name = 'purchase.order'

    @mapping
    def partner_id(self, record):
        if 'PurchaseOrder' in record:
            if 'DocNumber' in record['PurchaseOrder']:
                return {'name': record['PurchaseOrder']['DocNumber']}
    @mapping
    def partner_id(self, record):
        if 'PurchaseOrder' in record:
            if 'VendorRef' in record['PurchaseOrder']:
                rec = record['PurchaseOrder']
                if rec['VendorRef']:

                    partner_id = self.env['res.partner'].search(
                        [('quickbook_id', '=', rec['VendorRef']['value']),
                        ('name', '=', rec['VendorRef']['name'])])
                    if not partner_id:
                        raise Warning(('Please import "Customer" First'))
                        
                    partner_id = partner_id.id or False
                else:
                    partner_id = False
                return {'partner_id': partner_id}
    @mapping
    def date_order(self, record):
        if 'PurchaseOrder' in record:
            
            if 'TxnDate' in record['PurchaseOrder']:
                rec = record['PurchaseOrder']
                return{'date_order': rec['TxnDate']}
    @mapping
    def order_line(self, record):
        if 'PurchaseOrder' in record:
            rec = record['PurchaseOrder']
            if 'Line' in rec:
                product_ids = []
                for lines in rec['Line']:
                    if 'ItemBasedExpenseLineDetail' in lines:
                        product_template_id = self.env['product.template'].search(
                            [('quickbook_id', '=', lines['ItemBasedExpenseLineDetail']['ItemRef']['value']),
                             ('name', '=', lines['ItemBasedExpenseLineDetail']['ItemRef']['name'])])
                        # product_id = self.env['product.product'].search([('id', '=', product_template_id.id),
                        #      ('name', '=', product_template_id.name)])
                        product_id = self.env['product.product'].search([('name', '=', product_template_id.name)])
                        order_id = self.env['purchase.order'].search([('backend_id', '=', self.backend_record.id),('quickbook_id', '=', rec['Id'])])
                        
                        tax_id = [self.env['account.tax'].search([('amount_type', '=', 'group'), ('quickbook_id', '=', lines['ItemBasedExpenseLineDetail']['TaxCodeRef']['value'])]).id]
                        order = self.env['purchase.order.line'].search([('order_id', '=', order_id.id), ('quickbook_id', '=', lines['Id']),('name', '=', lines['Description'])])
                        result = {'product_id':product_id.id,
                            # 'sequence': lines['LineNum'],
                            'price_unit': lines['ItemBasedExpenseLineDetail']['UnitPrice'],
                            'product_qty': lines['ItemBasedExpenseLineDetail']['Qty'],
                            # 'tax_id': [(6, 0, tax_id)],
                            'product_uom': 1,
                            'price_subtotal': lines['Amount'],
                            'name': lines['Description'],
                            'quickbook_id': lines['Id'],
                            'date_planned': rec['TxnDate']
                            }
                        if not order:

                            product_ids.append([0,0,result]) or False
                        else:
                            product_ids.append([1,order.id,result])

                return {'order_line': product_ids}


    @mapping
    def amount_total(self, record):
        if 'PurchaseOrder' in record:
            rec = record['PurchaseOrder']
            if rec['TotalAmt']:
                return {'amount_total': rec['TotalAmt']}



    @mapping
    def type(self, record):
        if 'PurchaseOrder' in record:

            if 'Type' in record['PurchaseOrder']:
                rec = record['PurchaseOrder']
                if rec['Type']:
                    categ_id = self.env['purchase.order'].search(
                        [('name', '=', rec['Type'])])

    @mapping
    def type(self, record):
        if 'PurchaseOrder' in record:
            if 'POStatus' in record['PurchaseOrder']:
                rec = record['PurchaseOrder']
                if rec['POStatus']:
                    if rec['POStatus'] == 'Open':
                        status = 'draft'
                    if rec['POStatus'] == 'Closed':
                        status = 'done'
                    return {'state': status }
    # location_id
    # @mapping
    # def partner_ref(self, record):
    #     if 'PurchaseOrder' in record:
            
    #         if 'VendorRef' in record['PurchaseOrder']:
    #             rec = record['PurchaseOrder']
    #             return {'partner_ref': rec['VendorRef']['name']}

	# @mapping
	# def property_account_income(self, record):
	# 	if 'PurchaseOrder' in record:

	# 			rec = record['PurchaseOrder']
	# 			if rec['APAccountRef']:
	# 				property_account_income = self.env['account.account'].search(
	# 					[('name', '=', rec['Name']), ('quickbook_id', '=', rec['value'])])
	# 				if not property_account_income:
	# 					property_account_income = self.env['purchase.order'].create(
	# 						{'name': rec['name'],'quickbook_id': rec['value']})
	# 					property_account_income = property_account_income.id or False
	# 			else:
	# 				property_account_income = False
	# 				return {'property_account_income': property_account_income}
	
	# @mapping
	# def property_account_expense(self, record):
	# 	if 'PurchaseOrder' in record:

	# 			rec = record['PurchaseOrder']
	# 			if rec['ExpenseAccountRef']:
	# 				property_account_expense = self.env['purchase.order'].search(
	# 					[('name', '=', rec['Name']), ('quickbook_id', '=', rec['value'])])
	# 				if not property_account_expense:
	# 					property_account_expense = self.env['purchase.order'].create(
	# 						{'name': rec['Name'],'quickbook_id': rec['value']})
	# 					property_account_expense = property_account_expense.id or False
	# 			else:
	# 				property_account_expense = False
	# 				return {'property_account_expense': property_account_expense}


    @mapping
    def id(self, record):
        if 'PurchaseOrder' in record:
            rec = record['PurchaseOrder']
            if rec['Id']:
                return {'quickbook_id': rec['Id']}

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}


@quick
class PurchaseExporter(Exporter):
    _model_name = ['purchase.order']

    def _get_data(self, product, fields):
        result = {}
        return result

    def _domain_for_update_purchase(self):
        return [
            ('backend_id', '!=', None),
            # ('tda_booking', '=', True),
        ]

    def run(self, binding_id, fields):
        """ Export the product inventory to wordpress """

        purchase_obj = self.env['purchase.order']
        domain = self._domain_for_update_purchase()

        purchase_data = purchase_obj.search(domain)

        if purchase_data:
            for purchase in purchase_data:
                self.backend_adapter.update_purchase(purchase.quickbook_id,
                                                       {'purchase': purchase})

    def run_sync(self, binding_id, data):
        
        self.backend_adapter.update_purchase(binding_id, {'purchase': data})



PurchaseExporter = PurchaseExporter  # deprecated


# @job(default_channel='root.quick')
# @related_action(action=unwrap_binding)
# def export_purchase_details(session, model_name, record_id, fields=None):
#     """ Export the inventory configuration and quantity of a product. """

#     purchase = session.env[model_name].browse(record_id)
#     try:
#         if purchase.backend_id:
#             backend_id = purchase.backend_id.id
#         else:
#             backend_id = record_id

#     finally:
#         pass

#     env = get_environment(session, model_name, backend_id)
#     inventory_exporter = env.get_connector_unit(
#         PurchaseExporter)


#     return inventory_exporter.run(record_id, fields)
##########################################
############ End Instructor ##############
##########################################

class quickbook_purchase_order_line(models.Model):

    _inherit = 'purchase.order.line'

    backend_id = fields.Many2one(comodel_name='qb.backend',
                                 string='quick Backend', store=True,
                                 readonly=False, required=False,
                                 )

    quickbook_id = fields.Char(
        string='ID on Quickbook', readonly=False, required=False)
    sync_date = fields.Datetime(string='Last synchronization date')