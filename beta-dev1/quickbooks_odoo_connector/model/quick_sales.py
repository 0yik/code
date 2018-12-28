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


class quickbook_sale_order(models.Model):

    _inherit = 'sale.order'

    backend_id = fields.Many2one(comodel_name='qb.backend',
                                 string='Quick Backend', store=True,
                                 readonly=False, required=False,
                                 )

    quickbook_id = fields.Char(
        string='ID on Quickbook', readonly=False, required=False)
    sync_date = fields.Datetime(string='Last synchronization date')

    @api.multi
    def sync_sale(self):
        """ Import Sales Order. """

        env = self.backend_id.get_environment(self._name)
        
        # session = ConnectorSession(self.env.cr, self.env.uid,
        #                            context=self.env.context)
        # env = get_environment(session, 'sale.order', self.backend_id[0].id)
        product_exporter = env.get_connector_unit(SaleExporter)
        product_exporter.run_sync(self.quickbook_id or 0, self)

    @api.multi
    @job(default_channel='root.quick')
    def sale_import_batch(session, model_name, backend_id, filters=None):
        """ Import Sales Order. """

        env = get_environment(session, model_name, backend_id)
        importer = env.get_connector_unit(SaleBatchImporter)
        importer.run(filters=filters)

    @job(default_channel='root.quick')
    @related_action(action=unwrap_binding)
    def export_sale_details(self, backend_id):
        """ Export Sales Order. """

        env = backend_id.get_environment(self._name)
        # env = get_environment(session, model_name, backend_id)
        inventory_exporter = env.get_connector_unit(
            SaleExporter)

        return inventory_exporter.run(backend_id, fields)
        

@quick
class SaleAdapter(GenericAdapter):
    _model_name = 'sale.order'
    _booking_model = 'salesreceipt'
    url = None

    def _call(self, method, arguments):
        print method
        try:
            return super(SaleAdapter, self)._call(method, arguments)
        except xmlrpclib.Fault as err:
            # this is the error in the Quickbook API
            # when the salesreceipt does not exist
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
        # the search method is on ol_salesreceipt instead of salesreceipt
        # return self._call('staff/list',
        #                   [filters] if filters else [{}])

        if 'url' in filters:
            if filters['url'] is 'salesreceipt':
                return self._call('/query?query=select%20from%20salesreceipt',
                                  [filters] if filters else [{}])

            # elif filters['url'] is 'salesreceipt':
            #     return self._call('/query?query=select%20ID%20from%20salesreceipt',
            #                       [filters] if filters else [{}])

    def update_salesreceipts(self, id, data):
        # product_stock.update is too slow
        return self._call_salesreceipts('update_salesreceipts', [int(id), data])


@quick
class SaleBatchImporter(DelayedBatchImporter):

    """ Import the Quickbook Partners.

    For every partner in the list, a delayed job is created.
    """
    _model_name = ['sale.order']
    url = None

    def _import_record(self, quickbook_id, priority=None):
        """ Delay a job for the import """

        super(SaleBatchImporter, self)._import_record(
            quickbook_id, priority=priority)

    def run(self, filters=None):
        """ Run the synchronization """
        from_date = filters.pop('from_date', None)
        to_date = filters.pop('to_date', None)
        count = 1
        record_ids = ['start']
        filters['url'] = 'salesreceipt'
        while record_ids:
            filters['count'] = count
            record_ids = self.backend_adapter.search(
                filters,
                from_date=from_date,
                to_date=to_date,
            )
    #         record_ids = self.env['bk.backend'].get_salesreceipt_ids(record_ids)
            _logger.info('search for salesreceipt %s returned %s',
                         filters, record_ids)
            count += 300
            self.url = 'salesreceipt'
            if 'SalesReceipt' in record_ids['QueryResponse']:
                record_ids = record_ids['QueryResponse']['SalesReceipt']
                for record_id in record_ids:

                    self._import_record(int(record_id['Id']), 40)
            else:
                record_ids = record_ids['QueryResponse']

SaleBatchImporter = SaleBatchImporter  # deprecated


@quick
class SaleImporter(WooImporter):
    _model_name = ['sale.order']
    url = None

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        record = self.woo_record
        # record = record['product']
        if 'SalesReceipt' in record:
            if 'CustomerRef' in record['SalesReceipt']:
                if record['SalesReceipt']['CustomerRef']:
                    self._import_dependency(record['SalesReceipt']['CustomerRef']['value'],
                                    'res.partner')
        return

    def _create(self, data):
        openerp_binding = super(SaleImporter, self)._create(data)
        return openerp_binding

    def _after_import(self, binding):
        """ Hook called at the end of the import """
        return

SaleImporter = SaleImporter  # deprecated


