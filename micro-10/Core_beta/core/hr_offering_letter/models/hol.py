

import base64
import datetime
import logging
import psycopg2
import threading

from email.utils import formataddr

from odoo import _, api, fields, models
from odoo import tools
from odoo.addons.base.ir.ir_mail_server import MailDeliveryException
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class ApplicantCustom(models.Model):
    _inherit = "hr.applicant"
    
    state_the_state = fields.Char(related='stage_id.name')
    @api.multi
    def action_print_offering_letter(self):
        active_ids = self.env.context.get('active_ids', [])
        datas = {
            'ids': active_ids,
             'model': 'report.model',
             'form': self.read()[0]
        }
        return self.env['report'].get_action(self, 'hr_offering_letter.report_summary',data=datas)
    
    @api.multi
    def action_email_offering_letter(self):
        active_ids = self.env.context.get('active_ids', [])
        login = self.env['res.users'].search([('id','=',active_ids)])
        template_obj = self.env['mail.mail']
        message_body ='<p style="margin:0px 0px 9px 0px;font-size:13px;font-family:&quot;Lucida Grande&quot;, Helvetica, Verdana, Arial, sans-serif;">Private and Confidential </p><p style="margin:0px 0px 9px 0px;font-size:13px;font-family:&quot;Lucida Grande&quot;, Helvetica, Verdana, Arial, sans-serif;">Dear '+ self.name +' </p><p style="margin:0px 0px 9px 0px;font-size:13px;font-family:&quot;Lucida Grande&quot;, Helvetica, Verdana, Arial, sans-serif;">\nThank you once again for your interest in '+self.company_id.name +'\n </p><p>We are pleased to offer you the '+ self.job_id.name+ ' opportunity with \n '+ self.company_id.name +'.\n</p><p style="margin:0px 0px 9px 0px;font-size:13px;font-family:&quot;Lucida Grande&quot;, Helvetica, Verdana, Arial, sans-serif;">Essential Job Functions:\n '+str(self.description)+' \n</p><p style="margin:0px 0px 9px 0px;font-size:13px;font-family:&quot;Lucida Grande&quot;, Helvetica, Verdana, Arial, sans-serif;"><p>Salary\n</p>The company will pay you a starting salary at the rate of '+ login.currency_id.name+' '+str(self.salary_proposed) +' per month, payable in accordance with the Company\'s standard payroll\nschedule.\n</p><p style="margin:0px 0px 9px 0px;font-size:13px;font-family:&quot;Lucida Grande&quot;, Helvetica, Verdana, Arial, sans-serif;">This salary will be subject to adjustment pursuant to the company\'s employee compensation policies.\n</p><p style="margin:0px 0px 9px 0px;font-size:13px;font-family:&quot;Lucida Grande&quot;, Helvetica, Verdana, Arial, sans-serif;">Please do let us know if you have any further questions at this point of time. Once you send me an email confirming your acceptance of\nthe offer, we will prepare your contract. We look forward to join our company in order to work with you.\n</p><p style="margin:0px 0px 9px 0px;font-size:13px;font-family:&quot;Lucida Grande&quot;, Helvetica, Verdana, Arial, sans-serif;"><br></p><p style="margin:0px 0px 9px 0px;font-size:13px;font-family:&quot;Lucida Grande&quot;, Helvetica, Verdana, Arial, sans-serif;">Sincerely,\n</p><p style="margin:0px 0px 9px 0px;font-size:13px;font-family:&quot;Lucida Grande&quot;, Helvetica, Verdana, Arial, sans-serif;"> '+self.user_id.name+'</p>'
        template_data = {
                'subject': 'Due Invoice Notification : ',
                'body_html': message_body,
                'email_from': self.env['res.users'].search([('id','=',active_ids)]).login,
                'email_to': self.email_from,
                }
        template_id = template_obj.create(template_data)
        template_obj.send(template_id)



