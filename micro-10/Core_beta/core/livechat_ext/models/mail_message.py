from odoo import models, api

class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.multi
    def message_format(self):
        result = super(MailMessage, self).message_format()
        for count in range(0,len(result)):
            message = self.browse(result[count].get('id'))
            if not message.author_id.ids and not message.email_from and (message.model == 'mail.channel'):
                channel = self.env['mail.channel'].browse(message.res_id)
                result[count].update({'email_from': channel.anonymous_name})
        return result

    @api.model
    def create(self, vals):
        self.notify_message(vals)
        return super(MailMessage, self).create(vals)

    @api.model
    def notify_message(self, vals):
        if vals.get('model') == 'mail.channel':
            channel_obj = self.env[vals.get('model')].browse(vals.get('res_id'))
            if channel_obj.livechat_channel_id and channel_obj.livechat_channel_id.notify_to_ids and channel_obj.livechat_channel_id.idle_minutes:
                user_ids = self.env['res.users'].search([('partner_id','in',channel_obj.channel_partner_ids.ids)])
                self.env.cr.execute("""
                    SELECT
                        user_id as id,
                        CASE WHEN age(now() AT TIME ZONE 'UTC', last_poll) > interval %s THEN 'offline'
                             WHEN age(now() AT TIME ZONE 'UTC', last_presence) > interval %s THEN 'offline'
                             ELSE 'online'
                        END as status
                    FROM bus_presence
                    WHERE user_id IN %s
                    """, ("%s minutes" % channel_obj.livechat_channel_id.idle_minutes, "%s minutes" % channel_obj.livechat_channel_id.idle_minutes, tuple(user_ids.ids)))
                result = dict(((status['id'], status['status']) for status in self.env.cr.dictfetchall()))

                for user in user_ids:
                    if result.get(user.id) != 'online':
                        message = '<p><i><font style="font-size: 18px;" class="">Hi</font><font style="font-size: 18px;">&nbsp;'+user.name+\
                        '!</font></i></p><p>You seem to be offline for more than '+str(channel_obj.livechat_channel_id.idle_minutes)+\
                        ' minute(s). You have the following message in your livechat<br></p><p style="color:red;"></p><pre><font style="color: rgb(255, 0, 0);">'\
                        +vals.get('body')+'</font></pre><p><font style="font-size: 14px;">Live chat&nbsp;</font><font style="font-size: 14px;">Ref :&nbsp;<b>'+channel_obj.name+'</b></font></p>'

                        email_to = ''
                        for usr in channel_obj.livechat_channel_id.notify_to_ids:
                            email_to += usr.email+', '
                        mail_values = {
                            'email_from': False,
                            'reply_to': False,
                            'email_to': email_to[:-2],
                            'subject': 'Livechat Message : Notification',
                            'body_html': message,
                            'notification': True,
                        }
                        mail = self.env['mail.mail'].create(mail_values)
                        mail.send()
                        break
        return True

MailMessage()