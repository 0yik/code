# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import except_orm, Warning

class TimeFrame(models.Model):
    _name = 'time.frame'

    start = fields.Selection([(x, x) for x in range(0,24)], string="Start")
    finish = fields.Selection([(x, x) for x in range(0,24)], string="Finish")
    price =fields.Float('Price')
    qty = fields.Integer('Daily Qtauntity Limit')

    @api.onchange('start', 'finish')
    def _onchange_esti_delivery_from(self):
        for obj in self:
            if obj.start and obj.finish and obj.start > obj.finish:
                raise Warning('Please Select Valid Time.')