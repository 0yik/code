# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from datetime import datetime, date
from openerp.exceptions import UserError, ValidationError


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if self._context.get('kra_employee_id', False):
            employee_id = self.browse(self._context.get('kra_employee_id', False))
            manager = employee_id.parent_id
            manager_ids = []
            while manager:
                manager_ids.append(manager.id)
                manager = manager.parent_id
            domain = [('id', 'in', manager_ids)]
        if domain:
            recs = self.search(domain + args + [('name', operator, name)], limit=limit)
        else:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()
