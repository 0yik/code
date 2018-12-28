# -*- coding: utf-8 -*-

from odoo import models,fields

class equipment_lines(models.Model):
    _name = 'equipment.lines'
    
    product_id = fields.Many2one("product.product","Equipment",domain=[('is_an_equipment','=',True)])
    serial_no_id = fields.Many2one("stock.production.lot","Serial No.")
    team_id = fields.Many2one("booking.team","Team")
    sale_order_id = fields.Many2one("sale.order","Sale Order")
    picking_id = fields.Many2one("stock.picking","Picking")
    
class booking_team(models.Model):
    _name= 'booking.team'
    
    name = fields.Char("Team Name",required=True)
    team_leader_id = fields.Many2one("hr.employee","Team leader")
    employee_ids = fields.Many2many("hr.employee","booking_team_employee_rel",'team_id','employee_id',"Employees")
    equipments_ids = fields.One2many("equipment.lines",'team_id','Equipments')
    
    