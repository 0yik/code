# -*- encoding: utf-8 -*-
from odoo import models, fields, api, tools
from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
try:
    import pycurl, json
except:
    import json
from StringIO import StringIO

class AisApiConfig(models.Model):
    _name = 'ais.api.config'
    _inherit = ['mail.thread']
    _description = 'AIS API Configuration'
    _order = 'id desc'

    name = fields.Char(required=True, string='API URL', track_visibility='onchange')
    client_id = fields.Char(string='Client ID')
    client_id2 = fields.Char(string='Client ID')
    display_client_id = fields.Char(compute='compute_client_id', string='Client ID')
    client_secret = fields.Char(string='Client Secret')
    client_secret2 = fields.Char(string='Client Secret')
    display_client_secret= fields.Char(compute='compute_client_secret', string='Client Secret')
    show_client_id = fields.Boolean(string='Show')
    show_client_secret = fields.Boolean(string='Show')
    company_id = fields.Many2one('res.company', string='Company', required=True, track_visibility='onchange', default=lambda self: self.env.user.company_id)
    history_ids = fields.One2many('ais.api.history', 'ais_api_id', string='History')

    @api.multi
    def compute_client_id(self):
        for record in self:
            if record.client_id:
                if len(record.client_id) <= 8:
                    record.display_client_id = record.client_id
                else:
                    client_id = record.client_id[:4]
                    for i in range(0, len(record.client_id[4:-4])):
                        client_id += '*'
                    client_id += record.client_id[-4:]
                    record.display_client_id = client_id
            else:
                record.display_client_id = False

    @api.multi
    def compute_client_secret(self):
        for record in self:
            if record.client_secret:
                if len(record.client_secret) <= 8:
                    record.display_client_secret = record.client_secret
                else:
                    client_secret = record.client_secret[:4]
                    for i in range(0, len(record.client_secret[4:-4])):
                        client_secret += '*'
                    client_secret += record.client_secret[-4:]
                    record.display_client_secret = client_secret
            else:
                record.display_client_secret = False

    @api.onchange('client_id')
    def onchange_client_id(self):
        if self._context.get('onchange_client_id', False):
            self.client_id2 = self.client_id

    @api.onchange('client_id2')
    def onchange_client_id2(self):
        if self._context.get('onchange_client_id2', False):
            self.client_id = self.client_id2

    @api.onchange('client_secret')
    def onchange_client_secret(self):
        if self._context.get('onchange_client_secret', False):
            self.client_secret2 = self.client_secret

    @api.onchange('client_secret2')
    def onchange_client_secret2(self):
        if self._context.get('onchange_client_secret2', False):
            self.client_secret = self.client_secret2

    @api.multi
    def action_connect(self):
        return {
            'name': 'Next Schedule',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ais.api.schedule',
            'target': 'new',
            'context': {'default_company_id': self.company_id.id}
        }

    @api.model
    def upload_txt_files(self):
        form_type = {'appendix8a': 'APPENDIX8A', 'ir8a': 'IR8A', 'ir8s': 'IR8S'}
        for line in self.env['ais.api.history'].search([('state', '=', 'pending'), ('next_schedule_date', '<=', str(date.today()))], order='id asc'):
            ais_api_id = line.ais_api_id
            header_list = [
                'accept: application/json',
                'Content-Type: application/json',
                'x-ibm-client-id: %s' % ais_api_id.client_id,
                'x-ibm-client-secret: %s' % ais_api_id.client_secret,
            ]
            json_data = {
                "clientID": "%s" % ais_api_id.client_id,
                "inputType": "TEXT",
                "a8bInput": "",
                "a8aInput": "",
                "ir8sInput": "",
                "ir8aInput": "",
                "userIDType": "%s" % line.user_id_type,
                "userID": "%s" % line.user_id,
                "bypass": "true",
                "validateOnly": "false"
            }
            vals = {}
            vals['start_date'] = line.start_date
            vals['end_date'] = line.end_date
            vals['source'] = line.source
            vals['organization_id_type'] = line.organization_id_type
            vals['organization_id_no'] = line.organization_id_no
            vals['batch_indicatior'] = line.batch_indicatior
            vals['batch_date'] = line.batch_date
            vals['payroll_user'] = line.payroll_user
            vals['company_id'] = line.company_id.id
            vals['print_type'] = 'text'
            vals['employee_ids'] = [(6, 0, line.employee_ids.ids)]
            submission_date = datetime.strptime(line.submission_date, DEFAULT_SERVER_DATETIME_FORMAT).strftime('%d/%m/%Y')
            if line.form_type == 'ir8a':
                try:
                    ir8a_id = self.env['emp.ir8a.text.file'].create(vals)
                    data = ir8a_id.download_ir8a_txt_file()
                    file_wizard = self.env[data['res_model']].browse(data['res_id'])
                    line.write({'file': file_wizard.ir8a_txt_file, 'filename': file_wizard.name})
                    json_data['ir8aInput'] = line.file.decode('base64')
                except Exception, e:
                    line.write({'state': 'failed'})
                    ais_api_id.message_post('<ul style="color:red"><li><b>Form Type : </b>%s</li><li><b>Status : </b>%s</li><li><b>Submission Date : </b>%s</li><li><b>Reason : </b>%s</li></ul>' %
                         (form_type[line.form_type], 'Failed', submission_date, e))
                    continue
            elif line.form_type == 'ir8s':
                try:
                    ir8s_id = self.env['emp.ir8s.text.file'].create(vals)
                    data = ir8s_id.download_ir8s_txt_file()
                    file_wizard = self.env[data['res_model']].browse(data['res_id'])
                    line.write({'file': file_wizard.ir8s_txt_file, 'filename': file_wizard.name})
                    json_data['ir8sInput'] = line.file.decode('base64')
                except Exception, e:
                    line.write({'state': 'failed'})
                    ais_api_id.message_post('<ul style="color:red"><li><b>Form Type : </b>%s</li><li><b>Status : </b>%s</li><li><b>Submission Date : </b>%s</li><li><b>Reason : </b>%s</li></ul>' %
                        (form_type[line.form_type], 'Failed', submission_date, e))
                    continue
            elif line.form_type == 'appendix8a':
                try:
                    appendix8a_id = self.env['emp.appendix8a.text.file'].create(vals)
                    data = appendix8a_id.download_appendix8a_txt_file()
                    file_wizard = self.env[data['res_model']].browse(data['res_id'])
                    line.write({'file': file_wizard.appendix8a_txt_file, 'filename': file_wizard.name})
                    json_data['a8aInput'] = line.file.decode('base64')
                except Exception, e:
                    line.write({'state': 'failed'})
                    ais_api_id.message_post('<ul style="color:red"><li><b>Form Type : </b>%s</li><li><b>Status : </b>%s</li><li><b>Submission Date : </b>%s</li><li><b>Reason : </b>%s</li></ul>' %
                        (form_type[line.form_type], 'Failed', submission_date, e))
                    continue
            try:
                c = pycurl.Curl()
                buffer = StringIO()
                c.setopt(c.URL, 'https://apisandbox.iras.gov.sg/iras/sb/AISubmission/submit')
                c.setopt(c.WRITEDATA, buffer)
                c.setopt(c.HTTPHEADER, header_list)
                c.setopt(c.POSTFIELDS, json.dumps(json_data))
                c.perform()
                c.close()
                response_data = buffer.getvalue()
                if type(response_data) == str:
                    response_data = json.loads(response_data)
                if response_data.get('statusCode', False) != '200':
                    line.write({'state': 'failed'})
                    ais_api_id.message_post('<ul style="color:red"><li><b>Form Type : </b>%s</li><li><b>Status : </b>%s</li><li><b>Submission Date : </b>%s</li><li><b>Reason : </b>%s</li></ul>' %
                        (form_type[line.form_type], 'Failed', submission_date, str(response_data)))
                else:
                    line.write({'state': 'success', 'no_of_records': len(line.employee_ids.ids)})
                    ais_api_id.message_post('<ul style="color:green"><li><b>Form Type : </b>%s</li><li><b>Status : </b>%s</li><li><b>Submission Date : </b>%s</li><li><b>Response : </b>%s</li></ul>' %
                        (form_type[line.form_type], 'Success', submission_date, str(response_data)))
            except Exception, e:
                line.write({'state': 'failed'})
                ais_api_id.message_post('<ul style="color:red"><li><b>Form Type : </b>%s</li><li><b>Status : </b>%s</li><li><b>Submission Date : </b>%s</li><li><b>Reason : </b>%s</li></ul>' %
                    (form_type[line.form_type], 'Failed', submission_date, e))

