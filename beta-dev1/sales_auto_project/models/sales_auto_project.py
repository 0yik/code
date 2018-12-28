from odoo import api, fields, models

class sales_auto_project(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        res = super(sales_auto_project, self).action_confirm()
        data_project = {
            'name' : self.partner_id.name,
            'user_id' : self.user_id.id,
            'partner_id' : self.partner_id.id
        }
        project_id = self.env['project.project'].create(data_project)
        quotations_data_pdf = self.env['report'].get_pdf([self.id], 'ham_modifier_printout.report_sale_quotation', data=None)
        vals = {
            'name' : 'Document Sales Order %s'%(self.name),
            'res_name': self.partner_id.name,
            'res_model' : 	'project.project',
            'res_id' : project_id.id,
            'datas_fname': 'sale_order_%s.pdf'%(self.name),
            'datas': quotations_data_pdf.encode('base64'),
            'mimetype': 'application/pdf',
            'type': 'binary',
        }
        self.env['ir.attachment'].create(vals)
        return res