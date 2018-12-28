from odoo import api, fields, models,_

class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    project_id = fields.Many2one('project.project')
    product_to_manufacture_ids = fields.One2many('product.to.manufacture','contract_id','Product To Manufacture')
    mrp_production_ids = fields.One2many('mrp.production','contract_id')

    @api.multi
    def open_project(self):
        project = self.mapped('project_id')
        action = self.env.ref('project.open_view_project_all_config').read()[0]
        if project:
            action['views'] = [(self.env.ref('project.edit_project').id, 'form')]
            action['res_id'] = project.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def open_manufacture_order(self):
        for rec in self:
            manufacture = rec.mapped('mrp_production_ids')
            action = self.env.ref('mrp.mrp_production_action').read()[0]
            if manufacture:
                action['domain'] = [('id', 'in', manufacture.ids)]
            else:
                action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def set_open(self):
        vals = {}
        for rec in self:
            vals.update({'name':rec.name})
            project = self.env['project.project'].create(vals)
            rec.project_id = project.id
            manufacture_vals = {}
            manufacture_lst = []
            for mo_line in rec.product_to_manufacture_ids:
                if mo_line:
                    if mo_line.product_id.bom_ids:
                        manufacture_rec = self.env['mrp.production'].with_context(mail_create_nosubscribe=True)
                        manufacture_vals.update({'product_id':mo_line.product_id.id,'bom_id':mo_line.product_id.bom_ids.id,
                                                 'product_uom_id':mo_line.product_id.product_tmpl_id.uom_id.id,
                                                 'name': self.env['ir.sequence'].next_by_code('mrp.production'),'product_qty':mo_line.quantity,
                                                 })
                        manufacture = manufacture_rec.create(manufacture_vals)
                        manufacture_lst.append(manufacture.id)
            rec.mrp_production_ids = [(6, 0, manufacture_lst)]
        return super(account_analytic_account, self).set_open()

class producttomanufacture(models.Model):
    _name = 'product.to.manufacture'

    contract_id = fields.Many2one('account.analytic.account','Contract')
    product_id = fields.Many2one('product.product','Product')
    quantity = fields.Float('Quantity')


class mrpproduction(models.Model):
    _inherit = 'mrp.production'

    contract_id = fields.Many2one('account.analytic.account')

