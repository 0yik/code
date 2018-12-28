from odoo import models, fields, api, _, SUPERUSER_ID

class ResUsers(models.Model):
    _inherit = 'res.users'

    pin_number = fields.Integer(string="PIN Number")

    _sql_constraints = [
        ('unique_pin', 'unique (pin_number)', 'The PIN NUmber must be unique!')
    ]
    
    @api.model
    def compare_pin_number(self, pin_number):
        group_pos_manager_id = self.env.ref('point_of_sale.group_pos_manager')
        user_ids = self.search([('groups_id', 'in', group_pos_manager_id.id)])
        all_pins = [user.pin_number for user in user_ids]
        if int(pin_number) in all_pins:
            return True
        return False

    @api.model
    def send_mail_pos_managers(self, note):
        last_pos_order = self.env['pos.order'].search([])[0]
        last_pos_order.state = 'draft'
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        group_pos_manager_id = self.env.ref('point_of_sale.group_pos_manager')
        user_ids = self.search([('groups_id', 'in', group_pos_manager_id.id)])
        admin_user_id = self.browse(SUPERUSER_ID)
        subject = """Staff Meal Order : %s """ % (note)
        mail_sent = False
        for user_id in user_ids:
            mail_vals = {}
            message = """
                        <p>Hello %s,</p>
                        <p>Please process the order regarding staff meal for %s </p>
                        <a href='%s/confirm-pos-order/%s'>Approve %s</a>
                        <p>Regards,</p>
                        <p>Admin</p>""" % (user_id.name, note,base_url,str(last_pos_order.id),str(last_pos_order.name))

            mail_vals['email_from'] = admin_user_id.partner_id.email
            mail_vals['email_to'] = user_id.partner_id.email
            mail_vals['subject'] = subject
            mail_vals['state'] = 'outgoing'
            mail_vals['body_html'] = message
            mail_id = self.env['mail.mail'].create(mail_vals)
            if mail_id:
                is_mail_sent = mail_id.send()
                mail_sent = True
        if mail_sent:
            return True
        return False

    @api.model
    def send_sms_pos_managers(self, note):
        last_pos_order = self.env['pos.order'].search([])[0]
        last_pos_order.state = 'draft'
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        group_pos_manager_id = self.env.ref('point_of_sale.group_pos_manager')
        user_ids = self.search([('groups_id', 'in', group_pos_manager_id.id)])
        sms_setting_id = self.env['mail.message.settings'].search([('message_type','=','sms'),('default','=',True)], limit=1)
        whatsapp_setting_id = self.env['mail.message.settings'].search([('message_type','=','whatsapp'),('default','=',True)], limit=1)

        for user_id in user_ids:
            employee_ids = self.env['hr.employee'].search([('user_id','=',user_id.id)])
            for employee in employee_ids:
                if employee.work_phone:
                    try:
                        message = """Hello %s,
Please process the order regarding staff meal for %s 
%s/confirm-pos-order/%s Approve (%s)
Regards,
Admin""" % (user_id.name, note,base_url,str(last_pos_order.id),str(last_pos_order.name))
                        vals = {}
                        vals['mobile_no'] = employee.work_phone
                        vals['message'] = message
                        if sms_setting_id:
                            vals['message_settings_id'] = sms_setting_id.id
                            message = self.env['mail.message.log'].create(vals)
                            message.action_send()
                        if whatsapp_setting_id:
                            vals['message_settings_id'] = whatsapp_setting_id.id
                            message = self.env['mail.message.log'].create(vals)
                            message.action_send()
                    except:
                        pass
        return True
