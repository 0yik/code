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

    _inherit = 'account.account'

    backend_id = fields.Many2one(comodel_name='qb.backend',
                                 string='Quick Backend', store=True,
                                 readonly=False, required=False,
                                 )

    quickbook_id = fields.Char(
        string='ID on Quickbook', readonly=False, required=False)
    sync_date = fields.Datetime(string='Last synchronization date')

    @api.multi
    def sync_account(self):
        """ Export the configuration and data of a Account. """

        env = self.backend_id.get_environment(self._name)
        product_exporter = env.get_connector_unit(AccountExporter)
        product_exporter.run_sync(self.quickbook_id or 0, self)

    @job(default_channel='root.quick')
    def account_import_batch(session, model_name, backend_id, filters=None):
        """ Import Chart of a Account. """

        env = get_environment(session, model_name, backend_id)
        importer = env.get_connector_unit(AccountBatchImporter)
        importer.run(filters=filters)

    @job(default_channel='root.quick')
    @related_action(action=unwrap_binding)
    def export_account_details(self, backend_id):
        """ Export the configuration and data of a Account. """

        env = backend_id.get_environment(self._name)
        # env = get_environment(session, model_name, backend_id)
        inventory_exporter = env.get_connector_unit(
            AccountExporter)

        return inventory_exporter.run(backend_id, fields)
        
@quick
class AccountAdapter(GenericAdapter):
    _model_name = 'account.account'
    _booking_model = 'account'
    url = None

    def _call(self, method, arguments):
        print method
        try:
            return super(AccountAdapter, self)._call(method, arguments)
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
            if filters['url'] is 'account':
                return self._call('/query?query=select%20from%20account',
                                  [filters] if filters else [{}])

            # elif filters['url'] is 'salesreceipt':
            #     return self._call('/query?query=select%20ID%20from%20salesreceipt',
            #                       [filters] if filters else [{}])

    def update_account(self, id, data):
        # product_stock.update is too slow

        return self._call_account('update_account', [int(id), data])


@quick
class AccountBatchImporter(DelayedBatchImporter):

    """ Import the Quickbook Partners.

    For every partner in the list, a delayed job is created.
    """
    _model_name = ['account.account']
    url = None

    def _import_record(self, quickbook_id, priority=None):
        """ Delay a job for the import """

        super(AccountBatchImporter, self)._import_record(
            quickbook_id, priority=priority)

    def run(self, filters=None):
        """ Run the synchronization """
        from_date = filters.pop('from_date', None)
        to_date = filters.pop('to_date', None)

        count = 1
        record_ids = ['start']
        filters['url'] = 'account'
        while record_ids:
            filters['count'] = count
            record_ids = self.backend_adapter.search(
                filters,
                from_date=from_date,
                to_date=to_date,
            )
    #         record_ids = self.env['bk.backend'].get_salesreceipt_ids(record_ids)
            _logger.info('search for account %s returned %s',
                         filters, record_ids)
            count += 300
            self.url = 'account'
            if 'Account' in record_ids['QueryResponse']:
                record_ids = record_ids['QueryResponse']['Account']
                for record_id in record_ids:

                    self._import_record(int(record_id['Id']), 40)
            else:
                record_ids = record_ids['QueryResponse']


AccountBatchImporter = AccountBatchImporter  # deprecated


@quick
class AccountImporter(WooImporter):
    _model_name = ['account.account']
    url = None

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        return

    def _create(self, data):
        openerp_binding = super(AccountImporter, self)._create(data)
        return openerp_binding

    def _after_import(self, binding):
        """ Hook called at the end of the import """
        return

AccountImporter = AccountImporter  # deprecated


@quick
class AccountImportMapper(ImportMapper):
    _model_name = 'account.account'
    #
# rec['Line'][0]['SalesItemLineDetail']['TaxCodeRef']

    @mapping
    def name(self, record):
        if 'Account' in record:
            rec = record['Account']
            if 'Name' in rec:
                return {'name': rec['Name'],
                'code': self.env['ir.sequence'].next_by_code('account.account')}

    @mapping
    def active(self, record):
        if 'Account' in record:
            rec = record['Account']
            if 'SubAccount' in rec:
                return {'active': rec['Active']}

    @mapping
    def user_type_id(self, record):
        if 'Account' in record:

            rec = record['Account']
            if 'AccountType' in rec:
                user_type = self.env['account.account.type'].search(
                    [('name', '=', rec['AccountType'])])
                if not user_type:
                    user_type = self.env['account.account.type'].create(
                        {'name':  rec['AccountType'],
                        'code': random.randint(100,1000)})
                user_type = user_type.id or False
            else:
                user_type = False
            return {'user_type_id': user_type}

    @mapping
    def balance(self, record):
        if 'Account' in record:
            rec = record['Account']
            if 'CurrentBalance' in rec:
                return {'balance': rec['CurrentBalance']}

    # @mapping
    # def currency_id(self, record):
    #     if 'Account' in record:

    #         rec = record['Account']
    #         if 'CurrencyRef' in rec:
    #             currency_id = self.env['res.currency'].search(
    #                 [('name', '=', rec['CurrencyRef']['value'])])
    #             if not currency_id:
    #                 currency_id = self.env['res.currency'].create(
    #                     {'name', '=', rec['CurrencyRef']['value']})
    #             currency_id = currency_id.id or False
    #         else:
    #             currency_id = False
    #             return {'currency_id': currency_id}

        # "Classification": "Asset",

        # currency_id "CurrencyRef":
        # {
        #     "value": "USD",
        #     "name": "United States Dollar"
        # },

    @mapping
    def id(self, record):
        if 'Account' in record:
            rec = record['Account']
            if rec['Id']:
                return {'quickbook_id': rec['Id']}

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}



@quick
class AccountExporter(Exporter):
    _model_name = ['account.account']

    def _get_data(self, product, fields):
        result = {}
        return result

    def _domain_for_update_account(self):
        return [
            ('backend_id', '!=', None),
            # ('tda_booking', '=', True),
        ]

    def run(self, binding_id, fields):
        """ Export the product inventory to wordpress """

        account_obj = self.env['account.account']
        domain = self._domain_for_update_account()

        account_data = account_obj.search(domain)

        if account_data:
            for account in account_data:
                self.backend_adapter.update_account(account.quickbook_id,
                                                       {'account': account})

    def run_sync(self, binding_id, data):
        
        self.backend_adapter.update_account(binding_id, {'account': data})



AccountExporter = AccountExporter  # deprecated


# @job(default_channel='root.quick')
# @related_action(action=unwrap_binding)
# def export_account_details(session, model_name, record_id, fields=None):
#     """ Export the inventory configuration and quantity of a product. """
#     account = session.env[model_name].browse(record_id)
#     try:
#         if account.backend_id:
#             backend_id = account.backend_id.id
#         else:
#             backend_id = record_id

#     finally:
#         pass

#     env = get_environment(session, model_name, backend_id)
#     inventory_exporter = env.get_connector_unit(
#         AccountExporter)


#     return inventory_exporter.run(record_id, fields)


##########################################
############ End Instructor ##############
##########################################
