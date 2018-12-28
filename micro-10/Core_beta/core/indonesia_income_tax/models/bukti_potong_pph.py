from odoo import models, fields, api, SUPERUSER_ID
from datetime import datetime
from odoo.exceptions import Warning as UserError
from odoo.tools.translate import _


class BuktiPotongPPh(models.Model):
    _name = "l10n_id.bukti_potong_pph"
    _inherit = ["mail.thread"]
    _description = "Bukti Potong PPh"

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id.id

    @api.model
    def _default_type_id(self):
        return False

    @api.model
    def _default_wajib_pajak_id(self):
        obj_type = self.env["l10n_id.bukti_potong_pph_type"]
        type_id = self._default_type_id()
        if not type_id:
            return False
        direction = obj_type.browse(type_id)[0].direction
        if direction == "in":
            return self.env.user.company_id.partner_id.id
        else:
            return False

    @api.model
    def _default_pemotong_pajak_id(self):
        obj_type = self.env["l10n_id.bukti_potong_pph_type"]
        type_id = self._default_type_id()
        if not type_id:
            return False
        direction = obj_type.browse(type_id)[0].direction
        if direction == "out":
            return self.env.user.company_id.partner_id.id
        else:
            return False

    @api.model
    def _default_date(self):
        return datetime.now().strftime("%Y-%m-%d")

    @api.multi
    @api.depends(
        "line_ids",
        "line_ids.amount_tax",
    )
    def _compute_tax(self):
        for bukpot in self:
            bukpot.total_tax = 0.0
            for line in bukpot.line_ids:
                bukpot.total_tax += line.amount_tax

    @api.multi
    @api.depends(
        "type_id",
        "type_id.journal_ids"
    )
    def _compute_allowed_journal(self):
        obj_journal = self.env["account.journal"]
        for bukpot in self:
            if bukpot.type_id.journal_ids:
                bukpot.allowed_journal_ids = bukpot.type_id.journal_ids
            else:
                criteria = [
                    ("type", "=", "closed"),
                ]
                bukpot.allowed_journal_ids = obj_journal.search(criteria)

    @api.multi
    @api.depends(
        "type_id",
        "type_id.account_ids",
    )
    def _compute_allowed_account(self):
        obj_account = self.env["account.account"]
        for bukpot in self:
            if bukpot.type_id.account_ids:
                bukpot.allowed_account_ids = bukpot.type_id.account_ids
            # else:
            #     criteria = [
            #         ("type", "not in", [
            #          "view", "liquidity", "consolidation", "closed"]),
            #     ]
            #     bukpot.allowed_account_ids = obj_account.search(criteria)

    @api.multi
    @api.depends(
        "type_id",
    )
    def _compute_allowed_tax_code(self):
        obj_code = self.env["account.tax"]
        for bukpot in self:
            if bukpot.type_id.tax_code_ids:
                bukpot.allowed_tax_code_ids = bukpot.type_id.tax_code_ids
            else:
                criteria = []
                bukpot.allowed_tax_code_ids = obj_code.search(criteria)

    @api.multi
    @api.depends(
        "type_id",
    )
    def _compute_allowed_base_code(self):
        obj_code = self.env["account.tax"]
        for bukpot in self:
            if bukpot.type_id.base_code_ids:
                bukpot.allowed_base_code_ids = bukpot.type_id.base_code_ids
            else:
                criteria = []
                bukpot.allowed_base_code_ids = obj_code.search(criteria)

    @api.multi
    @api.depends(
        "type_id",
    )
    def _compute_allowed_tax(self):
        obj_code = self.env["account.tax"]
        for bukpot in self:
            if bukpot.type_id.tax_ids:
                bukpot.allowed_tax_ids = bukpot.type_id.tax_ids
            else:
                criteria = []
                bukpot.allowed_tax_ids = obj_code.search(criteria)

    @api.multi
    @api.depends(
        "state",
        "type_id.allow_confirm_group_ids",
        "type_id.allow_approve_group_ids",
        "type_id.allow_cancel_group_ids",
        "type_id.allow_reset_group_ids",
    )
    def _compute_policy(self):
        for bukpot in self:
            if self.env.user.id == SUPERUSER_ID:
                bukpot.confirm_ok = bukpot.approve_ok = bukpot.cancel_ok = \
                    bukpot.reset_ok = True
                continue

            bukpot_type = bukpot.type_id

            bukpot.confirm_ok = self._get_button_policy(
                bukpot_type, "confirm")
            bukpot.approve_ok = self._get_button_policy(
                bukpot_type, "approve")
            bukpot.cancel_ok = self._get_button_policy(
                bukpot_type, "cancel")
            bukpot.reset_ok = self._get_button_policy(
                bukpot_type, "reset")

    name = fields.Char(
        string="# Bukti Potong",
        required=True,
        default="/",
        copy=False,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        }
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
        default=lambda self: self._default_company_id(),
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        }
    )
    direction = fields.Selection(
        string="Type",
        selection=[
            ("in", "In"),
            ("out", "Out"),
        ],
        related="type_id.direction",
        store=False,
        readonly=True,
    )
    type_id = fields.Many2one(
        string="Form Type",
        comodel_name="l10n_id.bukti_potong_pph_type",
        ondelete="restrict",
        required=True,
        readonly=True,
    )
    allowed_journal_ids = fields.Many2many(
        string="Allowed Journals",
        comodel_name="account.journal",
        compute="_compute_allowed_journal",
        store=False,
    )
    allowed_tax_code_ids = fields.Many2many(
        string="Allowed Tax Code",
        comodel_name="account.tax",
        compute="_compute_allowed_tax_code",
        store=False,
    )
    allowed_base_code_ids = fields.Many2many(
        string="Allowed Base Code",
        comodel_name="account.tax",
        compute="_compute_allowed_base_code",
        store=False,
    )
    allowed_tax_ids = fields.Many2many(
        string="Allowed Tax",
        comodel_name="account.tax",
        compute="_compute_allowed_tax",
        store=False,
    )
    allowed_account_ids = fields.Many2many(
        string="Allowed Accounts",
        comodel_name="account.account",
        compute="_compute_allowed_account",
        store=False,
    )
    date = fields.Date(
        string="Date",
        required=True,
        default=lambda self: self._default_date(),
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        }
    )

    @api.multi
    @api.depends(
        "date",
    )
    def _compute_tax_period(self):
        obj_tax_period = self.env["l10n_id.tax_period"]
        for bukpot in self:
            try:
                bukpot.tax_period_id = obj_tax_period._find_period(bukpot.date)
            except:
                bukpot.tax_period_id = False

    tax_period_id = fields.Many2one(
        string="Tax Period",
        comodel_name="l10n_id.tax_period",
        compute="_compute_tax_period",
        store=True,
    )
    period_id = fields.Many2one(
        string="Period",
        comodel_name="l10n_id.tax_period",
        required=True,
        readonly=True,
        ondelete="restrict",
        states={
            "draft": [
                ("readonly", False),
            ],
        }
    )
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        }
    )
    account_id = fields.Many2one(
        string="Account",
        comodel_name="account.account",
        required=True,
        readonly=True,
        ondelete="restrict",
        states={
            "draft": [
                ("readonly", False),
            ],
        }
    )
    kpp_id = fields.Many2one(
        string="KPP",
        comodel_name="res.partner",
        required=True,
        readonly=True,
        ondelete="restrict",
        states={
            "draft": [
                ("readonly", False),
            ],
        }
    )
    wajib_pajak_id = fields.Many2one(
        string="Wajib Pajak",
        comodel_name="res.partner",
        required=True,
        ondelete="restrict",
        default=lambda self: self._default_wajib_pajak_id(),
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        }
    )
    pemotong_pajak_id = fields.Many2one(
        string="Pemotong Pajak",
        comodel_name="res.partner",
        required=True,
        ondelete="restrict",
        default=lambda self: self._default_pemotong_pajak_id(),
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        }
    )
    ttd_id = fields.Many2one(
        string="TTD",
        comodel_name="res.partner",
        readonly=True,
        ondelete="restrict",
        states={
            "draft": [
                ("readonly", False),
            ],
        }
    )
    total_tax = fields.Float(
        string="Total Tax",
        compute="_compute_tax",
        store=True,
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        required=True,
        readonly=True,
    )
    line_ids = fields.One2many(
        string="Bukti Potong Line",
        comodel_name="l10n_id.bukti_potong_pph_line",
        inverse_name="bukti_potong_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        }
    )
    move_id = fields.Many2one(
        string="Accounting Entry",
        comodel_name="account.move",
        readonly=True,
        copy=False,
    )
    # move_line_ids = fields.One2many(
    #     string="Move Lines",
    #     comodel_name="account.move.line",
    #     related="move_id.line_id",
    #     store=False,
    # )
    confirm_ok = fields.Boolean(
        string="Confirm Ok",
        compute="_compute_policy",
        readonly=True,
    )
    approve_ok = fields.Boolean(
        string="Approve Ok",
        compute="_compute_policy",
        readonly=True,
    )
    cancel_ok = fields.Boolean(
        string="Cancel Ok",
        compute="_compute_policy",
        readonly=True,
    )
    reset_ok = fields.Boolean(
        string="Confirm Ok",
        compute="_compute_policy",
        readonly=True,
    )

    @api.multi
    def workflow_action_draft(self):
        for bukpot in self:
            bukpot.write(self._prepare_draft_data())

    @api.multi
    def workflow_action_confirm(self):
        for bukpot in self:
            bukpot.write(self._prepare_confirm_data())

    @api.multi
    def workflow_action_done(self):
        for bukpot in self:
            bukpot.write(self._prepare_done_data())
            bukpot._create_aml()

    @api.multi
    def workflow_action_cancel(self):
        for bukpot in self:
            bukpot._unreconcile_aml()
            if bukpot._check_move():
                bukpot.move_id.button_cancel()
            bukpot.move_id.unlink()
            bukpot.write(self._prepare_cancel_data())

    @api.multi
    def workflow_action_reset(self):
        for bukpot in self:
            bukpot.write(self._prepare_reset_data())

    @api.multi
    def _prepare_draft_data(self):
        self.ensure_one()
        data = {
            "state": "draft",
        }
        return data

    @api.multi
    def _prepare_confirm_data(self):
        self.ensure_one()
        data = {
            "state": "confirm",
        }
        return data

    @api.multi
    def _prepare_done_data(self):
        self.ensure_one()
        move = self._create_accounting_entry()
        data = {
            "state": "done",
            "move_id": move.id,
        }
        return data

    @api.multi
    def _prepare_cancel_data(self):
        self.ensure_one()
        data = {
            "state": "cancel",
        }
        return data

    @api.multi
    def _prepare_reset_data(self):
        self.ensure_one()
        data = {
            "state": "draft",
        }
        return data

    @api.multi
    def _check_move(self):
        self.ensure_one()
        result = False
        if self.move_id.state == "posted":
            result = True
        return result

    @api.model
    def _get_button_policy(self, bukpot_type, button_type):
        result = False
        user = self.env.user
        group_ids = user.groups_id.ids

        if button_type == "confirm":
            button_group_ids = bukpot_type.allow_confirm_group_ids.ids
        elif button_type == "approve":
            button_group_ids = bukpot_type.allow_approve_group_ids.ids
        elif button_type == "cancel":
            button_group_ids = bukpot_type.allow_cancel_group_ids.ids
        elif button_type == "reset":
            button_group_ids = bukpot_type.allow_reset_group_ids.ids

        if not button_group_ids:
            result = True
        else:
            if (set(button_group_ids) & set(group_ids)):
                result = True
        return result

    @api.multi
    def _create_sequence(self, journal_id):
        journal = self.env["account.journal"].browse(journal_id)
        name = self.env["ir.sequence"].\
            next_by_id(journal.sequence_id.id) or "/"
        return name

    @api.model
    def create(self, values):
        new_values = self._prepare_create_data(values)
        return super(BuktiPotongPPh, self).create(new_values)

    @api.model
    def _prepare_create_data(self, values):
        name = values.get("name", False)
        if not name or name == "/":
            values["name"] = self._create_sequence(values["journal_id"])
        return values

    @api.multi
    def _create_accounting_entry(self):
        self.ensure_one()
        obj_move = self.env["account.move"]
        if self.total_tax <= 0.0:
            raise UserError(_("Total tax has to be greater than 0"))
        move = obj_move.create(
            self._prepare_accounting_entry_data())
        return move

    @api.multi
    def _create_aml(self):
        self.ensure_one()
        pairs = []
        for line in self.line_ids:
            result = line._create_aml()
            if result:
                pairs.append(result)
        for pair in pairs:
            pair.reconcile_partial()

    @api.multi
    def _prepare_accounting_entry_data(self):
        self.ensure_one()
        data = {
            "name": self.name,
            "date": self.date,
            "journal_id": self.journal_id.id,
            "period_id": self.period_id.id,
        }
        return data

    @api.multi
    def _unreconcile_aml(self):
        self.ensure_one()
        for aml in self.move_line_ids:
            aml.refresh()
            reconcile = aml.reconcile_id or aml.reconcile_partial_id or \
                False
            if reconcile:
                move_lines = reconcile.line_id
                move_lines -= aml
                reconcile.unlink()

                if len(move_lines) > 2:
                    move_lines.reconcile_partial()

    # @api.onchange("date")
    # def onchange_period_id(self):
    #     period = self.env["account.period"].find(
    #         self.date)
    #     self.period_id = period[0].id

    @api.onchange("pemotong_pajak_id")
    def onchange_pemotong_pajak_id(self):
        self.ttd_id = False