@quick
class SaleImportMapper(ImportMapper):
    _model_name = 'sale.order'

    @mapping
    def partner_id(self, record):
        if 'SalesReceipt' in record:
            if 'CustomerRef' in record['SalesReceipt']:
                rec = record['SalesReceipt']
                if 'CustomerRef' in rec:
                    partner_id = self.env['res.partner'].search(
                        [('quickbook_id', '=', rec['CustomerRef']['value']),
                         ('name', '=', rec['CustomerRef']['name'])])
                    # if not partner_id:
                    #     raise Warning(('Please import "Customer" First'))

                    partner_id = partner_id.id or False
                else:
                    partner_id = False
                return {'partner_id': partner_id}

    @mapping
    def date_order(self, record):

        if 'SalesReceipt' in record:
            rec = record['SalesReceipt']

            return{'date_order': rec['TxnDate']}

    @mapping
    def client_order_ref(self, record):
        if 'SalesReceipt' in record:
            rec = record['SalesReceipt']
            if 'DocNumber' in rec:
                return{'client_order_ref': rec['DocNumber']}

    @mapping
    def order_line(self, record):
        if 'SalesReceipt' in record:
            rec = record['SalesReceipt']
            if 'Line' in rec:
                product_ids = []
                for lines in rec['Line']:
                    if 'SalesItemLineDetail' in lines:
                        product_template_id = self.env['product.template'].search(
                            [('quickbook_id', '=', lines['SalesItemLineDetail']['ItemRef']['value']),
                             ('name', '=', lines['SalesItemLineDetail']['ItemRef']['name'])])
                        # product_id = self.env['product.product'].search([('id', '=', product_template_id.id),
                        #      ('name', '=', product_template_id.name)])
                        product_id = self.env['product.product'].search([('name', '=', product_template_id.name)])
                        
                        order_id = self.env['sale.order'].search([('backend_id', '=', self.backend_record.id),('quickbook_id', '=', rec['Id'])])                       
                        # tax_id = [self.env['account.tax'].search([('amount_type', '=', 'group'),('quickbook_id', '=', lines['SalesItemLineDetail']['TaxCodeRef']['value'])]).id]
                        tax_id = []
                        if lines['SalesItemLineDetail']['TaxCodeRef']['value'] == 'TAX':
                            if 'TxnTaxDetail' in rec and 'TxnTaxCodeRef' in rec.get('TxnTaxDetail'):
                                tax_id = [self.env['account.tax'].search([('amount_type', '=', 'group'),('quickbook_id', '=', rec['TxnTaxDetail']['TxnTaxCodeRef']['value'])]).id]

                        order = self.env['sale.order.line'].search([('order_id', '=', order_id.id),('quickbook_id', '=', lines['Id'])])

                        result = {'product_id':product_id.id,
                            'sequence': lines['LineNum'],
                            'price_unit': lines['SalesItemLineDetail']['UnitPrice'],
                            'product_uom_qty': lines['SalesItemLineDetail']['Qty'],
                            'tax_id': [(6, 0, tax_id)],
                            'product_uom': 1,
                            'price_subtotal': lines['Amount'],
                            'name': lines['Description'],
                            'quickbook_id': lines['Id'],
                            }
                        if not order:

                            product_ids.append([0,0,result]) or False
                        else:
                            product_ids.append([1,order.id,result])

                return {'order_line': product_ids}

    # @mapping
    # def price_unit(self, record):
    #     if 'SalesReceipt' in record:
    #         if 'Line' in record['SalesReceipt']:
    #             rec = record['SalesReceipt']
    #             return {'price_unit': float(rec['Line'][0]['SalesItemLineDetail']['UnitPrice']) or 0.0}

    # @mapping
    # def product_uom_qty(self, record):
    #     if 'SalesReceipt' in record:
    #         if 'Line' in record['SalesReceipt']:
    #             rec = record['SalesReceipt']
    #             return {'product_uom_qty': float(rec['Line'][0]['SalesItemLineDetail']['Qty']) or 0.0}

    # @mapping
    # def name_dec(self, record):
    #     if 'SalesReceipt' in record:
    #         if 'Line' in record['SalesReceipt']:
    #             rec = record['SalesReceipt']
    #             return {'name': rec['Line'][0]['Description']}
# rec['Line'][0]['SalesItemLineDetail']['TaxCodeRef']

    @mapping
    def id(self, record):
        if 'SalesReceipt' in record:
            rec = record['SalesReceipt']
            if rec['Id']:
                return {'quickbook_id': rec['Id']}

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}



@quick
class SaleExporter(Exporter):
    _model_name = ['sale.order']

    def _get_data(self, product, fields):
        result = {}
        return result

    def _domain_for_update_sales(self):
        return [
            ('backend_id', '!=', None),
            # ('tda_booking', '=', True),
        ]

    def run(self, binding_id, fields):
        """ Export the product inventory to wordpress """

        sale_obj = self.env['sale.order']
        domain = self._domain_for_update_sales()

        sale_data = sale_obj.search(domain)

        if sale_data:
            for sale in sale_data:
                self.backend_adapter.update_salesreceipts(sale.quickbook_id,
                                                         {'sale': sale})

    def run_sync(self, binding_id, data):
        self.backend_adapter.update_salesreceipts(binding_id, {'sale': data})


SaleExporter = SaleExporter  # deprecated


# @job(default_channel='root.quick')
# @related_action(action=unwrap_binding)
# def export_sale_details(session, model_name, record_id, fields=None):
#     """ Export the inventory configuration and quantity of a product. """
#     sale = session.env[model_name].browse(record_id)
#     try:
#         if sale.backend_id:
#             backend_id = sale.backend_id.id
#         else:
#             backend_id = record_id

#     finally:
#         pass

#     env = get_environment(session, model_name, backend_id)
#     inventory_exporter = env.get_connector_unit(
#         SaleExporter)

#     return inventory_exporter.run(record_id, fields)


##########################################
############ End Instructor ##############
##########################################


class quickbook_sale_order_line(models.Model):

    _inherit = 'sale.order.line'

    backend_id = fields.Many2one(comodel_name='qb.backend',
                                 string='quick Backend', store=True,
                                 readonly=False, required=False,
                                 )

    quickbook_id = fields.Char(
        string='ID on Quickbook', readonly=False, required=False)
    sync_date = fields.Datetime(string='Last synchronization date')

    # @api.multi
    # def sync_sale(self):
    #     session = ConnectorSession(self.env.cr, self.env.uid,
    #                                context=self.env.context)
    #     env = get_environment(session, 'sale.order', self.backend_id[0].id)
    #     product_exporter = env.get_connector_unit(ItemExporter)
    #     product_exporter.run_sync(self.quickbook_id or 0, self)