# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import math, time
from datetime import datetime
from dateutil.relativedelta import relativedelta

class MasterListWizard(models.TransientModel):
    _name = 'master.list.wizard'
    
    @api.multi
    def generate_master_list(self):
        data = {}
        main_lst = []
        master_list = self.env['master.list'].browse(self._context.get('active_ids', []))
        class_list = list(set([x.class_id for x in master_list]))
        for class_id in class_list:
            line_list = []
            for master_id in master_list:
                if master_id.class_id == class_id:
                    line_dict = {'student_id': master_id.student_id.name,
                                 'class_id': master_id.class_id.name,
                                 'class_teacher_id': master_id.class_teacher_id.name,
                                 'sp_id': [{'sp_id': x.sp_id.name, 'number':x.number} for x in master_id.sp_line],
                                 'ot_id': [{'ot_id': x.ot_id.name, 'number':x.number} for x in master_id.ot_line],
                                 'ap_id': [{'ap_id': x.ap_id.name, 'number':x.number} for x in master_id.ap_line],
                                 'pc_id': [{'pc_id': x.pc_id.name, 'number':x.number} for x in master_id.pc_line],
                                 'sw_id': [{'sw_id': x.sw_id.name, 'number':x.number} for x in master_id.sw_line],
                                 'tc_id': [{'tc_id': x.tc_id.name, 'number':x.number} for x in master_id.tc_line],
                                 'financial_assistance': master_id.financial_assistance,
                                 'remarks': master_id.remarks
                                 }
                    line_list.append(line_dict)
            sp_total = []
            ot_total = []
            ap_total = []
            pc_total = []
            sw_total = []
            tc_total = []
            fa_sa = 0
            for line in line_list:
                for i in range(0, len(line.get('sp_id'))):
                    if len(sp_total) == len(line.get('sp_id')):
                        sp_total[i] = sp_total[i] + line['sp_id'][i]['number']
                    else:
                        sp_total.append(line['sp_id'][i]['number'])
                        
                for i in range(0, len(line.get('ot_id'))):
                    if len(ot_total) == len(line.get('ot_id')):
                        ot_total[i] = ot_total[i] + line['ot_id'][i]['number']
                    else:
                        ot_total.append(line['ot_id'][i]['number'])
                        
                for i in range(0, len(line.get('ap_id'))):
                    if len(ap_total) == len(line.get('ap_id')):
                        ap_total[i] = ap_total[i] + line['ap_id'][i]['number']
                    else:
                        ap_total.append(line['ap_id'][i]['number'])
                for i in range(0, len(line.get('pc_id'))):
                    if len(pc_total) == len(line.get('pc_id')):
                        pc_total[i] = pc_total[i] + line['pc_id'][i]['number']
                    else:
                        pc_total.append(line['pc_id'][i]['number'])
                        
                for i in range(0, len(line.get('sw_id'))):
                    if len(sw_total) == len(line.get('sw_id')):
                        sw_total[i] = sw_total[i] + line['sw_id'][i]['number']
                    else:
                        sw_total.append(line['sw_id'][i]['number'])
                        
                for i in range(0, len(line.get('tc_id'))):
                    if len(tc_total) == len(line.get('tc_id')):
                        tc_total[i] = tc_total[i] + line['tc_id'][i]['number']
                    else:
                        tc_total.append(line['tc_id'][i]['number'])
                        
                fa_sa += line['financial_assistance']
                        
            main_lst.append({'class': class_id.name,
                             'lines': line_list,
                             'sp_total' : sp_total,
                             'ot_total' : ot_total,
                             'ap_total' : ap_total,
                             'pc_total' : pc_total,
                             'sw_total' : sw_total,
                             'tc_total' : tc_total,
                             'fa_sa' : fa_sa,
                             })
        data.update({'get_data': main_lst})
        data.update(self.read([])[0])
        return self.env['report'].get_action([], 'ap_intervention.master_list_report', data=data)
