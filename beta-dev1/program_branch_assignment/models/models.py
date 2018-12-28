# -*- coding: utf-8 -*-

from odoo import models, fields, api

class pos_config(models.Model):
    _inherit = 'pos.config'

    branch_id = fields.Many2one('res.branch', string="Branch")

class program_branch(models.Model):
    _inherit='pos.promotion'

    branch_ids = fields.Many2many('res.branch', 'branch_pos_promotion_rel', 'pos_promotion_id', 'branch_id', string='Branch')

    @api.model
    def create(self, vals):
        create_id = super(program_branch, self).create(vals)
        if vals['branch_ids']:
            for branch in vals['branch_ids'][0][2]:     
                pos_config_record = self.env['pos.config'].search([('branch_id.id', '=', branch)])
                pos_config_record.write({'promotion_ids':[(4, create_id.id)]})
        return create_id
    
    @api.multi
    def write(self, vals):
        befor_branch_ids = self.branch_ids.ids
        result = super(program_branch, self).write(vals)
        after_branch_ids = self.branch_ids.ids

        if befor_branch_ids:
            pos_config_records = self.env['pos.config'].search([('branch_id.id', 'in', befor_branch_ids)])
            
            if pos_config_records:
                for pos_config_record in pos_config_records:
                    update_record = pos_config_record.promotion_ids - self
                    update_record = {'promotion_ids':[(6, 0, update_record.ids)]}
                    pos_config_record.write(update_record)    

        if after_branch_ids:
            pos_config_records = self.env['pos.config'].search([('branch_id.id', 'in', after_branch_ids)])
            
            if pos_config_records:
                for pos_config_record in pos_config_records:
                    update_record = pos_config_record.promotion_ids + self
                    update_record = {'promotion_ids':[(6, 0, update_record.ids)]}
                    pos_config_record.write(update_record)

        return result
    
