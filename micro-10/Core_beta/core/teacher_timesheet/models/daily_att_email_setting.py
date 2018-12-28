# -*- coding: utf-8 -*-
from odoo import fields, models, exceptions, api
from odoo.tools.translate import _

from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import ustr

class DailyAttEmailSetting(models.Model):
    _name = 'daily.attendance.email.setting'
    
    def _get_body(self):
        msg = '''Dear %s,<br/>
            %s forgot to submit attendance sheet.<br/>
            <b>Class</b>:%s<br/>
            <b>Subject</b>:%s <br/>
            <b>URL</b>:<a href=%s target='new'>Click here</a><br/>
            Regards,<br/>
            %s'''
        return msg
        
    send = fields.Boolean(String="SendEmail?", help="IF Ticked then Only Emails will be send.")        
    days = fields.Integer(string="Reminder Days",required=True)
    subject = fields.Char(string="Subject",required=True,default="Daily Attendance Sheet Submission")
    body = fields.Html(string="Body",required=True,default=_get_body)
    
    _rec_name = 'subject'
    
class DailyAttExt(models.Model):
    _inherit = 'daily.attendance'
    
    @api.multi
    def cron_remind_admin_daily_att_submission(self):
        daily_att_email = self.env['daily.attendance.email.setting'].search([],limit=1)
        if daily_att_email and daily_att_email[0].send:
            open_daily_atts = self.search([('state','=','draft')])
            admin = self.env['res.users'].browse(self._uid)
            url = str(self.env['ir.config_parameter'].get_param('web.base.url'))
            for rec in open_daily_atts:
                rec_date = datetime.strptime(rec.date.split(' ')[0],"%Y-%m-%d")
                rec_date = (rec_date + relativedelta(days=daily_att_email.days)).strftime("%Y-%m-%d")
                if str(rec_date).split(' ')[0] == str(datetime.today().date()):
                    url += '/web#id=%s&view_type=%s&model=%s'%(rec.id,'form','daily.attendance')
                    mail_values = {
                        'subject':ustr(daily_att_email.subject),
                        'author_id':self.env.user.partner_id.id,
                        'email_from':admin.partner_id.email or '',
                        'email_to':admin.partner_id.email or '',
                        'reply_to':admin.partner_id.email or '',
                        'body_html':ustr(daily_att_email.body)%(admin.partner_id.name,rec.teacher_id.name,rec.class_id.name,rec.subject_id.name,url,admin.partner_id.name),
                    }
                    mail_sent = self.env['mail.mail'].create(mail_values).send()
