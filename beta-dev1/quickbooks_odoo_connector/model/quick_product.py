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
from ..unit.import_synchronizer import (DelayedBatchImporter,  WooImporter)
from odoo.addons.connector.unit.synchronizer import (Importer, Exporter)
from odoo.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper
                                                  )
from odoo.addons.queue_job.job import job, related_action
import xmlrpclib

from odoo.exceptions import except_orm, Warning, RedirectWarning
from ..related_action import unwrap_binding
import random

from requests_oauthlib import OAuth1Session, OAuth2Session
import requests
from requests_oauthlib import OAuth1
import urllib2
import base64
_logger = logging.getLogger(__name__)


class quickbook_product_template(models.Model):

    _inherit = 'product.template'

    backend_id = fields.Many2one(comodel_name='qb.backend',
                                      string='Quick Backend', store=True,
                                      readonly=False, required=False,
                                      )

    quickbook_id = fields.Char(
        string='ID on Quickbook', readonly=False, required=False)
    sync_date = fields.Datetime(string='Last synchronization date')
    # select from item
    image_name = fields.Char('Image Name', help='QBO Image Name') 
    image_id = fields.Char('Image ID', help='QBO Image ID')
    purchase_tax_included = fields.Boolean(string='Purchase Tax Included',default=False)
    sales_tax_included = fields.Boolean(string='Sales Tax Included', default=False)
    abatement_rate = fields.Char(string='AbatementRate')
    reverse_charge_rate = fields.Char(string='ReverseChargeRate')
    taxable = fields.Boolean(string='Taxable', default=False)

    @api.multi
    def sync_product(self):
        """ Export the inventory configuration and quantity of a product. """
        
        env = self.backend_id.get_environment(self._name)
        product_exporter = env.get_connector_unit(ItemExporter)
        product_exporter.run_sync(self.quickbook_id or 0, self)

    @api.multi
    def sync_product_image(self):
        """ Export Product images."""
        
        env = self.backend_id.get_environment(self._name)
        product_exporter = env.get_connector_unit(ItemExporter)
        product_exporter.run_image_sync(self.image_id or 0, self)
    
    @api.multi   
    @job(default_channel='root.quick')
    def Item_import_batch(session, model_name, backend_id, filters=None):
        """ Import the inventory configuration and quantity of a product. """

        env = get_environment(session, model_name, backend_id)
        importer = env.get_connector_unit(ItemBatchImporter)
        importer.run(filters=filters)

    @job(default_channel='root.quick')
    @related_action(action=unwrap_binding)
    def export_item_inventory(self, backend_id):
        """ Export the inventory configuration and quantity of a product. """

        env = backend_id.get_environment(self._name)
        # env = get_environment(session, model_name, backend_id)
        inventory_exporter = env.get_connector_unit(
            ItemExporter)

        return inventory_exporter.run(backend_id, fields)
        
@quick
class ItemAdapter(GenericAdapter):
    _model_name = 'product.template'
    _booking_model = 'item'
    url = None

    def _call(self, method, arguments):
        print method
        try:
            return super(ItemAdapter, self)._call(method, arguments)
        except xmlrpclib.Fault as err:
            # this is the error in the Quickbook API
            # when the Item does not exist
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
        # the search method is on ol_Item instead of Item
        # return self._call('staff/list',
        #                   [filters] if filters else [{}])

        if 'url' in filters:
            if filters['url'] is 'item':
                return self._call('/query?query=select%20from%20item',
                                  [filters] if filters else [{}])

            # elif filters['url'] is 'Item':
            #     return self._call('/query?query=select%20ID%20from%20Item',
            #                       [filters] if filters else [{}])

    def update_item(self, id, data):
        # product_stock.update is too slow

        return self._call_item('update_item', [int(id), data])

    def update_item_image(self, id, data):
        # product_stock.update is too slow

        return self._call_attachments('update_item_image', [int(id), data])


