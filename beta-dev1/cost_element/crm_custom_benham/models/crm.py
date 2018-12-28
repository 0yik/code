import logging
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.tools import email_re, email_split
from odoo.exceptions import UserError, AccessError

# from odoo.addons.base.res.res_partner import FormatAddress
# 
# from . import crm_stage

class CrmSource(models.Model):
    _name = 'crm.source'
    
    name    = fields.Char('Name')
    
class Lead(models.Model):
    _inherit = "crm.lead"

    crm_source_id   = fields.Many2one('crm.source', string='Source')
    work_phone      = fields.Char('Work Phone')
    property        = fields.Char('Property 1')
    accom           = fields.Char('Accom 1')
    surname         = fields.Char('Surname')
    contact_name    = fields.Char('Contact First Name')
    contact_surname = fields.Char('Contact Surname')
    br_notes        = fields.Text('BR Notes')
    lea_off         = fields.Text('Leasing Office')
    mana_fe         = fields.Text('Management Fee')
    parking         = fields.Text('Parking')
    partner_id      = fields.Many2one('res.partner', string='First Name', track_visibility='onchange', index=True,
        help="Linked partner (optional). Usually created when converting the lead.")


    mobile_num      = fields.Char('Mobile Number')
    other_num       = fields.Char('Other Number')
    rental_1        = fields.Char('Rental 1')
    property_2      = fields.Char('Property 2')
    accom_2         = fields.Char('Accom 2')
    rental_2        = fields.Char('Rental 2')
    property_3      = fields.Char('Property 3')
    accom_3         = fields.Char('Accom 3')
    rental_3        = fields.Char('Rental 3')
    sent_mail_opportunity = fields.Boolean(default=False)

    @api.model
    def _get_tracked_fields(self, updated_fields):
        """ Return a structure of tracked fields for the current model.
            :param list updated_fields: modified field names
            :return dict: a dict mapping field name to description, containing
                always tracked fields and modified on_change fields
        """
        tracked_fields = []
        for name, field in self._fields.items():
            if getattr(field, 'string'):
                tracked_fields.append(name)

        if tracked_fields:
            return self.fields_get(tracked_fields)
        return {}

    @api.model
    def autosend_notification(self):
        lead_obj = self.env['crm.lead']
        message_obj = self.env['mail.compose.message']
        ir_model_data = self.env['ir.model.data']
        timenow  = datetime.now()
        lead_id = lead_obj.search([('date_action','<=',str(timenow))])
        for list in lead_id:
            if not list.sent_mail_opportunity:
                template_id = ir_model_data.get_object_reference('crm_custom_benham', 'email_template_notify_opportunity')[1]
                values = message_obj.onchange_template_id(template_id, 'comment', 'crm.lead', list.id)['value']
                message_id = message_obj.create(values)
                message_id.send_mail()
                list.write({'sent_mail_opportunity': True})
        return 1

class Partner(models.Model):
    _inherit = 'res.partner'
    
    name            = fields.Char(index=True, string="First Name")
    surname         = fields.Char('Surname')
