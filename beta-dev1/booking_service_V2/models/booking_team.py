# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

from odoo.exceptions import ValidationError


class booking_team(models.Model):
    _name = 'booking.team'

    name           = fields.Char('Team Name', required=True)
    team_leader    = fields.Many2one('hr.employee', string='Team leader')
    team_employees = fields.One2many('booking.team.employee', 'team_id')
    product_ids    = fields.One2many('booking.team.product', 'team_id')




class booking_team_product(models.Model):
    _name = 'booking.team.product'

    product_id = fields.Many2one('product.template', string="Equipments", domain=[('is_equipment', '=', True)],
                                 required=True)
    lot_id     = fields.Many2one('stock.production.lot', string="Serial Number")
    team_id    = fields.Many2one('booking.team')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            return {
                   'domain': {
                       'lot_id': [('product_id', '=', self.product_id.id)]
                   },
            }

    @api.model
    def create(self, values):
        lot = values['lot_id']
        if lot is False:
            raise ValidationError("Serial Number can't be blank")
        record = super(booking_team_product, self).create(values)
        return record

    @api.model
    def write(self, values):
        lot = values['lot_id']
        if lot is False:
            raise ValidationError("Serial Number can't be blank")
        record = super(booking_team_product, self).write(values)
        return record


class booking_team_employee(models.Model):
    _name = 'booking.team.employee'

    employee_id = fields.Many2one('hr.employee', string="Employees", required=True)
    team_id = fields.Many2one('booking.team')