@quick
class ItemBatchImporter(DelayedBatchImporter):

    """ Import the Quickbook Partners.

    For every partner in the list, a delayed job is created.
    """
    _model_name = ['product.template']
    url = None

    def _import_record(self, quickbook_id, priority=None):
        """ Delay a job for the import """

        super(ItemBatchImporter, self)._import_record(
            quickbook_id, priority=priority)

    def run(self, filters=None):
        """ Run the synchronization """
        from_date = filters.pop('from_date', None)
        to_date = filters.pop('to_date', None)
        count = 1
        record_ids = ['start']
        filters['url'] = 'item'
        while record_ids:
            filters['count'] = count
            record_ids = self.backend_adapter.search(
                filters,
                from_date=from_date,
                to_date=to_date,
            )
    #         record_ids = self.env['bk.backend'].get_Item_ids(record_ids)
            _logger.info('search for item %s returned %s',
                         filters, record_ids)
            count += 300
            self.url = 'item'
            if 'Item' in record_ids['QueryResponse']:
                record_ids = record_ids['QueryResponse']['Item']
                for record_id in record_ids:

                    self._import_record(int(record_id['Id']), 40)
            else:
                record_ids = record_ids['QueryResponse']


ItemBatchImporter = ItemBatchImporter  # deprecated


@quick
class ItemImporter(WooImporter):
    _model_name = ['product.template']
    url = None

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        record = self.woo_record
        # record = record['product']
        if 'IncomeAccountRef' in record['Item']:
            if record['Item']['IncomeAccountRef']:
                self._import_dependency(record['Item']['IncomeAccountRef']['value'],
                                    'account.account')
        if 'ExpenseAccountRef' in record['Item']:
            if record['Item']['ExpenseAccountRef']:
                self._import_dependency(record['Item']['ExpenseAccountRef']['value'],
                                        'account.account')
        if 'SalesTaxCodeRef' in record['Item']:
            if record['Item']['SalesTaxCodeRef']:
                self._import_dependency(record['Item']['SalesTaxCodeRef']['value'],
                                    'account.tax')
        if 'PurchaseTaxCodeRef' in record['Item']:
            if record['Item']['PurchaseTaxCodeRef']:
                self._import_dependency(record['Item']['PurchaseTaxCodeRef']['value'],
                                        'account.tax')
        return

    def _create(self, data):
        openerp_binding = super(ItemImporter, self)._create(data)
        return openerp_binding

    def _import_image(self, binding):
        """ Hook called at the end of the import """
        pro_id  = binding
        if self.backend_record.type == 'oauth1':
            headeroauth = OAuth1(self.backend_record.client_key, self.backend_record.client_secret,
                     self.backend_record.resource_owner_key, self.backend_record.resource_owner_secret,
                     signature_type='auth_header')
            ris = self.backend_record.location+self.backend_record.company_id + \
                    '/query?query=select%20Id%20from%20attachable%20where%20AttachableRef.EntityRef.Type%20%3D%20%27Item%27%20and%20AttachableRef.EntityRef.value%3D%27'+str(pro_id)+'%27'+'&minorversion=4'

            headers = {'accept': 'application/json'}
            r = requests.get(ris, auth=headeroauth, headers=headers)
            response = r.json()
        elif self.backend_record.type == 'oauth2':
            headeroauth = OAuth2Session(self.backend_record.client_key)
            ris = self.backend_record.location+self.backend_record.company_id + \
                    '/query?query=select%20Id%20from%20attachable%20where%20AttachableRef.EntityRef.Type%20%3D%20%27Item%27%20and%20AttachableRef.EntityRef.value%3D%27'+str(pro_id)+'%27'+'&minorversion=4'

            headers = {'Authorization': 'Bearer %s' %self.backend_record.access_token, 
                        'content-type': 'application/json', 'accept': 'application/json'}
            r = headeroauth.get(ris, headers=headers)
            response = r.json()
            if response['QueryResponse']:
                img_id = response['QueryResponse']['Attachable'][0]['Id']
                method = self.backend_record.location+self.backend_record.company_id + \
                    '/attachable/' + str(img_id)+'?minorversion=4'
                image = headeroauth.get(method, headers=headers)
                re = image.json()
                return re

    def _get_binary_image(self, image_data):
        url = image_data.encode('utf8').strip()
        url = str(url).replace("\\", '')
        try:
            if url != '':
                request = urllib2.Request(url, headers={'User-Agent': "odoo"})
                binary = urllib2.urlopen(request)
            else:
                return
        except urllib2.HTTPError as err:
            if err.code == 404:
                # the image is just missing, we skip it
                return
            else:
                # we don't know why we couldn't download the image
                # so we propagate the error, the import will fail
                # and we have to check why it couldn't be accessed
                raise
        else:
            return {'image': binary.read(), 'url': url}

    def _after_import(self, binding):
        """ Hook called at the end of the import """
        record = self.woo_record
        if record['Item']['Id']:
            values  = self._import_image(record['Item']['Id'])
            if values:
                if values['Attachable'] and values['Attachable']['ContentType'] == 'image/jpeg':
                    if values['Attachable']['TempDownloadUri']:
                        featured_src = values['Attachable']['TempDownloadUri']
                        featured = self._get_binary_image(featured_src)
                        if featured:
                            binding.write({'image': base64.b64encode(featured['image']), 'image_name': values['Attachable']['FileName'],'image_id': values['Attachable']['Id']})


