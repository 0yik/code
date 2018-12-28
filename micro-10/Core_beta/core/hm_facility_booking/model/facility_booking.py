# -*- coding: utf-8 -*-

from datetime import datetime

from lxml import etree
from odoo import api, fields, models,_
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError


class FacilityBooking(models.Model):
    _name = 'facility.booking'

    name = fields.Char(default='/')
    tenant_id = fields.Many2one('res.partner', string="Tenant")
    street = fields.Char('Address')
    phone = fields.Char('Phone')
    mobile = fields.Char('Mobile')
    email = fields.Char('Email')
    location_id = fields.Many2one('location', string="Location")
    facility_id = fields.Many2one('maintenance.equipment', domain=[('required_booking', '=', True)])
    booking_start_date = fields.Datetime('Booking Start Date')
    booking_end_date = fields.Datetime('Booking End Date')
    remarks = fields.Text('Remarks')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Canceling'),
    ], default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('facility.booking')
        res = super(FacilityBooking, self).create(vals)
        return res

    @api.onchange('tenant_id')
    def onchane_tenant_id(self):
        if self.tenant_id:
            self.street = self.tenant_id.street
            self.phone = self.tenant_id.phone
            self.mobile = self.tenant_id.mobile
            self.email = self.tenant_id.email

    @api.onchange('location_id')
    def onchange_location_id(self):
        if self.location_id:
            return {
                'domain': {
                    'facility_id': [('location_id', '=', self.location_id.id), ('required_booking', '=', True)]
                }
            }

    def check_overlapped_booking(self, facility_id, start_date , end_date):
        domain = [
            ('facility_id', '=', int(facility_id)),
            ('state', '=', 'confirm'),
            ('booking_start_date', '=', start_date),
            ('booking_end_date', '=', end_date),
        ]
        check_overlapped = self.search(domain)
        return  check_overlapped

    def action_facility_confirm(self):
        facility = self.facility_id.id
        check_overlapped = self.check_overlapped_booking(facility,self.booking_start_date, self.booking_end_date)
        if check_overlapped:
            mess = "This Facility has already been booked from %s to %s" % (
            datetime.strptime(self.booking_start_date, DEFAULT_SERVER_DATETIME_FORMAT).strftime('%d/%m/%Y %I:%M:%S'),
            datetime.strptime(self.booking_end_date,
                              DEFAULT_SERVER_DATETIME_FORMAT).strftime(
                '%d/%m/%Y %I:%M:%S')
            )
            raise UserError(_(mess))

        self.state = 'confirm'

    def action_facility_cancel(self):
        self.state = 'cancel'


FacilityBooking()
