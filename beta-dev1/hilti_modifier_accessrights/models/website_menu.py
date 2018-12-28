from odoo import models, api, fields, SUPERUSER_ID

class websiteMenus(models.Model):

    _inherit = 'website.menu'

    group_id = fields.Many2many('res.groups', string="Groups")

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        menus = super(websiteMenus, self).search( args, offset=offset, limit=limit, order=order, count=count)
        if self._uid != SUPERUSER_ID:
            if ('backend_menu' in self._context and not self._context.get('backend_menu')) or ('backend_menu' not in self._context):
                user_group = self.env["res.users"].browse(self._uid).groups_id
                new_menu = []
                for menu in menus:
                    menu_group = menu.group_id
                    if not(menu_group and menu_group & user_group):
                        new_menu.append(menu.id)
                return self.browse(new_menu)
        return menus