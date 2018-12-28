# -*- coding: utf-8 -*-
from odoo.osv.orm import setup_modifiers
from datetime import datetime
from dateutil.relativedelta import relativedelta
from lxml import etree
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
import odoo.addons.decimal_precision as dp


class crm_lead(models.Model):
    _inherit = "crm.lead"
    
	
    name = fields.Char('Opportunity', required=True, index=True)
    priority = fields.Selection(
                                [
	                                ('0','Very Low'),
	                                ('1','Low'),
	                                ('2','Normal'),
	                                ('3','High'),
	                                ('4','Very High'),
	                                ('5','Urgent'),
	                                ('6','Very Urgent'),
	                                ('7','Extreme'),
	                                ('8','Very Extreme'),
	                                ('9','Danger'),
                                ]
                                ,string='Priority')
    bridal_adviser1_id = fields.Many2one('hr.employee','Bridal Advisor')
    bridal_adviser2_id = fields.Many2one('hr.employee','Bridal Advisor2')

    #Bride Information
    bride_frist_name = fields.Char("Bride's First Name")
    bride_last_name = fields.Char("Bride's Last Name")
    bride_email = fields.Char("Email")
    bride_phone = fields.Char("Bride's Phone")
    bride_street = fields.Char('Street')
    bride_street2 = fields.Char('Street2')
    bride_zip = fields.Char('Zip', change_default=True)
    bride_city = fields.Char('City')
    bride_state_id = fields.Many2one("res.country.state", string='State')
    bride_country_id = fields.Many2one('res.country', string='Country')
    bride_dob = fields.Date('DOB')
    bride_nric = fields.Char('NRIC')

    #Groom Information
    groom_frist_name = fields.Char("Groom's First Name")
    groom_last_name = fields.Char("Groom's Last Name")
    groom_email = fields.Char("Email")
    groom_phone = fields.Char("Groom's Phone")
    groom_street = fields.Char('Street')
    groom_street2 = fields.Char('Street2')
    groom_zip = fields.Char('Zip', change_default=True)
    groom_city = fields.Char('City')
    groom_state_id = fields.Many2one("res.country.state", string='State')
    groom_country_id = fields.Many2one('res.country', string='Country')
    groom_dob = fields.Date('DOB')
    groom_nric = fields.Char('NRIC')

    date_of_rom = fields.Date('Date Of ROM')
    wedding_date_1 = fields.Date('Pre-Wedding Date')
    wedding_date_2 = fields.Date('Actual Date')
    wedding_venue = fields.Char('Wedding Venue')
    lunch_dinner = fields.Selection([('lunch','Lunch'),('dinner','Dinner')],'Lunch/Dinner')
    number_of_guests = fields.Integer('Number Of Guests')
    
    meet_up_date = fields.Date('First Appointment')
    return_date = fields.Date('2nd Return Date')
    return_date_2 = fields.Date('3rd Return Date')
    
    #Referal Details
    referal1_id = fields.Many2one('res.partner','Referal First Name')
    referal2_id = fields.Many2one('res.partner','Referal Last Name')
    referal_customer_id = fields.Many2one('hr.employee','Referal Customer ID')
    referal_email = fields.Char('Referal Email')

    opportunity_remarks = fields.Text('Remarks')

    #Wedding Details
    wedding_type_id = fields.Many2one('wedding.type', 'Wedding Type')
    venus_type_id = fields.Many2one('venus.type', 'Venus Type')
    gowns_trying_id = fields.Many2one('gowns.trying', 'Trying of Gowns')
    gowns_shapes_id = fields.Many2one('gowns.shapes', 'Shapes of Gowns Looking for')
    gowns_styles_id = fields.Many2one('gowns.styles', 'Styles of Gowns')
    items_required_id = fields.Many2one('items.required', 'Item Requires')
    photography_requirement_id = fields.Many2one('photography.requirement', 'Photography Required')
    reference_source_id = fields.Many2one('reference.source', 'How you find about us?')

    
    
    @api.depends('date_open')
    def _compute_day_open(self):
        """ Compute difference between create date and open date """
        for lead in self.filtered(lambda l: l.date_open):
            date_create = fields.Datetime.from_string(lead.create_date)
            date_open = fields.Datetime.from_string(lead.date_open)
            if date_create and date_open:
                lead.day_open = abs((date_open - date_create).days)

    @api.depends('date_closed')
    def _compute_day_close(self):
        """ Compute difference between current date and log date """
        for lead in self.filtered(lambda l: l.date_closed):
            date_create = fields.Datetime.from_string(lead.create_date)
            date_close = fields.Datetime.from_string(lead.date_closed)
            if date_create and date_close:
                lead.day_close = abs((date_close - date_create).days)
    
    