AisApiConfig()

class AisApiHistory(models.Model):
    _name = 'ais.api.history'
    _description = 'AIS API History'
    _order = 'id desc'

    @api.multi
    def _get_payroll_user_name(self):
        supervisors_list = []
        data_obj = self.env['ir.model.data']
        result_data = data_obj._get_id('l10n_sg_hr_payroll', 'group_hr_payroll_admin')
        model_data = data_obj.browse(result_data)
        group_data = self.env['res.groups'].browse(model_data.res_id)
        for user in group_data.users:
            supervisors_list.append((tools.ustr(user.id), tools.ustr(user.name)))
        return supervisors_list

    ais_api_id = fields.Many2one('ais.api.config', string='AIS Config')
    form_type = fields.Selection([('ir8a', 'IR8A'), ('ir8s', 'IR8S'), ('appendix8a', 'APPENDIX8A')], string='Form Type')
    submission_date = fields.Datetime(string='Submission Date')
    no_of_records = fields.Integer(string='No. of Records Submitted')
    state = fields.Selection([('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')], default='pending', string='Connection Status')
    next_schedule_date = fields.Date(string='Next Schedule Date')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    source = fields.Selection(selection=[
        ('1', 'Mindef'),
        ('4', 'Government Department'),
        ('5', 'Statutory Board'),
        ('6', 'Private Sector'),
        ('9', 'Others')], string='Source', default='6', required=True)
    organization_id_type = fields.Selection(selection=[
        ('7', 'UEN – Business Registration number issued by ACRA'),
        ('8', 'UEN – Local Company Registration number issued by ACRA'),
        ('A', 'ASGD – Tax Reference number assigned by IRAS'),
        ('I', 'ITR – Income Tax Reference number assigned by IRAS'),
        ('U', 'UENO – Unique Entity Number Others')], string='Organization ID Type', default='8', required=True)
    organization_id_no = fields.Char('Organization ID No', size=16, required=True)
    batch_indicatior = fields.Selection(selection=[
        ('O', 'Original'),
        ('A', 'Amendment')], string='Batch Indicator', required=True)
    batch_date = fields.Date('Batch Date', required=True, default=fields.Date.today)
    payroll_user = fields.Selection(_get_payroll_user_name, string='Authorised Person', size=128)
    file = fields.Binary()
    filename = fields.Char()
    user_id = fields.Char(string='User ID')
    user_id_type = fields.Selection([('1', 'NRIC'), ('2', 'FIN'), ('4', 'WP'), ('A', 'ASGD'), ('11', 'MIC')], string='User ID Type')
    employee_ids = fields.Many2many('hr.employee', string='Employees')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)

    def action_redo(self):
        self.write({'state': 'pending'})

AisApiHistory()