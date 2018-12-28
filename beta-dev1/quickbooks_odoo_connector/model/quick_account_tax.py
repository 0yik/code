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

from requests_oauthlib import OAuth1Session, OAuth2Session
import requests
from requests_oauthlib import OAuth1
import logging
from odoo.addons.connector.event import on_record_create, on_record_write
from odoo.addons.connector.connector import ConnectorEnvironment

from ..connector import get_environment
from ..backend import quick
from ..unit.backend_adapter import (GenericAdapter)
from ..unit.import_synchronizer import (DelayedBatchImporter, WooImporter)
from odoo.addons.connector.unit.synchronizer import (Importer, Exporter)
from odoo.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper
                                                  )
from odoo.addons.queue_job.job import job, related_action
import xmlrpclib

from odoo.exceptions import except_orm, Warning, RedirectWarning
from ..related_action import unwrap_binding

_logger = logging.getLogger(__name__)
import random

class quickbook_acount(models.Model):

    _inherit = 'account.tax'

    backend_id = fields.Many2one(comodel_name='qb.backend',
                                 string='Quick Backend', store=True,
                                 readonly=False, required=False,
                                 )

    quickbook_id = fields.Char(
        string='ID on Quickbook', readonly=False, required=False)
    rate_quickbook_id = fields.Char(
        string='Rate ID on Quickbook', readonly=False, required=False)
    sync_date = fields.Datetime(string='Last synchronization date')

    @api.multi
    def sync_Tax(self):
        """ Export the configuration and data of a Tax. """

        env = self.backend_id.get_environment(self._name)
        product_exporter = env.get_connector_unit(TaxExporter)
        product_exporter.run_sync(self.quickbook_id or 0, self)

    @job(default_channel='root.quick')
    def tax_import_batch(session, model_name, backend_id, filters=None):
        """ Import Chart of a Tax. """

        env = get_environment(session, model_name, backend_id)
        importer = env.get_connector_unit(TaxBatchImporter)
        importer.run(filters=filters)

    @job(default_channel='root.quick')
    @related_action(action=unwrap_binding)
    def export_Tax_details(self, backend_id):
        """ Export the configuration and data of a Tax. """

        env = backend_id.get_environment(self._name)
        # env = get_environment(session, model_name, backend_id)
        inventory_exporter = env.get_connector_unit(
            TaxExporter)

        return inventory_exporter.run(backend_id, fields)
        
@quick
class TaxAdapter(GenericAdapter):
    _model_name = 'account.tax'
    _booking_model = 'taxcode'
    url = None

    def _call(self, method, arguments):
        print method
        try:
            return super(TaxAdapter, self)._call(method, arguments)
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
            if filters['url'] is 'taxrate':
                return self._call('/query?query=select%20ID%20from%20taxrate',
                                  [filters] if filters else [{}])
            
            elif filters['url'] is 'taxcode':
                return self._call('/query?query=select%20from%20taxcode',
                                  [filters] if filters else [{}])

    def update_Tax(self, id, data):
        # product_stock.update is too slow
        return self._call_service('update_taxes', [int(id), data])


@quick
class TaxBatchImporter(DelayedBatchImporter):

    """ Import the Quickbook Partners.

    For every partner in the list, a delayed job is created.
    """
    _model_name = ['account.tax']
    url = None

    def _import_record(self, quickbook_id, priority=None):
        """ Delay a job for the import """

        super(TaxBatchImporter, self)._import_record(
            quickbook_id, priority=priority)

    def run(self, filters=None):
        """ Run the synchronization """
        from_date = filters.pop('from_date', None)
        to_date = filters.pop('to_date', None)
        count = 1
        record_ids = ['start']
        filters['url'] = 'taxcode'
        while record_ids:
            filters['count'] = count
            record_ids = self.backend_adapter.search(
                filters,
                from_date=from_date,
                to_date=to_date,
            )
    #         record_ids = self.env['bk.backend'].get_salesreceipt_ids(record_ids)
            _logger.info('search for Tax %s returned %s',
                         filters, record_ids)
            count += 300
            self.url = 'taxcode'
            if 'TaxCode' in record_ids['QueryResponse']:
                record_ids = record_ids['QueryResponse']['TaxCode']
                for record_id in record_ids:
                    self._import_record(int(record_id['Id']), 40)
            else:
                record_ids = record_ids['QueryResponse']

