# -*- coding: utf-8 -*-

from odoo import api, models, _


class studentracedetailreport(models.AbstractModel):
    _name = 'report.atts_student_fields.report_student_race_enrolment'
    
    @api.multi
    def _female_student_race(self):
        asd_chinese_list, asd_indian_list, asd_malay_list, asd_others_list = [], [], [], []
        mid_chinese_list, mid_indian_list, mid_malay_list, mid_others_list = [], [], [], []
        integrated_chinese_list, integrated_indian_list, integrated_malay_list, integrated_others_list = [], [], [], []
        chinese_list, indian_list, malay_list, other_list = [], [], [], []
        race_list = ['Chinese', 'Indian', 'Malay']
        asd_dict, mid_dict, integrated_dict = {}, {}, {}
        race_dict = {}
        female_race = {}
        student_obj = self.env['student.student']
        student_search_obj = student_obj.search([('state_custom','=','draft'),('gender', '=', 'female')])
        if student_search_obj:
            for student_id in student_search_obj:
                race = student_id.race_id.name
                programme = student_id.programme
                if race:
                    if race == 'Chinese':
                        chinese_list.append(race)
                    if race == 'Indian':
                        indian_list.append(race)
                    if race == 'Malay':
                        malay_list.append(race)
                    if race not in race_list:
                        other_list.append(race)
                if programme:
                    if programme == 'ASD':
                        if race == 'Chinese':
                            asd_chinese_list.append(race)
                            asd_dict[race] = len(asd_chinese_list)
                        if race == 'Indian':
                            asd_indian_list.append(race)
                            asd_dict[race] = len(asd_indian_list)
                        if race == 'Malay':
                            asd_malay_list.append(race)
                            asd_dict[race] = len(asd_malay_list)
                        if race not in race_list:
                            asd_others_list.append(race)
                            asd_dict['others'] = len(asd_others_list)
                    if programme == 'MID':
                        if race == 'Chinese':
                            mid_chinese_list.append(race)
                            mid_dict[race] = len(mid_chinese_list)
                        if race == 'Indian':
                            mid_indian_list.append(race)
                            mid_dict[race] = len(mid_indian_list)
                        if race == 'Malay':
                            mid_malay_list.append(race)
                            mid_dict[race] = len(mid_malay_list)
                        if race not in race_list:
                            mid_others_list.append(race)
                            mid_dict['others'] = len(mid_others_list)
                    if programme == 'Integrated':
                        if race == 'Chinese':
                            integrated_chinese_list.append(race)
                            integrated_dict[race] = len(integrated_chinese_list)
                        if race == 'Indian':
                            integrated_indian_list.append(race)
                            integrated_dict[race] = len(integrated_indian_list)
                        if race == 'Malay':
                            integrated_malay_list.append(race)
                            integrated_dict[race] = len(integrated_malay_list)
                        if race not in race_list:
                            integrated_others_list.append(race)
                            integrated_dict['others'] = len(integrated_others_list)
            race_dict['ASD'] = asd_dict
            race_dict['asd_total'] = sum(asd_dict.itervalues())
            race_dict['MID'] = mid_dict
            race_dict['mid_total'] = sum(mid_dict.itervalues())
            race_dict['Integrated'] = integrated_dict     
            race_dict['integrated_total'] = sum(integrated_dict.itervalues())
            female_race['chinese'] = len(chinese_list)
            female_race['indian'] = len(indian_list)
            female_race['malay'] = len(malay_list)
            female_race['other'] = len(other_list)
            female_race['grand_total'] = len(chinese_list) + len(indian_list) + len(malay_list) + len(other_list)
            race_dict['Female'] = female_race
            return race_dict
        else:
            return race_dict
        
    @api.multi
    def _male_student_race(self):
        asd_chinese_list, asd_indian_list, asd_malay_list, asd_others_list = [], [], [], []
        mid_chinese_list, mid_indian_list, mid_malay_list, mid_others_list = [], [], [], []
        integrated_chinese_list, integrated_indian_list, integrated_malay_list, integrated_others_list = [], [], [], []
        chinese_list, indian_list, malay_list, other_list = [], [], [], []
        race_list = ['Chinese', 'Indian', 'Malay']
        asd_dict, mid_dict, integrated_dict = {}, {}, {}
        race_dict = {}
        male_race = {}
        student_obj = self.env['student.student']
        student_search_obj = student_obj.search([('gender', '=', 'male'),('state_custom', '=', 'draft')])
        if student_search_obj:
            for student_id in student_search_obj:
                race = student_id.race_id.name
                programme = student_id.programme
                if race:
                    if race == 'Chinese':
                        chinese_list.append(race)
                    if race == 'Indian':
                        indian_list.append(race)
                    if race == 'Malay':
                        malay_list.append(race)
                    if race not in race_list:
                        other_list.append(race)
                if programme:
                    if programme == 'ASD':
                        if race == 'Chinese':
                            asd_chinese_list.append(race)
                            asd_dict[race] = len(asd_chinese_list)
                        if race == 'Indian':
                            asd_indian_list.append(race)
                            asd_dict[race] = len(asd_indian_list)
                        if race == 'Malay':
                            asd_malay_list.append(race)
                            asd_dict[race] = len(asd_malay_list)
                        if race not in race_list:
                            asd_others_list.append(race)
                            asd_dict['others'] = len(asd_others_list)
                    if programme == 'MID':
                        if race == 'Chinese':
                            mid_chinese_list.append(race)
                            mid_dict[race] = len(mid_chinese_list)
                        if race == 'Indian':
                            mid_indian_list.append(race)
                            mid_dict[race] = len(mid_indian_list)
                        if race == 'Malay':
                            mid_malay_list.append(race)
                            mid_dict[race] = len(mid_malay_list)
                        if race not in race_list:
                            mid_others_list.append(race)
                            mid_dict['others'] = len(mid_others_list)
                    if programme == 'Integrated':
                        if race == 'Chinese':
                            integrated_chinese_list.append(race)
                            integrated_dict[race] = len(integrated_chinese_list)
                        if race == 'Indian':
                            integrated_indian_list.append(race)
                            integrated_dict[race] = len(integrated_indian_list)
                        if race == 'Malay':
                            integrated_malay_list.append(race)
                            integrated_dict[race] = len(integrated_malay_list)
                        if race not in race_list:
                            integrated_others_list.append(race)
                            integrated_dict['others'] = len(integrated_others_list)
            race_dict['ASD'] = asd_dict
            race_dict['asd_total'] = sum(asd_dict.itervalues())
            race_dict['MID'] = mid_dict
            race_dict['mid_total'] = sum(mid_dict.itervalues())
            race_dict['Integrated'] = integrated_dict     
            race_dict['integrated_total'] = sum(integrated_dict.itervalues())    
            male_race['chinese'] = len(chinese_list)
            male_race['indian'] = len(indian_list)
            male_race['malay'] = len(malay_list)
            male_race['other'] = len(other_list)
            male_race['grand_total'] = len(chinese_list) + len(indian_list) + len(malay_list) + len(other_list)
            race_dict['male'] = male_race
            return race_dict
        else:
            return race_dict
    @api.multi
    def render_html(self, docids, data=None):
        female_chinese, male_chinese, female_indian, male_indian, female_malay, male_malay, female_other, male_other, female_grand_total, male_grand_total = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        self.model = self.env.context.get('active_model')
        model = self.env.context.get('active_model')
        female_dict, male_dict = self._female_student_race() , self._male_student_race()
        female_chinese, female_indian, female_malay, female_other, female_grand_total = female_dict.get('Female') and female_dict.get('Female').get('chinese'), female_dict.get('Female') and female_dict.get('Female').get('indian'), female_dict.get('Female') and female_dict.get('Female').get('malay'), female_dict.get('Female') and female_dict.get('Female').get('other'), female_dict.get('Female') and female_dict.get('Female').get('grand_total')   
        male_chinese, male_indian, male_malay, male_other, male_grand_total = male_dict.get('male') and male_dict.get('male').get('chinese'), male_dict.get('male') and male_dict.get('male').get('indian'), male_dict.get('male') and male_dict.get('male').get('malay'), male_dict.get('male') and male_dict.get('male').get('other'), male_dict.get('male') and male_dict.get('male').get('grand_total')   
        docargs = {
            'doc_ids': self._ids,
            'doc_model': model or 'student.student',
            'docs': self.env['student.student'].browse(1),
            'female_dict':female_dict,
            'male_dict':male_dict,
            'chinese_total': female_chinese or 0 + male_chinese or 0 ,
            'indian_total': female_indian or 0 + male_indian or 0 ,
            'malay_total': female_malay or 0 + male_malay or 0 ,
            'other_total': female_other or 0 + male_other or 0,
            'grand_total': female_grand_total or 0 + male_grand_total or 0 
        }
        return self.env['report'].render('atts_student_fields.report_student_race_enrolment', docargs)

