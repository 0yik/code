# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError

class Website(models.Model):
    _inherit = "website"

    website_advance_deposit = fields.Float("Default Advance Deposit")


class custom_made(models.Model):
    _name = 'custom.made'
    _description = "Info of Custom Made Costume"
    
    name = fields.Char('Name',required=1)
    email = fields.Char('Email',required=1)
    phone = fields.Char('Phone',)
    quantity = fields.Char('Quantity',required=1)
    fabric = fields.Char('Fabric',required=1)
    budget = fields.Char('Budget',required=1)
    deadline = fields.Char('Deadline',required=1)
    u_image = fields.Binary('Upload',required=1)
    file_name = fields.Char("File Name",required=1)
    remarks = fields.Text('Remarks',required=1)


