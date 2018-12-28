#-*- coding:utf-8 -*-

# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from odoo import api, fields, models


class ReportClassList(models.AbstractModel):
    _name = 'report.atts_class.report_class_list'

    def get_data(self):
        data_class = []
        data_class_new = []
        class_obj = self.env['class.class']
        act_domain = []
        class_ids = class_obj.search(act_domain, order='class_level,class_no ASC')
        total_class=total_class7=total_class8=total_class9=total_class10=total_class11=total_class12=total_class13=total_class14=total_class15=total_class16=total_class17=total_class18=0
        gtotal_class=gtotal_class7=gtotal_class8=gtotal_class9=gtotal_class10=gtotal_class11=gtotal_class12=gtotal_class13=gtotal_class14=gtotal_class15=gtotal_class16=gtotal_class17=gtotal_class18=0
        for data in class_ids:
            male7=male8=male9=male10=male11=male12=male13=male14=male15=male16=male17=male18=0
            male7_asd=male8_asd=male9_asd=male10_asd=male11_asd=male12_asd=male13_asd=male14_asd=male15_asd=male16_asd=male17_asd=male18_asd=0
            male7_mid=male8_mid=male9_mid=male10_mid=male11_mid=male12_mid=male13_mid=male14_mid=male15_mid=male16_mid=male17_mid=male18_mid=0
            male7_imid=male8_imid=male9_imid=male10_imid=male11_imid=male12_imid=male13_imid=male14_imid=male15_imid=male16_imid=male17_imid=male18_imid=0                        
            female7=female8=female9=female10=female11=female12=female13=female14=female15=female16=female17=female18=0
            female7_asd=female8_asd=female9_asd=female10_asd=female11_asd=female12_asd=female13_asd=female14_asd=female15_asd=female16_asd=female17_asd=female18_asd=0
            female7_mid=female8_mid=female9_mid=female10_mid=female11_mid=female12_mid=female13_mid=female14_mid=female15_mid=female16_mid=female17_mid=female18_mid=0
            female7_imid=female8_imid=female9_imid=female10_imid=female11_imid=female12_imid=female13_imid=female14_imid=female15_imid=female16_imid=female17_imid=female18_imid=0
            
            total_male=total_female=total_male_asd=total_male_mid=total_male_imid=total_female_asd=total_female_mid=total_emale_imid=0
            for student in self.env['class.student.list'].search([('class_id','=',data.id)]):
                if student.student_id.gender=='male' and student.student_id.age==7 and student.student_id.state=='done':
                    male7 = male7+1
                if student.student_id.gender=='male' and student.student_id.age==8 and student.student_id.state=='done':
                    male8 = male8+1
                if student.student_id.gender=='male' and student.student_id.age==9 and student.student_id.state=='done':
                    male9 = male9+1
                if student.student_id.gender=='male' and student.student_id.age==10 and student.student_id.state=='done':
                    male10 = male10+1
                if student.student_id.gender=='male' and student.student_id.age==11 and student.student_id.state=='done':
                    male11 = male11+1
                if student.student_id.gender=='male' and student.student_id.age==12 and student.student_id.state=='done':
                    male12 = male12+1
                if student.student_id.gender=='male' and student.student_id.age==13 and student.student_id.state=='done':
                    male13 = male13+1
                if student.student_id.gender=='male' and student.student_id.age==14 and student.student_id.state=='done':
                    male14 = male14+1
                if student.student_id.gender=='male' and student.student_id.age==15 and student.student_id.state=='done':
                    male15 = male15+1
                if student.student_id.gender=='male' and student.student_id.age==16 and student.student_id.state=='done':
                    male16 = male16+1
                if student.student_id.gender=='male' and student.student_id.age==17 and student.student_id.state=='done':
                    male17 = male17+1
                if student.student_id.gender=='male' and student.student_id.age==18 and student.student_id.state=='done':
                    male18 = male18+1
                total_male=male7+male8+male9+male10+male11+male12+male13+male14+male15+male16+male17+male18
                
                if student.student_id.gender=='male' and student.student_id.age==7 and student.student_id.programme=='ASD' and student.student_id.state=='done':
                    male7_asd = male7_asd+1
                if student.student_id.gender=='male' and student.student_id.age==8 and student.student_id.programme=='ASD' and student.student_id.state=='done':
                    male8_asd = male8_asd+1
                if student.student_id.gender=='male' and student.student_id.age==9 and student.student_id.programme=='ASD' and student.student_id.state=='done':
                    male9_asd = male9_asd+1
                if student.student_id.gender=='male' and student.student_id.age==10 and student.student_id.programme=='ASD' and student.student_id.state=='done':
                    male10_asd = male10_asd+1
                if student.student_id.gender=='male' and student.student_id.age==11 and student.student_id.programme=='ASD' and student.student_id.state=='done':
                    male11_asd = male11_asd+1
                if student.student_id.gender=='male' and student.student_id.age==12 and student.student_id.programme=='ASD' and student.student_id.state=='done':
                    male12_asd = male12_asd+1
                if student.student_id.gender=='male' and student.student_id.age==13 and student.student_id.programme=='ASD' and student.student_id.state=='done':
                    male13_asd = male13_asd+1
                if student.student_id.gender=='male' and student.student_id.age==14 and student.student_id.programme=='ASD' and student.student_id.state=='done':
                    male14_asd = male14_asd+1
                if student.student_id.gender=='male' and student.student_id.age==15 and student.student_id.programme=='ASD' and student.student_id.state=='done':
                    male15_asd = male15_asd+1
                if student.student_id.gender=='male' and student.student_id.age==16 and student.student_id.programme=='ASD' and student.student_id.state=='done':
                    male16_asd = male16_asd+1
                if student.student_id.gender=='male' and student.student_id.age==17 and student.student_id.programme=='ASD' and student.student_id.state=='done':
                    male17_asd = male17_asd+1
                if student.student_id.gender=='male' and student.student_id.age==18 and student.student_id.programme=='ASD' and student.student_id.state=='done':
                    male18_asd = male18_asd+1
                total_male_asd=male7_asd+male8_asd+male9_asd+male10_asd+male11_asd+male12_asd+male13_asd+male14_asd+male15_asd+male16_asd+male17_asd+male18_asd
                    
                if student.student_id.gender=='male' and student.student_id.age==7 and student.student_id.programme=='MID' and student.student_id.state=='done':
                    male7_mid = male7_mid+1
                if student.student_id.gender=='male' and student.student_id.age==8 and student.student_id.programme=='MID' and student.student_id.state=='done':
                    male8_mid = male8_mid+1
                if student.student_id.gender=='male' and student.student_id.age==9 and student.student_id.programme=='MID' and student.student_id.state=='done':
                    male9_mid = male9_mid+1
                if student.student_id.gender=='male' and student.student_id.age==10 and student.student_id.programme=='MID' and student.student_id.state=='done':
                    male10_mid = male10_mid+1
                if student.student_id.gender=='male' and student.student_id.age==11 and student.student_id.programme=='MID' and student.student_id.state=='done':
                    male11_mid = male11_mid+1
                if student.student_id.gender=='male' and student.student_id.age==12 and student.student_id.programme=='MID' and student.student_id.state=='done':
                    male12_mid = male12_mid+1
                if student.student_id.gender=='male' and student.student_id.age==13 and student.student_id.programme=='MID' and student.student_id.state=='done':
                    male13_mid = male13_mid+1
                if student.student_id.gender=='male' and student.student_id.age==14 and student.student_id.programme=='MID' and student.student_id.state=='done':
                    male14_mid = male14_mid+1
                if student.student_id.gender=='male' and student.student_id.age==15 and student.student_id.programme=='MID' and student.student_id.state=='done':
                    male15_mid = male15_mid+1
                if student.student_id.gender=='male' and student.student_id.age==16 and student.student_id.programme=='MID' and student.student_id.state=='done':
                    male16_mid = male16_mid+1
                if student.student_id.gender=='male' and student.student_id.age==17 and student.student_id.programme=='MID' and student.student_id.state=='done':
                    male17_mid = male17_mid+1
                if student.student_id.gender=='male' and student.student_id.age==18 and student.student_id.programme=='MID' and student.student_id.state=='done':
                    male18_mid = male18_mid+1
                total_male_mid=male7_mid+male8_mid+male9_mid+male10_mid+male11_mid+male12_mid+male13_mid+male14_mid+male15_mid+male16_mid+male17_mid+male18_mid
                
                if student.student_id.gender=='male' and student.student_id.age==7 and student.student_id.programme=='Integrated' and student.student_id.state=='done':
                    male7_imid = male7_imid+1
                if student.student_id.gender=='male' and student.student_id.age==8 and student.student_id.programme=='Integrated' and student.student_id.state=='done':
                    male8_imid = male8_imid+1
                if student.student_id.gender=='male' and student.student_id.age==9 and student.student_id.programme=='Integrated' and student.student_id.state=='done':
                    male9_imid = male9_imid+1
                if student.student_id.gender=='male' and student.student_id.age==10 and student.student_id.programme=='Integrated' and student.student_id.state=='done':
                    male10_imid = male10_imid+1
                if student.student_id.gender=='male' and student.student_id.age==11 and student.student_id.programme=='Integrated' and student.student_id.state=='done':
                    male11_imid = male11_imid+1
                if student.student_id.gender=='male' and student.student_id.age==12 and student.student_id.programme=='Integrated' and student.student_id.state=='done':
                    male12_imid = male12_imid+1
                if student.student_id.gender=='male' and student.student_id.age==13 and student.student_id.programme=='Integrated' and student.student_id.state=='done':
                    male13_imid = male13_imid+1
                if student.student_id.gender=='male' and student.student_id.age==14 and student.student_id.programme=='Integrated' and student.student_id.state=='done':
                    male14_imid = male14_imid+1
                if student.student_id.gender=='male' and student.student_id.age==15 and student.student_id.programme=='Integrated' and student.student_id.state=='done':
                    male15_imid = male15_imid+1
                if student.student_id.gender=='male' and student.student_id.age==16 and student.student_id.programme=='Integrated' and student.student_id.state=='done':
                    male16_imid = male16_imid+1
                if student.student_id.gender=='male' and student.student_id.age==17 and student.student_id.programme=='Integrated' and student.student_id.state=='done':
                    male17_imid = male17_imid+1
                if student.student_id.gender=='male' and student.student_id.age==18 and student.student_id.programme=='Integrated' and student.student_id.state=='done':
                    male18_imid = male18_imid+1
                total_male_imid=male7_imid+male8_imid+male9_imid+male10_imid+male11_imid+male12_imid+male13_imid+male14_imid+male15_imid+male16_imid+male17_imid+male18_imid
                    
                if student.student_id.gender=='female' and student.student_id.age==7 and student.student_id.state=='done':
                    female7 = female7+1
                if student.student_id.gender=='female' and student.student_id.age==8 and student.student_id.state=='done':
                    female8 = female8+1
                if student.student_id.gender=='female' and student.student_id.age==9 and student.student_id.state=='done':
                    female9 = female9+1
                if student.student_id.gender=='female' and student.student_id.age==10 and student.student_id.state=='done':
                    female10 = female10+1
                if student.student_id.gender=='female' and student.student_id.age==11 and student.student_id.state=='done':
                    female11 = female11+1
                if student.student_id.gender=='female' and student.student_id.age==12 and student.student_id.state=='done':
                    female12 = female12+1
                if student.student_id.gender=='female' and student.student_id.age==13 and student.student_id.state=='done':
                    female13 = female13+1
                if student.student_id.gender=='female' and student.student_id.age==14 and student.student_id.state=='done':
                    female14 = female14+1
                if student.student_id.gender=='female' and student.student_id.age==15 and student.student_id.state=='done':
                    female15 = female15+1
                if student.student_id.gender=='female' and student.student_id.age==16 and student.student_id.state=='done':
                    female16 = female16+1
                if student.student_id.gender=='female' and student.student_id.age==17 and student.student_id.state=='done':
                    female17 = female17+1
                if student.student_id.gender=='female' and student.student_id.age==18 and student.student_id.state=='done':
                    female18 = female18+1
                total_female=female7+female8+female9+female10+female11+female12+female13+female14+female15+female16+female17+female18
                    
                if student.student_id.gender=='female' and student.student_id.age==7 and student.student_id.programme=='ASD' and student.student_id.state=='done':
                    female7_asd = female7_asd+1
                if student.student_id.gender=='female' and student.student_id.age==8 and student.student_id.programme=='ASD' and student.student_id.state=='done':
                    female8_asd = female8_asd+1
                if student.student_id.gender=='female' and student.student_id.age==9 and student.student_id.programme=='ASD' and student.student_id.state=='done':
                    female9_asd = female9_asd+1
                if student.student_id.gender=='female' and student.student_id.age==10 and student.student_id.programme=='ASD' and student.student_id.state=='done':
                    female10_asd = female10_asd+1
                if student.student_id.gender=='female' and student.student_id.age==11 and student.student_id.programme=='ASD' and student.student_id.state=='done':
                    female11_asd = female11_asd+1
                if student.student_id.gender=='female' and student.student_id.age==12 and student.student_id.programme=='ASD' and student.student_id.state=='done':
                    female12_asd = female12_asd+1 
                if student.student_id.gender=='female' and student.student_id.age==13 and student.student_id.programme=='ASD' and student.student_id.state=='done':
                    female13_asd = female13_asd+1
                if student.student_id.gender=='female' and student.student_id.age==14 and student.student_id.programme=='ASD' and student.student_id.state=='done':
                    female14_asd = female14_asd+1
                if student.student_id.gender=='female' and student.student_id.age==15 and student.student_id.programme=='ASD' and student.student_id.state=='done':
                    female15_asd = female15_asd+1
                if student.student_id.gender=='female' and student.student_id.age==16 and student.student_id.programme=='ASD' and student.student_id.state=='done':
                    female16_asd = female16_asd+1
                if student.student_id.gender=='female' and student.student_id.age==17 and student.student_id.programme=='ASD' and student.student_id.state=='done':
                    female17_asd = female17_asd+1
                if student.student_id.gender=='female' and student.student_id.age==18 and student.student_id.programme=='ASD' and student.student_id.state=='done':
                    female18_asd = female18_asd+1
                total_female_asd=female7_asd+female8_asd+female9_asd+female10_asd+female11_asd+female12_asd+female13_asd+female14_asd+female15_asd+female16_asd+female17_asd+female18_asd
                    
                if student.student_id.gender=='female' and student.student_id.age==7 and student.student_id.programme=='MID' and student.student_id.state=='done':
                    female7_mid = female7_mid+1
                if student.student_id.gender=='female' and student.student_id.age==8 and student.student_id.programme=='MID' and student.student_id.state=='done':
                    female8_mid = female8_mid+1
                if student.student_id.gender=='female' and student.student_id.age==9 and student.student_id.programme=='MID' and student.student_id.state=='done':
                    female9_mid = female9_mid+1
                if student.student_id.gender=='female' and student.student_id.age==10 and student.student_id.programme=='MID' and student.student_id.state=='done':
                    female10_mid = female10_mid+1
                if student.student_id.gender=='female' and student.student_id.age==11 and student.student_id.programme=='MID' and student.student_id.state=='done':
                    female11_mid = female11_mid+1
                if student.student_id.gender=='female' and student.student_id.age==12 and student.student_id.programme=='MID' and student.student_id.state=='done':
                    female12_mid = female12_mid+1
                if student.student_id.gender=='female' and student.student_id.age==13 and student.student_id.programme=='MID' and student.student_id.state=='done':
                    female13_mid = female13_mid+1
                if student.student_id.gender=='female' and student.student_id.age==14 and student.student_id.programme=='MID' and student.student_id.state=='done':
                    female14_mid = female14_mid+1
                if student.student_id.gender=='female' and student.student_id.age==15 and student.student_id.programme=='MID' and student.student_id.state=='done':
                    female15_mid = female15_mid+1
                if student.student_id.gender=='female' and student.student_id.age==16 and student.student_id.programme=='MID' and student.student_id.state=='done':
                    female16_mid = female16_mid+1
                if student.student_id.gender=='female' and student.student_id.age==17 and student.student_id.programme=='MID' and student.student_id.state=='done':
                    female17_mid = female17_mid+1
                if student.student_id.gender=='female' and student.student_id.age==18 and student.student_id.programme=='MID' and student.student_id.state=='done':
                    female18_mid = female18_mid+1
                total_female_mid=female7_mid+female8_mid+female9_mid+female10_mid+female11_mid+female12_mid+female13_mid+female14_mid+female15_mid+female16_mid+female17_mid+female18_mid
                
                if student.student_id.gender=='female' and student.student_id.age==7 and student.student_id.programme=='Integrated' and student.student_id.state=='done':
                    female7_imid = female7_imid+1
                if student.student_id.gender=='female' and student.student_id.age==8 and student.student_id.programme=='Integrated' and student.student_id.state=='done':
                    female8_imid = female8_imid+1
                if student.student_id.gender=='female' and student.student_id.age==9 and student.student_id.programme=='Integrated' and student.student_id.state=='done':
                    female9_imid = female9_imid+1
                if student.student_id.gender=='female' and student.student_id.age==10 and student.student_id.programme=='Integrated' and student.student_id.state=='done':
                    female10_imid = female10_imid+1
                if student.student_id.gender=='female' and student.student_id.age==11 and student.student_id.programme=='Integrated' and student.student_id.state=='done':
                    female11_imid = female11_imid+1
                if student.student_id.gender=='female' and student.student_id.age==12 and student.student_id.programme=='Integrated' and student.student_id.state=='done':
                    female12_imid = female12_imid+1
                if student.student_id.gender=='female' and student.student_id.age==13 and student.student_id.programme=='Integrated' and student.student_id.state=='done':
                    female13_imid = female13_imid+1
                if student.student_id.gender=='female' and student.student_id.age==14 and student.student_id.programme=='Integrated' and student.student_id.state=='done':
                    female14_imid = female14_imid+1
                if student.student_id.gender=='female' and student.student_id.age==15 and student.student_id.programme=='Integrated' and student.student_id.state=='done':
                    female15_imid = female15_imid+1
                if student.student_id.gender=='female' and student.student_id.age==16 and student.student_id.programme=='Integrated' and student.student_id.state=='done':
                    female16_imid = female16_imid+1
                if student.student_id.gender=='female' and student.student_id.age==17 and student.student_id.programme=='Integrated' and student.student_id.state=='done':
                    female17_imid = female17_imid+1
                if student.student_id.gender=='female' and student.student_id.age==18 and student.student_id.programme=='Integrated' and student.student_id.state=='done':
                    female18_imid = female18_imid+1
                total_female_imid=female7_imid+female8_imid+female9_imid+female10_imid+female11_imid+female12_imid+female13_imid+female14_imid+female15_imid+female16_imid+female17_imid+female18_imid
            total_class7=male7+female7
            total_class8=male8+female8
            total_class9=male9+female9
            total_class10=male10+female10
            total_class11=male11+female11
            total_class12=male12+female12
            total_class13=male13+female13
            total_class14=male14+female14
            total_class15=male15+female15
            total_class16=male16+female16
            total_class17=male17+female17
            total_class18=male17+female18 
            total_class=total_male+total_female
            gtotal_class7+=total_class7
            gtotal_class8+=total_class8
            gtotal_class9+=total_class9
            gtotal_class10+=total_class10
            gtotal_class11+=total_class12
            gtotal_class13+=total_class13
            gtotal_class14+=total_class14
            gtotal_class15+=total_class16
            gtotal_class17+=total_class17
            gtotal_class18+=total_class18
            gtotal_class+=total_class
            data_class.append({'name': data.class_level,
                               'class_no':data.class_no,
                               'teacher':data.class_teacher_id.name,
                               'female':'Female',
                               'male':'Male',
                               'asd':'ASD',
                               'mid':'MID',
                               'imid':'Integrated MID',
                               'male7':male7,
                               'male8':male8,
                               'male9':male9,
                               'male10':male10,
                               'male11':male11,
                               'male12':male12,
                               'male13':male13,
                               'male14':male14,
                               'male15':male15,
                               'male16':male16,
                               'male17':male17,
                               'male18':male18,
                               ##################
                               'female7':female7,
                               'female8':female8,
                               'female9':female9,
                               'female10':female10,
                               'female11':female11,
                               'female12':female12,
                               'female13':female13,
                               'female14':female14,
                               'female15':female15,
                               'female16':female16,
                               'female17':female17,
                               'female18':female18,
                               ###################
                               'male7_asd':male7_asd,
                               'male8_asd':male8_asd,
                               'male9_asd':male9_asd,
                               'male10_asd':male10_asd,
                               'male11_asd':male11_asd,
                               'male12_asd':male12_asd,
                               'male13_asd':male13_asd,
                               'male14_asd':male14_asd,
                               'male15_asd':male15_asd,
                               'male16_asd':male16_asd,
                               'male17_asd':male17_asd,
                               'male18_asd':male18_asd,
                               
                               ########################
                               
                               'male7_mid':male7_mid,
                               'male8_mid':male8_mid,
                               'male9_mid':male9_mid,
                               'male10_mid':male10_mid,
                               'male11_mid':male11_mid,
                               'male12_mid':male12_mid,
                               'male13_mid':male13_mid,
                               'male14_mid':male14_mid,
                               'male15_mid':male15_mid,
                               'male16_mid':male16_mid,
                               'male17_mid':male17_mid,
                               'male18_mid':male18_mid,
                               
                                ########################
                               
                               'male7_imid':male7_imid,
                               'male8_imid':male8_imid,
                               'male9_imid':male9_imid,
                               'male10_imid':male10_imid,
                               'male11_imid':male11_imid,
                               'male12_imid':male12_imid,
                               'male13_imid':male13_imid,
                               'male14_imid':male14_imid,
                               'male15_imid':male15_imid,
                               'male16_imid':male16_imid,
                               'male17_imid':male17_imid,
                               'male18_imid':male18_imid,
                               
                                ###################
                               'female7_asd':female7_asd,
                               'female8_asd':female8_asd,
                               'female9_asd':female9_asd,
                               'female10_asd':female10_asd,
                               'female11_asd':female11_asd,
                               'female12_asd':female12_asd,
                               'female13_asd':female13_asd,
                               'female14_asd':female14_asd,
                               'female15_asd':female15_asd,
                               'female16_asd':female16_asd,
                               'female17_asd':female17_asd,
                               'female18_asd':female18_asd,
                               
                               ########################
                               
                               'female7_mid':female7_mid,
                               'female8_mid':female8_mid,
                               'female9_mid':female9_mid,
                               'female10_mid':female10_mid,
                               'female11_mid':female11_mid,
                               'female12_mid':female12_mid,
                               'female13_mid':female13_mid,
                               'female14_mid':female14_mid,
                               'female15_mid':female15_mid,
                               'female16_mid':female16_mid,
                               'female17_mid':female17_mid,
                               'female18_mid':female18_mid,
                               
                                ########################
                               
                               'female7_imid':female7_imid,
                               'female8_imid':female8_imid,
                               'female9_imid':female9_imid,
                               'female10_imid':female10_imid,
                               'female11_imid':female11_imid,
                               'female12_imid':female12_imid,
                               'female13_imid':female13_imid,
                               'female14_imid':female14_imid,
                               'female15_imid':female15_imid,
                               'female16_imid':female16_imid,
                               'female17_imid':female17_imid,
                               'female18_imid':female18_imid,
                               
                               
                               ##############################
                               'total_male':total_male,
                               'total_female':total_female,
                               'total_male_asd':total_male_asd,
                               'total_male_mid':total_male_mid,
                               'total_male_imid':total_male_imid,
                               'total_female_asd':total_female_asd,
                               'total_female_mid':total_female_mid,
                               'total_female_imid':total_female_imid,
                               #####################################
                               'total_class7':total_class7,
                               'total_class8':total_class8,
                               'total_class9':total_class9,
                               'total_class10':total_class10,
                               'total_class11':total_class11,
                               'total_class12':total_class12,
                               'total_class13':total_class13,
                               'total_class14':total_class14,
                               'total_class15':total_class15,
                               'total_class16':total_class16,
                               'total_class17':total_class17,
                               'total_class18':total_class18,
                               'total_class':total_class,
                               
                              
                               })
