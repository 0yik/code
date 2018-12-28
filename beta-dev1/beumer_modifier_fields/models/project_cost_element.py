# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class cost_element(models.Model):
    _inherit = 'project.cost_element'

    def get_recursive_name(self, record):
        # if not record.parent_cost_element or not record.parent_cost_element.id:
        if record.cost_element_code:
            if record.name:
                name = "%s - %s" % (record.cost_element_code, record.name)
            else:
                name = record.cost_element_code
        else:
            if record.name:
                name = record.name
            else:
                name = None
        return name
        # if record.parent_cost_element.id == self.id:
        #     if record.cost_element_code:
        #         if record.name:
        #             name = "%s - %s" % (record.cost_element_code, record.name)
        #         else:
        #             name = record.cost_element_code
        #     else:
        #         name = record.name
        #     return name
        # parent_name = self.get_recursive_name(record.parent_cost_element)
        # # parent_name = record.parent_cost_element.name
        # return "%s - %s" % (parent_name, record.name)

    @api.multi
    def name_get(self):
        result = []

        for record in self:
            name = self.get_recursive_name(record)
            result.append((record.id, name))
        return result

    # @api.constrains('parent_cost_element')
    # def _check_parent_cost_element(self):
    #     for record in self:
    #         if record.parent_cost_element and self.name in record.parent_cost_element.display_name:
    #             raise ValidationError("Can not choose parent cost element: %s" % record.parent_cost_element.display_name)
