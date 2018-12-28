# -*- coding: utf-8 -*-
from odoo import api, fields, models
import openpyxl
from tempfile import TemporaryFile
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class LeadImport(models.TransientModel):
    _name = 'lead.import'
    _description = 'Lead Import'

    file = fields.Binary('File to Import')
    filename = fields.Char()

    @api.multi
    def action_lead_import(self):
        try:
            excel_file = self.file.decode('base64')
            excel_fileobj = TemporaryFile('wb+')
            excel_fileobj.write(excel_file)
            excel_fileobj.seek(0)

            workbook = openpyxl.load_workbook(excel_fileobj, data_only=True)
            sheet = workbook[workbook.get_sheet_names()[0]]
            count = 0
            missing_lines = []

        except Exception, e:
            _logger.exception("Kindly check the file. The file must be in Excel format(i.e. .XLS, .XLSX)")
            raise UserError(("Kindly check the file. The file must be in Excel format(i.e. .XLS, .XLSX)"))

        # Checking Template Data
        for row in sheet.rows:
            count += 1
            if len(row) != 14:
                raise UserError("No of column not satisfied. \n - Required 14 for %s \n - In line - %s" % (len(row), count))
            else:
                if not row[0].value and not row[1].value and not row[2].value and not row[3].value and not row[4].value and not row[5].value and \
                        not row[6].value and not row[7].value and not row[8].value and not row[9].value and not row[10].value and not row[11].value\
                        and not row[12].value and not row[13].value:
                    continue
                elif not row[1].value or not row[2].value or not row[4].value or not row[13].value:
                    missing_lines.append(count)
        if missing_lines:
            raise UserError(("Data missing on line : %r. \n Check the following columns \n\t- Service\n\t- Product\n\t- Customer\n\t- Status") % missing_lines)
        vals = {}
        vals['user_id'] = self._uid
        vals['state'] = 'draft'
        vals['file'] = self.file
        vals['filename'] = self.filename
        vals['lead_type'] = 'individual'
        self.env['crm.lead.queue'].create(vals)
        return True

    @api.multi
    def action_lead_import2(self):
        try:
            excel_file = self.file.decode('base64')
            excel_fileobj = TemporaryFile('wb+')
            excel_fileobj.write(excel_file)
            excel_fileobj.seek(0)

            workbook = openpyxl.load_workbook(excel_fileobj, data_only=True)
            sheet = workbook[workbook.get_sheet_names()[0]]
            count = 0
            missing_lines = []
        except Exception, e:
            _logger.exception("Kindly check the file. The file must be in Excel format(i.e. .XLS, .XLSX)")
            raise UserError(("Kindly check the file. The file must be in Excel format(i.e. .XLS, .XLSX)"))

        # Checking Template Data
        for row in sheet.rows:
            count += 1
            if len(row) != 15:
                raise UserError("No of column not satisfied. \n - Required 15 for %s \n - In line - %s" % (len(row), count))
            else:
                if not row[0].value and not row[1].value and not row[2].value and not row[3].value and not row[4].value and not row[5].value and \
                        not row[6].value and not row[7].value and not row[8].value and not row[9].value and not row[10].value and not row[11].value \
                        and not row[12].value and not row[13].value and not row[14].value:
                    continue
                elif not row[1].value or not row[2].value or not row[3].value or not row[5].value or not row[14].value:
                    missing_lines.append(count)
        if missing_lines:
            raise UserError(("Data missing on line : %r. \n Check the following columns \n\t- Service\n\t- Product\n\t- Company\n\t- Customer\n\t- Status") % missing_lines)
        vals = {}
        vals['user_id'] = self._uid
        vals['file'] = self.file
        vals['filename'] = self.filename
        vals['lead_type'] = 'company'
        self.env['crm.lead.queue'].create(vals)
        return True

LeadImport()