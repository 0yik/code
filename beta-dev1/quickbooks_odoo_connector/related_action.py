# -*- coding: utf-8 -*-
#
#
#    TechSpawn Solutions Pvt. Ltd.
#    Copyright (C) 2016-TODAY TechSpawn(<http://www.TechSpawn.com>).
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

import functools
from odoo import exceptions, _
# from odoo.addons.connector import related_action
from .connector import get_environment
from .unit.backend_adapter import GenericAdapter
from .unit.binder import WooBinder
from openerp.addons.connector.models.queue_job import QueueJob
unwrap_binding = functools.partial(QueueJob,
                                   binder_class=WooBinder)


def link(session, job, backend_id_pos=2, quickbook_id_pos=3):
    """ Open a Woo URL on the admin page to view/edit the record
    related to the job.
    """
    binding_model = job.args[0]
    # shift one to the left because session is not in job.args
    backend_id = job.args[backend_id_pos - 1]
    quickbook_id = job.args[quickbook_id_pos - 1]
    env = get_environment(session, binding_model, backend_id)
    adapter = env.get_connector_unit(GenericAdapter)
    try:
        url = adapter.admin_url(quickbook_id)
    except ValueError:
        raise exceptions.Warning(
            _('No admin URL configured on the backend or '
              'no admin path is defined for this record.')
        )

    action = {
        'type': 'ir.actions.act_url',
        'target': 'new',
        'url': url,
    }
    return action
