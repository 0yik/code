# -*- encoding: utf-8 -*-
import base64
import tempfile
from datetime import date, datetime
from odoo import models, fields, api
from odoo.exceptions import UserError

class GiroBulkPayment(models.TransientModel):
    _name = 'giro.bulk.payment'
    _description = 'Giro Bulk Payment'

    sequence_number = fields.Char(size=2, required=True, string='Sequence No')
    payment_type = fields.Selection([('P', 'Payment'), ('R', 'Payroll')], required=True, string='Payment Type')
    service_type = fields.Char(default='NORMAL', size=10, required=True, string='Service Type')
    company_id = fields.Char(size=12, string='Company ID')
    originating_bic_code = fields.Char(size=11, required=True, string='Originating BIC Code')
    originating_account_number = fields.Char(size=10, required=True, string='Originating A/c No')
    originating_account_name = fields.Char(required=True, string='Originating A/c Name')
    creation_date = fields.Date(default=date.today(), required=True, string='Creation Date')
    value_date = fields.Date(default=date.today(), required=True, string='Value Date')
    ultimate_originating_customer = fields.Char(help='Must be different from Originating A/C Name.', string='Ultimate Originating Customer')
    bulk_customer_reference = fields.Char(size=16, required=True, string='Bulk Customer Reference')
    software_label = fields.Char(size=10, string='Software Label')
    line_ids = fields.One2many('giro.bulk.payment.line', 'giro_id', string='Vendors')
    line_ids2 = fields.One2many('giro.bulk.payment.line', 'giro_id2', string='Employees')
    txt_file = fields.Binary('Click On Download Link To Download Text File', readonly=True)
    filename = fields.Char(invisible=True)
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')

    @api.model
    def _get_file_name(self):
        date = datetime.today().strftime('%d%m')
        return 'UGBI%s%s'% (date, self.sequence_number)

    def get_ascii_sum(self, value, hash_index=0, hash_code=1):
        cnt = 1
        sum = 0
        for i in [ord(x) for x in value]:
            if hash_index:
                if cnt < hash_index:
                    sum += i * cnt
            else:
                sum += i * cnt
            cnt += 1
        return sum*hash_code

    @api.multi
    def generate_text_file(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise UserError('Start Date should not be greater than End Date.')
        tgz_tmp_filename = tempfile.mktemp('.' + "txt")
        tmp_file = open(tgz_tmp_filename, "wb")
        filename = self._get_file_name()
        try:
            header = '1'.ljust(1)
            header += filename.ljust(10)
            if self.payment_type == 'P':
                header += 'P'
            else:
                header += 'R'
            service_type = self.service_type or ''
            header += service_type.ljust(10)
            header += ' '
            company_id = self.company_id or ''
            header += company_id.ljust(12)
            bic_code = self.originating_bic_code.ljust(11)
            sum1 = self.get_ascii_sum(bic_code)
            header += bic_code
            header += 'SGD'
            originating_account_number = self.originating_account_number.ljust(34)
            sum2 = self.get_ascii_sum(originating_account_number)
            header += originating_account_number
            originating_account_name = self.originating_account_name.upper()
            originating_account_name = originating_account_name.ljust(140)
            sum3 = self.get_ascii_sum(originating_account_name)
            header += originating_account_name
            creation_date = datetime.strptime(self.creation_date, "%Y-%m-%d")
            header += creation_date.strftime('%Y%m%d').ljust(8)
            value_date = datetime.strptime(self.value_date, "%Y-%m-%d")
            header += value_date.strftime('%Y%m%d').ljust(8)
            ultimate_originating_customer = self.ultimate_originating_customer or ''
            header += ultimate_originating_customer.ljust(140)
            header += self.bulk_customer_reference.ljust(16)
            software_label = self.software_label or ''
            header += software_label.ljust(10)
            header += ''.ljust(210)
            tmp_file.write(header)
            amount_total = 0.0
            count = 0
            domain = []
            sum4 = 0
            sum5 = 0
            sum6 = 0
            sum7 = 0
            if self.payment_type == 'P':
                payment_code = 20
                if self.start_date:
                    domain += [('date_invoice', '>=', self.start_date)]
                if self.end_date:
                    domain += [('date_invoice', '<=', self.end_date)]
            else:
                payment_code = 22
                domain += [('slip_id.date_from', '>=', self.start_date), ('slip_id.date_to', '<=', self.end_date), ('slip_id.state', '=', 'done')]
            hash_code = 1
            if self.payment_type == 'P':
                for line in self.line_ids:
                    detail = '\r\n'
                    detail += '2'.ljust(1)
                    bic_code = line.bank_id.bank_bic if line.bank_id.bank_bic else ''
                    bic_code = bic_code.ljust(11)
                    sum1 += self.get_ascii_sum(bic_code)
                    detail += bic_code
                    account_no = line.bank_id.acc_number
                    account_no = account_no.ljust(34)
                    sum2 += self.get_ascii_sum(account_no, hash_index=35, hash_code=hash_code)
                    detail += account_no
                    receiving_name = line.partner_id.name.upper()
                    receiving_name = receiving_name.ljust(140)
                    sum3 += self.get_ascii_sum(receiving_name, hash_index=141, hash_code=hash_code)
                    detail += receiving_name
                    sum4 += self.get_ascii_sum('SGD')
                    detail += 'SGD'
                    amount = 0.0
                    domain += [('partner_id', '=', line.partner_id.id), ('type', '=', 'in_invoice'), ('state', '=', 'open')]
                    for invoice_id in self.env['account.invoice'].search(domain):
                        amount += abs(invoice_id.residual_company_signed)
                    amount = '%.2f' % amount
                    amount_total += float(amount)
                    amount_split = amount.split('.')
                    rfill = '0'.zfill(16 - len(amount_split[0]))
                    amount = rfill + amount_split[0] + amount_split[1]
                    sum5 += self.get_ascii_sum(amount)
                    detail += amount.rjust(18)
                    detail += line.end_to_end_id.ljust(35)
                    detail += ''.ljust(35)
                    purpose_code = line.purpose_code.ljust(4)
                    sum6 += self.get_ascii_sum(purpose_code, hash_index=5)
                    detail += purpose_code
                    remittance_code = line.remittance_code or ''
                    detail += remittance_code.ljust(140)
                    ultimate_receiving_customer = line.ultimate_receiving_customer or ''
                    detail += ultimate_receiving_customer.ljust(140)
                    customer_reference = line.customer_reference or ''
                    detail += customer_reference.ljust(16)
                    detail += ''.ljust(38)
                    sum7 += payment_code * hash_code
                    if int(amount) > 0:
                        tmp_file.write(detail)
                        count += 1
                        if hash_code == 9:
                            hash_code = 1
                        else:
                            hash_code += 1
            else:
                for line in self.line_ids2:
                    emp_id = line.employee_id
                    detail = '\r\n'
                    detail += '2'.ljust(1)
                    bank_id = emp_id.bank_account_id
                    bic_code = bank_id.bank_bic if bank_id.bank_bic else ''
                    bic_code = bic_code.ljust(11)
                    sum1 += self.get_ascii_sum(bic_code)
                    detail += bic_code
                    account_no = bank_id.acc_number
                    account_no = account_no.ljust(34)
                    sum2 += self.get_ascii_sum(account_no, hash_index=35, hash_code=hash_code)
                    detail += account_no
                    receiving_name = emp_id.name.upper()
                    receiving_name = receiving_name.ljust(140)
                    sum3 += self.get_ascii_sum(receiving_name, hash_index=141, hash_code=hash_code)
                    detail += receiving_name
                    sum4 += self.get_ascii_sum('SGD')
                    detail += 'SGD'
                    amount = 0.0
                    for payslip_line in self.env['hr.payslip.line'].search([('slip_id.employee_id', '=', emp_id.id), ('code', '=', 'NET'), ('amount', '!=', 0)] + domain):
                        amount += payslip_line.amount
                    amount = '%.2f'% amount
                    amount_total += float(amount)
                    amount_split = amount.split('.')
                    rfill = '0'.zfill(16-len(amount_split[0]))
                    amount = rfill + amount_split[0] + amount_split[1]
                    sum5 += self.get_ascii_sum(amount)
                    detail += amount.rjust(18)
                    detail += line.end_to_end_id.ljust(35)
                    detail += ''.ljust(35)
                    purpose_code = line.purpose_code.ljust(4)
                    sum6 += self.get_ascii_sum(purpose_code, hash_index=5)
                    detail += purpose_code
                    remittance_code = line.remittance_code or ''
                    detail += remittance_code.ljust(140)
                    ultimate_receiving_customer = line.ultimate_receiving_customer or ''
                    detail += ultimate_receiving_customer.ljust(140)
                    customer_reference = line.customer_reference or ''
                    detail += customer_reference.ljust(16)
                    detail += ''.ljust(38)
                    sum7 += payment_code * hash_code
                    if int(amount) > 0:
                        tmp_file.write(detail)
                        count += 1
                        if hash_code == 9:
                            hash_code = 1
                        else:
                            hash_code += 1
            trailer = '\r\n'
            trailer += '9'.ljust(1)
            amount_total = '%.2f' % amount_total
            amount_total_split = amount_total.split('.')
            rfill = '0'.zfill(16 - len(amount_total_split[0]))
            amount_total = rfill + amount_total_split[0] + amount_total_split[1]
            trailer += amount_total.ljust(18)
            count = str(count)
            rfill = '0'.zfill(7 - len(count))
            count = rfill + count
            trailer += str(count).ljust(7)
            hash_total = sum1 + sum2 + sum3 + sum4 + sum5 + sum6 + sum7
            hash_total = str(hash_total)
            rfill = '0'.zfill(16 - len(hash_total))
            hash_total = rfill + hash_total
            trailer += hash_total.ljust(16)
            trailer += ''.ljust(573)
            tmp_file.write(trailer)
        finally:
            tmp_file.close()
        file = open(tgz_tmp_filename, "rb")
        out = file.read()
        file.close()
        binary_file = base64.b64encode(out)
        self.write({'txt_file': binary_file, 'filename': '%s.txt'% filename})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_id': self.env['ir.model.data'].xmlid_to_res_id('think_tank_giro.download_file_wizard'),
            'view_mode': 'form',
            'target': 'new',
        }

GiroBulkPayment()

class GiroBulkPaymentLine(models.TransientModel):
    _name = 'giro.bulk.payment.line'

    giro_id = fields.Many2one('giro.bulk.payment')
    giro_id2 = fields.Many2one('giro.bulk.payment')
    partner_id = fields.Many2one('res.partner', string='Vendor')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    bank_id = fields.Many2one('res.partner.bank', string='Bank')
    end_to_end_id = fields.Char(size=35, required=True, help='Reference to be printed on Receiving Bank A/C Statement.', string='End to End ID')
    purpose_code = fields.Char(size=4, required=True, help='To be printed on Receiving Bank A/C Statement', string='Purpose Code')
    remittance_code = fields.Char(size=140, help='Additional Payment Details', string='Remittance Info')
    ultimate_receiving_customer = fields.Char(help='Must be different from Receiving A/C Name.', string='Ultimate Beneficiary Name')
    customer_reference = fields.Char(size=16, help='Only for internal reference.', string='Customer Ref')

GiroBulkPaymentLine()