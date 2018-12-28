from odoo import api, fields, models
 
class website_config_setting(models.TransientModel):
    _inherit = 'website.config.settings'
    
    honos_header_style_one = fields.Char('honos header style1',related='website_id.honos_header_style_one')
    honos_header_style_two = fields.Char("honos header style2",related='website_id.honos_header_style_two')
    honos_header_style_three = fields.Char("honos header style3",related='website_id.honos_header_style_three')
