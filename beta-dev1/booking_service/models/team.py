# -*- coding: utf-8 -*-

from odoo import models,fields,api

class BookingTeam(models.Model):
    _name= 'team.management'
    
    name = fields.Char("Name",required=True)
    team_employees = fields.Many2many("hr.employee","team_employee_rel","team_id","employee_id","Employees")
    team_equipments = fields.One2many("team.equipmemnts",'team_id','Equipments')
    leader_id = fields.Many2one("hr.employee","Team leader")
    
class TeamEquipments(models.Model):
    _name = 'team.equipmemnts'
    
    product_id = fields.Many2one("product.product","Equipment",domain=[("is_an_equipment",'=',True)])
    team_id = fields.Many2one("team.management","Team")    
    serial_no = fields.Many2one("stock.production.lot","Serial Number")
    sale_id = fields.Many2one("sale.order","Related Sale Order")
    picking_id = fields.Many2one("stock.picking","Related Picking")

        
    