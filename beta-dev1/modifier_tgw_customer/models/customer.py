# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang

import odoo.addons.decimal_precision as dp

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _description = 'Partner'
    _rec_name = 'bride_firstname'

    # name = fields.Char('Name', default=' ')

    bridal_advisor = fields.Many2one('hr.employee', ' Coordinator')
    bridal_advisor2 = fields.Many2one('hr.employee', 'Back up Bridal Specialist')
    bridal_specialist = fields.Many2one('hr.employee', string="Bridal Specialist")
    customer_id = fields.Char(string="Customer ID")
    referral_code = fields.Char('Referral Code', track_visibility='onchange', copy=False)
    loyalty_points = fields.Integer('Loyalty Points') #compute="_compute_loyalty_points"

    bride_firstname = fields.Char("Bride's First Name",required=True)
    bride_lastname = fields.Char("Bride's Last Name",required=True)
    bride_email = fields.Char(string="Email",required=True)
    bride_phone = fields.Char(string="Bride's Phone",required=True)
    bride_street = fields.Char(string="Street",required=True)
    bride_street2 = fields.Char(string="Street2",required=True)
    bride_zip = fields.Char(string="Zip", size=24, change_default=True,required=True)
    bride_city = fields.Char(string="City",required=True)
    bride_state_id = fields.Many2one(
        "res.country.state", string="State", ondelete='restrict',required=True)
    bride_country_id = fields.Many2one(
        'res.country', string="Country", ondelete='restrict',required=True)
    bride_birthdate = fields.Date(string="DOB")
    bride_nric = fields.Char(string="NRIC")
    
    groom_firstname = fields.Char("Groom's First Name")
    groom_lastname = fields.Char("Groom's Last Name")
    groom_name = fields.Char(string="Name")
    groom_email = fields.Char(string="Email")
    groom_phone = fields.Char(string="Groom's Phone")
    groom_street = fields.Char(string="Street")
    groom_street2 = fields.Char(string="Street2")
    groom_zip = fields.Char(string="Zip", size=24, change_default=True)
    groom_city = fields.Char(string="City")
    groom_state_id = fields.Many2one("res.country.state", string="State",
                                     ondelete='restrict')
    groom_country_id = fields.Many2one('res.country', string="Country",
                                       ondelete='restrict')
    groom_birthdate = fields.Date(string="DOB")
    groom_nric = fields.Char(string="NRIC")

    crm_lead_id = fields.Many2one('crm.lead', string='Lead')
    first_enquiry_venue = fields.Char('First Enquiry Venue (Shop/Fair)')
    prospect_onwer = fields.Many2one('res.users', string='Prospect Owner')
    personal_note = fields.Char('Personal Notes')

    # total_wishing_stars = fields.Integer(string='Total wishing stars') #compute='_compute_total_wishing_stars', 
    # remaining_wishing_stars = fields.Integer(string='Remaining wishing stars') #compute='_compute_remaining_wishing_stars',

    date_wedd = fields.Datetime(string="Wedding Date 1")
    date_wedd2 = fields.Datetime(string="Wedding Date 2")
    date_rom = fields.Datetime(string="Date of ROM")

    #Measurements
    bride_thigh = fields.Char(string="Thigh")
    bride_above_bust = fields.Char(string="Above the Bust")
    bride_bust = fields.Char(string="Bust")
    bride_hips = fields.Char(string="Hips")
    bride_waist = fields.Char(string="Waist")
    bride_biceps = fields.Char(string="Biceps")
    bride_shoulder = fields.Char(string="Shoulder")
    brides_father_jacket_sleeve = fields.Char("Bride's Father's Jacket Sleeve")
    brides_father_jacket_shoulder = fields.Char(string="Bride's Father's Jacket Shoulder")
    brides_father_jacket_tummy = fields.Char(string="Bride's Father's Jacket Tummy")
    brides_father_jacket_pant_waist = fields.Char(string="Bride's Father's Jacket Pant Waist")
    brides_father_jacket_pant_length = fields.Char(string="Bride's Father's Jacket Pant Length")
    
    groom_sleeve = fields.Char(string="Sleeve")
    groom_waist = fields.Char(string="Waist")
    groom_pants = fields.Char(string="Pants")
    groom_hips = fields.Char(string="Hips")
    groom_thigh = fields.Char(string="Thigh")
    groom_calf = fields.Char(string="Calf")
    groom_pants_length = fields.Char(string="Pants Length")
    grooms_father_jacket_sleeve = fields.Char("Groom's Father's Jacket Sleeve")
    grooms_father_jacket_shoulder = fields.Char(string="Bride's Father's Jacket Shoulder")
    grooms_father_jacket_tummy = fields.Char(string="Bride's Father's Jacket Tummy")
    grooms_father_jacket_pant_waist = fields.Char(string="Bride's Father's Jacket Pant Waist")
    grooms_father_jacket_pant_length = fields.Char(string="Bride's Father's Jacket Pant Length")
    grooms_shoulder = fields.Char(string="Shoulder")
    grooms_biceps = fields.Char(string="Biceps")
    grooms_arms = fields.Char(string="Arms")
    grooms_chest = fields.Char(string="Chest")
    groom_jacket_length = fields.Char(string="Jacket Length")
    grooms_jacket_sleeve_length = fields.Char("Jacket Sleeve Length")
    last_reconciliation_date = fields.Datetime(
            'Latest Full Reconciliation Date', copy=False,
            help='Date on which the partner accounting entries were fully reconciled last time. '
                 'It differs from the last date where a reconciliation has been made for this partner, '
                 'as here we depict the fact that nothing more was to be reconciled at this date. '
                 'This can be achieved in 2 different ways: either the last unreconciled debit/credit '
                 'entry of this partner was reconciled, either the user pressed the button '
                 '"Nothing more to reconcile" during the manual reconciliation process.')


    contract_ids = fields.Many2many('account.analytic.account', string="Contracts")
    payment_ids = fields.One2many('account.voucher', 'partner_id', string="Payments", readonly=False)
    redeem_ids = fields.One2many('redeem.redeem', 'partner_id', string="Redeem History")
    loyalty_ids = fields.One2many('loyalty.loyalty', 'partner_id', string="Loyalty History")
    milestone_ids = fields.One2many('milestone.contract.bookings', 'partner_id', string='Analytic Booking Contract Line')
