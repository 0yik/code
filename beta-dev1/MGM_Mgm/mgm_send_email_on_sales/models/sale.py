from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('so_sent', 'SO Sent'),
        ('waiting', 'Waiting Approval'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    # state = fields.Selection(selection_add=[('so_sent', 'SO Sent')])
    vals_update = fields.Boolean('Vals Updated', default=True)

    @api.multi
    def write(self, vals):
        if vals and 'vals_update' not in vals:
            if 'message_follower_ids' not in vals and len(vals) >= 1:
                vals['vals_update'] = True
        res = super(SaleOrder, self).write(vals)
        return res

    @api.multi
    def action_quotation_send_sale(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            action_id = self.env['ir.model.data'].get_object_reference('sale', 'action_orders')[1]
            menu_id = self.env['ir.model.data'].get_object_reference('sale', 'menu_sale_order')[1]
            template_id = ir_model_data.get_object_reference('mgm_send_email_on_sales', 'email_template_edi_sale_sent')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'default_action_id': action_id,
            'default_menu_id': menu_id,
            'custom_layout': "sale.mail_template_data_notification_email_sale_order"
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }



class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    state = fields.Selection(selection_add=[('so_sent', 'SO Sent')])




