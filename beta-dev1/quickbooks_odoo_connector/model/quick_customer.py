from odoo import models, fields, api

import logging
from odoo.addons.connector.event import on_record_create, on_record_write
# from odoo.addons.connector.session import ConnectorSession
from odoo.addons.connector.connector import ConnectorEnvironment
from ..connector import get_environment
from ..backend import quick
from ..unit.backend_adapter import (GenericAdapter)
from ..unit.import_synchronizer import ( DelayedBatchImporter, DirectBatchImporter, WooImporter)
from odoo.addons.connector.unit.synchronizer import (Importer, Exporter)
from odoo.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper
                                                  )
from odoo.addons.queue_job.job import job, related_action
import xmlrpclib

from odoo.exceptions import except_orm, Warning, RedirectWarning
from .quick_vendor import VendorTemplateInventoryExporter

_logger = logging.getLogger(__name__)
from ..related_action import unwrap_binding

class quick_customer(models.Model):

    _inherit = 'res.partner'

    backend_id = fields.Many2one(comodel_name='qb.backend',
                                 string='Quick Backend', store=True,
                                 readonly=False, required=False,
                                 )
    company_name = fields.Char('Company Name', help='Quickbook Company Name')
    quickbook_id = fields.Char(
        string='ID on Quickbook', readonly=False, required=False)
    sync_date = fields.Datetime(string='Last synchronization date')
    first_name = fields.Char('First Name', readonly=False)
    last_name = fields.Char('Last Name', readonly=False)


    @api.multi
    def sync_res_partner(self):
        """ Export Customer / Vendors Details. """

        env = self.backend_id.get_environment(self._name)
        if self.supplier:
            supplier_exporter = env.get_connector_unit(
                VendorTemplateInventoryExporter)
            supplier_exporter.run_sync(self.quickbook_id, self)
        if self.customer:
            customer_exporter = env.get_connector_unit(
                CustomerExporter)
            customer_exporter.run_sync(self.quickbook_id, self)

    @api.multi
    @job(default_channel='root.quick')
    def customer_import_batch(session, model_name, backend_id, filters=None):
        """ Import Customer Details. """

        env = get_environment(session, model_name, backend_id)
        importer = env.get_connector_unit(CustomerBatchImporter)
        importer.run(filters=filters)

    @job(default_channel='root.quick')
    @related_action(action=unwrap_binding)
    def export_customer_inventory(self, backend_id):
        """ Export Customer Details. """

        env = backend_id.get_environment(self._name)
        # env = get_environment(session, model_name, backend_id)
        inventory_exporter = env.get_connector_unit(
            CustomerExporter)

        return inventory_exporter.run(backend_id, fields)

@quick
class CustomerAdapter(GenericAdapter):
    _model_name = 'res.partner'
    _booking_model = 'customer'
    url = None

    def _call(self, method, arguments):
        print method
        try:
            return super(CustomerAdapter, self)._call(method, arguments)
        except xmlrpclib.Fault as err:
            # this is the error in the Quickbook API
            # when the Customer does not exist
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
        else:
            filters.setdefault('updated_at', {})
            filters['updated_at']['from'] = 'null'
        # the search method is on ol_customer instead of customer
        # return self._call('staff/list',
        #                   [filters] if filters else [{}])
        
        if 'url' in filters:
            if filters['url'] is 'vendor':
                return self._call('/query?query=select%20%2A%20from%20vendor',
                                  [filters] if filters else [{}])

            elif filters['url'] is 'customer':
                return self._call('/query?query=select%20ID%20from%20customer',
                          [filters] if filters else [{}])
                # return self._call('/query?query=select%20ID%20from%20customer',
                #                   [filters] if filters else [{}])

    def update_vendor(self, id, data):
        # product_stock.update is too slow

        return self._call_vendor('update_vendor', [int(id), data])

    def update_customer(self, id, data):
        # product_stock.update is too slow

        return self._call_customer('update_customer', [int(id), data])


