# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    location_id = fields.Many2one('location',string='Location')
    facility_id = fields.Many2one('maintenance.equipment',string='Facility')

    @api.model
    def create(self, vals):
        res = super(HelpdeskTicket, self).create(vals)
        help_ticket_obj = self.env['helpdesk.ticket.type'].search([('name', '=', 'Issue')], limit=1)
        issue_obj = self.search([('ticket_type_id', '=', help_ticket_obj.id)], limit=1)

        location_obj = self.env['location'].search([('id', '=', vals.get('location_id', False) )], limit=1)
        facility_obj = self.env['maintenance.equipment'].search([('id', '=', vals.get('facility_id', False))],limit=1)

        if issue_obj and facility_obj:
            vals = {}
            vals['name']= res.name
            if res.partner_id:
                partner_obj = self.env['res.partner'].search([('id', '=', res.partner_id.id)], limit=1)
                user_obj = self.env['res.users'].search([('name', '=', partner_obj.name)], limit=1)
                vals['owner_user_id'] = user_obj.id
                if not user_obj:
                    vals = {}
                    vals['name'] = res.name
                    vals['login'] =   res.name
                    user_obj =self.env['res.users'].create(vals)
                    vals['owner_user_id'] = user_obj.id
            else:
                vals['owner_user_id'] = False
            vals['location_id'] = location_obj.id if location_obj else False
            vals['equipment_id'] = facility_obj.id
            vals['description'] = res.description or ''
            vals['request_date'] = fields.datetime.today()
            vals['maintenance_type'] = 'corrective'
            vals['maintenance_team_id'] = facility_obj.maintenance_team_id.id if facility_obj.maintenance_team_id else False
            vals['technician_user_id'] = facility_obj.technician_user_id.id if facility_obj.technician_user_id else False
            if res.ticket_type_id.name == 'Issue':
                self.env['maintenance.request'].create(vals)
        return res


HelpdeskTicket()