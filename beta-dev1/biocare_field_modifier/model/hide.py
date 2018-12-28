from odoo import api, fields, models

class hide_hide(models.TransientModel):
    _name = 'hide.menu'

    @api.model
    def hide_menu(self):
        menu_obj = self.env['ir.ui.menu']
        # # TODO Project menu
        project_menu = menu_obj.search([('name','=','Project'),('parent_id','=',None)])
        project_menu.write({
              'active': False
          })

        link_menu = menu_obj.sudo().search([
            ('name','in',['Link Tracker', 'Timesheets',
                          'Module Board', 'Invoicing',
                          ]), ('parent_id','in', [False, None]),
             ('active', '=', True)])
        link_menu.write({
              'active': False
          })


        timesheet_profit = menu_obj.search(
            [('name','=','Timesheet Profit', ),
             ('parent_id.name','=', 'Reports')])

        timesheet_profit.write({
               'active': False
           })

        timesheet_mate = menu_obj.search(
            [('name','=','Time & Materials to Invoice'),
             ('parent_id.name','=', 'Invoicing')])

        timesheet_mate.write({
               'active': False
           })


        # # TODO Iventory menu
        # inventory_menu = menu_obj.search([('name','=','Inventory'),('parent_id','=',None)])
        #
        # inventory_control_menu = menu_obj.search([('name','=','Inventory Control'),('parent_id','=',inventory_menu.id)])
        #
        # #Hide Inventory Product
        #
        # inventory_product_menu = menu_obj.search([('name','=','Products'),('parent_id','=',inventory_control_menu.id)])
        # inventory_product_menu.write({
        #     'active': False
        # })
        #
        # #Hide Inventory Reordering Rules
        # inventory_reordering_rules_menu = menu_obj.search(
        #     [('name', '=', 'Reordering Rules'), ('parent_id', '=', inventory_control_menu.id)])
        # inventory_reordering_rules_menu.write({
        #     'active': False
        # })
        #
        # # Hide Inventory Inventory Adjustments
        # inventory_inventory_adjustments_menu = menu_obj.search(
        #     [('name', '=', 'Inventory Adjustments'), ('parent_id', '=', inventory_control_menu.id)])
        # inventory_inventory_adjustments_menu.write({
        #     'active': False
        # })
        #
        # # Hide Inventory Scrap
        # inventory_scrap_menu = menu_obj.search(
        #     [('name', '=', 'Scrap'), ('parent_id', '=', inventory_control_menu.id)])
        # inventory_scrap_menu.write({
        #     'active': False
        # })

        # TODO Invoicing menu
        #invoicing_menu = menu_obj.search([('name','=','Invoicing'),('parent_id','=', None)])
        #invoicing_menu.write({
        #    'active': False
        #})