ItemImporter = ItemImporter  # deprecated

@quick
class ItemImportMapper(ImportMapper):
    _model_name = 'product.template'

    @mapping
    def name(self, record):
        if 'Item' in record:
        	rec = record['Item']
        	return{'name': rec['Name']}

    @mapping
    def active(self, record):
        if 'Item' in record:
        	rec = record['Item']
        	return{'active': rec['Active']}

    @mapping
    def price(self, record):
        if 'Item' in record:
            # extra = 10 'price_extra': extra
            return {'lst_price': float(record['Item']['UnitPrice']) or 0.0}
    @mapping
    def purchase_tax_included(self, record):
        if 'Item' in record:
            rec = record['Item']
            if 'PurchaseTaxIncluded' in rec:
                return{'purchase_tax_included': rec['PurchaseTaxIncluded']}
            if '' in rec:
                return{'sales_tax_included': rec['SalesTaxIncluded']}

    @mapping
    def taxable(self, record):
        if 'Item' in record:
            rec = record['Item']
            if 'Taxable' in rec:
                return{'taxable': rec['Taxable']}

    @mapping
    def abatement_rate(self, record):
        if 'Item' in record:
            rec = record['Item']
            if 'AbatementRate' in rec:
                return{'abatement_rate': rec['AbatementRate']}

    @mapping
    def reverse_charge_rate(self, record):
        if 'Item' in record:
            rec = record['Item']
            if 'ReverseChargeRate' in rec:
                return{'reverse_charge_rate': rec['ReverseChargeRate']}




    # @mapping
    # def categ_id(self, record):
    #     if 'Item' in record:
    #         if 'Type' in record['Item']:
    #             rec = record['Item']
    #             if rec['Type']:
    #                 categ_id = self.env['product.template'].search(
    #                     [('name', '=', rec['Type'])])
    #                 if not categ_id:
    #                     categ_id = self.env['product.product'].create(
    #                         {'name': rec['Type']})
    #                 categ_id = categ_id.id or False
    #             else:
    #                 categ_id = False
    #             return {'categ_id': categ_id}
    @mapping
    def type(self, record):
        if 'Item' in record:
            if 'Type' in record['Item']:
                rec = record['Item']
                if rec['Type']:
                    if rec['Type'] == 'Service':
                        product_type = 'service'
                    if rec['Type'] == 'NonInventory':
                        product_type = 'consu'
                    if rec['Type'] == 'Inventory':
                        product_type = 'product'
                    return {'type': product_type}
    # @mapping
    # def track_all(self, record):
    #     if 'Item' in record:
    #         rec = record['Item']
    #         return{'track_all': rec['TrackQtyOnHand']}
    @mapping
    def description(self, record):
        if 'Item' in record:
            rec = record['Item']
            if 'Description' in rec:
                return{'description': rec['Description']}

    @mapping
    def description_sale(self, record):
        if 'Item' in record:
            rec = record['Item']
            if 'Description' in rec:
                return{'description_sale': rec['Description']}

    @mapping
    def standard_price(self, record):
        if 'Item' in record:
            rec = record['Item']
            return{'standard_price': rec['PurchaseCost']}

    # @mapping
    # def active(self, record):
    #     if 'Item' in record:
    #     	rec = record['Item']
    #     	return{'standard_price': rec['InvStartDate']}

    @mapping
    def qty_available(self, record):
        if 'Item' in record:
            rec = record['Item']
            if 'QtyOnHand' in rec:
                return {'qty_available': rec['QtyOnHand']}

    @mapping
    def property_account_income_id(self, record):
        if 'Item' in record:
            rec = record['Item']
            if 'IncomeAccountRef' in rec:
                if rec['IncomeAccountRef']:
                        property_account_income = self.env['account.account'].search(
                            [('name', '=', rec['IncomeAccountRef']['name']), ('quickbook_id', '=', rec['IncomeAccountRef']['value'])])
                        # if not property_account_income:
                        #     property_account_income = self.env['account.account'].create(
                        #         {'name': rec['IncomeAccountRef']['name'], 'code': random.randint(100,1000), 'quickbook_id': rec['IncomeAccountRef']['value']})
                        property_account_income = property_account_income.id or False
                else:
                        property_account_income = False
                return {'property_account_income_id': property_account_income}

    @mapping
    def property_account_expense_id(self, record):
        if 'Item' in record:
            rec = record['Item']
            if 'ExpenseAccountRef' in rec:
                if rec['ExpenseAccountRef']:
                        property_account_expense = self.env['account.account'].search(
                            [('name', '=', rec['ExpenseAccountRef']['name']), ('quickbook_id', '=', rec['ExpenseAccountRef']['value'])])
                        # if not property_account_expense:
                        #     property_account_expense = self.env['account.account'].create(
                        #         {'name': rec['ExpenseAccountRef']['name'], 'code': random.randint(100,1000), 'quickbook_id': rec['ExpenseAccountRef']['value']})
                        property_account_expense = property_account_expense.id or False
                else:
                        property_account_expense = False
                return {'property_account_expense_id': property_account_expense}




    @mapping
    def taxes_id(self, record):
        if 'Item' in record:
            taxes_ids = []
            rec = record['Item']
            if 'SalesTaxCodeRef' in rec:
                if rec['SalesTaxCodeRef']:
                    taxes_id = self.env['account.tax'].search(
                        [('quickbook_id', '=', rec['SalesTaxCodeRef']['value'])])
                    
                    taxes_ids.append(taxes_id.id)
            return {'taxes_id': [(6,0,taxes_ids)] or None}

    @mapping
    def supplier_taxes_id(self, record):
        if 'Item' in record:
            supplier_taxes_ids = []
            rec = record['Item']
            if 'PurchaseTaxCodeRef' in rec:
                if rec['PurchaseTaxCodeRef']:
                    supplier_taxes_id = self.env['account.tax'].search(
                        [('quickbook_id', '=', rec['PurchaseTaxCodeRef']['value'])])
                    
                    supplier_taxes_ids.append(supplier_taxes_id.id)
            return {'supplier_taxes_id': [(6,0,supplier_taxes_ids)] or None}

    @mapping
    def description_purchase(self, record):
        if record['Item']:
            rec = record['Item']
            if 'PurchaseDesc' in rec:

                return {'description_purchase': rec['PurchaseDesc'] or None}

    @mapping
    def id(self, record):
        if 'Item' in record:
            rec = record['Item']
            if rec['Id']:
                return {'quickbook_id': rec['Id']}

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}


