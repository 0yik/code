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
    _inherit = 'low.stock.export.excel'

    name = fields.Char('Name')

    def make_file_runrate(self, vals=False, location=False):
        if not vals or vals == []:
            return False
        else:
            workbook = xlwt.Workbook()
            header_bold = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour gray25;")
            header_plain = xlwt.easyxf("pattern: pattern solid, fore_colour gray25;")
            worksheet = workbook.add_sheet('Products Low Stock')

            worksheet.write(0, 0, 'Location', header_plain)
            worksheet.write(0, 1, 'Products', header_plain)
            worksheet.write(0, 2, 'Runrate Index', header_plain)
            worksheet.write(0, 3, 'Avaiable Quantity', header_plain)
            worksheet.col(0).width = 10000
            worksheet.col(1).width = 5000
            worksheet.col(2).width = 5000
            index = 1
            for data in vals:
                if index == 1:
                    worksheet.write(index, 0, location)
                worksheet.write(index, 1, data[0])
                worksheet.write(index, 2, data[1])
                worksheet.write(index, 3, data[2])
                index += 1
            today = datetime.now()
            filepath = self.get_tmp_path('%s-product_low_stock_runrate.xls' % (today.strftime('%Y-%m-%d-%H-%M-%S')))
            workbook.save(filepath)
            attachment_id = self.make_odoo_attachment(filepath)
        return attachment_id