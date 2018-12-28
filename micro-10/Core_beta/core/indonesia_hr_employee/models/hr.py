from odoo import api, models, fields, _

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    province_id = fields.Many2one('province.wage.range', string='Province')
    npwp_number = fields.Char('NPWP Number')
    ptkp_status = fields.Many2one('l10n_id.ptkp_category', string='PTKP Status')
    tax_calculation_method = fields.Selection([('pegawai_tetap', 'Pegawai Tetap')], string='Tax Calculation Method')
    bpjs_ketenagakerjaan_number = fields.Char('BPJS Ketenagakerjaan Number')
    bpjs_kesehatan_number = fields.Char('BPJS Kesehatan Number')
    bpjs_ketenagakerjaan_date = fields.Date('BPJS Ketenagakerjaan Date')
    bpjs_kesehatan_date = fields.Date('BPJS Kesehatan Date')
    jkk_percentage = fields.Float('JKK Percentage')
    tax_deduction_method = fields.Selection([('gross','Gross'),('gross_up','Gross-Up'),('netto','Netto')], string='Tax Deduction Method')

    @api.onchange('npwp_number')
    def onchange_npwp_number(self):
        warning = {}
        if self.npwp_number and len(self.npwp_number) > 0:
            if len(self.npwp_number) == 15:
                self.npwp_number = str(self.npwp_number)[:2] + '.' + str(self.npwp_number)[2:5] + '.' + str(self.npwp_number)[5:8] + '.' + str(self.npwp_number)[8:9] + '-' + str(self.npwp_number)[9:12] + '.' + str(self.npwp_number)[12:15]
            else:
                warning = {'title': 'Value Error', 'message': "NPWP Number should be 15 digits."}
        return {'warning': warning}

hr_employee()
