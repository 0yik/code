from odoo import models, fields, api
from datetime import datetime, timedelta, date
import time
from dateutil.relativedelta import relativedelta

class branch_target(models.Model):
	_inherit = 'branch.target'

	#button function 
	@api.multi
	def count_daily_target(self):
		for target_line in self.target_id:
			#convert in date
			from_date = datetime.strptime(target_line.date_from, '%Y-%m-%d')
			to_date = datetime.strptime(target_line.date_to, '%Y-%m-%d')
			diff_days = abs(from_date - to_date).days 
			if diff_days == 0:
			    diff_days = 1
			target_line.daily_target = (target_line.target/diff_days)
		return True

	@api.multi
	def count_daily_so(self):
		total = 0
		final_amount = 0.0
		records = self.env['sale.order'].search([('date_order', '>=', datetime.now().strftime('%Y-%m-%d 00:00:00')),('date_order', '<=', datetime.now().strftime('%Y-%m-%d 23:23:59'))])
		for record in records:
			total = total + record.amount_total
		#add total for current date so between date_to and date_from	
		target_achivement_records = self.env['target.achievement'].search([('date_to', '>=', datetime.now().strftime('%Y-%m-%d 00:00:00')),('date_from', '<=', datetime.now().strftime('%Y-%m-%d 23:23:59'))])
		#add total between date_to and date_from
		for target_achivement_record in target_achivement_records:
		    target_achivement_record.daily_achivement = total
		current_date_ids = target_achivement_records.mapped('id')
		other_date_records = self.target_id.filtered(lambda a: a.id not in current_date_ids)
		#change total between date_to and date_from
		for other_date_record in other_date_records:
		    other_date_record.daily_achivement = 0.0

		return True
 
class target_achivement(models.Model):
	_inherit = 'target.achievement' 

	daily_target = fields.Float('Daily Target', readonly=True)
	daily_achivement = fields.Float('Daily Achivement', readonly=True)

