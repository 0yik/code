# -*- coding: utf-8 -*-

from odoo import models, fields, api

class waste_manager(models.Model):
    _name = 'waste.manager'

    name =  fields.Char(string='Name')
    date = fields.Date(string="Date")
    waste_scrap_ids = fields.One2many('waste.scrap','waste_manager_id',string='Scrap')
    state = fields.Selection(
        [('draft', 'Draft'), ('to_approved', 'To Approved'), ('approved', 'Approved'),('rejected', 'Rejected')],
        string='Status',readonly=True, default='draft')

    @api.multi
    def approved(self):
        for record in self:
            record.state = 'approved'
            if record.waste_scrap_ids:
                for waste_scrap in record.waste_scrap_ids:
                    waste_scrap.stock_scrap_id.do_scrap()
#             else:
#                 vars = {
#                     'scrap_qty' : scrap.scrap_qty ,
#                     'location_id' : scrap.location_id.id,
#                     'product_id'  : scrap.product_id.id,
#                     'product_uom_id' : scrap.product_uom_id.id,
#                     'state'       : 'done',
#                     'date_expected' : scrap.date_expected,
#                     'scrap_location_id' : scrap.scrap_location_id.id,
#                 }
#                 scrap_stock_id = self.env['stock.scrap'].create(vars)
#                 scrap.stock_scrap_id = scrap_stock_id

    @api.multi
    def request_approved(self):
        for record in self:
            record.state = 'to_approved'

    @api.multi
    def reject(self):
        for record in self:
            record.state = 'rejected'

    @api.multi
    def reset(self):
        for record in self:
            record.state = 'draft'
            if record.waste_scrap_ids:
                for scrap in record.waste_scrap_ids:
                    if scrap.stock_scrap_id:
                        scrap.stock_scrap_id.state = 'draft'

class waste_manager(models.Model):
    _name = 'waste.scrap'
    _inherits = {'stock.scrap': 'stock_scrap_id'}

    waste_manager_id = fields.Many2one('waste.manager')
    stock_scrap_id = fields.Many2one('stock.scrap')

