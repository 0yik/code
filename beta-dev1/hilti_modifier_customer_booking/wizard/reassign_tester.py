# -*- coding: utf-8 -*-


from openerp import api, exceptions, fields, models, _
import datetime


class ReassignTester(models.TransientModel):
    _name = 'reassign.tester'
    _description = 'Reassign Tester'

    is_reassign_manually = fields.Boolean("Want to assign Tester manually?")
    partner_id = fields.Many2one("res.partner","Available Testers")

    @api.model
    def searching_booking_partner(self):
        partner_ids = []
        booking_ids = self._context.get('active_ids')
        booking_objs = self.env['project.booking'].browse(booking_ids)
        booking_before_time = self.env['ir.values'].get_default('admin.configuration', 'booking_before_time')
        booking_after_time = self.env['ir.values'].get_default('admin.configuration', 'booking_after_time')
        for book_obj in booking_objs:
            start_time = fields.Datetime.from_string(book_obj.final_start_dtime)
            end_time = fields.Datetime.from_string(book_obj.final_end_dtime)
            # actual time for the booking by adding and subtracting
            if not start_time or not end_time:
                raise exceptions.UserError(_("Either start time %s or end time %s not found." %(start_time, end_time)))
            actual_st_time = start_time - datetime.timedelta(
                minutes=int(booking_before_time * 60))
            actula_end_time = end_time + datetime.timedelta(
                minutes=int(booking_after_time * 60))
            all_tester_ids = self.env['res.partner'].search(
                [('type_of_user', '=', 'hilti_tester')])
            bookings = self.env['project.booking'].search(
                        [('status', 'not in', ['completed', 'cancelled']),
                         ('final_start_dtime', '>=', fields.Datetime.to_string(actual_st_time)),
                         ('final_end_dtime', '<=', fields.Datetime.to_string(actula_end_time)),
                         ])
            # listing all the tester which have booking on that date
            allocated_tester_ids = [bo.user_tester_id.partner_id.id for bo in bookings]

            all_tester_list = [partner.id for partner in all_tester_ids]
            # only append those tester which have not BO on that date
            for partner in all_tester_list:
                if partner not in allocated_tester_ids:
                    partner_ids.append(partner)
        return partner_ids


    @api.multi
    @api.onchange('is_reassign_manually')
    def onchange_is_reassing_manually(self):
        if not self.is_reassign_manually:
            return {'domain': {'partner_id': []}}
        else:
            partner_ids = []
            vals = {}
            partner_ids = self.searching_booking_partner()
            domain = {'partner_id': [('id', 'in', partner_ids)]}
            vals.update({'domain': domain})
            #self.update(vals)
            return vals


    @api.multi
    def action_reassing(self):
        booking_ids = self._context.get('active_ids')
        booking_objs = self.env['project.booking'].browse(booking_ids)
        if not booking_objs:
            raise exceptions.Warning(_('Please select Bookings.'))
        for self_obj in self:
            if self_obj.is_reassign_manually:
                tester_id = self.env['res.users'].sudo().search(
                    [('partner_id', '=', self_obj.partner_id.id)])
                if not tester_id:
                    raise exceptions.Warning(_("No tester user found for the selected partner."))
                booking_objs.write({'user_tester_id': tester_id.id})
            else:
                # Call the function created by nitin
                for booking_obj in booking_objs:
                    booking_obj.reassign_tester_from_admin()
        return {'type': 'ir.actions.act_window_close'}


ReassignTester()
