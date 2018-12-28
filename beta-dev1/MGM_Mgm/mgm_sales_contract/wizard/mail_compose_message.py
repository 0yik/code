from odoo import api, models

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    def send_mail(self, auto_commit=False):
        if self._context.get('default_model') == 'sale.requisition' and self._context.get('default_res_id') and self._context.get('mark_fixture_as_sent'):
            order = self.env['sale.requisition'].browse([self._context['default_res_id']])
            if order.state =='draft1':
                order.state = 'inprogress'
            if order.state =='drafts':
                order.state = 'in_progress'
            self = self.with_context(mail_post_autofollow=True)
        return super(MailComposeMessage, self).send_mail(auto_commit=auto_commit)
