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
class RateBatchImporter(DelayedBatchImporter):

    """ Import the Quickbook Partners.

    For every partner in the list, a delayed job is created.
    """
    _model_name = ['account.tax']
    url = None

    def _import_record(self, quickbook_id, priority=None):
        """ Delay a job for the import """
        
        super(RateBatchImporter, self)._import_record(
            quickbook_id, priority=priority)

    def run(self, filters=None):
        """ Run the synchronization """
        
        from_date = filters.pop('from_date', None)
        to_date = filters.pop('to_date', None)
        filters['url'] = 'taxrate'
        record_ids = self.backend_adapter.search(
            filters,
            from_date=from_date,
            to_date=to_date,
        )
        
        _logger.info('search for quickbook tax rates %s returned %s',
                     filters, record_ids)
        self.url = 'taxrate'
        if 'TaxRate' in record_ids['QueryResponse']:
            record_ids = record_ids['QueryResponse']['TaxRate']
            for record_id in record_ids:
                self._import_record(int(record_id['Id']), 40)


RateBatchImporter = RateBatchImporter  # deprecated

class quick_rate(models.Model):

    _inherit = 'account.tax'

    @api.multi
    @job(default_channel='root.quick')
    def rate_import_batch(session, model_name, backend_id, filters=None):
        
        """ Prepare the import of Rate """
        
        env = get_environment(session, model_name, backend_id)
        importer = env.get_connector_unit(RateBatchImporter)
        importer.run(filters=filters)