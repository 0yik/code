# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime, timedelta, time, date
import pytz
# import time
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.exceptions import except_orm, Warning
from dateutil import tz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_TIME_FORMAT
import math

class tester_myreqest(models.Model):
    _inherit = 'my.request'


    @api.model
    def get_overtime_config_time(self):
        vals = {}
        start = self.env['ir.values'].get_default('admin.configuration', 'ot_start_time')
        end = self.env['ir.values'].get_default('admin.configuration', 'ot_end_time')
        vals["ot_start_time"] = self.float_time_convert(start)
        vals["ot_end_time"] = self.float_time_convert(end)
        return vals

    def float_time_convert(self,float_val):
        val = abs(float_val)
        st_con = '0'
        if '.' in str(val):
            st_dec = int(str(val).split('.')[1])
            conversion = (st_dec * 60) / 100
            st_dec = str(str(val).split('.')[0])
            if len(str(val).split('.')[0])==1:
                st_dec = "0"+str(val).split('.')[0]
            if len(str(conversion))==1:
                conversion = str(conversion)+"0"
            st_con = st_dec+":"+str(conversion)
        return st_con

tester_myreqest()

class res_users(models.Model):
    _inherit = "res.users"

    @api.multi
    def get_user_data_app(self):
        user = self.search([('id','=',self.id)])
        if user:
            partner_obj  = self.env.user.partner_id
            vals={}
            vals["name"] = self.env.user.name
            vals["email"] = self.env.user.email if self.env.user.email else ""
            vals["image_medium"] = self.env.user.image_medium if self.env.user.image_medium else ""
            vals["phone"] = partner_obj.phone if partner_obj.phone else ""
            
            # finding partner address details
            vals["partner_id"] = partner_obj.id
            vals["street"] = partner_obj.street or ''
            vals["street2"] = partner_obj.street2 or ''
            vals["city"] = partner_obj.city or ''
            vals["state"] = partner_obj.state_id.name if partner_obj.state_id.name else ''
            vals["zip"] = partner_obj.zip or ''
            vals["country"] = partner_obj.country_id.name if partner_obj.country_id.name else ''

            # finding partner all state and country
            if  vals["state"]:
                all_state = self.env['res.country.state'].search_read([('name', '!=', vals["state"])], fields=['name'])
            else:
                all_state = self.env['res.country.state'].search_read([],['name'])
            vals['all_state'] =  all_state
            if vals["country"]:
                all_country = self.env['res.country'].search_read([('name', '!=', vals["country"])], fields=['name'])
            else:
                all_country = self.env['res.country'].search_read([],['name'])
            vals['all_country'] = all_country

            # finding sic ,equi and zone
            vals["sic_access"] = [sic.name for sic in partner_obj.project_ids]
            vals["equipment"] = [equi.name for equi in partner_obj.equipment_ids]
            vals["zone"] = partner_obj.zone_id.name if partner_obj.zone_id.name else ''

            # finding all sic ,equip,
            if vals["sic_access"]:
                all_sic = self.env['project.project'].search_read([('name', '!=', vals["sic_access"])], fields=['name'])
            else:
                all_sic = self.env['project.project'].search_read([],['name'])
            vals["all_sic_access"] = all_sic
            if vals["equipment"]:
                all_equip = self.env['equipment.equipment'].search_read([('name', '!=', vals["equipment"])], fields=['name'])
            else:
                all_equip = self.env['equipment.equipment'].search_read([],['name'])
            vals["all_equipment"] = all_equip

            # finding group
            group_hilti_customer = self.has_group('hilti_modifier_accessrights.group_hilti_customer')
            group_hilti_tester = self.has_group('hilti_modifier_accessrights.group_hilti_tester')
            group_hilti_account_manager = self.has_group('hilti_modifier_accessrights.group_hilti_account_manager')
            group_hilti_cs_engineer = self.has_group('hilti_modifier_accessrights.group_hilti_cs_engineer')
            group_hilti_admin = self.has_group('hilti_modifier_accessrights.group_hilti_admin')
            hilti_group = ''
            if group_hilti_customer:
                hilti_group = 'Customer'
            elif group_hilti_tester:
                hilti_group = 'Tester'
            elif group_hilti_account_manager:
                hilti_group = 'Account Manager'
            elif group_hilti_cs_engineer:
                hilti_group = 'CS and Engineer'
            elif group_hilti_admin:
                hilti_group = 'Admin'
            else:
                hilti_group = ''
            vals['hilti_group'] = hilti_group
            return vals
        else:
            return False

    @api.multi
    def get_user_edit_app(self, vals):
        user_obj = self.search([('id', '=', self.id)])
        if user_obj:
            user_val = {}
            user_val['name'] = vals.get('name', '')
            user_val['street'] = vals.get('street', '')
            user_val['street2'] = vals.get('street2', '')
            user_val['city'] = vals.get('city', '')
            user_val['email'] = vals.get('email', '')
            user_val['phone'] = vals.get('phone', '')
            user_val['image_medium'] = vals.get('image_medium', '')
            sic_ids = self.env['project.project'].search([('name', '=', vals.get('sic_access', ''))])
            all_records = []
            for sic_id in sic_ids:
                all_records.append(sic_id.id)
            user_val['project_ids'] = [(6, 0, all_records)]
            user_obj.sudo().write(user_val)
            return True
        else:
            return False

res_users()