@quick
class CustomerBatchImporter(DelayedBatchImporter):

    """ Import the Quickbook Partners.

    For every partner in the list, a delayed job is created.
    """
    _model_name = ['res.partner']
    url = None

    def _import_record(self, quickbook_id, priority=None):
        """ Delay a job for the import """
        super(CustomerBatchImporter, self)._import_record(
            quickbook_id, priority=priority)

    def run(self, filters=None):
        """ Run the synchronization """
        from_date = filters.pop('from_date', None)
        to_date = filters.pop('to_date', None)

        count = 1
        record_ids = ['start']
        filters['url'] = 'customer'
        while record_ids:
            filters['count'] = count
            record_ids = self.backend_adapter.search(
                filters,
                from_date=from_date,
                to_date=to_date,
            )
    #         record_ids = self.env['bk.backend'].get_customer_ids(record_ids)
            _logger.info('search for customers %s returned %s',
                     filters, record_ids)
            count += 300
            self.url = 'customer'
            if 'Customer' in record_ids['QueryResponse']:
                record_ids = record_ids['QueryResponse']['Customer']
                for record_id in record_ids:

                    self._import_record(int(record_id['Id']), 40)
            else:
                record_ids = record_ids['QueryResponse']

CustomerBatchImporter = CustomerBatchImporter  # deprecated


@quick
class CustomerImporter(WooImporter):
    _model_name = ['res.partner']
    url = None

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        return

    def _create(self, data):
        openerp_binding = super(CustomerImporter, self)._create(data)
        return openerp_binding

    def _after_import(self, binding):
        """ Hook called at the end of the import """
        return

CustomerImporter = CustomerImporter  # deprecated


