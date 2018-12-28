from odoo import models, fields, api
from odoo.tools.translate import _


class BuktiPotongPPhLine(models.Model):
    _name = "l10n_id.bukti_potong_pph_line"
    _description = "Bukti Potong PPh Line"
    _order = "sequence, id"
    _sql_constraints = [
        ("tax_code_unique", "unique(tax_code_id, bukti_potong_id)",
         "Tax code must be unique"),
    ]

    @api.model
    def _default_partner_id(self):
        direction = self._context.get("default_direction", False)
        wajib_pajak_id = self._context.get("wajib_pajak_id", False)
        pemotong_pajak_id = self._context.get("pemotong_pajak_id", False)
        return self._choose_partner(
            direction,
            wajib_pajak_id,
            pemotong_pajak_id)

    @api.multi
    @api.depends(
        "income_move_line_ids",
        "income_move_line_ids.debit",
        "income_move_line_ids.credit",
        "bukti_potong_id.direction",
    )
    def _compute_amount(self):
        for line in self:
            line.amount = 0.0
            for move_line in line.income_move_line_ids:
                if line.bukti_potong_id.direction == "in":
                    line.amount += move_line.credit
                else:
                    line.amount += move_line.debit
            if line.amount != 0.0:
                tax = line.tax_id.compute_all(line.amount, 1.0)
                line.amount_tax = tax["total_included"] - tax["total"]

    @api.multi
    @api.depends(
        "bukti_potong_id",
        "bukti_potong_id.direction",
    )
    def _compute_direction(self):
        for line in self:
            line.direction = line.bukti_potong_id.direction

    @api.multi
    @api.depends(
        "bukti_potong_id",
        "bukti_potong_id.wajib_pajak_id",
        "bukti_potong_id.pemotong_pajak_id",
        "bukti_potong_id.direction",
    )
    def _compute_partner(self):
        for line in self:
            bukpot = line.bukti_potong_id
            line.partner_id = self._choose_partner(
                bukpot.direction,
                bukpot.wajib_pajak_id,
                bukpot.pemotong_pajak_id)

    name = fields.Char(
        string="Description",
        required=True,
        default="/",
    )
    bukti_potong_id = fields.Many2one(
        string="Bukti Potong",
        comodel_name="l10n_id.bukti_potong_pph",
        ondelete="cascade",
    )
    sequence = fields.Integer(
        string="Sequence",
        required=True,
        default=5,
    )
    direction = fields.Selection(
        string="Type",
        selection=[
            ("in", "In"),
            ("out", "Out"),
        ],
        compute="_compute_direction",
        store=False,
        readonly=True,
    )
    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        compute="_compute_partner",
        store=False,
        readonly=True,
        default=lambda self: self._default_partner_id(),
    )
    tax_code_id = fields.Many2one(
        string="Tax Code",
        comodel_name="account.tax",
        required=False,
        ondelete="restrict",
    )
    base_code_id = fields.Many2one(
        string="Base Code",
        comodel_name="account.tax",
        required=False,
        ondelete="restrict",
    )
    tax_id = fields.Many2one(
        string="Tax",
        comodel_name="account.tax",
        required=True,
        ondelete="restrict",
    )
    analytic_account_id = fields.Many2one(
        string="Analytic Account",
        comodel_name="account.analytic.account",
    )
    move_line_id = fields.Many2one(
        string="Move Line",
        comodel_name="account.move.line",
        copy=False,
        ondelete="restrict",
    )
    income_move_line_ids = fields.Many2many(
        string="Income Move Lines",
        comodel_name="account.move.line",
        relation="rel_bukpot_line_2_income_move",
        column1="bukpot_line_id",
        column2="account_move_id",
    )
    amount = fields.Float(
        string="Amount",
        compute="_compute_amount",
        store=True,
    )
    amount_tax = fields.Float(
        string="Tax",
        compute="_compute_amount",
        store=True,
    )

    @api.onchange("tax_id")
    def tax_code_id_onchange(self):
        if self.tax_code_id:
            self.name = self.tax_code_id.name

    @api.multi
    def _get_tax_code_id(self):
        self.ensure_one()
        result = False
        if self.tax_code_id:
            result = self.tax_code_id.id
        if not result and self.tax_id.tax_code_id:
            result = self.tax_id.tax_code_id.id
        return result

    @api.multi
    def _get_base_code_id(self):
        self.ensure_one()
        result = False
        if self.base_code_id:
            result = self.base_code_id.id
        if not result and self.tax_id.base_code_id:
            result = self.tax_id.base_code_id.id
        return result

    @api.multi
    def _create_aml(self):
        self.ensure_one()
        obj_aml = self.env["account.move.line"]
        pair = False
        obj_aml.create(
            self._prepare_tax_aml_data())
        contra_tax_aml = obj_aml.create(
            self._prepare_contra_tax_aml_data())
        if self.move_line_id:
            pair = contra_tax_aml + self.move_line_id
        return pair

    @api.model
    def _prepare_aml_data(
            self, name, account_id, debit, credit, partner_id, tax_code_id,
            tax_amount, analytic_account_id, move_id):
        result = {
            "name": name,
            "account_id": account_id,
            "debit": debit,
            "credit": credit,
            "partner_id": partner_id,
            "tax_code_id": tax_code_id,
            "tax_amount": tax_amount,
            "analytic_account_id": analytic_account_id,
            "move_id": move_id,
        }
        return result

    @api.multi
    def _get_tax_aml_amount(self):
        self.ensure_one()
        bukpot = self.bukti_potong_id
        debit = credit = 0.0
        if bukpot.direction == "in":
            debit = self.amount_tax
        else:
            credit = self.amount_tax
        return debit, credit

    @api.multi
    def _get_contra_tax_aml_amount(self):
        self.ensure_one()
        bukpot = self.bukti_potong_id
        debit = credit = 0.0
        if bukpot.direction == "out":
            debit = self.amount_tax
        else:
            credit = self.amount_tax
        return debit, credit

    @api.multi
    def _prepare_tax_aml_data(self):
        self.ensure_one()
        bukpot = self.bukti_potong_id
        debit, credit = self._get_tax_aml_amount()
        result = self._prepare_aml_data(
            name=self.name,
            account_id=self._select_tax_account().id,
            debit=debit,
            credit=credit,
            partner_id=bukpot.kpp_id.commercial_partner_id.id,
            tax_code_id=self._get_tax_code_id(),
            tax_amount=self.tax_id.tax_sign * self.amount_tax,
            analytic_account_id=self.analytic_account_id and
            self.analytic_account_id.id or False,
            move_id=bukpot.move_id.id,
        )
        return result

    @api.multi
    def _prepare_contra_tax_aml_data(self):
        self.ensure_one()
        bukpot = self.bukti_potong_id
        debit, credit = self._get_contra_tax_aml_amount()
        partner = self._get_partner()
        result = self._prepare_aml_data(
            name=self.name,
            account_id=bukpot.account_id.id,
            debit=debit,
            credit=credit,
            partner_id=partner.id,
            tax_code_id=self._get_base_code_id(),
            tax_amount=self.tax_id.tax_sign * float(int(self.amount)),
            analytic_account_id=self.analytic_account_id and
            self.analytic_account_id.id or False,
            move_id=bukpot.move_id.id,
        )
        return result

    @api.multi
    def _get_partner(self):
        self.ensure_one()
        bukpot = self.bukti_potong_id
        return self._choose_partner(
            bukpot.direction, bukpot.wajib_pajak_id,
            bukpot.pemotong_pajak_id)

    @api.model
    def _choose_partner(
            self, direction, wajib_pajak_id,
            pemotong_pajak_id):
        if direction == "in":
            partner = pemotong_pajak_id
        else:
            partner = wajib_pajak_id
        return partner

    @api.multi
    def _select_tax_account(self):
        self.ensure_one()
        tax = self.tax_id
        if tax.account_collected_id:
            return tax.account_collected_id
        else:
            raise UserWarning(
                _("Please configure invoice tax account for %s") %
                (tax.name))

    @api.onchange("partner_id", "direction", "move_line_id")
    def onchange_move_line_id(self):

        result = {
            "domain": {
                "move_line_id": [
                    ("reconcile_id", "=", False),
                    ("account_id.reconcile", "=", True),
                ]
            }
        }
        if self.direction == "out":
            result["domain"]["move_line_id"].append(
                ("credit", ">", 0))
        else:
            result["domain"]["move_line_id"].append(
                ("debit", ">", 0))

        if self.partner_id:
            if self.move_line_id:
                result["domain"]["move_line_id"].append(
                    ("partner_id", "=", self.partner_id.id))
                if self.move_line_id.partner_id != self.partner_id:
                    self.move_line_id = False
            else:
                result["domain"]["move_line_id"].append(
                    ("partner_id", "=", self.partner_id.id))
        else:
            self.move_line_id = False
            result["domain"]["move_line_id"].append(
                ("partner_id", "=", False))
        return result
