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

class quickbook_acount_payment(models.Model):

    _inherit = 'account.payment'

    backend_id = fields.Many2one(comodel_name='qb.backend',
                                 string='Quick Backend', store=True,
                                 readonly=False, required=False,
                                 )

    quickbook_id = fields.Char(
        string='ID on Quickbook', readonly=False, required=False)
    sync_date = fields.Datetime(string='Last synchronization date')

    @api.multi
    def sync_payment(self):
        """ Export the configuration and data of a Account. """

        env = self.backend_id.get_environment(self._name)
        payment_exporter = env.get_connector_unit(AccountPaymentExporter)
        payment_exporter.run_sync(self.quickbook_id or 0, self)

    @job(default_channel='root.quick')
    def payment_import_batch(session, model_name, backend_id, filters=None):
        """ Import Chart of a Account. """

        env = get_environment(session, model_name, backend_id)
        importer = env.get_connector_unit(PaymentBatchImporter)
        importer.run(filters=filters)

    @job(default_channel='root.quick')
    @related_action(action=unwrap_binding)
    def export_payment_details(self, backend_id):
        """ Export the configuration and data of a Payment. """

        env = backend_id.get_environment(self._name)
        # env = get_environment(session, model_name, backend_id)
        inventory_exporter = env.get_connector_unit(
            AccountPaymentExporter)

        return inventory_exporter.run(backend_id, fields)
        
@quick
class AccountPaymentAdapter(GenericAdapter):
    _model_name = 'account.payment'
    _booking_model = 'payment'
    url = None

    def _call(self, method, arguments):
        print method
        try:
            return super(AccountPaymentAdapter, self)._call(method, arguments)
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
            if filters['url'] is 'payment':
                return self._call('/query?query=select%20from%20payment',
                                  [filters] if filters else [{}])

            # elif filters['url'] is 'salesreceipt':
            #     return self._call('/query?query=select%20ID%20from%20salesreceipt',
            #                       [filters] if filters else [{}])

    def update_payment(self, id, data):
        # product_stock.update is too slow

        return self._call_payment('update_payment', [int(id), data])


@quick
class PaymentBatchImporter(DelayedBatchImporter):

    """ Import the Quickbook Partners.

    For every partner in the list, a delayed job is created.
    """
    _model_name = ['account.payment']
    url = None

    def _import_record(self, quickbook_id, priority=None):
        """ Delay a job for the import """

        super(PaymentBatchImporter, self)._import_record(
            quickbook_id, priority=priority)

    def run(self, filters=None):
        """ Run the synchronization """
        from_date = filters.pop('from_date', None)
        to_date = filters.pop('to_date', None)

        count = 1
        record_ids = ['start']
        filters['url'] = 'payment'
        while record_ids:
            filters['count'] = count
            record_ids = self.backend_adapter.search(
                filters,
                from_date=from_date,
                to_date=to_date,
            )
    #         record_ids = self.env['bk.backend'].get_salesreceipt_ids(record_ids)
            _logger.info('search for payment %s returned %s',
                         filters, record_ids)
            count += 300
            self.url = 'payment'
            if 'Payment' in record_ids['QueryResponse']:
                record_ids = record_ids['QueryResponse']['Payment']
                for record_id in record_ids:

                    self._import_record(int(record_id['Id']), 40)
            else:
                record_ids = record_ids['QueryResponse']


PaymentBatchImporter = PaymentBatchImporter  # deprecated


@quick
class AccountImporter(WooImporter):
    _model_name = ['account.payment']
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
class PaymentImportMapper(ImportMapper):
    _model_name = 'account.payment'

    @mapping
    def partner_id(self, record):
        if 'Payment' in record:
            if 'CustomerRef' in record['Payment']:
                rec = record['Payment']
                if 'CustomerRef' in rec:
                    partner_id = self.env['res.partner'].search(
                        [('quickbook_id', '=', rec['CustomerRef']['value'])])
                    if partner_id and partner_id.customer:
                        partner_type = 'customer'
                    else:
                        partner_type = 'supplier'
                    partner_id = partner_id.id or False

                else:
                    partner_id = False

                return {'partner_id': partner_id, 'partner_type':partner_type}

    @mapping
    def communication(self, record):
        if 'Payment' in record:
            rec = record['Payment']
            for lines in rec['Line']:
                for trnx in lines['LinkedTxn']:
                    if trnx['TxnType'] == 'Invoice':
                        inv_id =  self.env['account.invoice'].search(
                        [('quickbook_id', '=', trnx['TxnId'])])
                        communication = inv_id.number or ''
                        ID = []
                        if inv_id:
                            ID = inv_id.id
                        return {'communication': communication, 'invoice_ids': [(4, ID, None)]}
    @mapping
    def active(self, record):
        if 'Payment' in record:
            rec = record['Payment']
            if 'Active' in rec:
                return {'active': rec['Active']}

    @mapping
    def journal_id(self, record):
        if 'Payment' in record:
            rec = record['Payment']
            
            return {'journal_id': 7}

    @mapping
    def payment_type(self, record):
        if 'Payment' in record:
            rec = record['Payment']
            
            return {'payment_type': 'inbound', 'payment_method_id': 1}

    @mapping
    def amount(self, record):
        if 'Payment' in record:
            rec = record['Payment']
            if 'TotalAmt' in rec:
                return {'amount': rec['TotalAmt']}
    @mapping
    def payment_date(self, record):
        if 'Payment' in record:
            rec = record['Payment']
            if 'TxnDate' in rec:
                return {'payment_date': rec['TxnDate']}


    @mapping
    def id(self, record):
        if 'Payment' in record:
            rec = record['Payment']
            if rec['Id']:
                return {'quickbook_id': rec['Id']}

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}



@quick
class AccountPaymentExporter(Exporter):
    _model_name = ['account.payment']

    def _get_data(self, product, fields):
        result = {}
        return result

    def _domain_for_update_payment(self):
        return [
            ('backend_id', '!=', None),
            # ('tda_booking', '=', True),
        ]

    def run(self, binding_id, fields):
        """ Export the product inventory to wordpress """

        payment_obj = self.env['account.payment']
        domain = self._domain_for_update_payment()

        payment_data = payment_obj.search(domain)

        if payment_data:
            for payment in payment_data:
                self.backend_adapter.update_payment(payment.quickbook_id,
                                                       {'payment': payment})

    def run_sync(self, binding_id, data):
        
        self.backend_adapter.update_payment(binding_id, {'payment': data})



AccountPaymentExporter = AccountPaymentExporter  # deprecated


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
#         AccountPaymentExporter)


#     return inventory_exporter.run(record_id, fields)


##########################################
############ End Instructor ##############
##########################################


@on_record_create(model_names=['account.payment'])
# @on_record_write(model_names=['account.payment'])
def create_payment(session, model_name, record_id, fields=None):
    if 'job_uuid' in session.context.keys():
        payment_id = session[model_name].search([('id', '=', record_id)])
        if payment_id:
            payment_id.post()
        
