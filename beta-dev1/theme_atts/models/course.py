# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api, tools
from odoo.tools import image

class SubjectSubject(models.Model):
    _inherit = "subject.subject"

    image = fields.Binary('Image', attachment=True)
    image_medium = fields.Binary('Medium', compute="_get_image", store=True, attachment=True)
    image_thumb = fields.Binary('Thumbnail', compute="_get_image", store=True, attachment=True)

    @api.depends('image')
    def _get_image(self):
        for record in self:
            if record.image:
                record.image_medium = image.crop_image(record.image, type='top', ratio=(4, 3), thumbnail_ratio=4)
                record.image_thumb = image.crop_image(record.image, type='top', ratio=(4, 3), thumbnail_ratio=6)
            else:
                record.image_medium = False
                record.iamge_thumb = False

    description = fields.Text(
        'Description', translate=True,
        help="A precise description of the Course, used only for internal information purposes.")
    is_popular = fields.Boolean("Popular Course", default=False)
    is_footer = fields.Boolean("Show in Footer", default=False)

    @api.model
    def create(self, vals):
        res = super(SubjectSubject, self).create(vals)
        res.onchage_courcse_set_menu()
        return res

    @api.onchange('course_level','industry_level')
    def onchage_courcse_set_menu(self):
        course = industry = ''
        for course_level_id in self.env['course.level'].sudo().search([]):
            course += '<li class="menu-item"><a href="/course/level/%s">%s</a></li>' % (course_level_id.id, course_level_id.name)
        for industry_id in self.env['course.industry'].sudo().search([]):
            industry += '<li class="menu-item"><a href="/industry/%s">%s</a></li>' % (industry_id.id, industry_id.name)
        menu_content = """
                <div class="mega-dropdown-custome">
                    <div class="row">
                        <div class="mega-col-nav col-sm-4">
                            <div class="mega-inner">
                                <ul class="mega-nav">
                                    <li class="menu-item group"><a href="#">By Course Type</a></li>
                                    <li class="menu-item"><a href="/course/0">All Courses</a></li>
                                    """ + course + """
                                    <t t-call="theme_atts.aa"/>
                                </ul>
                            </div>
                        </div>
                        <div class="mega-col-nav col-sm-4">
                            <div class="mega-inner">
                                <ul class="mega-nav">
                                    <li class="menu-item group"><a href="#">By Industry</a></li>
                                    <li class="menu-item"><a href="/industry/0">All Courses</a></li>
                                    """ + industry + """
                                </ul>
                            </div>
                        </div>
                        <div class="mega-col-nav col-sm-4 image-class">
                            <div class="mega-inner">
                                <ul class="mega-nav">
                                    <li class="menu-item">
                                        <div class="mod-content" align="left">
                                            <p><img src="/theme_atts/static/src/img/find_a_course_mega_menu.jpg" alt="Ceramics" style="width: 250px; height:200px;"></p>
                                        </div>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
        """
        self.env.ref('theme_atts.mega_menu_course').write({'menu_content': menu_content})


class Class(models.Model):
    _inherit = 'class.class'

    class_schedule = fields.Char('Class Schedule', compute='_get_class_schedule')

    def _get_class_schedule(self):
        for c in self:
            date_start = ''
            class_schedule = ''
            if c.date_start:
                date_start = datetime.strptime(c.date_start, tools.DEFAULT_SERVER_DATE_FORMAT)
                class_schedule += date_start.strftime('%d') +' '+ date_start.strftime('%b') +' '+ date_start.strftime('%Y')
            if c.date_end:
                date_end = datetime.strptime(c.date_end, tools.DEFAULT_SERVER_DATE_FORMAT)
                if date_start:
                    class_schedule += ' - '
                class_schedule += date_end.strftime('%d') +' '+ date_end.strftime('%b') +' '+ date_end.strftime('%Y')
            class_schedule += '   '+ '{0:02.0f}:{1:02.0f}'.format(*divmod(c.time_start * 60, 60)) + '-' + '{0:02.0f}:{1:02.0f}'.format(*divmod(c.time_end * 60, 60))
            c.class_schedule = class_schedule
