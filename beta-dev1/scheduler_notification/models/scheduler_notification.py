from odoo import api, fields, models, http
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class ir_cron(models.Model):
    _inherit = 'ir.cron'

    @api.depends('transaction', 'res_id')
    def get_record_name(self):
        for rec in self:
            rec.record_name = ''
            if rec.transaction and rec.res_id != 0:
                model = rec.transaction.model
                record = rec.env[model].sudo().search([('id', '=', rec.res_id)])
                if record:
                    rec.record_name = record.name

    scheduler_setup = fields.Boolean("Scheduler Setup", default=False)
    transaction = fields.Many2one('ir.model', string='Transaction')
    transaction_model = fields.Char('Related Document Model', index=True, )
    res_id = fields.Integer('Transaction No', index=True, )
    record_name = fields.Char("Transaction No", compute="get_record_name")
    rec_date = fields.Datetime(string="Date", default=fields.Datetime.now)
    start_date = fields.Datetime("Start Reminder From", default=fields.Datetime.now)
    end_date = fields.Datetime("End Reminder To")
    subject = fields.Char('Email Subject', translate=True, help="Subject (placeholders may be used here)")
    body_html = fields.Html('Email Body', translate=True, sanitize=False)
    department_id = fields.Many2one('hr.department', string="Department")
    employee_ids = fields.Many2many('hr.employee', string='Employees')

    status = fields.Selection(selection=[('run','Running'),('done','Done'),('cancel','Cancel'),],
                             string='Status', default='run', help='Various states for record.')


    @api.onchange('employee_ids')
    def onchange_employee_ids(self):
        if self.record_name:
            self.name = self.transaction.name+' - '+self.record_name
            self.subject = "Reminder for " + self.name
            view = self.record_name
        else:
            self.name = self.transaction.name
            self.subject = "Reminder for " + self.name
            view = self.transaction.name

        link = self._context.get('record_url')

        if self.employee_ids:
            email_to = ''
            for employee in self.employee_ids:
                if employee.user_id and employee.user_id.login:
                    email_to = email_to + employee.name + ','

            if email_to:
                self.body_html = """
                    <p>
                        Dear %s
                    </p>
    
                    <p>
                        We would like to remind you about <a href=%s style = "padding: 5px 10px; font-size: 12px; line-height: 18px;
                     color: #FFFFFF; border-color:#875A7B; text-decoration: none; display: inline-block;
                     margin-bottom: 0px; font-weight: 400; text-align: center; vertical-align: middle;
                     cursor: pointer; white-space: nowrap; background-image: none; background-color: #875A7B;
                     border: 1px solid #875A7B; border-radius:3px">%s</a>  from %s.  
                    </p>
    
                    <p> Thank You. </p>""" % (email_to, link, view, self.env.user.company_id.name)

        else:
            email_to = "Receiver,"

            self.body_html = """
                <p>
                    Dear %s
                </p>
    
                <p>
                    We would like to remind you about <a href=%s style = "padding: 5px 10px; font-size: 12px; line-height: 18px;
                 color: #FFFFFF; border-color:#875A7B; text-decoration: none; display: inline-block;
                 margin-bottom: 0px; font-weight: 400; text-align: center; vertical-align: middle;
                 cursor: pointer; white-space: nowrap; background-image: none; background-color: #875A7B;
                 border: 1px solid #875A7B; border-radius:3px">%s</a>  from %s.  
                </p>
    
                <p> Thank You. </p>""" % (email_to, link, view, self.env.user.company_id.name)


    @api.onchange('start_date')
    def onchange_start_date(self):
        if self.start_date:
            self.nextcall = self.start_date

    @api.onchange('end_date')
    def onchange_end_date(self):
        if self.end_date:
            end_date = datetime.strptime(self.end_date, DEFAULT_SERVER_DATETIME_FORMAT)
            if datetime.now() > end_date:
                self.status = "done"
                self.active = False
            else:
                self.status = "run"
                self.active = True

    @api.onchange('record_name')
    def onchange_record_name(self):
        if self.record_name:
            self.name = self.transaction.name+' - '+self.record_name
            self.subject = "Reminder for " + self.name
            view = self.record_name
        else:
            self.name = self.transaction.name
            self.subject = "Reminder for " + self.name
            view = self.transaction.name

        link = self._context.get('record_url')
        email_to = "Receiver,"

        self.body_html = """
            <p>
                Dear %s
            </p>

            <p>
                We would like to remind you about <a href=%s style = "padding: 5px 10px; font-size: 12px; line-height: 18px;
             color: #FFFFFF; border-color:#875A7B; text-decoration: none; display: inline-block;
             margin-bottom: 0px; font-weight: 400; text-align: center; vertical-align: middle;
             cursor: pointer; white-space: nowrap; background-image: none; background-color: #875A7B;
             border: 1px solid #875A7B; border-radius:3px">%s</a>  from %s.  
            </p>

            <p> Thank You. </p>""" % (email_to, link, view, self.env.user.company_id.name)


    @api.onchange('department_id')
    def onchange_department_id(self):
        self.employee_ids = self.env['hr.employee'].search(
            [('department_id', '=', self.department_id.id), ('department_id', '!=', False)])


    @api.model
    def create(self,vals):
        res = super(ir_cron, self).create(vals)
        res.args = "("+ str(res.id)+",)"
        return res

    @api.onchange('transaction_model')
    def onchange_transaction_model(self):
        self.transaction = False
        if self.transaction_model:
            model_id = self.env['ir.model'].sudo().search([('model', '=', self.transaction_model)], limit=1)
            if model_id:
                self.transaction = model_id.id

    @api.multi
    def cancel_schedule_action(self):
        for rec in self:
            rec.active = False
            rec.status = "cancel"

    @api.multi
    def active_schedule_action(self):
        for rec in self:
            rec.active = True
            rec.status = "run"

    @api.multi
    def action_go_to_document(self):
        self.ensure_one()
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self.transaction.model,
            'res_id': self.res_id,
            'view_id': False,
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def action_close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def page_reload(self):
        return {'type': 'ir.actions.act_window_close'}


class SchedulerNotification(models.Model):
    _name = 'scheduler.notification'


    @api.multi
    def send_scheduler_notification_email(self, record_id=False):
        """ this method is called from Schedule setup """
        if record_id:
            schedule_action = self.env['ir.cron'].sudo().search([('id', '=', record_id),('active','=',True)],limit=1)
            if schedule_action:
                end_date = datetime.strptime(schedule_action.end_date, DEFAULT_SERVER_DATETIME_FORMAT)
                if datetime.now() > end_date:
                    schedule_action.active = False
                    schedule_action.status = "done"
                    return

                email_to = ''
                for employee in schedule_action.employee_ids:
                    """ send email to selected emaployee """
                    if employee.user_id and employee.user_id.login:
                        email_to = email_to + employee.user_id.login + ','

                if email_to:
                    vals = {
                        'auto_delete':True,
                        'state': 'outgoing',
                        'subject': schedule_action.subject,
                        'body_html': '%s' % schedule_action.body_html,
                        'email_to': email_to,
                        'email_from': self.env.user.company_id.email or 'Administrator <admin@example.com>',
                    }
                    email = self.env['mail.mail'].create(vals)
                    if email:
                        email.send()