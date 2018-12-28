from odoo import fields,api,models,_

class stock_production_lot(models.Model):
	_inherit = "stock.production.lot"

	events_ids = fields.One2many('calendar.event','serial_number_id')

	@api.multi
	def view_event(self):
		context = self._context.copy()
		return {
    		'name':_('View Event'),
    		'view_type':'form',
    		'view_mode':'tree',
    		'res_model': 'calendar.event',
            'view_id':self.env.ref('calendar.view_calendar_event_tree').id,
            'type': 'ir.actions.act_window',
            'domain':[('id','in',self.events_ids.ids)],
           	'context':context,
			}