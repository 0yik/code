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

    _inherit = 'account.payment.term'

    backend_id = fields.Many2one(comodel_name='qb.backend',
                                 string='Quick Backend', store=True,
                                 readonly=False, required=False,
                                 )

    quickbook_id = fields.Char(
        string='ID on Quickbook', readonly=False, required=False)
    sync_date = fields.Datetime(string='Last synchronization date')

    @api.multi
    def sync_term(self):
        """ Export the configuration and data of a Term. """

        env = self.backend_id.get_environment(self._name)
        product_exporter = env.get_connector_unit(TermExporter)
        product_exporter.run_sync(self.quickbook_id or 0, self)

    @job(default_channel='root.quick')
    def term_import_batch(session, model_name, backend_id, filters=None):
        """ Import Chart of a Term. """

        env = get_environment(session, model_name, backend_id)
        importer = env.get_connector_unit(TermBatchImporter)
        importer.run(filters=filters)

    @job(default_channel='root.quick')
    @related_action(action=unwrap_binding)
    def export_Term_details(self, backend_id):
        """ Export the configuration and data of a Term. """

        env = backend_id.get_environment(self._name)
        # env = get_environment(session, model_name, backend_id)
        inventory_exporter = env.get_connector_unit(
            TermExporter)

        return inventory_exporter.run(backend_id, fields)
        
@quick
class TermAdapter(GenericAdapter):
    _model_name = 'account.payment.term'
    _booking_model = 'term'
    url = None

    def _call(self, method, arguments):
        print method
        try:
            return super(TermAdapter, self)._call(method, arguments)
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
            if filters['url'] is 'term':
                return self._call('/query?query=select%20from%20term',
                                  [filters] if filters else [{}])

            # elif filters['url'] is 'salesreceipt':
            #     return self._call('/query?query=select%20ID%20from%20salesreceipt',
            #                       [filters] if filters else [{}])

    def update_Term(self, id, data):
        # product_stock.update is too slow
        return self._call_Term('update_term', [int(id), data])


@quick
class TermBatchImporter(DelayedBatchImporter):

    """ Import the Quickbook Partners.

    For every partner in the list, a delayed job is created.
    """
    _model_name = ['account.payment.term']
    url = None

    def _import_record(self, quickbook_id, priority=None):
        """ Delay a job for the import """

        super(TermBatchImporter, self)._import_record(
            quickbook_id, priority=priority)

    def run(self, filters=None):
        """ Run the synchronization """
        from_date = filters.pop('from_date', None)
        to_date = filters.pop('to_date', None)

        count = 1
        record_ids = ['start']
        filters['url'] = 'term'
        while record_ids:
            filters['count'] = count
            record_ids = self.backend_adapter.search(
                filters,
                from_date=from_date,
                to_date=to_date,
            )
    #         record_ids = self.env['bk.backend'].get_salesreceipt_ids(record_ids)
            _logger.info('search for term %s returned %s',
                         filters, record_ids)
            count += 300
            self.url = 'term'
            if 'Term' in record_ids['QueryResponse']:
                record_ids = record_ids['QueryResponse']['Term']
                for record_id in record_ids:
                    self._import_record(int(record_id['Id']), 40)
            else:
                record_ids = record_ids['QueryResponse']

TermBatchImporter = TermBatchImporter  # deprecated


@quick
class TermImporter(WooImporter):
    _model_name = ['account.payment.term']
    url = None

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        return

    def _create(self, data):
        openerp_binding = super(TermImporter, self)._create(data)
        return openerp_binding

    def _after_import(self, binding):
        """ Hook called at the end of the import """
        return

TermImporter = TermImporter  # deprecated


@quick
class TermImportMapper(ImportMapper):
    _model_name = 'account.payment.term'
    #
# rec['Line'][0]['SalesItemLineDetail']['TaxCodeRef']

    @mapping
    def name(self, record):
        if 'Term' in record:

            rec = record['Term']
            if 'Name' in rec:
                return {'name': rec['Name'], 'note': rec['Name'],}

    @mapping
    def active(self, record):
        if 'Term' in record:
            rec = record['Term']
            if 'Active' in rec:
                return {'active': rec['Active']}

    @mapping
    def type(self, record):
        if 'Term' in record:
            rec = record['Term']
            if 'Type' in rec:
                lines_pay_ids = []
                term = self.env['account.payment.term'].search([('quickbook_id', '=', rec['Id']),('name', '=', rec['Name'])])
                line = term.line_ids
                if rec['Type'] == 'STANDARD':
                    value = 'balance'
                    option = 'day_after_invoice_date'
                    duedate = rec['DueDays']

                if rec['Type'] == 'DATE_DRIVEN':
                    value = 'balance'
                    option = 'last_day_following_month'
                    duedate = 0
                
                result = {
                    'days': duedate,
                    'value': value,
                    'option': option,

                    }
                if not line:

                    lines_pay_ids.append([0,0,result]) or False
                else:
                    lines_pay_ids.append([1,line.id,result])

                return {'line_ids': lines_pay_ids}

    @mapping
    def id(self, record):
        if 'Term' in record:
            rec = record['Term']
            if rec['Id']:
                return {'quickbook_id': rec['Id']}

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}



@quick
class TermExporter(Exporter):
    _model_name = ['account.payment.term']

    def _get_data(self, product, fields):
        result = {}
        return result

    def _domain_for_update_Term(self):
        return [
            ('backend_id', '!=', None),
            # ('tda_booking', '=', True),
        ]

    def run(self, binding_id, fields):
        """ Export the product inventory to wordpress """

        Term_obj = self.env['account.payment.term']
        domain = self._domain_for_update_Term()

        Term_data = Term_obj.search(domain)

        if Term_data:
            for Term in Term_data:
                self.backend_adapter.update_Term(Term.quickbook_id,
                                                       {'term': Term})

    def run_sync(self, binding_id, data):
        
        self.backend_adapter.update_Term(binding_id, {'term': data})



TermExporter = TermExporter  # deprecated


# @job(default_channel='root.quick')
# @related_action(action=unwrap_binding)
# def export_Term_details(session, model_name, record_id, fields=None):
#     """ Export the inventory configuration and quantity of a product. """
#     Term = session.env[model_name].browse(record_id)
#     try:
#         if Term.backend_id:
#             backend_id = Term.backend_id.id
#         else:
#             backend_id = record_id

#     finally:
#         pass

#     env = get_environment(session, model_name, backend_id)
#     inventory_exporter = env.get_connector_unit(
#         TermExporter)


#     return inventory_exporter.run(record_id, fields)


##########################################
############ End Instructor ##############
##########################################
