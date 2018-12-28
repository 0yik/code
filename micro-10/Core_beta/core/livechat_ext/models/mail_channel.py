from odoo import models, fields, api

class MailChannel(models.Model):
    _inherit = 'mail.channel'

    display_start_page = fields.Boolean('Display Start Page?', default=True)
    anonymous_email = fields.Char('Anonymous Email')

    @api.multi
    def channel_info(self, extra_info=False):
        channel_infos = super(MailChannel, self).channel_info(extra_info)
        for count in range(0, len(channel_infos)):
            channel_obj = self.browse(channel_infos[count].get('id'))
            channel_infos[count].update({'display_start_page': channel_obj.display_start_page})
        return channel_infos

MailChannel()

class ImLivechatChannel(models.Model):
    _inherit = 'im_livechat.channel'

    notify_to_ids = fields.Many2many('res.users', string='Notify To')
    idle_minutes = fields.Integer('Idle Minutes before Notifications')

ImLivechatChannel()