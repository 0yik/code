from odoo import fields, api, models
import json

class PosOrder(models.Model):
    _name = 'pos.order.delivery.report'

    address = fields.Char()
    city = fields.Char()
    d_name = fields.Char()
    delivery_date = fields.Char()
    email = fields.Char()
    mobile = fields.Char()
    order_note = fields.Char()
    person_id = fields.Many2one('hr.employee')
    street = fields.Char()
    zip = fields.Char()
    order_data = fields.Text()



    @api.multi
    def get_id_action_report(self,data,json_order_data):
        self._cr.execute("DELETE FROM pos_order_delivery_report")
        data.update({
            'order_data' : json.dumps(json_order_data),
        })
        report_id = self.create(data)
        action_report_ids = self.env['ir.actions.report.xml'].search(
            [('model', '=', 'pos.order.delivery.report'), ('report_name', '=', 'tm_pos_print_home_delivery.pos_delivery_order_report')])
        return action_report_ids and [action_report_ids[0].id,report_id.id]or False

class report_timesheet_line(models.Model):
    _name = "report.tm_pos_print_home_delivery.pos_delivery_order_report"

    @api.multi
    def render_html(self, docids, data):
        doc = self.env['pos.order.delivery.report'].browse(docids[0])
        order_data = json.loads(doc.order_data)
        order_lines = list(map(lambda item: item[2], order_data.get('lines')))
        docargs = {
            'doc_ids': docids,
            'docs' : doc,
            'order_data': order_data,
            'order_lines': order_lines
        }
        return self.env['report'].render('tm_pos_print_home_delivery.pos_delivery_order_report', docargs)