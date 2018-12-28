from odoo import fields,models,api

class Pos_wizard(models.TransientModel):
    _name= 'pos1.wizard'
    
    satrt_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    bom = fields.Selection([
                    ('all_bom','All Bom'),
                    ('one_bom','One Bom')],string="Bom")
    bom_id = fields.Many2one('mrp.bom',"Bom name")