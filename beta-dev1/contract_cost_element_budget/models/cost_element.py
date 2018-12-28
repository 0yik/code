# -*- coding: utf-8 -*-

from odoo import models, fields, api

class cost_element(models.Model):
    _inherit = 'project.cost_element'

    def get_recursive_name(self, record):
        if not record.parent_cost_element or not record.parent_cost_element.id:
            return record.name
        parent_name = self.get_recursive_name(record.parent_cost_element)
        return "%s / %s" %(parent_name, record.name)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = self.get_recursive_name(record)
            result.append((record.id, name))

        return result