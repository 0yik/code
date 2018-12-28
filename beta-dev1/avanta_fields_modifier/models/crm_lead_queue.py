# -*- coding: utf-8 -*-
from odoo import models, fields, api
import openpyxl
from tempfile import TemporaryFile
from datetime import datetime

class CrmLeadQueue(models.Model):
    _name = 'crm.lead.queue'
    _inherit = ['mail.thread']
    _description = 'CRM Lead Queue'
    _rec_name = 'filename'
    _order = 'id desc'

    file = fields.Binary(readonly=True, string='Import File')
    filename = fields.Char()
    lead_type = fields.Selection([('individual', 'Individual'), ('company', 'Company')], readonly=True, string='Lead Type')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user.id, readonly=True, string='User')
    error_message = fields.Text('Error Message')
    state = fields.Selection([('draft', 'Draft'), ('inprogress', 'In Progress'), ('fail', 'Failed'), ('done', 'Done')], default='draft', string='Status')
    testing_field = fields.Char()

    def action_retry(self):
        self.write({'state': 'draft'})

    @api.model
    def create_crm_leads(self):
        for record in self.search([('state', 'not in', ['fail', 'done'])], order='id asc', limit=1):
            self._cr.execute("update crm_lead_queue set state='inprogress' where id=%s"% record.id)
            self._cr.commit()
            excel_file = record.file.decode('base64')
            excel_fileobj = TemporaryFile('wb+')
            excel_fileobj.write(excel_file)
            excel_fileobj.seek(0)

            workbook = openpyxl.load_workbook(excel_fileobj, data_only=True)
            sheet = workbook[workbook.get_sheet_names()[0]]
            if record.lead_type == 'individual':
                record.import_individual_leads(sheet)
            else:
                record.import_company_leads(sheet)
        return True

    def import_individual_leads(self, sheet):
        first_row = True
        count = 0
        try:
            for row in sheet.rows:
                count += 1
                # Individual leads import
                lead_vals, partner_vals = {}, {}
                if first_row:
                    first_row = False
                    continue

                if not row[0].value and not row[1].value and not row[2].value and not row[3].value and not row[4].value and not row[5].value and \
                        not row[6].value and not row[7].value and not row[8].value and not row[9].value and not row[10].value and not row[11].value\
                        and not row[12].value and not row[13].value:
                    break

                date = row[0].value
                service_name = row[1].value.replace("'", "")
                product_name = row[2].value.replace("'", "")
                customer_name = row[4].value.replace("'", "")
                address = row[5].value
                zip = row[6].value
                country = row[7].value
                job_position = row[8].value
                industry_type = row[9].value
                mobile = row[10].value
                email = row[11].value
                source_name = row[12].value
                status = row[13].value and row[13].value.lower()

                if not product_name or not service_name:
                    continue
                if customer_name:
                    if service_name:
                        self._cr.execute("SELECT id FROM product_template WHERE name ilike '%s' AND type='service'"% service_name)
                        data = self._cr.fetchone()
                        if data:
                            service_id = data[0]
                        else:
                            service_id = self.env['product.template'].sudo().create({'name': service_name, 'type': 'service'}).id
                        lead_vals['services'] = service_id
                    if product_name:
                        self._cr.execute("SELECT id FROM product_template WHERE name ilike '%s' AND type='consu'"% product_name)
                        data = self._cr.fetchone()
                        if data:
                            product_id = data[0]
                        else:
                            product_id = self.env['product.template'].sudo().create({'name': product_name, 'type': 'consu'}).id
                        lead_vals['products'] = product_id
                        lead_vals['on_products'] = False
                    if customer_name:
                        self._cr.execute("SELECT id FROM res_partner WHERE name ilike '%s' AND customer=True"% customer_name)
                        data = self._cr.fetchone()
                        if data:
                            partner_id = data[0]
                        else:
                            partner_id = self.env['res.partner'].sudo().create({'name': customer_name, 'company_type': 'person', 'customer':True, 'user_id': self.user_id.id if self.user_id else False}).id
                        lead_vals['partner_id'] = partner_id
                        lead_vals['name'] = self.env['res.partner'].sudo().browse(partner_id).display_name if partner_id else ''
                        if address:
                            partner_vals['street'] = address
                            lead_vals['street'] = address
                        if zip:
                            partner_vals['zip'] = zip
                            lead_vals['zip'] = zip
                        if job_position:
                            partner_vals['function'] = job_position
                            lead_vals['function'] = job_position
                        if industry_type:
                            industry_type_id = self.env['industry.type'].sudo().search([('name', 'ilike', industry_type)], limit=1)
                            if industry_type_id:
                                partner_vals['industry_type'] = industry_type_id.id
                            else:
                                partner_vals['industry_type'] = self.env['industry.type'].sudo().create({'name': industry_type}).id
                        if country:
                            country_ids = self.env['res.country'].sudo().search([('name', 'ilike', country.strip())])
                            if country_ids:
                                country_id = country_ids[0]
                                lead_vals['country_id'] = country_id.id
                        if mobile:
                            partner_vals['mobile'] = mobile
                            lead_vals['mobile'] = mobile
                            partner_vals['phone'] = mobile
                            lead_vals['phone'] = mobile
                        if email:
                            partner_vals['email'] = email
                            lead_vals['email_from'] = email
                        partner_vals['company_type'] = 'person'
                        partner_vals['is_company'] = False
                        self.env['res.partner'].sudo().browse(partner_id).write(partner_vals)
                    if source_name:
                        self._cr.execute("SELECT id FROM utm_source WHERE name ilike '%s'"% source_name)
                        data = self._cr.fetchone()
                        if data:
                            source_id = data[0]
                        else:
                            source_id = self.env['utm.source'].sudo().create({'name': source_name}).id
                        lead_vals['source_id'] = source_id
                    if date:
                        date = str(date).strip()
                        if "/" in date:
                            date = str(datetime.strptime(date, '%d/%m/%Y'))
                        if "." in date:
                            split_data = date.split('.')
                            if len(split_data[2]) == 2:
                                date = str(datetime.strptime(date, '%d.%m.%y'))
                            else:
                                date = str(datetime.strptime(date, '%d.%m.%Y'))
                        lead_vals['creation_date'] = date
                    lead_vals['user_id'] = self.user_id.id if self.user_id else False
                    lead_id = self.env['crm.lead'].sudo().create(lead_vals)
                    lead_won_obj = self.env['crm.lead.won'].sudo()
                    lead_lost_obj = self.env['crm.lead.lost'].sudo()
                    if status.lower() == 'dead':
                        lead_id.to_dead()
                    elif status.lower() == 'kiv':
                        lead_id.to_followup()
                    elif status.lower() == 'won':
                        lead_id.sudo().to_followup()
                        lead_won_vals = {}
                        lead_won_vals['won_reason'] = 'closed'
                        lead_won_vals['lead_id'] = lead_id.id
                        lead_won_id = lead_won_obj.sudo().create(lead_won_vals)
                        lead_won_id.action_won_reason_apply()
                    elif status.lower() == 'inprogress':
                        lead_id.to_followup()
                        lead_inprogress_vals = {}
                        lead_inprogress_vals['won_reason'] = 'in_progress'
                        lead_inprogress_vals['lead_id'] = lead_id.id
                        lead_inprogress_id = lead_won_obj.sudo().create(lead_inprogress_vals)
                        lead_inprogress_id.action_won_reason_apply()
                    elif status.lower() == 'lost':
                        lead_id.to_followup()
                        lead_lost_vals = {}
                        self._cr.execute("SELECT id FROM crm_lost_reason WHERE name ilike 'Too expensive' AND active=True")
                        data = self._cr.fetchone()
                        if data:
                            reason_id = data[0]
                            lead_lost_vals['lost_reason_id'] = reason_id
                            lead_lost_vals['lead_id'] = lead_id.id
                            lead_lost_obj = lead_lost_obj.sudo().create(lead_lost_vals)
                            lead_lost_obj.action_lost_reason_apply()
                    else:
                        stage_id = self.env['ir.model.data'].xmlid_to_res_id('avanta_fields_modifier.crm_status_enquiry')
                        if stage_id:
                            lead_id.sudo().write({'stage_id': stage_id})
            self.write({'state': 'done'})
        except Exception, e:
            self._cr.rollback()
            self._cr.execute("update crm_lead_queue set state='fail', error_message='Error while import. Line no %s' where id=%s"% (str(count), str(self.id)))
            self._cr.commit()

    def import_company_leads(self, sheet):
        excel_file = self.file.decode('base64')
        excel_fileobj = TemporaryFile('wb+')
        excel_fileobj.write(excel_file)
        excel_fileobj.seek(0)

        workbook = openpyxl.load_workbook(excel_fileobj, data_only=True)
        sheet = workbook[workbook.get_sheet_names()[0]]
        first_row = True
        count = 0
        try:
            for row in sheet.rows:
                count += 1
                # Company leads import
                lead_vals, partner_vals = {}, {}
                if first_row:
                    first_row = False
                    continue

                if not row[0].value and not row[1].value and not row[2].value and not row[3].value and not row[4].value and not row[5].value and \
                        not row[6].value and not row[7].value and not row[8].value and not row[9].value and not row[10].value and not row[11].value \
                        and not row[12].value and not row[13].value and not row[14].value:
                    break

                date = row[0].value
                service_name = row[1].value.replace("'", "")
                product_name = row[2].value.replace("'", "")
                company_name = row[3].value.replace("'", "")
                customer_name = row[5].value.replace("'", "")
                address = row[6].value
                zip = row[7].value
                country = row[8].value
                job_position = row[9].value
                industry_type = row[10].value
                mobile = row[11].value
                email = row[12].value
                source_name = row[13].value
                status = row[14].value and row[14].value.lower()

                if company_name:
                    if service_name:
                        self._cr.execute("SELECT id FROM product_template WHERE name ilike '%s' AND type='service'"% service_name)
                        data = self._cr.fetchone()
                        if data:
                            service_id = data[0]
                        else:
                            service_id = self.env['product.template'].sudo().create({'name': service_name, 'type': 'service'}).id
                        lead_vals['services'] = service_id

                    if product_name:
                        self._cr.execute("SELECT id FROM product_template WHERE name ilike '%s' AND type='consu'"% product_name)
                        data = self._cr.fetchone()
                        if data:
                            product_id = data[0]
                        else:
                            product_id = self.env['product.template'].sudo().create({'name': product_name, 'type': 'consu'}).id
                        lead_vals['products'] = product_id
                        lead_vals['on_products'] = False

                    if company_name:
                        self._cr.execute("SELECT id FROM res_partner WHERE name ilike '%s' AND customer=True"% company_name)
                        data = self._cr.fetchone()
                        if data:
                            partner_id = data[0]
                        else:
                            partner_id = self.env['res.partner'].sudo().create({'name': company_name, 'company_type': 'company', 'customer':True, 'user_id': self.user_id.id if self.user_id else False}).id
                        lead_vals['partner_id'] = partner_id
                        lead_vals['partner_name'] = customer_name
                        lead_vals['name'] = self.env['res.partner'].sudo().browse(partner_id).display_name if partner_id else ''
                        if address:
                            partner_vals['street'] = address
                            lead_vals['street'] = address
                        if zip:
                            partner_vals['zip'] = zip
                            lead_vals['zip'] = zip
                        if job_position:
                            partner_vals['function'] = job_position
                            lead_vals['function'] = job_position
                        if industry_type:
                            industry_type_id = self.env['industry.type'].sudo().search([('name', 'ilike', industry_type)], limit=1)
                            if industry_type_id:
                                partner_vals['industry_type'] = industry_type_id.id
                            else:
                                partner_vals['industry_type'] = self.env['industry.type'].sudo().create({'name': industry_type}).id
                        if country:
                            country_ids = self.env['res.country'].sudo().search([('name', 'ilike', country.strip())])
                            if country_ids:
                                country_id = country_ids[0]
                                lead_vals['country_id'] = country_id.id
                        if mobile:
                            partner_vals['mobile'] = mobile
                            lead_vals['mobile'] = mobile
                            partner_vals['phone'] = mobile
                            lead_vals['phone'] = mobile
                        if email:
                            partner_vals['email'] = email
                            lead_vals['email_from'] = email
                        if company_name:
                            partner_vals['company_type'] = 'company'
                            partner_vals['is_company'] = True
                        self.env['res.partner'].sudo().browse(partner_id).write(partner_vals)
                    if source_name:
                        self._cr.execute("SELECT id FROM utm_source WHERE name ilike '%s' "% source_name)
                        data = self._cr.fetchone()
                        if data:
                            source_id = data[0]
                        else:
                            source_id = self.env['utm.source'].sudo().create({'name': source_name}).id
                        lead_vals['source_id'] = source_id
                    if date:
                        date = str(date).strip()
                        if "/" in date:
                            lead_vals['creation_date'] = str(datetime.strptime(date, '%d/%m/%Y'))
                        if "." in date:
                            split_data = date.split('.')
                            if len(split_data[2]) == 2:
                                lead_vals['creation_date'] = str(datetime.strptime(date, '%d.%m.%y'))
                            else:
                                lead_vals['creation_date'] = str(datetime.strptime(date, '%d.%m.%Y'))
                    lead_vals['user_id'] = self.user_id.id if self.user_id else False
                    lead_id = self.env['crm.lead'].sudo().create(lead_vals)
                    lead_won_obj = self.env['crm.lead.won'].sudo()
                    lead_lost_obj = self.env['crm.lead.lost'].sudo()
                    if status.lower() == 'dead':
                        lead_id.to_dead()
                    elif status.lower() == 'kiv':
                        lead_id.to_followup()
                    elif status.lower() == 'won':
                        lead_id.sudo().to_followup()
                        lead_won_vals = {}
                        lead_won_vals['won_reason'] = 'closed'
                        lead_won_vals['lead_id'] = lead_id.id
                        lead_won_id = lead_won_obj.sudo().create(lead_won_vals)
                        lead_won_id.action_won_reason_apply()
                    elif status.lower() == 'inprogress':
                        lead_id.to_followup()
                        lead_inprogress_vals = {}
                        lead_inprogress_vals['won_reason'] = 'in_progress'
                        lead_inprogress_vals['lead_id'] = lead_id.id
                        lead_inprogress_id = lead_won_obj.sudo().create(lead_inprogress_vals)
                        lead_inprogress_id.action_won_reason_apply()
                    elif status.lower() == 'lost':
                        lead_id.to_followup()
                        lead_lost_vals = {}
                        self._cr.execute("SELECT id FROM crm_lost_reason WHERE name ilike 'Too expensive' AND active=True")
                        data = self._cr.fetchone()
                        if data:
                            reason_id = data[0]
                            lead_lost_vals['lost_reason_id'] = reason_id
                            lead_lost_vals['lead_id'] = lead_id.id
                            lead_lost_obj = lead_lost_obj.sudo().create(lead_lost_vals)
                            lead_lost_obj.action_lost_reason_apply()
                    else:
                        stage_id = self.env['ir.model.data'].xmlid_to_res_id('avanta_fields_modifier.crm_status_enquiry')
                        if stage_id:
                            lead_id.sudo().write({'stage_id': stage_id})
            self.write({'state': 'done'})
        except Exception, e:
            self._cr.rollback()
            self._cr.execute("update crm_lead_queue set state='fail', error_message='Error while import. Line no %s' where id=%s"% (str(count), str(self.id)))
            self._cr.commit()

CrmLeadQueue()