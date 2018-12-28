from odoo import api, models, fields
import pytz
from datetime import datetime
from dateutil import tz

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    analytic_contract_id = fields.Many2one('account.analytic.account',string='Contract')
    sales_tc = fields.Text(compute='update_sale_tc', string="Sales TC")
    client_name = fields.Char(compute='update_client_data', string="Client Name")
    client_tel = fields.Char(compute='update_client_data', string="Client Tel")
    client_email = fields.Char(compute='update_client_data', string="Client Email")
    client_address = fields.Text(compute='update_client_data', string="Client Address")

    @api.multi
    def tgw_invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        self.sent = True
        return self.env['report'].get_action(self, 'tgw_account_invoice_modifier.report_tgw_account_invoice')

    @api.model
    def _get_company_address_line_1(self):
        for record in self:
            if record.company_id:
                street = (record.company_id.street).upper()
                street2 = (record.company_id.street2).upper()
                country = (record.company_id.country_id.name).upper()
                zip = record.company_id.zip
                tel = record.company_id.phone
                # result_text = "11 WOODLANDS CLOSE #06-08 SINGAPORE 248847 TEL: +65 6734 3998"
                result = street + ' ' + street2 + ' ' + country + ' ' + \
                            zip + ' TEL: ' + tel
                return str(result)

    @api.model
    def _get_company_address_line_2(self):
        for record in self:
            if record.company_id:
                website = record.company_id.website
                email = record.company_id.email
                # result_text = "https: //www.thegownwarehouse.sg/ Email: contact@thegownwarehouse.com"
                result = website + ' Email: ' + email
                return str(result)

    @api.model
    def _get_paid_amount(self):
        for record in self:
            if record.residual > 0.00:
                result = (record.amount_total - record.residual)
            else:
                result = record.amount_total
            return result

    @api.multi
    def update_sale_tc(self):
        for record in self:
            if record.analytic_contract_id and record.analytic_contract_id.agree_bool:
                terms_condition = self.env['sale.tc'].search([], limit=1)
                if terms_condition:
                    record.sales_tc = terms_condition.terms

    @api.model
    def update_client_data(self):
        for record in self:
            if record.analytic_contract_id:
                record.client_name = record.analytic_contract_id.bride_firstname + '/' + record.analytic_contract_id.groom_firstname
                record.client_tel = record.analytic_contract_id.bride_phone + '/' + record.analytic_contract_id.groom_phone
                record.client_email = str(record.analytic_contract_id.bride_email).replace('False', '- ') + '/' + str(record.analytic_contract_id.groom_email).replace('False', ' -')

                bride_street = record.analytic_contract_id.bride_street and record.analytic_contract_id.bride_street.encode('utf-8') or ''
                bride_street2 = record.analytic_contract_id.bride_street2 and record.analytic_contract_id.bride_street2.encode('utf-8') or ''
                bride_city = record.analytic_contract_id.bride_city and record.analytic_contract_id.bride_city.encode('utf-8') or ''
                bride_state = record.analytic_contract_id.bride_state_id.name and record.analytic_contract_id.bride_state_id.name.encode('utf-8') or ''
                bride_zip = record.analytic_contract_id.bride_zip and record.analytic_contract_id.bride_zip.encode('utf-8')
                bride_country = record.analytic_contract_id.bride_country_id.name.encode('utf-8')

                groom_street = record.analytic_contract_id.groom_street and record.analytic_contract_id.groom_street.encode('utf-8') or ''
                groom_street2 = record.analytic_contract_id.groom_street2 and record.analytic_contract_id.groom_street2.encode('utf-8') or ''
                groom_city = record.analytic_contract_id.groom_city and record.analytic_contract_id.groom_city.encode('utf-8') or ''
                groom_state = record.analytic_contract_id.groom_state_id.name and record.analytic_contract_id.groom_state_id.name.encode('utf-8') or ''
                groom_zip = record.analytic_contract_id.groom_zip and record.analytic_contract_id.groom_zip.encode('utf-8') or ''
                groom_country = record.analytic_contract_id.groom_country_id.name and record.analytic_contract_id.groom_country_id.name.encode('utf-8') or ''
                bride_address = str(bride_street) + ', ' + str(bride_street2) + '\n' + str(bride_city) + ', ' + \
                                str(bride_state) + ', ' + str(bride_zip) + '\n' + str(bride_country)

                groom_address = str(groom_street) + ', ' + str(groom_street2) + '\n' + str(groom_city) + ', ' + \
                                str(groom_state) + ', ' + str(groom_zip) + '\n' + str(groom_country)

                bride_address = bride_address.replace('False,', '')
                groom_address = groom_address.replace('False,', '')

                if len(bride_address) > 6:
                    record.client_address = bride_address
                elif len(groom_address) > 6:
                    record.client_address = groom_address
                else:
                    record.client_address = ''