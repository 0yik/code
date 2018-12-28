# -*- coding: utf-8 -*-
from odoo import api, models, fields
from odoo.exceptions import Warning

# class PurchaseOrder(models.Model):
#     _inherit = 'purchase.order'
#
#     attachment_id = fields.Many2many('ir.attachment', 'po_attachment_rel', 'po_id', 'attachment_id', 'Attachments')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    attachment_id = fields.Many2many('ir.attachment', 'po_attachment_rel', 'po_id', 'attachment_id', 'Attachments')


class Attachment(models.Model):
    _inherit = "ir.attachment"
    
    @api.multi
    def create(self, vals):
        result = super(Attachment, self).create(vals)
        if vals.has_key('res_model'):
            purchase_obj = self.env['purchase.order']
            if vals.get('res_model', False) == 'purchase.order':
                self.env.cr.execute(''' Insert into po_attachment_rel values(%s,%s) '''%(str(vals['res_id']),str(result.id)))
                mail_template = self.env['mail.template']
                ir_model_data = self.env['ir.model.data']
                message_obj = self.env['mail.compose.message']
                template_id = ir_model_data.get_object_reference('accesstech_modifier_access_rights', 'email_template_notify_pm_po')[1]
                values = message_obj.onchange_template_id(template_id, 'comment', 'purchase.order', vals['res_id'])['value']
                message_id = message_obj.create(values)
                message_id.send_mail()
        return result