TaxBatchImporter = TaxBatchImporter  # deprecated


@quick
class TaxImporter(WooImporter):
    _model_name = ['account.tax']
    url = None
    def _import_sale_rate(self, binding):
        """ Hook called at the end of the import """
        rate_id  = binding
        if self.backend_record.type == 'oauth1':
            headeroauth = OAuth1(self.backend_record.client_key, self.backend_record.client_secret,
                     self.backend_record.resource_owner_key, self.backend_record.resource_owner_secret,
                     signature_type='auth_header')
            ris = self.backend_record.location+self.backend_record.company_id + \
                    '/taxrate/' + str(rate_id)+'?minorversion=4'
            headers = {'accept': 'application/json'}
            r = requests.get(ris, auth=headeroauth, headers=headers)
            response = r.json()
        elif self.backend_record.type == 'oauth2':
            headeroauth = OAuth2Session(self.backend_record.client_key)
            ris = self.backend_record.location+self.backend_record.company_id + \
                    '/taxrate/' + str(rate_id)+'?minorversion=4'
            headers = {'Authorization': 'Bearer %s' %self.backend_record.access_token, 
                        'content-type': 'application/json', 'accept': 'application/json'}
            r = headeroauth.get(ris, headers=headers)
            response = r.json()
        return response

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        record = self.woo_record
        if 'SalesTaxRateList' in record['TaxCode']:
            if record['TaxCode']['SalesTaxRateList']['TaxRateDetail']:
                for rate in record['TaxCode']['SalesTaxRateList']['TaxRateDetail']:
                    values  = self._import_sale_rate(rate['TaxRateRef']['value'])
                    if values:
                        val = values['TaxRate']
                        if val['SpecialTaxType'] == "ADJUSTMENT_RATE":
                            adjustment  = True
                            amount = 0
                        elif val['SpecialTaxType'] == "NONE":
                            adjustment  = False
                            amount = val['RateValue']
                        elif val['SpecialTaxType'] == "ZERO_RATE":
                            adjustment  = False
                            amount = val['RateValue']
                        else:
                            adjustment  = False
                            amount = val['RateValue']
                        search_id = self.env['account.tax'].search([('backend_id', '=',  self.backend_record.id),('rate_quickbook_id', '=', val['Id'])])
                        if search_id:
                            if search_id['amount_type'] == 'percent':
                                search_id.write({
                                        'name': val['Name'],
                                        'description': val['Description'],
                                        'amount': amount,
                                        'tax_adjustment': adjustment,
                                        'tax_group_id': "1",
                                        'type_tax_use': 'sale',
                                        'amount_type': 'percent',
                                        'active':val['Description'],
                                        'rate_quickbook_id': val['Id'],
                                        'backend_id': self.backend_record.id,
                                })
                            if search_id['amount_type'] == 'group':
                                search_id.write({
                                        'name': val['Name'],
                                        'description': val['Description'],
                                        'amount': amount,
                                        'tax_adjustment': adjustment,
                                        'tax_group_id': "1",
                                        'type_tax_use': 'sale',
                                        'amount_type': 'group',
                                        'active':val['Description'],
                                        'rate_quickbook_id': val['Id'],
                                        'backend_id': self.backend_record.id,
                                })
                        else:
                            self.env['account.tax'].create({
                                'name': val['Name'],
                                'description': val['Description'],
                                'amount': amount,
                                'tax_adjustment': adjustment,
                                'tax_group_id': "1",
                                'type_tax_use': 'sale',
                                'amount_type': 'percent',
                                'active':val['Description'],
                                'rate_quickbook_id': val['Id'],
                                'backend_id': self.backend_record.id,
                            })
        # if 'PurchaseTaxRateList' in record['TaxCode']:
        #     if record['TaxCode']['PurchaseTaxRateList']['TaxRateDetail']:
        #         for rate in record['TaxCode']['PurchaseTaxRateList']['TaxRateDetail']:
        #             values  = self._import_sale_rate(rate['TaxRateRef']['value'])
        #             if values:
        #                 val = values['TaxRate']
        #                 if val['SpecialTaxType'] == "ADJUSTMENT_RATE":
        #                     adjustment  = True
        #                     amount = 0
        #                 elif val['SpecialTaxType'] == "NONE":
        #                     adjustment  = False
        #                     amount = val['RateValue']
        #                 elif val['SpecialTaxType'] == "ZERO_RATE":
        #                     adjustment  = False
        #                     amount = val['RateValue']
        #                 else:
        #                     adjustment  = False
        #                     amount = val['RateValue']
        #                 search_id = self.env['account.tax'].search([('backend_id', '=',  self.backend_record.id),('quickbook_id', '=', val['Id'])])
        #                 if search_id:
        #                     if search_id['amount_type'] == 'percent':
        #                         search_id.write({
        #                                 'name': val['Name'],
        #                                 'description': val['Description'],
        #                                 'amount': amount,
        #                                 'tax_adjustment': adjustment,
        #                                 'tax_group_id': "1",
        #                                 'type_tax_use': 'purchase',
        #                                 'amount_type': 'percent',
        #                                 'active':val['Description'],
        #                                 'quickbook_id': val['Id'],
        #                                 'backend_id': self.backend_record.id,
        #                         })
        #                     if search_id['amount_type'] == 'group':
        #                             search_id.write({
        #                                 'name': val['Name'],
        #                                 'description': val['Description'],
        #                                 'amount': amount,
        #                                 'tax_adjustment': adjustment,
        #                                 'tax_group_id': "1",
        #                                 'type_tax_use': 'purchase',
        #                                 'amount_type': 'group',
        #                                 'active':val['Description'],
        #                                 'quickbook_id': val['Id'],
        #                                 'backend_id': self.backend_record.id,
        #                         })
        #                         # search_id.write({'backend_id': self.backend_record.id})
        #                 else:
        #                     self.env['account.tax'].create({
        #                         'name': val['Name'],
        #                         'description': val['Description'],
        #                         'amount': amount,
        #                         'tax_adjustment': adjustment,
        #                         'tax_group_id': "1",
        #                         'type_tax_use': 'purchase',
        #                         'amount_type': 'percent',
        #                         'active':val['Description'],
        #                         'quickbook_id': val['Id'],
        #                         'backend_id': self.backend_record.id,
        #                     })
        return

    def _create(self, data):
        openerp_binding = super(TaxImporter, self)._create(data)
        return openerp_binding

    def _after_import(self, binding):
        """ Hook called at the end of the import """
        return


