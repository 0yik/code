# -*- coding: utf-8 -*-

from odoo import models, fields, api

class custom_sequence(models.Model):
    _inherit = 'ir.sequence'

    start_no = fields.Integer('Start Number')
    end_no = fields.Integer('End Number')
    category = fields.Many2one('product.category', 'Category')

    def create(self, vals):
        if 'code' in vals.keys():
            if vals['code'] == 'stock.lot.serial':
                vals['number_next']=vals['start_no']
        return super(custom_sequence, self).create(vals)

    def get_new_seq(self, code):
        """ Draw an interpolated string using the specified sequence.
        The sequence to use is specified by its code. This method is
        deprecated.
        """
        return self.get_id(code, 'code')

    @api.onchange('start_no') # if these fields are changed, call method
    def _check_change_start_no(self):
        self.number_next_actual = self.start_no
        if self.end_no < self.start_no :
            return {'warning': {'title': 'Error!', 'message': 'Start no. should be greater than End no.'}}

    @api.onchange('end_no') # if these fields are changed, call method
    def _check_change_end_no(self):
        if self.end_no < self.start_no :
            return {'warning': {'title': 'Error!', 'message': 'End no. should be greater than start no.'}}