@quick
class InstructorImportMapper(ImportMapper):
    _model_name = 'res.partner'

    @mapping
    def name(self, record):
        if 'Customer' in record:
            rec = record['Customer']
            if 'GivenName' and 'FamilyName' in rec:
                return {'first_name': rec['GivenName'], 'last_name': rec['FamilyName'], 'name': rec['DisplayName']}
            else:
                return {'name': rec['DisplayName']}
        elif 'Vendor' in record:
            rec = record['Vendor']
            if 'GivenName' and 'FamilyName' in rec:
                return {'first_name': rec['GivenName'], 'last_name': rec['FamilyName'], 'name': rec['DisplayName']}
            else:
                return {'name': rec['DisplayName']}

    @mapping
    def company(self, record):
        if 'Customer' in record:
            if 'CompanyName' in record['Customer']:
                rec = record['Customer']
                if rec['CompanyName']:
                    return {'company_name': rec['CompanyName']}
        elif 'Vendor' in record:
            if 'CompanyName' in record['Vendor']:
                rec = record['Vendor']
                if rec['CompanyName']:
                    return {'company_name': rec['CompanyName']}
                    

    # @mapping
    # def company(self, record):
    #     if 'Customer' in record:
    #         if 'CompanyName' in record['Customer']:
    #             rec = record['Customer']
    #             if rec['CompanyName']:
    #                 parent_id = self.env['res.partner'].search(
    #                     [('is_company', '=', True),
    #                      ('name', '=', rec['CompanyName'])])
    #                 if not parent_id:
    #                     parent_id = self.env['res.partner'].create(
    #                         {'name': rec['CompanyName'],
    #                          'is_company': True, 'customer': False, 'supplier': False})
    #                 parent_id = parent_id.id or False
    #             else:
    #                 parent_id = False
    #             return {'parent_id': parent_id}

    #     elif 'Vendor' in record:
    #         if 'CompanyName' in record['Vendor']:
    #             rec = record['Vendor']
    #             if rec['CompanyName']:
    #                 parent_id = self.env['res.partner'].search(
    #                     [('is_company', '=', True),
    #                      ('name', '=', rec['CompanyName']), ('backend_id', '=', self.backend_record.id)])
    #                 if not parent_id:
    #                     parent_id = self.env['res.partner'].create(
    #                         {'name': rec['CompanyName'],
    #                          'is_company': True, 'customer': False, 'supplier': False, 'backend_id': self.backend_record.id})
    #                 parent_id = parent_id.id or False
    #             else:
    #                 parent_id = False
    #             return {'parent_id': parent_id}

    
    @mapping
    def email(self, record):
        if 'Customer' in record:
            if 'PrimaryEmailAddr' in record['Customer']:
                rec = record['Customer']
                return {'email': rec['PrimaryEmailAddr']['Address'] or None}
        elif 'Vendor' in record:
            if 'PrimaryEmailAddr' in record['Vendor']:
                rec = record['Vendor']
                return {'email': rec['PrimaryEmailAddr']['Address'] or None}

    @mapping
    def phone(self, record):
        if 'Customer' in record:
            rec = record['Customer']
            if 'PrimaryPhone' in rec:
                return {'phone': rec['PrimaryPhone']['FreeFormNumber'] or None}
        elif 'Vendor' in record:
            rec = record['Vendor']
            if 'PrimaryPhone' in rec:
                return {'phone': rec['PrimaryPhone']['FreeFormNumber'] or None}

    @mapping
    def address(self, record):
        if 'Customer' in record:
            if 'BillAddr' in record['Customer']:
                rec = record['Customer']['BillAddr']
                if 'Line1' in rec:
                    return {'street': rec['Line1'] or None}
        elif 'Vendor' in record:
            if 'BillAddr' in record['Vendor']:
                rec = record['Vendor']['BillAddr']
                if 'Line1' in rec:
                    return {'street': rec['Line1'] or None}

    # @mapping
    # def name(self, record):
    #     if 'customer' in record:
    #         rec = record['customer']
    #         return {'name': rec['first_name'] , 'last_name': rec['last_name']}
    #     elif 'vendor' in record:
    #         rec = record['vendor']
    # return {'name': rec['first_name'] , 'last_name': rec['last_name']}

    @mapping
    def website(self, record):
        if 'Customer' in record:
            if 'WebAddr' in record['Customer']:
                rec = record['Customer']['WebAddr']
                return {'website': rec['URI'] or None}
        elif 'Vendor' in record:
            # rec = record['Vendor']
            if 'WebAddr' in record['Vendor']:
                rec = record['Vendor']['WebAddr']
                return {'website': rec['URI'] or None}

    @mapping
    def city(self, record):
        if 'Customer' in record:
            if 'BillAddr' in record['Customer']:
                rec = record['Customer']['BillAddr']
                if 'city' in rec:
                    return {'city': rec['City'] or None}
        elif 'Vendor' in record:
            if 'BillAddr' in record['Vendor']:
                rec = record['Vendor']['BillAddr']
                if 'city' in rec:
                    return {'city': rec['City'] or None}

    @mapping
    def zip(self, record):
        if 'Customer' in record:
            if 'BillAddr' in record['Customer']:
                rec = record['Customer']['BillAddr']
                if 'PostalCode' in rec:

                    return {'zip': rec['PostalCode'] or None}
        elif 'Vendor' in record:
            if 'BillAddr' in record['Vendor']:
                rec = record['Vendor']['BillAddr']
                if 'PostalCode' in rec:
                    return {'zip': rec['PostalCode'] or None}

    # @mapping
    # def address_2(self, record):
    #     if 'customer' in record:
    #         rec = record['customer']['BillAddr']
    #         return {'street2': rec['Line2'] or None}
    #     elif 'vendor' in record:
    #         rec = record['vendor']['vendor_address']
    #         return {'street2': rec['Line2'] or None}

    @mapping
    def country(self, record):
        if 'Customer' in record:
            if 'BillAddr' in record['Customer']:
                rec = record['Customer']['BillAddr']
                if 'Country' in rec:
                    if rec['Country']:
                        country_id = self.env['res.country'].search(
                            [('code', '=', rec['Country'])])
                        country_id = country_id.id
                    else:
                        country_id = False
                    return {'country_id': country_id}
        elif 'Vendor' in record:
            if 'BillAddr' in record['Vendor']:
                rec = record['Vendor']['BillAddr']
                if 'Country' in rec:
                    if rec['Country']:
                        country_id = self.env['res.country'].search(
                            [('code', '=', rec['Country'])])
                        country_id = country_id.id
                    else:
                        country_id = False
                    return {'country_id': country_id}

    @mapping  # 'state_id':rec['BillAddr']['CountrySubDivisionCode'],
    def state(self, record):
        if 'Customer' in record:
            if 'BillAddr' in record['Customer']:
                rec = record['Customer']['BillAddr']
                # if rec['CountrySubDivisionCode'] and rec['Country']:
                if 'CountrySubDivisionCode' in rec:
                    state_id = self.env['res.country.state'].search(
                        [('code', '=', rec['CountrySubDivisionCode'])])
                    if len(state_id) > 1:
                        state_id  = state_id[0]
                    else:
                        state_id  = state_id
                    # if not state_id:
                    #     country_id = self.env['res.country'].search(
                    #         [('code', '=', rec['Country'])])
                    #     state_id = self.env['res.country.state'].create(
                    #         {'name': rec['CountrySubDivisionCode'],
                    #          'code': rec['CountrySubDivisionCode'],
                    #          'country_id': country_id.id})
                    state_id = state_id.id or False
                else:
                    state_id = False
                return {'state_id': state_id}
        elif 'Vendor' in record:
            if 'BillAddr' in record['Vendor']:
                rec = record['Vendor']['BillAddr']
                # if rec['CountrySubDivisionCode'] and rec['Country']:
                if 'CountrySubDivisionCode' in rec:
                    state_id = self.env['res.country.state'].search(
                        [('code', '=', rec['CountrySubDivisionCode'])])
                    if len(state_id) > 1:
                        state_id  = state_id[0]
                    else:
                        state_id  = state_id
                    # if not state_id:
                    #     country_id = self.env['res.country'].search(
                    #         [('code', '=', rec['Country'])])
                    #     state_id = self.env['res.country.state'].create(
                    #         {'name': rec['CountrySubDivisionCode'],
                    #          'code': rec['CountrySubDivisionCode'],
                    #          'country_id': country_id.id})
                    state_id = state_id.id or False
                else:
                    state_id = False
                return {'state_id': state_id}
        #     rec = record['vendor']['vendor_address']
        #     if rec['state'] and rec['country']:
        #         state_id = self.env['res.country.state'].search(
        #             [('code', '=', rec['state'])])
        #         if not state_id:
        #             country_id = self.env['res.country'].search(
        #                 [('code', '=', rec['country'])])
        #             state_id = self.env['res.country.state'].create(
        #                 {'name': rec['state'],
        #                  'code': rec['state'],
        #                  'country_id': country_id.id})
        #         state_id = state_id.id or False
        #     else:
        #         state_id = False
        #         return {'state_id': state_id}

    @mapping
    def payment_term_id(self, record):
        if 'Customer' in record:
            rec = record
            if 'SalesTermRef' in rec:
                if rec['SalesTermRef']:
                    payment_term = self.env['account.payment.term'].search(
                        [('quickbook_id', '=', rec['SalesTermRef']['value'])])
                    payment_term = payment_term.id
                else:
                    payment_term = False
                return {'property_payment_term_id': payment_term}
        elif 'Vendor' in record:
            rec = record
            if 'TermRef' in rec:
                if rec['TermRef']:
                    payment_term = self.env['account.payment.term'].search(
                        [('quickbook_id', '=', rec['TermRef']['value'])])
                    payment_term = payment_term.id
                else:
                    payment_term = False
                return {'property_supplier_payment_term_id': payment_term}

    @mapping
    def supplier(self, record):
        if 'Customer' in record:
            return {'customer': True, 'supplier': False,'is_company': False}
        elif 'Vendor' in record:
            return {'customer': False, 'supplier': True, 'is_company': False}

    @mapping
    def id(self, record):
        if 'Customer' in record:
            rec = record['Customer']
            if rec['Id']:
                return {'quickbook_id': rec['Id']}
        elif 'Vendor' in record:
            rec = record['Vendor']
            if rec['Id']:
                return {'quickbook_id': rec['Id']}
