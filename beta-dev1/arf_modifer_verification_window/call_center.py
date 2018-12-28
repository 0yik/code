import json
from lxml import etree
from datetime import datetime
from dateutil.relativedelta import relativedelta
 
from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.tools.misc import formatLang
 
from odoo.exceptions import UserError, RedirectWarning, ValidationError
 
import odoo.addons.decimal_precision as dp
import logging

class VerificationWindow(models.TransientModel):
    _name = 'verification.window'
    
    @api.depends('name_tickmark', 'date_birth_tickmark', 'phone_tickmark', 'email_tickmark',
                 'nric_tickmark','passport_tickmark','policy_number_tickmark','vehicle_number_tickmark')
    def _get_verification_complete(self):
        print "###_get_verification_complete"
        value = False
        count = 0
        for val in self:
            print ">>>>>", self.name_tickmark
            if self.name_tickmark:
                count += 1
            if self.date_birth_tickmark:
                count += 1
            if self.phone_tickmark:
                count += 1
            if self.email_tickmark:
                count += 1
            if self.nric_tickmark:
                count += 1
            if self.passport_tickmark:
                count += 1
            if self.policy_number_tickmark:
                count += 1
            if self.vehicle_number_tickmark:
                count += 1
                
            if count >= 3:
                value = True
                
            val.update({'verification_complete' : value})
        print "MASUK####"
        if self.verification_complete==True:
            ticket = self.sudo().generate_ticket()
            
        return {
            'name': _('Open Customer'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'res.partner',
            'view_id': self.env.ref('base.res_partner_kanban_view').id,
            'type': 'ir.actions.act_window',
            'res_id': val.partner_id.id,
            #'context': context,
            'target': 'new'
        }

        
            
    partner_id  = fields.Many2one('res.partner', string='Customer')
    name        = fields.Char(string='Name')
    date_birth  = fields.Date(string='Date of Birth')
    phone       = fields.Char(string='Phone Number')
    email       = fields.Char(string='Mailing Address')
    
    nric        = fields.Char(string='NRIC/FIN')
    passport    = fields.Char(string='Passport No.')
    policy_number    = fields.Char(string='Policy Number')
    vehicle_number    = fields.Char(string='Vehicle Number')
    
    name_tickmark        = fields.Boolean(string='Tick Name')
    date_birth_tickmark  = fields.Boolean(string='Tick Date of Birth')
    phone_tickmark       = fields.Boolean(string='Tick Phone Number')
    email_tickmark       = fields.Boolean(string='Tick Mailing Address')
    
    nric_tickmark               = fields.Boolean(string='Tick NRIC/FIN')
    passport_tickmark           = fields.Boolean(string='Tick Passport No.')
    policy_number_tickmark      = fields.Boolean(string='Tick Policy Number')
    vehicle_number_tickmark     = fields.Boolean(string='Tick Vehicle Number')
    
    verification_complete       = fields.Boolean(string='Verification Complete',compute="_get_verification_complete")
 
    
    @api.multi
    def open_history(self):
        #self.ensure_one()
        print "MASUK####", self.partner_id.id
            
        return {
            'name': _('All Tickets'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'helpdesk.ticket',
            'view_id': self.env.ref('arf_modifer_verification_window.helpdesk_tickets_view_tree_editable').id,
            'type': 'ir.actions.act_window',
            #'res_id': self.partner_id.id,
            #'res_id': move_ids[0],
            #'context': context,
            'domain': "[('partner_id', '=', %s),('call','=',True)]" % self.partner_id.id,
            # 'domain': "[('customer_name', '=', %s),('call','=',True)]" % self.partner_id.id,
            #'nodestroy': True,
            'target': 'new'
        }
    
    @api.multi
    def open_profile(self):
        self.ensure_one()
        print "MASUK####", self.partner_id.id
            
        return {
            'name': _('Open Customer'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'res.partner',
            'view_id': self.env.ref('base.view_partner_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.partner_id.id,
            #'context': context,
            'domain': "[('id', '=', %s)]" % self.partner_id.id,
            'target': 'current'
        }
    
    @api.multi
    def generate_ticket(self):
        self.ensure_one()
        
        for o in self:
            customer_obj=self.env['res.partner'].search([('id','=',o.partner_id.id)])
            desk_obj=self.env['helpdesk.ticket']
            
            print "AAAAA---->>", customer_obj
            print "BBBBB---->>", customer_obj.id
            #'id':self.id
            partner_id = customer_obj.id
            values={'name':customer_obj.name,'date_birth':customer_obj.date_birth,'phone':customer_obj.phone,'email':customer_obj.email,
            'employer_name':customer_obj.name_employer,'contract_person':customer_obj.contract_person,'contract_hom':customer_obj.contract_hom,'contract_mobile':customer_obj.contract_mobile,
            'nature_of_business':customer_obj.nature_of_busines,'mailling':customer_obj.address,'age':customer_obj.age,'gender':customer_obj.gender,
            'marital_status':customer_obj.marital_status,'occupation':customer_obj.occupation,'license_pass_date': customer_obj.lic_part_date,
            'contract_work':customer_obj.office,'postal_code':customer_obj.postal_code,'customer_name':customer_obj.id,
            'nationality':customer_obj.nationality.id,'driving_experience':customer_obj.experience,'nric_fin':customer_obj.nric_passport_ros,'call':True,
            }
            
            ticket = desk_obj.create(values)
            
            query = """UPDATE helpdesk_ticket SET partner_id = %s where id = %s;"""
            self.env.cr.execute(query, (o.partner_id.id, ticket.id))
        return ticket
    
class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'
    
    @api.multi
    def open_link(self):
        context = dict(self.env.context or {})
        context['active_id'] = self.id
        
        return {
            'name': _('Help Desk Ticket'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'helpdesk.ticket',
            'view_id': self.env.ref('arf_modifer_verification_window.helpdesk_ticket_view_readonly_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'context': context,
            'target': 'new'
        }
    
    @api.multi
    def open(self):
        context = dict(self.env.context or {})
        context['active_id'] = self.id
        
        print "XXXXX",  self.env.ref('arf_modifer_verification_window.view_verification_window_wizard').id
        
        return {
            'name': _('Verification Windows'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'verification.window',
            'view_id': self.env.ref('arf_modifer_verification_window.view_verification_window_wizard').id,
            'type': 'ir.actions.act_window',
            #'res_id': self.env.context.get('cashbox_id'),
            'context': context,
            'target': 'new'
        }
    
