# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning

class project_project(models.Model):
    _inherit = 'project.project'
    
    
    partner_ids = fields.Many2many('res.partner','rela_pr_partner','project_id','partner_id', string="Customers")
    account_manager_id = fields.Many2one('res.partner', string="Account Manager", domain="[('type_of_user', '=', 'hilti_account_manager')]")
    tester_ids = fields.Many2many('res.partner', string="Reserved Testers", domain="[('type_of_user', '=', 'hilti_tester')]")
    email = fields.Char(string="Email")
    booking_ids = fields.One2many('project.booking', 'project_id', string="Booking")
    required_sic = fields.Boolean('Require SIC')
    is_new_project = fields.Boolean('Is New Project?')
    location_id = fields.Many2one('location.location')
    postal_code = fields.Many2one('postal.code', related="location_id.postal_code", string="Postal Code")
    
class locatino_location(models.Model):
    _inherit = 'location.location'
    
    project_id = fields.Many2one('project.project')
    
class project_booking(models.Model):
    _name = 'project.booking'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name='booking_no'
    
    def _get_partner_company(self):
        all_comapny = self.env['res.partner'].search([])
        record_list = [a.id for a in all_comapny if a.company_type == 'company']
        if record_list:
            return [('id', 'in', record_list)]
        else:
            return [('id', 'in', [])]
      
    @api.onchange('company_id')  
    def _get_partner_contact(self):
        if self.company_id and self._context and 'come_from_default' not in self._context.keys():
            self.partner_id = False
            return {'domain': {'partner_id': [('parent_id', '=', self.company_id and self.company_id.id)]}}
        else:
            return {'domain': {'partner_id': []}}
    
    
    booking_no = fields.Char('Booking Number')
    partner_id = fields.Many2one('res.partner', string="Login")
    company_id = fields.Many2one('res.partner', domain=_get_partner_company, string="Customer")
    #start_time = fields.Datetime('Start Time')
    #end_time = fields.Datetime('End Time')
    #booking_date = fields.Date('Booking Date')
    project_id = fields.Many2one('project.project', string="Project")
    location_id = fields.Many2one('location.location', string="Location")
    tester_id = fields.Many2one('res.partner', string="Tester", domain="[('type_of_user', '=', 'hilti_tester')]")
    sid_required = fields.Boolean('SIC Required')
    contact_id = fields.Char(string="Contact Name")
    contact_number = fields.Char(string="Contact Number")
    status = fields.Selection(
    [
        ('pending', 'Pending'),
        ('started', 'Started'),
        ('reconfirmed', 'Re-Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='pending')
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user)
    postal_code = fields.Many2one('postal.code', related="location_id.postal_code", string="Postal Code")
    address = fields.Text('Address', related="location_id.address")
    is_final = fields.Boolean('Is Final')
    
    
    @api.model
    def create(self, vals):
        import datetime
        now = datetime.datetime.now().strftime ("%Y-%m-%d")
        from datetime import datetime
        d1 = datetime.strptime(str(now), "%Y-%m-%d")
        reminder = self.env['admin.configuration'].search([], limit=1)
        vip_partner = False
        if vals and 'partner_id' in vals.keys():
            project = self.env['res.partner'].search([('id', '=', vals['partner_id'])])
            if project.is_vip == True:
                vip_partner = True
        if vals and vals['is_final'] == False and vip_partner == False:
            if vals['booking_type'] in ['normal', 'sic'] and 'time_booking_ids' in vals.keys() and vals['time_booking_ids'] and vals['time_booking_ids'][0] and vals['time_booking_ids'][0][2]:
                if vals['time_booking_ids'][0][2]['booking_date']:
                    from datetime import datetime
                    d1 = datetime.strptime(str(now), "%Y-%m-%d")
                    d2 = datetime.strptime(vals['time_booking_ids'][0][2]['booking_date'], "%Y-%m-%d")
                    if reminder and reminder.customer_booking_days:
                        if int(reminder.customer_booking_days) < abs((d2 - d1).days):
                            raise Warning(_("You can not book %s days before the present day.") % reminder.customer_booking_days)
            else:
                if vals['booking_type'] in ['special', 'sic'] and vals['start_date_time']:
                    import datetime
                    dt = datetime.datetime.strptime(vals['start_date_time'],'%Y-%m-%d %H:%M:%S')
                    d3 = dt.date()
                    from datetime import datetime
                    d2 = datetime.strptime(str(d3), "%Y-%m-%d")
                    if reminder and reminder.customer_booking_days:
                        if int(reminder.customer_booking_days) < abs((d2 - d1).days):
                            raise Warning(_("You can not book %s days before the present day.") % reminder.customer_booking_days)
                
        vals['booking_no'] = self.env['ir.sequence'].next_by_code('project.booking') or _('New')

        result = super(project_booking, self).create(vals)
        return result
