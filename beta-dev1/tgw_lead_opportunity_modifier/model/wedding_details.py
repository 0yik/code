# -*- coding: utf-8 -*-

from odoo import api, fields, models

class wedding_type(models.Model):

    _name = "wedding.type"
    _description = "Wedding Type"

    name = fields.Char(string="Wedding Type", required=True)

    _sql_constraints = [
        ('wedding_type_uniq', 'unique (name)', "Wedding Type already exists !"),
    ]

class venus_type(models.Model):

    _name = "venus.type"
    _description = "Venus Type"

    name = fields.Char(string="Venus Type", required=True)

    _sql_constraints = [
        ('venus_type_uniq', 'unique (name)', "Venus Type already exists !"),
    ]

class gowns_trying(models.Model):

    _name = "gowns.trying"
    _description = "Trying of Gowns"

    name = fields.Char(string="Trying of Gowns", required=True)

    _sql_constraints = [
        ('gowns_trying_uniq', 'unique (name)', "Trying of Gowns already exists !"),
    ]

class gowns_shapes(models.Model):

    _name = "gowns.shapes"
    _description = "Gowns Shapes"

    name = fields.Char(string="Gowns Shapes", required=True)

    _sql_constraints = [
        ('gowns_shapes_uniq', 'unique (name)', "Gowns Shapes already exists !"),
    ]

class gowns_styles(models.Model):

    _name = "gowns.styles"
    _description = "Gowns Styles"

    name = fields.Char(string="Gowns Styles", required=True)

    _sql_constraints = [
        ('gowns_styles_uniq', 'unique (name)', "Gowns Styles already exists !"),
    ]

class items_required(models.Model):

    _name = "items.required"
    _description = "Required Item"

    name = fields.Char(string="Item Name", required=True)

    _sql_constraints = [
        ('items_required_uniq', 'unique (name)', "Item Name already exists !"),
    ]

class photography_requirement(models.Model):

    _name = "photography.requirement"
    _description = "Photography Requirement"

    name = fields.Char(string="Photography Requirement", required=True)

    _sql_constraints = [
        ('photography_requirement_uniq', 'unique (name)', "Photography Requirement already exists !"),
    ]

class reference_source(models.Model):

    _name = "reference.source"
    _description = "Reference Source"

    name = fields.Char(string="Name", required=True)

    _sql_constraints = [
        ('source_name_uniq', 'unique (name)', "Name already exists !"),
    ]

