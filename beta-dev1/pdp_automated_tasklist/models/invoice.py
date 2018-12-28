from datetime import datetime
from odoo import api, exceptions, fields, models, _, modules


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_open(self):
        res = super(AccountInvoice, self).action_invoice_open()
        if res:
            order = self
            self.create_auto_mail_activity(order)
        return res

    @api.multi
    def create_auto_mail_activity(self, order):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        menu_id = self.env['ir.model.data'].get_object_reference('account', 'menu_action_invoice_tree1')[1]
        action_id = self.env['ir.model.data'].get_object_reference('account', 'action_invoice_tree1')[1]
        url = base_url + "/web?#id=" + str(order.id) + "&view_type=form&model=account.invoice&" \
            "menu_id="+str(menu_id)+"&action=" + str(action_id)

        name = 'Customer Invoice'

        activity_type_id = self.env['mail.activity.type'].search([('name', '=', 'Customer Invoice')])
        if not activity_type_id:
            activity_type_id = self.env['mail.activity.type'].create(
                {'name': 'Customer Invoice', 'summary': 'Follow up Customer Invoice Entries'})

        note = """
                <html>
                    <head>
                        Dear %s (requester)
                    </head>
                    <body>
                        <span>
                            You need to follow up the %s <a href="%s" target="_blank">%s</a> <br/>
                            Thank You,
                        </span>
                    </body> 
                <html>""" % (self.env.user.name, name, url, order.number)

        model_id = self.env['ir.model'].search([('model', '=', 'account.invoice')])
        activity_vals = {
            'user_id': self._uid,
            'date_deadline': datetime.today(),
            'activity_type_id': activity_type_id and activity_type_id[0].id,
            'note': note,
            'res_id': order.id,
            'res_model': 'account.invoice',
            'res_model_id': model_id.id,
            'summary': activity_type_id.summary
        }
        test = self.env['mail.activity'].create(activity_vals)
        return True