TaxImporter = TaxImporter  # deprecated


@quick
class TaxImportMapper(ImportMapper):
    _model_name = 'account.tax'

    # "Taxable": true,
    # "TaxGroup": true,

    # "AgencyRef": {
    #   "value": "1"
    # },
    # "SpecialTaxType": "NONE",
    # "DisplayType": "ReadOnly",
    
    # "RateValue":0,
    # "AgencyRef":{"value":"1"},
    # "SpecialTaxType":"ZERO_RATE",
    # "DisplayType":"HideInTransactionForms",
  
    @mapping
    def name(self, record):
        
        if 'TaxCode' in record:
            rec = record['TaxCode']
            if 'Name' in rec:
                return {'name': 'QBO'+rec['Name']}
        elif 'TaxRate' in record:
            rec = record['TaxRate']
            if 'Name' in rec:
                return {'name': rec['Name']}

    @mapping
    def Description(self, record):
        if 'TaxCode' in record:
            rec = record['TaxCode']
            if 'Description' in rec:
                return {'description': rec['Description']}
        elif 'TaxRate' in record:
            rec = record['TaxRate']
            if 'Description' in rec:
                return {'description': rec['Description']}

    @mapping
    def active(self, record):
        if 'TaxCode' in record:
            rec = record['TaxCode']
            if 'Active' in rec:
                return {'active': rec['Active']}
        elif 'TaxRate' in record:
            rec = record['TaxRate']
            if 'Active' in rec:
                return {'active': rec['Active']}

    @mapping
    def group(self, record):
        if 'TaxCode' in record:
            rec = record['TaxCode']
            if 'TaxGroup' in rec:
                if rec['TaxGroup'] == True:
                    option = 'group'
                    amount = 0
                return {'amount': amount, 'amount_type': option, 'tax_group_id': "1", 'tax_adjustment': False}
    @mapping
    def amount(self, record):
        if 'TaxRate' in record:
            rec = record['TaxRate']
            if rec:
                if rec['SpecialTaxType'] == "ADJUSTMENT_RATE":
                    adjustment  = True
                    amount = 0
                elif rec['SpecialTaxType'] == "NONE":
                    adjustment  = False
                    amount = rec['RateValue']
                elif rec['SpecialTaxType'] == "ZERO_RATE":
                    adjustment  = False
                    amount = rec['RateValue']
                else:
                    adjustment  = False
                    amount = rec['RateValue']
                return {'amount': amount, 'tax_adjustment': adjustment, 'tax_group_id': "1", 'amount_type': 'percent'}

    @mapping
    def sales_tax(self, record):
        if 'TaxCode' in record:
            rec = record['TaxCode']
            rate_ids = []
            if 'SalesTaxRateList' in rec:
                if 'TaxRateDetail' in rec['SalesTaxRateList']:
                    for rate in rec['SalesTaxRateList']['TaxRateDetail']:
                        if rate['TaxRateRef']:
                            user_type = self.env['account.tax'].search(
                                [('name', '=', rate['TaxRateRef']['name']),
                                ('rate_quickbook_id', '=', rate['TaxRateRef']['value'])])
                            if user_type: 
                                rate_ids.append(user_type.id) 
            # if 'PurchaseTaxRateList' in rec:
            #     if 'TaxRateDetail' in rec['PurchaseTaxRateList']:
            #         for rate in rec['PurchaseTaxRateList']['TaxRateDetail']:
            #             if rate['TaxRateRef']:
            #                 user_type = self.env['account.tax'].search(
            #                     [('name', '=', rate['TaxRateRef']['name']),
            #                     ('quickbook_id', '=', rate['TaxRateRef']['value'])])
            #                 if user_type: 
            #                     rate_ids.append(user_type.id) 
            return {'children_tax_ids': [(6, 0, rate_ids)] or None, 'type_tax_use': 'sale'}
    
    # @mapping
    # def purchase_tax(self, record):
    #     if 'TaxCode' in record:
    #         rec = record['TaxCode']
    #         if 'PurchaseTaxRateList' in rec:
    #             if 'TaxRateDetail' in rec['PurchaseTaxRateList']:
    #                 rate_ids = []
    #                 for rate in rec['PurchaseTaxRateList']['TaxRateDetail']:
    #                     if rate['TaxRateRef']:
    #                         user_type = self.env['account.tax'].search(
    #                             [('name', '=', rate['TaxRateRef']['name']),
    #                             ('quickbook_id', '=', rate['TaxRateRef']['value'])])
    #                         if user_type: 
    #                             rate_ids.append(user_type.id) 
    #                 return {'children_tax_ids': [6, 0, rate_ids] or None, 'type_tax_use': 'purchase'}
    @mapping
    def id(self, record):
        if 'TaxCode' in record:
            rec = record['TaxCode']
            if rec['Id']:
                return {'quickbook_id': rec['Id']}
        elif 'TaxRate' in record:
            rec = record['TaxRate']
            if rec['Id']:
                return {'quickbook_id': rec['Id']}

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}



@quick
class TaxExporter(Exporter):
    _model_name = ['account.tax']

    def _get_data(self, product, fields):
        result = {}
        return result

    def _domain_for_update_Tax(self):
        return [
            ('backend_id', '!=', None),
            # ('tda_booking', '=', True),
        ]

    def run(self, binding_id, fields):
        """ Export the product inventory to wordpress """

        Tax_obj = self.env['account.tax']
        domain = self._domain_for_update_Tax()

        Tax_data = Tax_obj.search(domain)

        if Tax_data:
            for Tax in Tax_data:
                self.backend_adapter.update_Tax(Tax.quickbook_id,
                                                       {'taxservice': Tax})

    def run_sync(self, binding_id, data):
        
        self.backend_adapter.update_Tax(binding_id, {'taxservice': data})



TaxExporter = TaxExporter  # deprecated


##########################################
############ End Instructor ##############
##########################################