# rec['Active']

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}




@quick
class CustomerExporter(Exporter):
    _model_name = ['res.partner']

    def _get_data(self, product, fields):
        result = {}
        return result

    def _domain_for_update_customer(self):
        return [
            ('backend_id', '!=', None),
        ]

    def run(self, binding_id, fields):
        """ Export the product inventory to wordpress """
        customer_obj = self.env['res.partner']
        domain = self._domain_for_update_customer()

        customer_data = customer_obj.search(domain)

        if customer_data:
            for customer in customer_data:
                self.backend_adapter.update_customer(customer.quickbook_id,
                                                       {'customer': customer})

    def run_sync(self, binding_id, data):
        
        self.backend_adapter.update_customer(binding_id, {'customer': data})



CustomerExporter = CustomerExporter  # deprecated

# @job(default_channel='root.quick')
    # @related_action(action=unwrap_binding)
    # def export_customer_inventory(self, model_name, backend_id, fields=None):
    #     """ Export the inventory configuration and quantity of a product. """

    #     customer = self.env[model_name].browse(record_id)
    #     try:
    #         if customer.backend_id:
    #             backend_id = customer.backend_id.id
    #         else:
    #             backend_id = record_id

    #     finally:
    #         pass

    #     env = get_environment(session, model_name, backend_id)
    #     inventory_exporter = env.get_connector_unit(
    #         CustomerExporter)


##########################################
############ End Customer   ##############
##########################################
