# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime


class GenerateQueue(models.Model):
    _name = 'generate.queue'
    _rec_name = 'queue_number'

    queue_number = fields.Char('Queue Number', readonly=True, copy=False, default='New')
    reference = fields.Many2one('stock.picking', "Reference")
    created_date = fields.Datetime(string="Date Created", readonly=True)
    check = fields.Boolean(string="check", default=False)
    state = fields.Selection([('draft', 'Draft'), ('queue_generated','Queue Generated'), ('done','Done')], string='State', readonly=True, copy=False, store=True, default='draft')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get("generate.queue"))

    
    @api.multi
    def generate_number(self):
        if self.queue_number == 'New':
            vals = self.env['ir.sequence'].next_by_code('generate.queue') or _('New')
            values = {'queue_number':vals, 'created_date': datetime.now(), 'state': 'queue_generated'}
            self.check = True
            return self.write(values)
        
    @api.multi
    def write(self, values):
        if values.get('reference'):
            values.update({'state': 'done'})
        result = super(GenerateQueue, self).write(values)
        return result


