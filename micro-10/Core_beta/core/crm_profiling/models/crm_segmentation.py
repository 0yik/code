# -*- coding: utf-8 -*-

from odoo import models, fields, api

class crm_segmentation(models.Model):
    '''
        A segmentation is a tool to automatically assign categories on partners.
        These assignations are based on criterions.
    '''
    _name = 'crm.segmentation'
    _description = 'Partner Segmentation'

    name = fields.Char('Name', required=True, help='The name of the segmentation.')
    description = fields.Text('Description')
    categ_id = fields.Many2one('res.partner.category', 'Partner Category',\
                         required=True, help='The partner category that will be \
added to partners that match the segmentation criterions after computation.')
    exclusif =  fields.Boolean('Exclusive', help='Check if the category is limited to partners that match the segmentation criterions.\
                        \nIf checked, remove the category from partners that doesn\'t match segmentation criterions')
    state = fields.Selection([('not_running','Not Running'),\
                    ('running','Running')], 'Execution Status', readonly=True, default='not_running')
    partner_id = fields.Integer('Max Partner ID processed', default=0)
    segmentation_line = fields.One2many('crm.segmentation.line', \
                            'segmentation_id', 'Criteria', required=True, copy=True)
    sales_purchase_active = fields.Boolean('Use The Sales Purchase Rules', help='Check if you want to use this tab as part of the segmentation rule. If not checked, the criteria beneath will be ignored')

    @api.multi
    def process_continue(self, start=False):

        partner_obj = self.env.get('res.partner')
        categs = self.read(['categ_id', 'exclusif', 'partner_id', 'sales_purchase_active', 'profiling_active'])
        for categ in categs:
            if start:
                if categ['exclusif']:
                    self._cr.execute('DELETE FROM res_partner_res_partner_category_rel WHERE \
                                category_id IN %s', (categ['categ_id'],))
                    partner_obj.invalidate_cache(['category_id'])
            id = categ['id']

            self._cr.execute('select id from res_partner order by id ')
            partners = [x[0] for x in self._cr.fetchall()]

            if categ['sales_purchase_active']:
                to_remove_list = []
                self._cr.execute('select id from crm_segmentation_line where segmentation_id=%s', (id,))
                line_ids = [x[0] for x in self._cr.fetchall()]

                for pid in partners:
                    lines = self.env.get('crm.segmentation.line').browse(line_ids)
                    if (not lines.test(pid)):
                        to_remove_list.append(pid)
                for pid in to_remove_list:
                    partners.remove(pid)

            if categ['profiling_active']:
                to_remove_list = []
                for pid in partners:

                    self._cr.execute('select distinct(answer) from partner_question_rel where partner=%s', (pid,))
                    answers_ids = [x[0] for x in self._cr.fetchall()]

                    if (not self.test_prof(pid, answers_ids)):
                        to_remove_list.append(pid)
                for pid in to_remove_list:
                    partners.remove(pid)

            for partner in partner_obj.browse(partners):
                category_ids = [categ_id.id for categ_id in partner.category_id]
                if categ['categ_id'][0] not in category_ids:
                    self._cr.execute(
                        'insert into res_partner_res_partner_category_rel (category_id,partner_id) values (%s,%s)',
                        (categ['categ_id'][0], partner.id))
                    partner_obj.invalidate_cache(['category_id'], [partner.id])

        self.write({'state': 'not running', 'partner_id': 0})

    @api.multi
    def process_stop(self):

        """ @param self: The object pointer
            @param cr: the current row, from the database cursor,
            @param uid: the current user’s ID for security checks,
            @param ids: List of Process stop’s IDs"""

        return self.write({'state':'not running', 'partner_id':0})

    @api.multi
    def process_start(self):

        """ @param self: The object pointer
            @param cr: the current row, from the database cursor,
            @param uid: the current user’s ID for security checks,
            @param ids: List of Process start’s IDs """

        self.write({'state':'running', 'partner_id':0})
        return self.process_continue(start=True)

class crm_segmentation_line(models.Model):
    """ Segmentation line """
    _name = 'crm.segmentation.line'
    _description = 'Segmentation line'

    name = fields.Char('Rule Name', required=True)
    segmentation_id = fields.Many2one('crm.segmentation', 'Segmentation')
    expr_name = fields.Selection([('sale','Sale Amount'),
                        ('purchase','Purchase Amount')], 'Control Variable', required=True, default='sale')
    expr_operator = fields.Selection([('<','<'),('=','='),('>','>')], 'Operator', required=True, default='>')
    expr_value = fields.Float('Value', required=True)
    operator = fields.Selection([('and','Mandatory Expression'),\
                        ('or','Optional Expression')],'Mandatory / Optional', required=True, default='and')

    @api.multi
    def test(self, partner_id):

        """ @param self: The object pointer
            @param cr: the current row, from the database cursor,
            @param uid: the current user’s ID for security checks,
            @param ids: List of Test’s IDs """

        expression = {'<': lambda x,y: x<y, '=':lambda x,y:x==y, '>':lambda x,y:x>y}
        ok = False
        for l in self:
            self._cr.execute('select * from ir_module_module where name=%s and state=%s', ('account','installed'))
            if self._cr.fetchone():
                if l['expr_name']=='sale':
                    self._cr.execute('SELECT SUM(l.price_unit * l.quantity) ' \
                            'FROM account_invoice_line l, account_invoice i ' \
                            'WHERE (l.invoice_id = i.id) ' \
                                'AND i.partner_id = %s '\
                                'AND i.type = \'out_invoice\'',
                            (partner_id,))
                    value = self._cr.fetchone()[0] or 0.0
                    self._cr.execute('SELECT SUM(l.price_unit * l.quantity) ' \
                            'FROM account_invoice_line l, account_invoice i ' \
                            'WHERE (l.invoice_id = i.id) ' \
                                'AND i.partner_id = %s '\
                                'AND i.type = \'out_refund\'',
                            (partner_id,))
                    value -= self._cr.fetchone()[0] or 0.0
                elif l['expr_name']=='purchase':
                    self._cr.execute('SELECT SUM(l.price_unit * l.quantity) ' \
                            'FROM account_invoice_line l, account_invoice i ' \
                            'WHERE (l.invoice_id = i.id) ' \
                                'AND i.partner_id = %s '\
                                'AND i.type = \'in_invoice\'',
                            (partner_id,))
                    value = self._cr.fetchone()[0] or 0.0
                    self._cr.execute('SELECT SUM(l.price_unit * l.quantity) ' \
                            'FROM account_invoice_line l, account_invoice i ' \
                            'WHERE (l.invoice_id = i.id) ' \
                                'AND i.partner_id = %s '\
                                'AND i.type = \'in_refund\'',
                            (partner_id,))
                    value -= self._cr.fetchone()[0] or 0.0
                res = expression[l['expr_operator']](value, l['expr_value'])
                if (not res) and (l['operator']=='and'):
                    return False
                if res:
                    return True
        return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: