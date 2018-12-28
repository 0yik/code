# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
from odoo.exceptions import Warning
import datetime


class TesterSwapBooking(models.TransientModel):
    _name = 'tester.swap.booking'

    @api.model
    def get_booking_ids(self, active_id):
        res = self.with_context(active_id=active_id)._default_get_booking_ids()
        return self.env['project.booking'].search_read(res, ['final_start_dtime', 'final_end_dtime', 'user_tester_id'])

    @api.multi
    def _default_get_booking_ids(self):
        booking_ids = []
        if not self._context.get('active_id'):
            return [('id', 'in', booking_ids)]
        booking_id = self._context.get('active_id')
        booking_obj = self.env['project.booking'].browse(booking_id)
        if not booking_obj.final_start_dtime or not booking_obj.final_end_dtime:
            raise exceptions.UserError(
                _("Either start time %s or \
                   end time %s not found" %(booking_obj.final_start_dtime, booking_obj.final_end_dtime)))
        booking_ids = self.env['project.booking'].search(
            [('final_start_dtime', '=', booking_obj.final_start_dtime),
             ('final_end_dtime', '=', booking_obj.final_end_dtime),
             ('status', 'in', ['pending', 'reconfirmed']),
             ('user_tester_id', '!=', booking_obj.user_tester_id.id),
             ('id', '!=', booking_obj.id),
             ]).ids
        domain = [('id', 'in', booking_ids)]
        return domain

    is_differ_time = fields.Boolean('Booking on different Date and Time?')
    booking_id = fields.Many2one(
        comodel_name='project.booking',
        string='Customer Booking',
        help='Please select customer booking to swap tester.',
        domain=_default_get_booking_ids,
    )
    start_time = fields.Datetime(
        string='Booking Start Date & Time', help='Start Time of Booking.')
    end_time = fields.Datetime(
        string='Booking End Date & Time', help='End Time of Booking.')
    tester_id = fields.Many2one('res.users', 'Tester')
    
    @api.model
    def is_differ_time_mobile(self, active_record_id, is_differ_time):
        res = self.sub_is_differ_time(self._context.get('active_id'), is_differ_time)
        return self.env['project.booking'].search_read(res, ['final_start_dtime', 'final_end_dtime', 'user_tester_id'])
    
    @api.model
    def sub_is_differ_time(self, active_record_id, is_differ_time):
        res = {}
        today_time = datetime.datetime.now()
        if active_record_id:
            active_id = self.env['project.booking'].browse(active_record_id)
            if not active_id.final_start_dtime or not active_id.final_end_dtime:
                raise exceptions.UserError(
                    _("Either start time %s or \
                       end time %s not found" % (active_id.final_start_dtime, active_id.final_end_dtime)))
            if is_differ_time == True:
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
            if is_differ_time == False:
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
        
        

    @api.onchange('is_differ_time')
    def onchange_is_differ_time(self):
        self.booking_id = False
        self.start_time = False
        self.end_time = False
        self.tester_id = False
        return self.sub_is_differ_time(self._context.get('active_id'), self.is_differ_time)
    
#     @api.model
#     def sub_booking_id(self, booking_id):
#         res = {}
#         if booking_id:
#             booking = self.env['project.booking'].browse(booking_id)
#             res.update({
#                 'start_time': booking.final_start_dtime,
#                 'end_time': booking.final_end_dtime,
#                 'tester_id': booking.user_tester_id.id,
#             })
#         return res
            
        
        
    
    @api.onchange('booking_id')
    def onchange_booking_id(self):
        if self.booking_id:
            self.start_time = self.booking_id.final_start_dtime
            self.end_time = self.booking_id.final_end_dtime
            self.tester_id = self.booking_id.user_tester_id.id

    def _tester_swap_request_send_notification(self, self_obj, active_booking_obj):
        #TODO by mustafa
        return True

    @api.model
    def create_swap_tester(self, vals, booking_id):
        return self.create(vals).with_context(active_id=booking_id).swap_by_tester()

    @api.multi
    def swap_by_tester(self):
        """ Sending tester swap request by tester"""
        for swap_obj in self:
            # active id obj to access record of active
            active_id = self._context.get('active_id')
            active_booking_obj = self.env['project.booking'].browse(active_id)
            if self.is_differ_time == True:
                booking_ids = self.env['project.booking'].search(
                    [('final_start_dtime', '=', self.booking_id.final_start_dtime),
                     ('final_end_dtime', '=', self.booking_id.final_end_dtime),
                     ('status', 'in', ['pending', 'reconfirmed']),
                     ('user_tester_id', '=', active_booking_obj.user_tester_id.id)
                     ])
                if booking_ids:
                    raise Warning(_("Swapping is not allow due to you already have booking at requested datetime."))
            if swap_obj.booking_id.is_swap_req_sent:
                raise exceptions.UserError(_("Sorry. Swap request already sent for the selected booking."))
            if active_booking_obj.is_swap_req_sent:
                if not active_booking_obj.is_swap_req_rejected and not active_booking_obj.is_swap_req_accepted:
                    raise exceptions.UserError("First please accept or reject received swap request.")

            active_booking_obj.write({
                'to_swap_req_booking_id': swap_obj.booking_id.id,
                'is_swap_req_sent': True,
                'is_swap_req_rejected': False,
            })
            swap_obj.booking_id.write({
                'is_swap_req_accepted': False,
                'from_swap_booking_id': active_id,
                'is_swap_req_get': True,
            })
            # SEND NOTIFICATION TO TESTER
            self._tester_swap_request_send_notification(
                swap_obj, active_booking_obj)
        return {'type': 'ir.actions.act_window_close'}



TesterSwapBooking()
