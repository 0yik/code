# -*- coding: utf-8 -*-
import StringIO
from collections import deque
from odoo.tools import config
from datetime import datetime, timedelta
from odoo import models, fields, api, SUPERUSER_ID
from odoo.tools import ustr
import os

try:
    import xlwt
except ImportError:
    xlwt = None

class auto_send_report(models.Model):
    _name = 'auto_send_report.config'

    @api.model
    def _list_all_models(self):
        self.env.cr.execute("""
            SELECT
                model, name
            FROM
                ir_model
            WHERE
                transient = False
            ORDER BY
                name
        """)
        return self.env.cr.fetchall()

    reporting_id = fields.Selection(_list_all_models, string='Reporting', required=True)
    filter_id = fields.Many2one('ir.filters', string='Filter', required=True)
    measure_ids = fields.Many2many('ir.model.fields', domain=[('name','!=','id'),'|',('ttype','=','float'),('ttype','=','integer')], string='Measures', required=True)
    recipient_ids = fields.Many2many('res.partner', string='Recipients', domain=[('email', '!=', False)], required=True)
    sending_frequency = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ], string='Sending Frequency', required=True)
    next_date = fields.Date('Next Date', required=True, default= lambda self: fields.Date.today())

    @api.multi
    def run_scheduler_send(self):
        allow_send_ids = []

        reports = self.search([])
        for report in reports:
            if not report.next_date:
                allow_send_ids.append(report.id)
            else:
                next_date = datetime.strptime(report.next_date, '%Y-%m-%d')
                today = datetime.strptime(fields.Date.today(), '%Y-%m-%d')

                timediff = next_date - today
                if timediff.total_seconds() <= 0:
                    allow_send_ids.append(report.id)
        if len(allow_send_ids) > 0:
            allowes = self.browse(allow_send_ids)
            allowes.sending_report()
            allowes.update_next_time()
        return True

    @api.multi
    def update_next_time(self):
        for report in self:
            today = datetime.strptime(fields.Date.today(), '%Y-%m-%d')

            delta = timedelta(days=+1)
            if report.sending_frequency == 'weekly':
                delta = timedelta(days=+7)
            elif report.sending_frequency == 'monthly':
                delta = timedelta(months=+1)

            next_date = today + delta
            report.write({
                'next_date': next_date.strftime('%Y-%m-%d')
            })

    @api.multi
    def sending_report(self):
        for report in self:
            report_data = report.get_report_data()
            excel_path = self.export_xls(report_data)
            report.send_email(excel_path)
        return True

    @api.model
    def build_data(self):
        return {
            'headers': self.build_headers(),
            'measure_row': self.build_measure_row(),
            'nbr_measures': self.get_measure_lenth(),
            'rows': self.build_rows(),
            'title': self.reporting_id,
        }

    @api.model
    def build_headers(self):
        report_obj = self.env.get(self.reporting_id)

        filter_context = eval(self.filter_id.context)
        if not filter_context:
            filter_context = {}

        pivot_measures = filter_context.get('pivot_measures', [])
        pivot_row_groupby = filter_context.get('pivot_row_groupby', [])
        pivot_column_groupby = filter_context.get('pivot_column_groupby', [])

        fields = []
        for measure in pivot_measures:
            fields.append(measure.split(':')[0])
        for row in pivot_row_groupby:
            fields.append(row.split(':')[0])
        for column in pivot_column_groupby:
            fields.append(column.split(':')[0])

        domain = eval(self.filter_id.domain)
        if not domain:
            domain = []

        measures = []
        group_labels = []
        for group_field in pivot_column_groupby:
            group_data = report_obj.read_group(domain=domain, fields=fields, groupby=[group_field])
            for group_item in group_data:
                for measure in pivot_measures:
                    if measure == '__count__':
                        measures.append({
                            'width': 1,
                            'height': 1,
                            'title': 'count',
                            # 'id': '2216',
                            'expanded': False
                        })
                    else:
                        measures.append({
                            'width': 1,
                            'height': 1,
                            'title': measure,
                            # 'id': '2216',
                            'expanded': False
                        })
                group_label = group_item.get(group_field)
                if not group_label:
                    group_label = 'Undefined'
                if type(group_label) == type(list()) or type(group_label) == type(tuple()):
                    group_label = group_label[1]
                group_labels.append({
                    'width': len(pivot_measures),
                    'height': 1,
                    'title': group_label,
                    # 'id': '2216',
                    'expanded': False
                })
        totals = []
        for measure in pivot_measures:
            if measure == '__count__':
                totals.append({
                    'width': 1,
                    'height': 1,
                    'title': 'count',
                    # 'id': '2216',
                    'expanded': False
                })
            else:
                totals.append({
                    'width': 1,
                    'height': 1,
                    'title': measure,
                    # 'id': '2216',
                    'expanded': False
                })
        return [[{
            'width': len(measures),
            'height': 1,
            'title': 'Total',
            'id': '2216',
            'expanded': False
        }, {
            'width': len(totals),
            'height': len(pivot_column_groupby),
            'title': '',
            'id': '2216',
            'expanded': False
        }], group_labels, measures + totals]

    @api.model
    def build_measure_row(self):
        result = []
        for measure in self.measure_ids:
            if measure.name:
                result.append({
                    'text': measure.field_description,
                    'is_bold': True
                })
        return result

    @api.model
    def get_measure_lenth(self):
        return len(self.measure_ids)

    @api.model
    def build_rows(self):
        result = []
        report_obj = self.env.get(self.reporting_id)

        filter_context = eval(self.filter_id.context)
        if not filter_context:
            filter_context = {}

        pivot_measures = filter_context.get('pivot_measures', [])
        pivot_row_groupby = filter_context.get('pivot_row_groupby', [])
        pivot_column_groupby = filter_context.get('pivot_column_groupby', [])

        fields = []
        for measure in pivot_measures:
            fields.append(measure.split(':')[0])
        for row in pivot_row_groupby:
            fields.append(row.split(':')[0])
        for column in pivot_column_groupby:
            fields.append(column.split(':')[0])

        domain = eval(self.filter_id.domain)
        if not domain:
            domain = []

        index = 0
        values = []
        table_data = {}
        table_index = []
        for group_field in pivot_column_groupby:
            group_data = report_obj.read_group(domain=domain, fields=fields, groupby=[group_field])
            for group_item in group_data:
                group_id = group_item.get(group_field)
                if type(group_id) == type(list()) or type(group_id) == type(tuple()):
                    group_id = group_id[0]
                for measure in pivot_measures:
                    table_index.append({
                        'id': group_id,
                        'measure': measure,
                        'index': index
                    })
                    if measure == '__count__':
                        table_data[index] = {
                            'value': group_item.get('%s_count' %(group_field,)),
                        }
                    else:
                        table_data[index] = {
                            'value': group_item.get(measure),
                        }
                    index = index + 1
        total_data = report_obj.read_group(domain=domain, fields=fields, groupby=[])
        for total_item in total_data:
            for measure in pivot_measures:
                table_index.append({
                    'id': 'root',
                    'measure': measure,
                    'index': index
                })
                if measure == '__count__':
                    table_data[index] = {
                        'value': total_item.get('__count')
                    }
                else:
                    table_data[index] = {
                        'value': total_item.get(measure)
                    }
                index = index + 1

        for table_item in table_index:
            index = table_item.get('index')
            values.append(table_data.get(index))

        result.append({
            # 'id': '2215',
            'indent': 0,
            'title': 'Total',
            'expanded': True,
            'values': values
        })

        if pivot_row_groupby:
            result += self._build_rows(table_index, domain, fields, pivot_column_groupby, pivot_measures, pivot_row_groupby)

        return result

    @api.model
    def _get_index_from_table(self, table_index, id, measure):
        index = 0
        for table_item in table_index:
            if table_item.get('id') == id and table_item.get('measure') == measure:
                index = table_item.get('index')
        return index

    @api.model
    def _build_rows(self, table_index, domain, fields, columns, measures, rows, field_index=0):
        result = []
        report_obj = self.env.get(self.reporting_id)
        if field_index < len(rows):
            group_field = rows[field_index]
            total_data = report_obj.read_group(domain=domain, fields=fields, groupby=[group_field])

            for total_item in total_data:
                new_domain = total_item.get('__domain')
                values = []
                table_data = {}
                for table_item in table_index:
                    index = table_item.get('index')
                    table_data[index] = {'value': 0}
                for column in columns:
                    group_data = report_obj.read_group(domain=new_domain, fields=fields, groupby=[column])
                    for group_item in group_data:
                        group_id = group_item.get(column)
                        if type(group_id) == type(list()) or type(group_id) == type(tuple()):
                            group_id = group_id[0]
                        for measure in measures:
                            index = self._get_index_from_table(table_index, group_id, measure)
                            if measure == '__count__':
                                table_data[index] = {
                                    'value': group_item.get('%s_count' %(column,))
                                }
                            else:
                                table_data[index] = {
                                    'value': group_item.get(measure)
                                }
                for measure in measures:
                    index = self._get_index_from_table(table_index, 'root', measure)
                    if measure == '__count__':
                        table_data[index] = {
                            'value': total_item.get('%s_count' %(group_field.split(':')[0],))
                        }
                    else:
                        table_data[index] = {
                            'value': total_item.get(measure)
                        }

                for table_item in table_index:
                    index = table_item.get('index')
                    values.append(table_data.get(index))

                if total_item.get(group_field):
                    field_label = total_item.get(group_field)
                    if type(field_label) == type(list()) or type(field_label) == type(tuple()):
                        result.append({
                            # 'id': '2215',
                            'indent': field_index + 1,
                            'title': field_label[1],
                            'expanded': True,
                            'values': values
                        })
                    else:
                        result.append({
                            # 'id': '2215',
                            'indent': field_index + 1,
                            'title': field_label,
                            'expanded': True,
                            'values': values
                        })
                else:
                    result.append({
                        # 'id': '2215',
                        'indent': field_index + 1,
                        'title': 'Undefined',
                        'expanded': True,
                        'values': values
                    })
                result += self._build_rows(table_index, new_domain, fields, columns, measures, rows, field_index + 1)

        return result

    @api.model
    def get_report_data(self):
        data = self.build_data()
        return data

    @api.model
    def get_email_template(self):
        return self.env.ref('auto_send_report.auto_report_template')

    @api.multi
    def send_email(self, excel_path):
        self.sudo()._send_email(excel_path)

    @api.multi
    def _send_email(self, excel_path):
        for report in self:
            result = False
            # email_obj = self.pool.get('mail.template')
            template = self.get_email_template()

            email_to = []
            for recipient in report.recipient_ids:
                if recipient.email:
                    email_to.append(recipient.email)
            email_to = ','.join(email_to)

            excel_data = ''
            with open(excel_path, 'r') as file:  # Use file to refer to the file object
                data = file.read()
                excel_data += data

            filename = 'report.xls'
            attachment = self.env.get('ir.attachment').create({
                'name': filename,
                'res_name': filename,
                'type': 'binary',
                'datas_fname': filename,
                'datas': excel_data.encode('base64'),
                'mimetype': 'application/vnd.ms-excel',
            })

            if email_to:
                template.write({
                    'email_to': email_to,
                    'attachment_ids': [(6, 0, [attachment.id])]
                })
                result = template.send_mail(report.id, True)
        return result

    @api.model
    def export_xls(self, jdata):
        nbr_measures = jdata['nbr_measures']
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet(jdata['title'][:30])
        header_bold = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour gray25;")
        header_plain = xlwt.easyxf("pattern: pattern solid, fore_colour gray25;")
        bold = xlwt.easyxf("font: bold on;")

        # Step 1: writing headers
        headers = jdata['headers']

        # x,y: current coordinates
        # carry: queue containing cell information when a cell has a >= 2 height
        #      and the drawing code needs to add empty cells below
        x, y, carry = 1, 0, deque()
        for i, header_row in enumerate(headers):
            worksheet.write(i,0, '', header_plain)
            for header in header_row:
                while (carry and carry[0]['x'] == x):
                    cell = carry.popleft()
                    for i in range(nbr_measures):
                        worksheet.write(y, x+i, '', header_plain)
                    if cell['height'] > 1:
                        carry.append({'x': x, 'height':cell['height'] - 1})
                    x = x + nbr_measures
                style = header_plain if 'expanded' in header else header_bold
                for i in range(header['width']):
                    worksheet.write(y, x + i, header['title'] if i == 0 else '', style)
                if header['height'] > 1:
                    carry.append({'x': x, 'height':header['height'] - 1})
                x = x + header['width'];
            while (carry and carry[0]['x'] == x):
                cell = carry.popleft()
                for i in range(nbr_measures):
                    worksheet.write(y, x+i, '', header_plain)
                if cell['height'] > 1:
                    carry.append({'x': x, 'height':cell['height'] - 1})
                x = x + nbr_measures
            x, y = 1, y + 1

        # Step 2: measure row
        if nbr_measures > 1:
            worksheet.write(y,0, '', header_plain)
            for measure in jdata['measure_row']:
                style = header_bold if measure['is_bold'] else header_plain
                worksheet.write(y, x, measure['text'], style);
                x = x + 1
            y = y + 1

        # Step 3: writing data
        x = 0
        for row in jdata['rows']:
            worksheet.write(y, x, row['indent'] * '     ' + ustr(row['title']), header_plain)
            for cell in row['values']:
                x = x + 1
                if cell.get('is_bold', False):
                    worksheet.write(y, x, cell['value'], bold)
                else:
                    worksheet.write(y, x, cell['value'])
            x, y = 0, y + 1

        filepath = self.get_tmp_path('report.xls')
        workbook.save(filepath)

        return filepath

    @api.model
    def get_tmp_path(self, filename):
        return os.path.join(config['data_dir'], 'filestore', self.env.cr.dbname, filename)

    def get_data_dir(self):
        return config['data_dir']

    @api.onchange('reporting_id')
    def _onchange_reporting_id(self):
        result = {}
        if self.reporting_id:
            self.filter_id = False
            self.measure_ids = []
            result = {
                'domain': {
                    'filter_id': [('model_id','=',self.reporting_id)],
                    'measure_ids': [('name','!=','id'),('model_id.model','=',self.reporting_id),'|',('ttype','=','float'),('ttype','=','integer')],
                }
            }
        return result