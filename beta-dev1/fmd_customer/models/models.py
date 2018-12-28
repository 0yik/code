
# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class GstQuarter(models.Model):
    _name = 'gst.quarter'
    
    name = fields.Char("Name")
    
class YearlyYearly(models.Model):
    _name = 'yearly.yearly'
    
    name = fields.Char("Name")

class HalfYear(models.Model):
    _name = 'half.year'
    
    name = fields.Char("Name")

class QuarterQuarter(models.Model):
    _name = 'quarter.quarter'
    
    name = fields.Char("Name")

class BiMonth(models.Model):
    _name = 'bi.month'
    
    name = fields.Char("Name")

class MonthMonth(models.Model):
    _name = 'month.month'
    
    name = fields.Char("Name")

class WeekWeek(models.Model):
    _name = 'week.week'
    
    name = fields.Char("Name")

class PeriodCycle(models.Model):
    _name = 'period.cycle'
    
    name = fields.Char("Name")

class AccountCycle(models.Model):
    _name = 'account.cycle'
    
    name = fields.Char("Name")

class Source(models.Model):
    _name = 'source.source'
    
    name = fields.Char("Name")

class ServiceNature(models.Model):
    _name = 'service.nature'
    
    name = fields.Char("Name")

class CommonSeal(models.Model):
    _name = 'common.seal'
    
    name = fields.Char("Name")

class ContactMode(models.Model):
    _name = 'contact.mode'
    
    name = fields.Char("Name")

class Position(models.Model):
    _name = 'position.position'
    
    name = fields.Char("Name")

class Year(models.Model):
    _name = 'year.year'
    
    name = fields.Char("Name")

class PartnerStatus(models.Model):
    _name = 'partner.status'
    
    name = fields.Char("Name")

class ClientClient(models.Model):
    _name = 'client.client'
    
    name = fields.Char("Name")
    
class EntityType(models.Model):
    _name = 'entity.type'
    
    name = fields.Char("Name")
    
class ContactType(models.Model):
    _name = 'contact.type'
    
    name = fields.Char("Name")
    
class FileFile(models.Model):
    _name = 'file.file'
    
    name = fields.Char("Name")
    
class GroupGroup(models.Model):
    _name = 'group.group'
    
    name = fields.Char("Name")
    
class Addresstype(models.Model):
    _name = 'address.type'
    
    name = fields.Char("Name")
    
class Businesstype(models.Model):
    _name = 'business.type'
    
    name = fields.Char("Name")

class BillingCode(models.Model):
    _name = 'billing.code'
    
    name = fields.Char("Name")
    
class VatRate(models.Model):
    _name = 'vat.rate'
    
    name = fields.Char("Name")
    
class CreditTerms(models.Model):
    _name = 'credit.terms'
    
    name = fields.Char("Name")
    
class OfficeOffice(models.Model):
    _name = 'office.office'
    
    name = fields.Char("Name")
    
class AccountStatus(models.Model):
    _name = 'account.status'
    
    name = fields.Char("Name")
    
class TaxStatus(models.Model):
    _name = 'tax.status'
    
    name = fields.Char("Name")
    
class EserviceAccess(models.Model):
    _name = 'eservice.access'
    
    name = fields.Char("Name")
    
class FYELastform(models.Model):
    _name = 'fye.lastform'
    
    name = fields.Char("Name")
    
class StocktakeRequired(models.Model):
    _name = 'stocktake.required'
    
    name = fields.Char("Name")
    
class ShareCapital(models.Model):
    _name = 'share.capital'
    
    name = fields.Char("Name")
    
class AddressAddress(models.Model):
    _name = 'address.address'
    _rec_name="address_type_id"
    
    partner_id = fields.Many2one("res.partner","Partner")
    address_type_id = fields.Many2one("address.type", "Address Type")
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    name=fields.Text("Address")

class SecAppointment(models.Model):
    _name = 'sec.appointment'
    
    name = fields.Char("Name of Secretary")
    partner_id = fields.Many2one("res.partner","Partner")
    date_appt = fields.Date("Date of Appt")
    date_resign = fields.Date("Date of Resign")
    
class ContactList(models.Model):
    _name = 'contact.list'
    
