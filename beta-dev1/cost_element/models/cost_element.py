# -*- coding: utf-8 -*-

from odoo import models, fields, api

class cost_element(models.Model):
    _name = 'project.cost_element'

    name                = fields.Char('Cost Element')
    parent_cost_element = fields.Many2one('project.cost_element',string="Parent Cost Element")
    # level               =  fields.Char('Level')
    level               = fields.Selection([('1', '1'), ('2', '2'), ('3', '3')],string="Level")
    cost_element_code   = fields.Char('Cost Element Code')


