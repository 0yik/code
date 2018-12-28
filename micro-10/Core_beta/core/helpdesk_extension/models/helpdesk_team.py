# coding: utf-8

from odoo import api, fields, models
from xml.etree.ElementTree import fromstring, ElementTree, Element, tostring


class helpdesk_team(models.Model):
    _inherit = 'helpdesk.team'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(helpdesk_team, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                         submenu=submenu)
        if res.get('arch', False) and view_type == 'kanban':
            arch = fromstring(res.get('arch'))
            target = arch.findall(".//field[@name='unassigned_tickets']/../../../..")
            if target[0].tag == 'div' and target[0].attrib.get('class', '') == 'mb4':
                add_xml = self.parse_view_for_view()
                if add_xml:
                    for element in add_xml:
                        target[0].append(element)
                    res['arch'] = tostring(arch)
        return res

    @api.model
    def parse_view_for_view(self):
        ticket_obj = self.env['helpdesk.ticket']
        stage_obj = self.env['helpdesk.stage']
        team_action = self.env.ref('helpdesk.helpdesk_ticket_action_team').id
        team_ids = self.search([])
        xml_string = False
        res = []
        for team in team_ids:
            self._cr.execute("""select stage_id from helpdesk_ticket where team_id = %s"""%(team.id))
            stage_ids = []
            for x in set(self._cr.fetchall()):
                stage_ids.append(x[0])
            stages = stage_obj.browse(stage_ids).sorted(key=lambda r: r.name)
            xml_string = '<div t-if="record.id.raw_value == %s">' % (team.id)
            for stage in stages:
                count = len(ticket_obj.search([('team_id', '=', team.id),('stage_id','=', stage.id)]))
                if stage.id:
                    child_tag = """
                        <a name="%s" type="action" context="{'search_default_team_id': active_id, 'search_default_stage_id': %s}">
                            <div style="display: inline-block;">
                                <div style="display: inline-block;width:35px;">%s</div>
                                <div style="display: inline-block" >%s Tickets</div>
                            </div>
                        </a> """ % (team_action, stage.id, count, stage.name)
                    xml_string += child_tag
            xml_string += '</div>'
            res.append(fromstring(xml_string))
        return res if xml_string != [] else False
