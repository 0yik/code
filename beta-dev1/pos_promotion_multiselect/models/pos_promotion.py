# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json 

class POSPromotionDays(models.Model):
    _name= "pos.promotion.days"

    # week_days = fields.Selection([
    #     ('sunday','Sunday'),
    #     ('monday','Monday'),
    #     ('tuesday','Tuesday'),
    #     ('wednesday','Wednesday'),
    #     ('thursday','Thursday'),
    #     ('friday','Friday'),
    #     ('saturday','Saturday')], string="Days")
    name = fields.Char('name')


class POSPromotion(models.Model):
    _inherit= "pos.promotion"

    week_days_ids = fields.Many2many('pos.promotion.days', string="Days")
    # starting_hours = fields.Char(string="Starting Hours")
    starting_hours = fields.Selection([
        ('1','1'),
        ('2','2'),
        ('3','3'),
        ('4','4'),
        ('5','5'),
        ('6','6'),
        ('7','7'),
        ('8','8'),
        ('9','9'),
        ('10','10'),
        ('11','11'),
        ('12','12'),
        ('13','13'),
        ('14','14'),
        ('15','15'),
        ('16','16'),
        ('17','17'),
        ('18','18'),
        ('19','19'),
        ('20','20'),
        ('21','21'),
        ('22','22'),
        ('23','23'),
        ('24','24'),
        ],string="Starting Hours")
    ending_hours = fields.Selection([
        ('1','1'),
        ('2','2'),
        ('3','3'),
        ('4','4'),
        ('5','5'),
        ('6','6'),
        ('7','7'),
        ('8','8'),
        ('9','9'),
        ('10','10'),
        ('11','11'),
        ('12','12'),
        ('13','13'),
        ('14','14'),
        ('15','15'),
        ('16','16'),
        ('17','17'),
        ('18','18'),
        ('19','19'),
        ('20','20'),
        ('21','21'),
        ('22','22'),
        ('23','23'),
        ('24','24'),
        ],string="Ending Hours")
    # ending_hours = fields.Char(string="Ending Hours")
    hours = fields.Text(string="Hours")

    @api.multi
    def calculat_hours_set(self):
        for record in self:
            if record.hours:
                record.hours +=  ', ' + str(record.starting_hours) + '-' + str(record.ending_hours)
            else:
                record.hours = str(record.starting_hours) + '-' + str(record.ending_hours)

            record.starting_hours = ''
            record.ending_hours = ''