class MailMail(models.Model):

    _inherit = 'mail.mail'


    @api.multi
    def send(self, auto_commit=False, raise_exception=False):
        """ Sends the selected emails immediately, ignoring their current
            state (mails that have already been sent should not be passed
            unless they should actually be re-sent).
            Emails successfully delivered are marked as 'sent', and those
            that fail to be deliver are marked as 'exception', and the
            corresponding error mail is output in the server logs.

            :param bool auto_commit: whether to force a commit of the mail status
                after sending each mail (meant only for scheduler processing);
                should never be True during normal transactions (default: False)
            :param bool raise_exception: whether to raise an exception if the
                email sending process has failed
            :return: True
        """
        IrMailServer = self.env['ir.mail_server']

        for mail_id in (self.ids or auto_commit.ids):
            try:
                mail = self.browse(mail_id)
                # TDE note: remove me when model_id field is present on mail.message - done here to avoid doing it multiple times in the sub method
                if mail.model:
                    model = self.env['ir.model'].sudo().search([('model', '=', mail.model)])[0]
                else:
                    model = None
                if model:
                    mail = mail.with_context(model_name=model.name)

                # load attachment binary data with a separate read(), as prefetching all
                # `datas` (binary field) could bloat the browse cache, triggerring
                # soft/hard mem limits with temporary data.
                attachments = [(a['datas_fname'], base64.b64decode(a['datas']))
                               for a in mail.attachment_ids.sudo().read(['datas_fname', 'datas'])]

                # specific behavior to customize the send email for notified partners
                email_list = []
                if mail.email_to:
                    email_list.append(mail.send_get_email_dict())
                for partner in mail.recipient_ids:
                    email_list.append(mail.send_get_email_dict(partner=partner))

                # headers
                headers = {}
                bounce_alias = self.env['ir.config_parameter'].get_param("mail.bounce.alias")
                catchall_domain = self.env['ir.config_parameter'].get_param("mail.catchall.domain")
                if bounce_alias and catchall_domain:
                    if mail.model and mail.res_id:
                        headers['Return-Path'] = '%s+%d-%s-%d@%s' % (bounce_alias, mail.id, mail.model, mail.res_id, catchall_domain)
                    else:
                        headers['Return-Path'] = '%s+%d@%s' % (bounce_alias, mail.id, catchall_domain)
                if mail.headers:
                    try:
                        headers.update(safe_eval(mail.headers))
                    except Exception:
                        pass

                # Writing on the mail object may fail (e.g. lock on user) which
                # would trigger a rollback *after* actually sending the email.
                # To avoid sending twice the same email, provoke the failure earlier
                mail.write({
                    'state': 'exception',
                    'failure_reason': _('Error without exception. Probably due do sending an email without computed recipients.'),
                })
                mail_sent = False

                # build an RFC2822 email.message.Message object and send it without queuing
                res = None
                for email in email_list:
                    msg = IrMailServer.build_email(
                        email_from=mail.email_from,
                        email_to=email.get('email_to'),
                        subject=mail.subject,
                        body=email.get('body'),
                        body_alternative=email.get('body_alternative'),
                        email_cc=tools.email_split(mail.email_cc),
                        reply_to=mail.reply_to,
                        attachments=attachments,
                        message_id=mail.message_id,
                        references=mail.references,
                        object_id=mail.res_id and ('%s-%s' % (mail.res_id, mail.model)),
                        subtype='html',
                        subtype_alternative='plain',
                        headers=headers)
                    try:
                        res = IrMailServer.send_email(msg, mail_server_id=mail.mail_server_id.id)
                    except AssertionError as error:
                        if error.message == IrMailServer.NO_VALID_RECIPIENT:
                            # No valid recipient found for this particular
                            # mail item -> ignore error to avoid blocking
                            # delivery to next recipients, if any. If this is
                            # the only recipient, the mail will show as failed.
                            _logger.info("Ignoring invalid recipients for mail.mail %s: %s",
                                         mail.message_id, email.get('email_to'))
                        else:
                            raise
                if res:
                    mail.write({'state': 'sent', 'message_id': res, 'failure_reason': False})
                    mail_sent = True

                # /!\ can't use mail.state here, as mail.refresh() will cause an error
                # see revid:odo@openerp.com-20120622152536-42b2s28lvdv3odyr in 6.1
                if mail_sent:
                    _logger.info('Mail with ID %r and Message-Id %r successfully sent', mail.id, mail.message_id)
                mail._postprocess_sent_message(mail_sent=mail_sent)
            except MemoryError:
                # prevent catching transient MemoryErrors, bubble up to notify user or abort cron job
                # instead of marking the mail as failed
                _logger.exception(
                    'MemoryError while processing mail with ID %r and Msg-Id %r. Consider raising the --limit-memory-hard startup option',
                    mail.id, mail.message_id)
                raise
            except psycopg2.Error:
                # If an error with the database occurs, chances are that the cursor is unusable.
                # This will lead to an `psycopg2.InternalError` being raised when trying to write
                # `state`, shadowing the original exception and forbid a retry on concurrent
                # update. Let's bubble it.
                raise
            except Exception as e:
                failure_reason = tools.ustr(e)
                _logger.exception('failed sending mail (id: %s) due to %s', mail.id, failure_reason)
                mail.write({'state': 'exception', 'failure_reason': failure_reason})
                mail._postprocess_sent_message(mail_sent=False)
                if raise_exception:
                    if isinstance(e, AssertionError):
                        # get the args of the original error, wrap into a value and throw a MailDeliveryException
                        # that is an except_orm, with name and value as arguments
                        value = '. '.join(e.args)
                        raise MailDeliveryException(_("Mail Delivery Failed"), value)
                    raise

            if auto_commit is True:
                self._cr.commit()
        return True

class ReportHOL(models.AbstractModel):
    _name = 'report.hr_offering_letter.report_summary' #report.modulename.your_modelname of report

    

    
    @api.model
    @api.multi
    def render_html(self, docids, data=None):
        arr=[]
        curr= self.env['res.company'].search([])[0].currency_id.name

        docargs = {
                   'datas':data,
                   'cur':curr
                    }

          
        return self.env['report'].render('hr_offering_letter.report_summary',docargs)
    
    
    
    