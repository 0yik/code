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
# from odoo.addons.connector.session import ConnectorSession
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


@quick
class VendorBatchImporter(DelayedBatchImporter):

    """ Import the Quickbook Partners.

    For every partner in the list, a delayed job is created.
    """
    _model_name = ['res.partner']
    url = None

    def _import_record(self, quickbook_id, priority=None):
        """ Delay a job for the import """
        
        super(VendorBatchImporter, self)._import_record(
            quickbook_id, priority=priority)

    def run(self, filters=None):
        """ Run the synchronization """
        
        from_date = filters.pop('from_date', None)
        to_date = filters.pop('to_date', None)

        count = 1
        record_ids = ['start']
        filters['url'] = 'vendor'
        while record_ids:
            filters['count'] = count
            record_ids = self.backend_adapter.search(
                filters,
                from_date=from_date,
                to_date=to_date,
            )
    #         record_ids = self.env['bk.backend'].get_customer_ids(record_ids)
            _logger.info('Search For QBO Vendor %s Returned %s',
                     filters, record_ids)
            count += 300
            self.url = 'vendor'
            if 'Vendor' in record_ids['QueryResponse']:
                record_ids = record_ids['QueryResponse']['Vendor']
                for record_id in record_ids:
                    self._import_record(int(record_id['Id']), 40)
            else:
                record_ids = record_ids['QueryResponse']


VendorBatchImporter = VendorBatchImporter  # deprecated

class quick_customer(models.Model):

    _inherit = 'res.partner'

    @api.multi
    @job(default_channel='root.quick')
    def vendor_import_batch(session, model_name, backend_id, filters=None):
        
        """ Prepare the import of vendor """
        
        env = get_environment(session, model_name, backend_id)
        importer = env.get_connector_unit(VendorBatchImporter)
        importer.run(filters=filters)

    @job(default_channel='root.quick')
    @related_action(action=unwrap_binding)
    def export_vendor_details(self, backend_id):
        """ Export the Vendors Details. """

        env = backend_id.get_environment(self._name)
        # env = get_environment(session, model_name, backend_id)
        inventory_exporter = env.get_connector_unit(
            VendorTemplateInventoryExporter)

        return inventory_exporter.run(backend_id, fields)

# vendor Template details 
@quick
class VendorTemplateInventoryExporter(Exporter):
    _model_name = ['res.partner']

    def _get_data(self, vendor, fields):
        result = {}       
        if 'quickbook_id' in fields:
            result.update({
                'id': vendor.quickbook_id,
            })
        return result
    def _domain_for_update_vendor(self):
        return [
            ('backend_id', '!=', None),
            ('supplier', '=', True),
        ]

    def run(self, binding_id, fields):
        """ Export the vendor Details to Quickbook """
        vendor_obj = self.env['res.partner']      
        domain = self._domain_for_update_vendor()  
        vendor_template =  vendor_obj.search(domain)
        print vendor_template
        if vendor_template:
            for template in vendor_template:
                self.backend_adapter.update_vendor(template.quickbook_id, {'vendor':template})

    def run_sync(self, binding_id, data):
        
        self.backend_adapter.update_vendor(binding_id, {'vendor': data})

VendorTemplateInventoryExport = VendorTemplateInventoryExporter  # deprecated

# fields which should not trigger an export of the products
# but an export of their inventory


# @job(default_channel='root.quick')
# @related_action(action=unwrap_binding)
# def export_vendor_details(session, model_name, record_id, fields=None):
#     """ Export the inventory configuration and quantity of a product. """
#     vendor = session.env[model_name].browse(record_id)
#     print vendor
#     try:
#         if vendor.backend_id :
#             backend_id = vendor.backend_id.id
#         else:
#             backend_id = record_id
#     finally:
#         pass

        
#     env = get_environment(session, model_name, backend_id)
#     inventory_exporter1 = env.get_connector_unit(
#         VendorTemplateInventoryExporter)
#     return inventory_exporter1.run(record_id, fields)



##########################################
############ End   Vendor   ##############
##########################################