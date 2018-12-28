# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ReporPaperFormatSelection(models.TransientModel):
    _name = "report.paper.format.selection"

    paper_format = fields.Many2one('report.paperformat','Paper Format', required=True)
    format = fields.Selection([
        ('A0', 'A0  5   841 x 1189 mm'),
        ('A1', 'A1  6   594 x 841 mm'),
        ('A2', 'A2  7   420 x 594 mm'),
        ('A3', 'A3  8   297 x 420 mm'),
        ('A4', 'A4  0   210 x 297 mm, 8.26 x 11.69 inches'),
        ('A5', 'A5  9   148 x 210 mm'),
        ('A6', 'A6  10  105 x 148 mm'),
        ('A7', 'A7  11  74 x 105 mm'),
        ('A8', 'A8  12  52 x 74 mm'),
        ('A9', 'A9  13  37 x 52 mm'),
        ('B0', 'B0  14  1000 x 1414 mm'),
        ('B1', 'B1  15  707 x 1000 mm'),
        ('B2', 'B2  17  500 x 707 mm'),
        ('B3', 'B3  18  353 x 500 mm'),
        ('B4', 'B4  19  250 x 353 mm'),
        ('B5', 'B5  1   176 x 250 mm, 6.93 x 9.84 inches'),
        ('B6', 'B6  20  125 x 176 mm'),
        ('B7', 'B7  21  88 x 125 mm'),
        ('B8', 'B8  22  62 x 88 mm'),
        ('B9', 'B9  23  33 x 62 mm'),
        ('B10', ':B10    16  31 x 44 mm'),
        ('C5E', 'C5E 24  163 x 229 mm'),
        ('Comm10E', 'Comm10E 25  105 x 241 mm, U.S. '
         'Common 10 Envelope'),
        ('DLE', 'DLE 26 110 x 220 mm'),
        ('Executive', 'Executive 4   7.5 x 10 inches, '
         '190.5 x 254 mm'),
        ('Folio', 'Folio 27  210 x 330 mm'),
        ('Ledger', 'Ledger  28  431.8 x 279.4 mm'),
        ('Legal', 'Legal    3   8.5 x 14 inches, '
         '215.9 x 355.6 mm'),
        ('Letter', 'Letter 2 8.5 x 11 inches, '
         '215.9 x 279.4 mm'),
        ('Tabloid', 'Tabloid 29 279.4 x 431.8 mm'),
        ('custom', 'Custom')
        ], 'Paper size')
    margin_top = fields.Float('Top Margin (mm)')
    margin_bottom = fields.Float('Bottom Margin (mm)')
    margin_left = fields.Float('Left Margin (mm)')
    margin_right = fields.Float('Right Margin (mm)')
    page_height = fields.Integer('Page height (mm)')
    page_width = fields.Integer('Page width (mm)')
    orientation = fields.Selection([
        ('Landscape', 'Landscape'),
        ('Portrait', 'Portrait')
    ], 'Orientation')
    header_line = fields.Boolean('Display a header line')
    header_spacing = fields.Integer('Header spacing')
    dpi = fields.Integer('Output DPI')

    @api.multi
    @api.onchange('paper_format', 'format')
    def onchange_paper_format(self):
        if self.paper_format:
            if not self.format:
                self.format = self.paper_format.format
            self.margin_bottom = self.paper_format.margin_bottom
            self.margin_top = self.paper_format.margin_top
            self.margin_left = self.paper_format.margin_left
            self.margin_right = self.paper_format.margin_right
            self.page_height = self.paper_format.page_height
            self.page_width = self.paper_format.page_width
            self.orientation = self.paper_format.orientation
            self.header_spacing = self.paper_format.header_spacing
            self.dpi = self.paper_format.dpi

    @api.multi
    def close_wizard(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def set_paper_format(self):
        paper_format_search = self.env['report.paperformat'].search([('id', '=', self.paper_format.id)], limit=1)
        for report in self:
            if report.format == 'custom':
                paper_format_search.format = self.format
                paper_format_search.margin_top = self.margin_top
                paper_format_search.margin_bottom = self.margin_bottom
                paper_format_search.margin_left = self.margin_left
                paper_format_search.margin_right = self.margin_right
                paper_format_search.page_height = self.page_height
                paper_format_search.page_width = self.page_width
                paper_format_search.orientation = self.orientation
                paper_format_search.header_line = self.header_line
                paper_format_search.header_spacing = self.header_spacing
                paper_format_search.dpi = self.dpi
            else:
                paper_format_search.page_height = ''
                paper_format_search.page_width = ''
                paper_format_search.format = self.format
                paper_format_search.margin_top = self.margin_top
                paper_format_search.margin_bottom = self.margin_bottom
                paper_format_search.margin_left = self.margin_left
                paper_format_search.margin_right = self.margin_right
                paper_format_search.orientation = self.orientation
                paper_format_search.header_line = self.header_line
                paper_format_search.header_spacing = self.header_spacing
                paper_format_search.dpi = self.dpi

        context = self.env.context
        report_name = context.get('report_name')
        report = self.env['ir.actions.report.xml'].search([('report_name', '=', report_name)], limit=1)
        report.paperformat_id = self.paper_format
        if not report:
            raise UserError(
                _("Bad Report Reference") + _("This report is not loaded into the database: %s.") % report_name)
        return {
            'context': context,
            'data': context.get('data'),
            'type': 'ir.actions.report.xml',
            'report_name': report.report_name,
            'report_type': report.report_type,
            'report_file': report.report_file,
            'name': report.name,
        }
