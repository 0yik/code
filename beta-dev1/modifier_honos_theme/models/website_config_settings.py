# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class WebsiteConfigSettings(models.TransientModel):
    _inherit = 'website.config.settings'

    website_advance_deposit = fields.Float("Default Advance Deposit (%)", related="website_id.website_advance_deposit")


class top_banner(models.Model):
    _name = 'top.banner'
    _description = "Configure Top Banner"

    name = fields.Char("Name",required=1)
    product_id = fields.Many2one('product.product','Product')
    text_content = fields.Text('Sub Content')
    sequence = fields.Integer('Sequence')
    pro_banner_img = fields.Binary('Product Banner Image')
    pro_banner_video = fields.Binary('Product Banner Video')
    file_name = fields.Char("File Name")
    video = fields.Boolean("Video File")
