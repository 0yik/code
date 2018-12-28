from odoo import api, fields, models

class CustomerWizard(models.TransientModel):
    _name = 'customer.wizard'
    _description = 'Customer Wizard'

    partner_name = fields.Char('Customer Name')
    contact_name = fields.Char('Contact Name')
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip')
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", string='State')
    country_id = fields.Many2one('res.country', string='Country')
    phone = fields.Char('Phone')
    fax = fields.Char('Fax')
    mobile = fields.Char('Mobile')
    function = fields.Char('Job Position')
    title = fields.Many2one('res.partner.title')
    email = fields.Char('Email')


    @api.multi
    def action_create_customer(self):
        ctx= self._context if self._context else {}
        if 'lead_id' in ctx:
            lead_obj= self.env['crm.lead'].browse(ctx['lead_id'])
            vals = {}
            vals['name'] = self.partner_name
            vals['street'] = self.street
            vals['street2'] = self.street2
            vals['city'] = self.city
            vals['state_id'] = self.state_id.id
            vals['zip'] = self.zip
            vals['country_id'] = self.country_id.id
            vals['title'] = self.title.id
            vals['function'] = self.function
            vals['phone'] = self.phone
            vals['mobile'] = self.mobile
            vals['fax'] = self.fax
            vals['email'] = self.email
            self.env['res.partner'].create(vals)
            lead_obj.action_set_won2()
        return True

CustomerWizard()