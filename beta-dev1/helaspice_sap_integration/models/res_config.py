from odoo import models, fields, api

class StockConfigSettings(models.TransientModel):
    _inherit = 'stock.config.settings'

    sap_url = fields.Char('URL')
    sap_username = fields.Char('Username')
    sap_password = fields.Char('Password')

    @api.model
    def get_default_sap_url(self, fields):
        sap_url = self.env['ir.config_parameter'].get_param('sap.url', default=None)
        return {'sap_url': sap_url or False}

    @api.multi
    def set_sap_url(self):
        for record in self:
            self.env['ir.config_parameter'].set_param('sap.url', record.sap_url or '')

    @api.model
    def get_default_sap_username(self, fields):
        sap_username = self.env['ir.config_parameter'].get_param('sap.username', default=None)
        return {'sap_username': sap_username or False}

    @api.multi
    def set_sap_username(self):
        for record in self:
            self.env['ir.config_parameter'].set_param('sap.username', record.sap_username or '')

    @api.model
    def get_default_sap_password(self, fields):
        sap_password = self.env['ir.config_parameter'].get_param('sap.password', default=None)
        return {'sap_password': sap_password or False}

    @api.multi
    def set_sap_password(self):
        for record in self:
            self.env['ir.config_parameter'].set_param('sap.password', record.sap_password or '')

StockConfigSettings()