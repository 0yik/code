# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import collections
from collections import defaultdict



class HouseColorAlloocation(models.Model):
    _name = "house.color.allocation"
    _description = "House Color Allocation To All "

    house_color_line = fields.One2many('house.color.allocation.lines','house_color_allocation_id',string='House Color')

    @api.model 
    def default_get(self, fields):
        rec = super(HouseColorAlloocation, self).default_get(fields)
        print"=============",self.id
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')
        rec.update({
            'house_color_line':[(0, 0, {'house_color_id':active_id}) for active_id in active_ids]
        })
        return rec
    
    @api.multi
    def allocate_all(self):
        house_color_list=[]
        for line in self.house_color_line:
            house_color_list.append(line.house_color_id.id)
        print house_color_list
        #self.house_allocation_staff(house_color_list)
        self.house_allocation_student(house_color_list) 
    
    
    @api.multi
    def house_allocation_student(self,house_color_lst):
        
        house_color_ids=self.env["house.colour"].browse(house_color_lst)
        student_ids=self.env["student.student"].search([('state','=','done'),('state_custom','=','draft')])
        
        student_obj = self.env["student.line"]
        student_line_dict={}
        house_color_dictionary={}
        house_color_gender_dictionary={}
        house_color_list=[]
        house_color_dictionary_gender={}
        
        for student_id in student_ids:
            for house_color in house_color_ids:
                    #student_line_ids=self.env["student.student"].search([('house_color_id','=',house_color.id)])
                    count=0
                    for line in house_color.student_line:
                        if line:
                            count=count+1
                    student_line_dict[house_color.id]=count
            
            if len(house_color_ids) == 1:
                house_color_id=house_color_ids.id
                student_obj.create({'student_id':student_id.id,'house_color_id':house_color_id})
            else:
                for house_color in house_color_ids:
                    #student_line_ids=self.env["student.student"].search([('house_color_id','=',house_color.id)])
                    age_count=0
                    if house_color:
                        for line in house_color.student_line:
                            if line:
                                age=line.student_id.age
                                if age == student_id.age:
                                    age_count=age_count+1
                        print "------",house_color.id,house_color_dictionary
                        house_color_dictionary[house_color.id]=age_count
                        print "---++++++---",house_color.id,house_color_dictionary
                sort_dic = {}
                for i in sorted(house_color_dictionary):
                    sort_dic.update({i:house_color_dictionary[i]})
                house_color_dictionary=sort_dic
                if house_color_dictionary:
                    noline=min(house_color_dictionary, key=house_color_dictionary.get)
                    if house_color_dictionary.get(noline)== 0:
                        student_obj.create({'student_id':student_id.id,'house_color_id':noline})
                    else:
                        first_shaders_dict = {}
                        duplicate_shaders_dict = {}
                        inverse_dict = defaultdict(list)
                        for k,v in house_color_dictionary.iteritems():
                            inverse_dict[v].append(k)
                        for v, ks in inverse_dict.iteritems():
                            if len(ks)> 1:
                                first, rest = ks[0], ks[0:]
                                first_shaders_dict[first] = v
                                for r in rest:
                                    duplicate_shaders_dict[r] = v
                            if len(ks)> 1:
                                first, rest = ks[0], ks[1:]
                                first_shaders_dict[first] = v
                                for r in rest:
                                    duplicate_shaders_dict[r] = v
                        print first_shaders_dict,"\n\n\n",duplicate_shaders_dict
                        if duplicate_shaders_dict:
                            house_color_minimum_duplicate=min(duplicate_shaders_dict, key=duplicate_shaders_dict.get)
                        else:
                            house_color_minimum_duplicate=-1
                        house_color_minimum_student=min(house_color_dictionary, key=house_color_dictionary.get)
                        if house_color_dictionary.get(house_color_minimum_student) < duplicate_shaders_dict.get(house_color_minimum_duplicate or -1 ):
                            house_color_minimum_student=min(house_color_dictionary, key=house_color_dictionary.get)
                            student_obj.create({'student_id':student_id.id,'house_color_id':house_color_minimum_student})
                        elif duplicate_shaders_dict:
                            for key,value in duplicate_shaders_dict.iteritems():
                                house_color_list.append(key)
                            if house_color_list:
                                for house_color_duplicate in self.env["house.colour"].browse(house_color_list):
                                    male_count=0
                                    female_count=0
                                    for line in house_color_duplicate.student_line:
                                        if line:
                                            gender=line.student_id.gender
                                            if gender == 'male':
                                                male_count=male_count+1
                                            elif gender == 'female':
                                                female_count=female_count+1
                                    house_color_gender_dictionary['male_count']=male_count
                                    house_color_gender_dictionary['female_count']=female_count
                                    house_color_dictionary_gender[house_color_duplicate.id]=house_color_gender_dictionary
                            if house_color_dictionary_gender:
                                minimum_male_countmin=min(house_color_dictionary_gender.keys(), key=lambda k, a=house_color_dictionary_gender: a[k]['male_count'])
                                minimum_female_countmin=min(house_color_dictionary_gender.keys(), key=lambda k, a=house_color_dictionary_gender: a[k]['female_count'])       
                                if student_id.gender == 'male':
                                    student_obj.create({'student_id':student_id.id,'house_color_id':minimum_male_countmin})
                                elif student_id.gender == 'female':
                                    student_obj.create({'student_id':student_id.id,'house_color_id':minimum_female_countmin})
                        elif not duplicate_shaders_dict:
                            for key,value in house_color_dictionary.iteritems():
                                house_color_list.append(key)
                            if house_color_list:
                                for house_color_dict in self.env["house.colour"].browse(house_color_list):
                                    male_count=0
                                    female_count=0
                                    for line in house_color_dict.student_line:
                                        if line:
                                            gender=line.student_id.gender
                                            if gender == 'male':
                                                male_count=male_count+1
                                            elif gender == 'female':
                                                female_count=female_count+1
                                    house_color_gender_dictionary['male_count']=male_count
                                    house_color_gender_dictionary['female_count']=female_count
                                    house_color_dictionary_gender[house_color_dict.id]=house_color_gender_dictionary
                            if house_color_dictionary_gender:
                                minimum_male_countmin=min(house_color_dictionary_gender.keys(), key=lambda k, a=house_color_dictionary_gender: a[k]['male_count'])
                                minimum_female_countmin=min(house_color_dictionary_gender.keys(), key=lambda k, a=house_color_dictionary_gender: a[k]['female_count'])       
                                if student_id.gender == 'male':
                                    student_obj.create({'student_id':student_id.id,'house_color_id':minimum_male_countmin})
                                elif student_id.gender == 'female':
                                    student_obj.create({'student_id':student_id.id,'house_color_id':minimum_female_countmin})
                        else:
                            minline=noline=min(student_line_dict, key=student_line_dict.get)
                            student_obj.create({'student_id':student_id.id,'house_color_id':minline})   
    
    
    @api.multi
    def house_allocation_staff(self,house_color_lst):

        house_color_ids=self.env["house.colour"].browse(house_color_lst)
        employee_ids=self.env["hr.employee"].search([])
        
        employee_obj = self.env["hr.employee.line"]
        house_color_obj=self.env["house.colour"]
        for employee_id in employee_ids:
            house_color_dictionary={}
            house_color_gender_dictionary={}
            house_color_list=[]
            house_color_dictionary_gender={}
            staff_line_dict={}
            
            
            for house_color in house_color_ids:
                #student_line_ids=self.env["student.student"].search([('house_color_id','=',house_color.id)])
                count=0
                for line in house_color.employee_line:
                    if line:
                        count=count+1
                staff_line_dict[house_color.id]=count
            
            if len(house_color_ids) == 1:
                house_color_id=house_color_ids.id
                obj=house_color_obj.browse(house_color_id)
                employee_obj.create({'employee_id':employee_id.id,'house_color_id':house_color_id})
                self.env["house.color.history"].create({'staff_id':employee_id.id,'house_color':obj.name,'start_date':obj.start_date,'end_date':obj.end_date})
            else:
                for house_color in house_color_ids:
                    #student_line_ids=self.env["student.student"].search([('house_color_id','=',house_color.id)])
                    age_count=0
                    for line in house_color.employee_line:
                        if line:
                            age=line.employee_id.age
                            if age == employee_id.age:
                                age_count=age_count+1
                    house_color_dictionary[house_color.id]=age_count
                if house_color_dictionary:
                    noline=min(house_color_dictionary, key=house_color_dictionary.get)
                    if house_color_dictionary.get(noline)== 0:
                        obj=house_color_obj.browse(noline)
                        employee_obj.create({'employee_id':employee_id.id,'house_color_id':noline})
                        self.env["house.color.history"].create({'staff_id':employee_id.id,'house_color':obj.name,'start_date':obj.start_date,'end_date':obj.end_date})
                    else:
                        first_shaders_dict = {}
                        duplicate_shaders_dict = {}
                        inverse_dict = defaultdict(list)
                        for k,v in house_color_dictionary.iteritems():
                            inverse_dict[v].append(k)
                        for v, ks in inverse_dict.iteritems():
                            if len(ks)> 1:
                                first, rest = ks[0], ks[0:]
                                first_shaders_dict[first] = v
                                for r in rest:
                                    duplicate_shaders_dict[r] = v
                            if len(ks)> 1:
                                first, rest = ks[0], ks[1:]
                                first_shaders_dict[first] = v
                                for r in rest:
                                    duplicate_shaders_dict[r] = v
                        if duplicate_shaders_dict:
                            house_color_minimum_duplicate=min(duplicate_shaders_dict, key=duplicate_shaders_dict.get)
                        else:
                            house_color_minimum_duplicate=-1
                        house_color_minimum_employee=min(house_color_dictionary, key=house_color_dictionary.get)
                        if house_color_dictionary.get(house_color_minimum_employee) < duplicate_shaders_dict.get(house_color_minimum_duplicate):
                            house_color_minimum_employee=min(house_color_dictionary, key=house_color_dictionary.get)
                            obj=house_color_obj.browse(house_color_minimum_employee)
                            employee_obj.create({'employee_id':employee_id.id,'house_color_id':house_color_minimum_employee})
                            self.env["house.color.history"].create({'staff_id':employee_id.id,'house_color':obj.name,'start_date':obj.start_date,'end_date':obj.end_date})
                        elif duplicate_shaders_dict:
                            for key,value in duplicate_shaders_dict.iteritems():
                                house_color_list.append(key)
                            for house_color_duplicate in self.env["house.colour"].browse(house_color_list):
                                male_count=0
                                female_count=0
                                for line in house_color_duplicate.employee_line:
                                    if line:
                                        gender=line.employee_id.gender
                                        if gender == 'male':
                                            male_count=male_count+1
                                        elif gender == 'female':
                                            female_count=female_count+1
                                house_color_gender_dictionary['male_count']=male_count
                                house_color_gender_dictionary['female_count']=female_count
                                house_color_dictionary_gender[house_color_duplicate.id]=house_color_gender_dictionary
                            if house_color_dictionary_gender:
                                minimum_male_countmin=min(house_color_dictionary_gender.keys(), key=lambda k, a=house_color_dictionary_gender: a[k]['male_count'])
                                minimum_female_countmin=min(house_color_dictionary_gender.keys(), key=lambda k, a=house_color_dictionary_gender: a[k]['female_count'])       
                                if employee_id.gender == 'male':
                                    obj=house_color_obj.browse(minimum_male_countmin)
                                    employee_obj.create({'employee_id':employee_id.id,'house_color_id':minimum_male_countmin})
                                    self.env["house.color.history"].create({'staff_id':employee_id.id,'house_color':obj.name,'start_date':obj.start_date,'end_date':obj.end_date})
                                elif employee_id.gender == 'female':
                                    obj=house_color_obj.browse(minimum_female_countmin)
                                    employee_obj.create({'employee_id':employee_id.id,'house_color_id':minimum_female_countmin})
                                    self.env["house.color.history"].create({'staff_id':employee_id.id,'house_color':obj.name,'start_date':obj.start_date,'end_date':obj.end_date})
                        elif not duplicate_shaders_dict:
                            for key,value in house_color_dictionary.iteritems():
                                house_color_list.append(key)
                            for house_color_duplicate in self.env["house.colour"].browse(house_color_list):
                                male_count=0
                                female_count=0
                                for line in house_color_duplicate.employee_line:
                                    if line:
                                        gender=line.employee_id.gender
                                        if gender == 'male':
                                            male_count=male_count+1
                                        elif gender == 'female':
                                            female_count=female_count+1
                                house_color_gender_dictionary['male_count']=male_count
                                house_color_gender_dictionary['female_count']=female_count
                                house_color_dictionary_gender[house_color_duplicate.id]=house_color_gender_dictionary
                            if house_color_dictionary_gender:
                                minimum_male_countmin=min(house_color_dictionary_gender.keys(), key=lambda k, a=house_color_dictionary_gender: a[k]['male_count'])
                                minimum_female_countmin=min(house_color_dictionary_gender.keys(), key=lambda k, a=house_color_dictionary_gender: a[k]['female_count'])       
                                if employee_id.gender == 'male':
                                    obj=house_color_obj.browse(minimum_male_countmin)
                                    employee_obj.create({'employee_id':employee_id.id,'house_color_id':minimum_male_countmin})
                                    self.env["house.color.history"].create({'staff_id':employee_id.id,'house_color':obj.name,'start_date':obj.start_date,'end_date':obj.end_date})
                                elif employee_id.gender == 'female':
                                    obj=house_color_obj.browse(minimum_female_countmin)
                                    employee_obj.create({'employee_id':employee_id.id,'house_color_id':minimum_female_countmin})
                                    self.env["house.color.history"].create({'staff_id':employee_id.id,'house_color':obj.name,'start_date':obj.start_date,'end_date':obj.end_date})
                        
                        else:
                            minline=noline=min(staff_line_dict, key=staff_line_dict.get)
                            obj=house_color_obj.browse(minline)
                            employee_obj.create({'employee_id':employee_id.id,'house_color_id':minline})
                            self.env["house.color.history"].create({'staff_id':employee_id.id,'house_color':obj.name,'start_date':obj.start_date,'end_date':obj.end_date})


# class HouseColorAlloocationLine(models.Model):
#     _name = "house.color.allocation.lines"
#     _description = "House Color Allocation To All Line"
# 
#     house_color_allocation_id = fields.Many2one("house.color.allocation","House Color")
#     house_color_id = fields.Many2one("house.colour","House Color")
    
    
    