from odoo import models, fields, api

class tax(models.Model):
    _inherit = 'account.tax'

    pph_option  = fields.Selection([(22,'22'),(23,'23'),(24,'24'),(25,'25')],string='PPh')

class move_line(models.Model):
    _inherit = 'account.move.line'

    attachment_id   = fields.Binary('Attachment',attachment=True)
    tax_amount      = fields.Float('Tax Amount',compute='cal_tax_amount')
    file_name       = fields.Char("File Name")
    pph_option      = fields.Selection([(22, '22'), (23, '23'), (24, '24'), (25, '25')], string='PPh')

    @api.multi
    def cal_tax_amount(self):
        for record in self:
            record.tax_amount = record.debit + record.credit

class pph_receipt_popup(models.TransientModel):
    _name = 'pph.receipt.popup'

    type        = fields.Selection([('sales','Sales'),('purchases','Purchases')],string='Transaction')
    pph_option  = fields.Selection([(22, '22'), (23, '23'), (24, '24'), (25, '25')], string='PPh')

    @api.multi
    def show_pph_receipt(self):
        # if self.type == 'purchases':
        #     account_id = self.env['account.account'].search([('name','ilike','Hutang Pajak PPh 23')])
        # elif self.type == 'sales':
        #     account_id = self.env['account.account'].search([('name', 'ilike', 'Piutang Pajak PPh 23')])
        # else:
        #     account_id = False
        # domain = [('account_id','in',account_id.ids)]
        domain = []
        if self.pph_option != False:
            if self.type == 'purchases':
                tax_ids = self.env['account.tax'].search([('type_tax_use','=','purchase'),('pph_option','=',self.pph_option)])
            elif self.type == 'sales':
                tax_ids = self.env['account.tax'].search([('type_tax_use', '=', 'sale'),('pph_option','=',self.pph_option)])
            else:
                tax_ids = False
        else:
            tax_ids = False
        if self.pph_option:
            domain.append((''))
        domain = [('account_id','in',tax_ids.mapped('account_id').ids)]
        items = self.env['account.move.line'].search([('account_id','in',tax_ids.mapped('account_id').ids)])
        for item in items:
            item.write({'pph_option':self.pph_option})
        return {
            'name': 'PPH Receipt',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'views'    : [[self.env.ref("pph_receipt.view_pph_receipt_tree").id, 'tree'], [self.env.ref("account.view_move_line_form").id, 'form']],
            # 'view_id'  : self.env.ref("pph_receipt.view_pph_receipt_tree").id,
            'target': 'current',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'search_view_id' : self.env.ref("account.view_account_move_line_filter").id,
            'domain' : domain
        }