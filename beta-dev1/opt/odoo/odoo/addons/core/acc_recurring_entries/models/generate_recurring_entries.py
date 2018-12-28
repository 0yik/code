from odoo import api, exceptions, fields, models, _
from datetime import datetime

class GenerateRecurringEntries(models.Model):
    _name = 'generate.recurring.entries'

    def action_generate_recurring_entries(self):
        record = self.env['account.subscription.generate'].create({'date': datetime.now().date()})
        record.action_generate()

GenerateRecurringEntries()