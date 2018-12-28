from odoo import models,fields,api,_

class indonesia_spt_report(models.AbstractModel):
    _name='indonesia.1721.1'

    @api.model
    def render_html(self, docids, data=None):
        rp = self.env['wizard.1721.1.report'].browse(docids[0])
        # parking_records = self.env['vehicle.parking'].search(['&', ('arrival_time', '>=', rp.arrival),
        #                                                       ('departure_time', '<=', rp.departure),
        #                                                       ('arrival_time', '<=', rp.departure),
        #                                                       ('departure_time', '>=', rp.arrival)])

        print "rp>>>>>>>>>>>",data

        return self.env['report'].render('indonesia_spt.report_1721_1',{

        })

