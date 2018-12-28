from odoo import api, fields, models

class website_config_settings(models.TransientModel):
    _inherit = 'website.config.settings'

    module_honos_shop_left = fields.Selection([
        (0, 'Uninstall Module'),
        (1, 'Install Module')
        ], "honos Shop Left Layout")
    module_honos_shop_right = fields.Selection([
        (0, 'Uninstall Module'),
        (1, 'Install Module')
        ], "honos Shop Right Layout")
    module_honos_shop_list = fields.Selection([
        (0, 'Uninstall Module'),
        (1, 'Install Module')
        ], "honos Shop List Layout")
    module_honos_blog = fields.Selection([
        (0, 'Uninstall Module'),
        (1, 'Install Module')
        ], "honos Blog")
    module_honos_compare = fields.Selection([
        (0, 'Uninstall Module'),
        (1, 'Install Module')
        ], "honos Product Compare")
    module_honos_account = fields.Selection([
        (0, 'Uninstall Module'),
        (1, 'Install Module')
        ], "honos Account")
    module_honos_reset_password = fields.Selection([
         (0, 'Uninstall Module'),
         (1, 'Install Module')
         ], "honos Reset Password")
        
    