#     @api.model
#     def create(self, vals):
#         print vals
#         temp={}
#         address_ids = vals['address_ids_list'] or []
#         if address_ids:
#             for address in address_ids:
#                 vals['address_ids_list'] = [address]
#                 temp = vals['address_ids_list'][0][2]
#                 for item in temp.items():
#                     if item[0]=='address_type':
#                         vals['address_type_id']=item[1]              
#                 res_id = super(ContactList,self).create(vals)
#         else:
#             res_id = super(ContactList,self).create(vals)
#         return res_id
# 
#     @api.multi
#     def write(self, vals):
#         address_ids = vals.get('address_ids_list' or False) and vals['address_ids_list'] or []
#         if address_ids:
#             count = 0
#             for address in address_ids:
#                 vals['address_ids_list'] = [address]
#                 if [address][0][2] != False and [address][0][2] !=[] :
#                     temp = [address][0][2]
#                     for kv in temp.items():
#                         if kv[0] == 'address_type':
#                             vals['address_type_id'] = kv[1]
#                 if count == 0:
#                     res_id = super(ContactList,self).write(vals)
#                     count +=1
#                 else:
#                     current_contact = self.search_read([('id','=',self.id)])[0]
#                     current_contact['write_uid'] = current_contact['write_uid'] and current_contact['write_uid'][0]
#                     current_contact['create_uid'] = current_contact['create_uid'] and current_contact['create_uid'][0]
#                     current_contact['partner_id'] = current_contact['partner_id'] and current_contact['partner_id'][0]
#                     current_contact['country_id'] = current_contact['country_id'] and current_contact['country_id'][0]
#                     current_contact['contact_type_id'] = current_contact['contact_type_id'] and current_contact['contact_type_id'][0]
#                     current_contact['position_id'] = current_contact['position_id'] and current_contact['position_id'][0]
#                     current_contact['file_as_id'] = current_contact['file_as_id'] and current_contact['file_as_id'][0]
#                     current_contact['state_id'] = current_contact['state_id'] and current_contact['state_id'][0]
#                     current_contact['address_ids_list'] = [address]
#                     temp = [address][0][2]
#                     for kv in temp.items():
#                         if kv[0] == 'address_type':
#                             current_contact['address_type_id'] = kv[1]
#                     res_id = super(ContactList,self).create(current_contact)        
#         else:
#             res_id = super(ContactList,self).write(vals)
#         return res_id

    partner_id = fields.Many2one("res.partner","Partner")
    contact_type_id = fields.Many2one("contact.type","CL Contact Type")
    reside_overseas = fields.Selection([('yes','Yes'),('no','No')],'CL Reside Overseas')
    name = fields.Char("CL Name")
    position_id = fields.Many2one("hr.job", "CL Position")
    phone = fields.Char("CL Phone")
    address_conatct = fields.Text("CL Address")
    mobile = fields.Char("CL Mobile")
    email = fields.Char("CL Email")
    contact_mode_c = fields.Many2one('contact.mode','CL Suggested Contact Mode')
    opt_out_c = fields.Boolean('CL Opt out Email')
    remarks = fields.Text('CL Remarks')
    other_t = fields.Text('CL Others(T)')
    
#     file_as_id = fields.Many2one("file.file", "File As")
#     job_title = fields.Char("Job Title")
#     address_type_id = fields.Many2one("address.type", "Address Type")
#     street = fields.Char()
#     street2 = fields.Char()
#     zip = fields.Char(change_default=True)
#     city = fields.Char()
#     state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
#     country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
#     phone2 = fields.Char("Phone 2")
#     mobile2 = fields.Char("Mobile 2")
#     fax = fields.Char("Fax")
#     email2 = fields.Char("Email 2")
#     web = fields.Char("Web")
#     skype = fields.Char("Skype")
#     other = fields.Char("Other")
#     other2 = fields.Char("Other 2")
#     send_emails = fields.Boolean("Send Emails")
#     sync_iphone = fields.Boolean("Synchronization with Iphone")
#     statutory_contact = fields.Boolean("Statutory Contact")
#     feedback_contact = fields.Boolean("Feedback Contact")
#     contact_address=fields.Text("Address")
#     prefer_contact_type=fields.Many2one('payment.contact.type',"Prefer Contact Method")
#     address_ids_list = fields.One2many("address.line", "partner_id", string="Address")
    
class DirectorList(models.Model):
    _name = 'director.list'
    
    partner_id = fields.Many2one("res.partner","Partner")
    name = fields.Char("Name")
    file_as_id = fields.Many2one("file.file", "File As")
    position_id = fields.Many2one("hr.job", "Position")
    job_title = fields.Char("Job Title")
    address_type_id = fields.Many2one("address.type", "Address Type")
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    phone = fields.Char("Phone")
    phone2 = fields.Char("Phone 2")
    mobile = fields.Char("Mobile")
    mobile2 = fields.Char("Mobile 2")
    fax = fields.Char("Fax")
    email = fields.Char("Email")
    email2 = fields.Char("Email 2")
    web = fields.Char("Web")
    skype = fields.Char("Skype")
    other = fields.Char("Other")
    other2 = fields.Char("Other 2")
    send_emails = fields.Boolean("Send Emails")
    sync_iphone = fields.Boolean("Synchronization with Iphone")
    statutory_contact = fields.Boolean("Statutory Contact")
    feedback_contact = fields.Boolean("Feedback Contact")

class payment_contact_method(models.Model):
    _name='payment.contact.method'

    name=fields.Char("Name")

class payment_contact_type(models.Model):
    _name='payment.contact.type'

    name=fields.Char("Name")

class tax_status_master(models.Model):
    _name='tax.status.master'

    name=fields.Char("Name")

class Address_line(models.Model):
    _name = 'address.line'

    partner_id = fields.Many2one("contact.list","Partner ID")
    address_type = fields.Many2one("address.type", "Address Type")
    name=fields.Text("Address")
