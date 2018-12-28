# -*- coding: utf-8 -*-
import StringIO
from collections import deque
from openerp.tools import config, ustr
from datetime import datetime, timedelta, date
from odoo import models, fields, api, SUPERUSER_ID
import os
import uuid

try:
    import xlwt
except ImportError:
    xlwt = None


class export_excel(models.TransientModel):
    _name = 'low.stock.export.excel'

    name = fields.Char('Name')

    def make_file(self, vals=False, localtion=False):
        if not vals or vals == []:
            return False
        else:
            workbook = xlwt.Workbook()
            header_bold = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour gray25;")
            header_plain = xlwt.easyxf("pattern: pattern solid, fore_colour gray25;")
            worksheet = workbook.add_sheet('Products Low Stock')

            worksheet.write(0, 0, 'Location', header_plain)
            worksheet.write(0, 1, 'Products', header_plain)
            worksheet.write(0, 2, 'Avaiable Quantity', header_plain)
            worksheet.col(0).width = 10000
            worksheet.col(1).width = 20000
            worksheet.col(2).width = 5000
            index = 1
            for data in vals:
                if index == 1:
                    worksheet.write(index, 0, localtion)
                worksheet.write(index, 1, data[0])
                worksheet.write(index, 2, data[1])
                index += 1
            today = datetime.now()
            filepath = self.get_tmp_path('%s-product_low_stock.xls' % (today.strftime('%Y-%m-%d-%H-%M-%S')))
            workbook.save(filepath)
            attachment_id = self.make_odoo_attachment(filepath)
        return attachment_id

    @api.model
    def make_odoo_attachment(self, filepath):
        excel_data = ''
        with open(filepath, 'r') as file:  # Use file to refer to the file object
            data = file.read()
            excel_data += data
        head, filename = os.path.split(filepath)
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'res_name': filename,
            'type': 'binary',
            'datas_fname': filename,
            'datas': excel_data.encode('base64'),
            'mimetype': 'application/vnd.ms-excel',
        })
        return attachment

    @api.model
    def get_tmp_path(self, filename):
        return os.path.join(config['data_dir'], 'filestore', self.env.cr.dbname, filename)
