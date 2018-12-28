# -*- coding: utf-8 -*-

from odoo import models, exceptions, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
import datetime


class swap_booking(models.TransientModel):
    
    _name = 'swap.booking'
    
    def _get_booking_ids(self):
        today_time = datetime.datetime.now()
        if self._context.get('active_id'):
            active_id = self.env['project.booking'].browse(self._context.get('active_id'))
            if not active_id.final_start_dtime or not active_id.final_end_dtime:
                raise exceptions.UserError(
                    _("Either start time %s or \
                       end time %s not found" % (active_id.final_start_dtime, active_id.final_end_dtime)))
            booking_ids_search = self.env['project.booking'].search(
                [('final_start_dtime', '=', active_id.final_start_dtime),
                 ('final_end_dtime', '=', active_id.final_end_dtime),
                 ('status', 'in', ['pending', 'reconfirmed']),
                 ('user_tester_id', '!=', active_id.user_tester_id.id),
                 ('id', '!=', active_id.id),
                 ]).ids
            if self._context and 'call_onchange' in self._context:
                return booking_ids_search
            if booking_ids_search:
                return [('id', 'in', booking_ids_search)]
            else:
                return [('id', 'in', [])]
            
        else:
            return [('id', 'in', [])]
    
    @api.onchange('is_differ_time')
    def onchange_is_differ_time(self):
        self.booking_id = False
        self.start_time = False
        self.end_time = False
        self.tester_id = False
        res = {}
        today_time = datetime.datetime.now()
        if self._context.get('active_id'):
            active_id = self.env['project.booking'].browse(self._context.get('active_id'))
            if not active_id.final_start_dtime or not active_id.final_end_dtime:
                raise exceptions.UserError(
                    _("Either start time %s or \
                       end time %s not found" % (active_id.final_start_dtime, active_id.final_end_dtime)))
            if self.is_differ_time == True:
                booking_ids = self.env['project.booking'].search(
                    [('final_start_dtime', '=', active_id.final_start_dtime),
                     ('final_end_dtime', '=', active_id.final_end_dtime),
                     ('status', 'in', ['pending', 'reconfirmed'])
                     ])
                all_tester = []
                if booking_ids:
                    all_tester = [a.user_tester_id.id for a in booking_ids if a.user_tester_id and a.user_tester_id.id]
                all_booking_ids = self.env['project.booking'].search(
                                                                     [('id', '!=', active_id.id),
                                                                      ('user_tester_id', 'not in', all_tester),
                                                                      ('user_tester_id', '!=', False),
                                                                      ('status', 'in', ['pending', 'reconfirmed']),
                                                                      ('final_start_dtime', '>=', str(today_time))])
                record_list = [a.id for a in all_booking_ids]
                if record_list:
                    res['domain'] = {'booking_id': [('id', 'in', record_list)]}
                else:
                    res['domain'] = {'booking_id': [('id', 'in', [])]}
                return res
            if self.is_differ_time == False:
                booking_ids_search = self.env['project.booking'].search(
                    [('final_start_dtime', '=', active_id.final_start_dtime),
                     ('final_end_dtime', '=', active_id.final_end_dtime),
                     ('status', 'in', ['pending', 'reconfirmed']),
                     ('user_tester_id', '!=', active_id.user_tester_id.id),
                     ('id', '!=', active_id.id),
                     ]).ids
                if booking_ids_search:
                    res['domain'] = {'booking_id': [('id', 'in', booking_ids_search)]}
                else:
                    res['domain'] = {'booking_id': [('id', 'in', [])]}
                return res
    
    is_differ_time = fields.Boolean('Booking on different Date and Time?')
    booking_id = fields.Many2one('project.booking', string="Swap Booking", domain=_get_booking_ids)
    start_time = fields.Datetime(
        string='Booking Start Date & Time', help='Start Time of Booking.')
    end_time = fields.Datetime(
        string='Booking End Date & Time', help='End Time of Booking.')
    tester_id = fields.Many2one('res.users', 'Tester')
    
    @api.onchange('booking_id')
    def onchange_booking_id(self):
        if self.booking_id:
            self.start_time = self.booking_id.final_start_dtime
            self.end_time = self.booking_id.final_end_dtime
            self.tester_id = self.booking_id.user_tester_id.id
    
    def swap_booking(self):
        active_id = self.env['project.booking'].browse(self._context.get('active_id'))
        if self.booking_id and active_id:
            if self.is_differ_time == True:
                booking_ids = self.env['project.booking'].search(
                    [('final_start_dtime', '=', self.booking_id.final_start_dtime),
                     ('final_end_dtime', '=', self.booking_id.final_end_dtime),
                     ('status', 'in', ['pending', 'reconfirmed']),
                     ('user_tester_id', '=', active_id.user_tester_id.id)
                     ])
                if booking_ids:
                    raise Warning(_("Swapping is not allow due to current tester already have booking at requested datetime."))
            ac_tester_id = active_id.tester_id and active_id.tester_id.id
            bo_tester_id = self.booking_id.tester_id and self.booking_id.tester_id.id
            self.booking_id.tester_id = ac_tester_id
            active_id.tester_id = bo_tester_id
    
    
