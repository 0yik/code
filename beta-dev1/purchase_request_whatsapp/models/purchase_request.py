from odoo import models, api

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    @api.multi
    def button_to_approve(self):
        for record in self:
            if record.product_ctg:
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                url = base_url + '/web#id=%s&view_type=form&model=purchase.request' % (record.id)
                approved_ids = record.product_ctg.line_ids.filtered(lambda r: r.check_amount(record.total_amout()) == True)
                for approved_id in self.env['pr.approving.matrix.line'].search([('id', 'in', approved_ids.ids)], order='sequence ASC', limit=1):
                    whatsapp_setting_id = self.env['mail.message.settings'].search([('message_type', '=', 'whatsapp'), ('default', '=', True)], limit=1)
                    if whatsapp_setting_id:
                        for employee in approved_id.employee_ids:
                            message = """Dear %s,
You have a Purchase Request *PR No %s waiting for your approval.
Please click %s to approve.
Vendor : %s.
Untaxed Amount : %s
Thank you
""" % (employee.name, record.name, url, record.requested_by.name if record.requested_by else '', record.total_amout())
                            vals = {}
                            vals['mobile_no'] = employee.work_phone
                            vals['message'] = message
                            vals['message_settings_id'] = whatsapp_setting_id.id
                            message = self.env['mail.message.log'].create(vals)
                            message.action_send()
        return super(PurchaseRequest, self).button_to_approve()

PurchaseRequest()
