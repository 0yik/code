# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import Warning


class TestingTimeslot(models.TransientModel):
    _name = 'testing.timeslot'
    
    booking_date = fields.Date('Date')
    time_slot = fields.Many2many('time.slot.start.end', string='Available Timeslots')
    
    @api.onchange('booking_date')
    def check_tester_free(self):
        allocated_slot = []
        tester = self.env['res.partner'].browse(self._context.get('active_ids', []))
        if tester and self.booking_date:
            booking_record = self.env['project.booking'].search([('tester_id', '=', tester.id)])
            for book in booking_record:
                if book.time_booking_ids:
                    for time in book.time_booking_ids:
                        if time.booking_date == self.booking_date:
                            allocated_slot.append(time.time_slot_id.id)
        slot = self.env['timeslot.master'].sudo().search([], limit=1)
        total_slot = [time.id for time in slot.time_slot_ids]
        remaining_slot = [aa for aa in total_slot if aa not in allocated_slot]
        if not self.booking_date:
            remaining_slot = []
        if remaining_slot:
            self.time_slot = [(6,0, remaining_slot)]
        else:
            self.time_slot = [(6,0, [])]
            
            
            
class TestingTimeslotAdmin(models.TransientModel):
    _name = 'testing.timeslotadmin'
    
    tester_id = fields.Many2one('res.partner', domain=[('type_of_user', '=', 'hilti_tester')], string="Tester")
    booking_date = fields.Date('Date')
    time_slot = fields.Many2many('time.slot.start.end', string='Available Timeslots')
    
    @api.onchange('booking_date', 'tester_id')
    def check_tester_freeadmin(self):
        allocated_slot = []
        if self.tester_id and self.booking_date:
            booking_record = self.env['project.booking'].search([('tester_id', '=', self.tester_id and self.tester_id.id)])
            for book in booking_record:
                if book.time_booking_ids:
                    for time in book.time_booking_ids:
                        if time.booking_date == self.booking_date:
                            allocated_slot.append(time.time_slot_id.id)
        slot = self.env['timeslot.master'].sudo().search([], limit=1)
        total_slot = [time.id for time in slot.time_slot_ids]
        remaining_slot = [aa for aa in total_slot if aa not in allocated_slot]
        if not self.booking_date:
            remaining_slot = []
        if not self.tester_id:
            remaining_slot = []
        if remaining_slot:
            self.time_slot = [(6,0, remaining_slot)]
        else:
            self.time_slot = [(6,0, [])]
    
  