#             data_class_new.append({
#                                     ########################################
#                                    'gtotal_class7':gtotal_class7,
#                                    'gtotal_class8':gtotal_class8,
#                                    'gtotal_class9':gtotal_class9,
#                                    'gtotal_class10':gtotal_class10,
#                                    'gtotal_class11':gtotal_class11,
#                                    'gtotal_class12':gtotal_class12,
#                                    'gtotal_class13':gtotal_class13,
#                                    'gtotal_class14':gtotal_class14,
#                                    'gtotal_class15':gtotal_class15,
#                                    'gtotal_class16':gtotal_class16,
#                                    'gtotal_class17':gtotal_class17,
#                                    'gtotal_class18':gtotal_class18,
#                                    'gtotal_class':gtotal_class,
#                                    })    
        return data_class, gtotal_class7,gtotal_class8,gtotal_class9,gtotal_class10,gtotal_class11,gtotal_class12,gtotal_class13,gtotal_class14,gtotal_class15,gtotal_class16,gtotal_class17,gtotal_class18,gtotal_class
    

    @api.model
    def render_html(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        data_res,gtotal_class7,gtotal_class8,gtotal_class9,gtotal_class10,gtotal_class11,gtotal_class12,gtotal_class13,gtotal_class14,gtotal_class15,gtotal_class16,gtotal_class17,gtotal_class18,gtotal_class=self.get_data()
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'class_level_data': data_res,
            'gtotal_class7':gtotal_class7,
            'gtotal_class8':gtotal_class8,
            'gtotal_class9':gtotal_class9,
            'gtotal_class10':gtotal_class10,
            'gtotal_class11':gtotal_class11,
            'gtotal_class12':gtotal_class12,
            'gtotal_class13':gtotal_class13,
            'gtotal_class14':gtotal_class14,
            'gtotal_class15':gtotal_class15,
            'gtotal_class16':gtotal_class16,
            'gtotal_class17':gtotal_class17,
            'gtotal_class18':gtotal_class18,
            'gtotal_class':gtotal_class,
            
            
            }
        render_model = 'atts_class.report_class_list'
        return self.env['report'].render(render_model, docargs)
