from odoo import api, models, fields
import pytz
from datetime import datetime
from dateutil import tz

class tgw_account_invoice_report(models.AbstractModel):
    _name = 'report.tgw_account_invoice_modifier.report_tgw_account_invoice'
    _template = 'tgw_account_invoice_modifier.report_tgw_account_invoice'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('tgw_account_invoice_modifier.report_tgw_account_invoice')

        invoice_obj = self.env['account.invoice']
        invoice_id = invoice_obj.browse(docids)

        docargs = {
            'doc_ids': invoice_id or False,
            'doc_model': report.model,
            'docs': self,
        }
        return report_obj.render('tgw_account_invoice_modifier.report_tgw_account_invoice', docargs)
