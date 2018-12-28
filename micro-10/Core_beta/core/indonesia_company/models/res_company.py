from odoo import api, models, fields, _

class res_company(models.Model):
    _inherit = 'res.company'

    company_npwp = fields.Char('Company NPWP')
    taxcutter_name = fields.Char('Tax Cutter Name')
    taxcutter_npwp = fields.Char('Tax Cutter NPWP')
    npp_bpjs_ketenagakerjaan = fields.Char('NPP BPJS Ketenagakerjaan')
    province_id = fields.Many2one('province.wage.range', string='Province')
    min_wage = fields.Float(related='province_id.min_wage', string='Min. Wage')
    bpjs_ketenagakerjaan_max = fields.Integer('BPJS Ketenagakerjaan Max')
    bpjs_kesehatan_max = fields.Integer('BPJS Kesehatan Max')

    @api.onchange('company_npwp')
    def onchange_company_npwp(self):
        warning = {}
        if self.company_npwp and len(self.company_npwp) > 0:
            if len(self.company_npwp) == 15:
                self.company_npwp = str(self.company_npwp)[:2] +'.'+ str(self.company_npwp)[2:5] +'.'+ str(self.company_npwp)[5:8] +'.'+str(self.company_npwp)[8:9] +'-'+ str(self.company_npwp)[9:12] + '.'+ str(self.company_npwp)[12:15]
            else:
                warning = {'title': 'Value Error', 'message': "Company NPWP should be 15 digits."}
        return {'warning': warning}

    @api.onchange('taxcutter_npwp')
    def onchange_taxcutter_npwp(self):
        warning = {}
        if self.taxcutter_npwp and len(self.taxcutter_npwp) > 0:
            if len(self.taxcutter_npwp) == 15:
                self.taxcutter_npwp = str(self.taxcutter_npwp)[:2] + '.' + str(self.taxcutter_npwp)[2:5] + '.' + str(self.taxcutter_npwp)[5:8] + '.' + str(self.taxcutter_npwp)[8:9] + '-' + str(self.taxcutter_npwp)[9:12] + '.' + str(self.taxcutter_npwp)[12:15]
            else:
                warning = {'title': 'Value Error', 'message': "Tax Cutter NPWP should be 15 digits."}
        return {'warning': warning}

res_company()