@quick
class ItemExporter(Exporter):
    _model_name = ['product.template']

    def _get_data(self, product, fields):
        result = {}
        return result

    def _domain_for_update_item(self):
        return [
            ('backend_id', '!=', None),
            # ('tda_booking', '=', True),
        ]

    def run(self, binding_id, fields):
        """ Export the product inventory to wordpress """

        item_obj = self.env['product.template']
        domain = self._domain_for_update_item()

        item_data = item_obj.search(domain)

        if item_data:
            for item in item_data:
                self.backend_adapter.update_item(item.quickbook_id,
                                                       {'item': item})

    def run_sync(self, binding_id, data):
        
        self.backend_adapter.update_item(binding_id, {'item': data})

    def run_image_sync(self, binding_id, data):
        
        self.backend_adapter.update_item_image(binding_id, {'image': data})



ItemExporter = ItemExporter  # deprecated


# @job(default_channel='root.quick')
# @related_action(action=unwrap_binding)
# def export_item_inventory(session, model_name, record_id, fields=None):
#     """ Export the inventory configuration and quantity of a product. """
#     item = session.env[model_name].browse(record_id)
#     try:
#         if item.backend_id:
#             backend_id = item.backend_id.id
#         else:
#             backend_id = record_id

#     finally:
#         pass

#     env = get_environment(session, model_name, backend_id)
#     inventory_exporter = env.get_connector_unit(
#         ItemExporter)


#     return inventory_exporter.run(record_id, fields)


##########################################
############ End Instructor ##############
##########################################
