# -*- coding: utf-8 -*-

from odoo import api, fields, models

class booking_event_warning(models.TransientModel):
    _name = "booking.event.warning"

    name = fields.Char("Name")
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(booking_event_warning, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,submenu=submenu)
        active_id = self._context.get('active_id')
        model = self._context.get('active_model')
        msg = self._context.get('warning_message','')
        if not active_id or model not in ['sale.order','stock.picking'] or not msg:
            return res
        if model =='sale.order':
            button_string = 'Confirm Sale'
        else:
            button_string = 'Mark as Todo'    
        
        res['arch'] = """
            <form string="Warning">
                <div>
                    <p class="oe_grey">
                       %s
                    </p>
                </div>
                <footer>
                    <button name="action_confirm" string="%s" type="object"/>
                    or
                    <button string="Cancel" class="oe_link" special="cancel"/>
                </footer>
           </form>
        """%(msg,button_string)
        return res
    
    @api.multi
    def action_confirm(self):
        active_model = self._context.get("active_model")
        active_id = self._context.get("active_id")
        if active_model and active_id:
            ctx = self._context.copy()
            ctx.update({'process_event_booking': True})
            self.env[active_model].browse(active_id).with_context(ctx).action_confirm()
        return True
