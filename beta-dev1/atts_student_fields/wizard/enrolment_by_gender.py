# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import collections


class enrolment_by_gender(models.TransientModel):
    _name = "enrolment.by.gender"
    _description = "Enrolment By Gender"

    enrolment_date = fields.Date("Enrolment Date")
    
    
    def _print_report(self, data):
        return self.env['report'].get_action(self, 'atts_student_fields.enrolment_by_gender_report_temp', data=data)
    
    
    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['enrolment_date'] = self.enrolment_date
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['enrolment_date'])[0]
        return self._print_report(data)



class enrolment_by_gender_report(models.AbstractModel):
    _name = 'report.atts_student_fields.enrolment_by_gender_report_temp'
    
    @api.multi
    def create_date_of_birth_year(self, enrolment_date):
        if enrolment_date:
            enrolment_year = enrolment_date.split("-")[0]
            birth_year = int(enrolment_year) - 7
            year_list = []
            for year in range(12):
                year_list.append(birth_year)
                birth_year = birth_year - 1
            return year_list
    
    @api.multi
    def _enrolment_by_gender_cal(self, data):
        
        students = self.env["student.student"].search([('state_custom','=','draft')])
        if students:
            year_list = self.create_date_of_birth_year(data.get("enrolment_date"))
            com_dictionary = {}
            total_dictionary = {}
            year_dictionary = {}
            grand_total_am = 0
            grand_total_pm = 0
            total_of_grand_total = 0
           
            for student in students:
                data = {}
                male_count_am = 0
                male_count_pm = 0
                female_count_am = 0
                female_count_pm = 0
                count_am = 0
                count_pm = 0
                date_of_birt = student.date_of_birth
                if date_of_birt:
                    year = date_of_birt.split("-")[0]
                    if int(year) in year_list:
                        if str(year) not in year_dictionary:
                            session = student.session
                            gender = student.gender
                            if gender:
                                if gender == 'male':
                                    if session == 'am':
                                        count_am = count_am + 1
                                        male_count_am = male_count_am + 1
                                    elif session == 'pm':
                                        count_pm = count_pm + 1
                                        male_count_pm = male_count_pm + 1
                                elif gender == 'female':
                                    if session == 'am':
                                        count_am = count_am + 1
                                        female_count_am = female_count_am + 1
                                    elif session == 'pm':
                                        count_pm = count_pm + 1
                                        female_count_pm = female_count_pm + 1
                            
                                data["male_count_am"] = male_count_am
                                data["total_male_count"] = male_count_am + male_count_pm
                                data["total_female_count"] = female_count_pm + female_count_am
                                data["total_count_am"] = male_count_am + female_count_am
                                data["total_count_pm"] = female_count_pm + male_count_pm
                                data["male_count_pm"] = male_count_pm
                                data["female_count_pm"] = female_count_pm
                                data["female_count_am"] = female_count_am
                                data["count_am"] = count_am
                                data["count_pm"] = count_pm
                                data["grand_total"] = female_count_pm + male_count_pm + male_count_am + female_count_am
                                year_dictionary[year] = data.copy()
                        else:
                            session = student.session
                            gender = student.gender
                            if gender:
                                if gender == 'male':
                                    if session == 'am':
                                        count_am = count_am + 1
                                        male_count_am = male_count_am + 1
                                        year_dictionary[year]["male_count_am"] = int(year_dictionary[year]["male_count_am"]) + male_count_am
                                    elif session == 'pm':
                                        count_pm = count_pm + 1
                                        male_count_pm = male_count_pm + 1
                                        year_dictionary[year]["male_count_pm"] = int(year_dictionary[year]["male_count_pm"]) + male_count_pm
                                elif gender == 'female':
                                    if session == 'am':
                                        count_am = count_am + 1
                                        female_count_am = female_count_am + 1
                                        year_dictionary[year]["female_count_am"] = int(year_dictionary[year]["female_count_am"]) + female_count_am
                                    elif session == 'pm':
                                        count_pm = count_pm + 1
                                        female_count_pm = female_count_pm + 1
                                        year_dictionary[year]["female_count_pm"] = int(year_dictionary[year]["female_count_pm"]) + female_count_pm
                            
                                year_dictionary[year]["total_male_count"] = int(year_dictionary[year]["total_male_count"]) + male_count_am + male_count_pm
                                year_dictionary[year]["total_female_count"] = int(year_dictionary[year]["total_female_count"]) + female_count_pm + female_count_am
                                year_dictionary[year]["total_count_am"] = int(year_dictionary[year]["total_count_am"]) + male_count_am + female_count_am
                                year_dictionary[year]["total_count_pm"] = int(year_dictionary[year]["total_count_pm"]) + female_count_pm + male_count_pm
                                year_dictionary[year]["count_am"] = count_am
                                year_dictionary[year]["count_pm"] = count_pm
                                year_dictionary[year]["grand_total"] = int(year_dictionary[year]["grand_total"]) + female_count_pm + male_count_pm + male_count_am + female_count_am
            for total in year_dictionary:
                if year_dictionary.get(total):
                    total_count_am = year_dictionary.get(total).get('total_count_am')
                    total_count_pm = year_dictionary.get(total).get('total_count_pm')
                    grand_total = year_dictionary.get(total).get('grand_total')
                    grand_total_am = grand_total_am + total_count_am
                    grand_total_pm = grand_total_pm + total_count_pm
                    total_of_grand_total = total_of_grand_total + grand_total
            total_dictionary["grand_total_am"] = grand_total_am
            total_dictionary["grand_total_pm"] = grand_total_pm
            total_dictionary["total_of_grand_total"] = total_of_grand_total
            for birth_year in year_list:
                if str(birth_year) in year_dictionary.keys():
                    pass
                else:
                    year_dictionary[str(birth_year)] = {}
            year_dictionary = SortedDisplayDict(year_dictionary)
            com_dictionary["year_dictionary"] = SortedDisplayDict(year_dictionary)
            com_dictionary["total_dictionary"] = total_dictionary
            year_dictionary = SortedDisplayDict(com_dictionary)
            dict_type = com_dictionary.get('year_dictionary')
            com_dictionary['year_dictionary'] = collections.OrderedDict(sorted(dict_type.items()))
            return com_dictionary
        else:
            return {'year_dictionary':{},'total_dictionary':{}}

    @api.multi
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env['student.student'].browse(self.env.context.get('active_ids', []))
        student_obj = self.env['student.student']
        student_search_obj = student_obj.search([])
        model = self.env.context.get('active_model')
        enrolment_by_gender_cal = self._enrolment_by_gender_cal(data)
        docargs = {
            'doc_ids': self._ids,
            'doc_model': model or 'student.student',
            'docs': self.env['student.student'].browse(1),
            'enrolment_by_gender_cal':enrolment_by_gender_cal,
        }
        return self.env['report'].render('atts_student_fields.enrolment_by_gender_report_temp', docargs)




class SortedDisplayDict(dict):
    def __str__(self):
        return "{" + ", ".join("%r: %r" % (key, self[key]) for key in sorted(self)) + "}"


