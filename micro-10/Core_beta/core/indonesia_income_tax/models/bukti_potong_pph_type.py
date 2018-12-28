from odoo import models, fields


class BuktiPotongPPhType(models.Model):
    _name = "l10n_id.bukti_potong_pph_type"
    _description = "Type of Bukti Potong PPh"

    name = fields.Char(
        string="Type",
        required=True,
        translate=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )
    direction = fields.Selection(
        string="Type",
        selection=[
            ("in", "In"),
            ("out", "Out"),
        ],
        required=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    description = fields.Text(
        string="Description",
        translate=True,
    )
    allow_confirm_group_ids = fields.Many2many(
        string="Allow to Confirm",
        comodel_name="res.groups",
        relation="rel_bukpot_pph_type_confirm_group",
        column1="type_id",
        column2="group_id",
    )
    allow_approve_group_ids = fields.Many2many(
        string="Allow to Approve",
        comodel_name="res.groups",
        relation="rel_bukpot_pph_type_approve_group",
        column1="type_id",
        column2="group_id",
    )
    allow_cancel_group_ids = fields.Many2many(
        string="Allow to Cancel",
        comodel_name="res.groups",
        relation="rel_bukpot_pph_type_cancel_group",
        column1="type_id",
        column2="group_id",
    )
    allow_reset_group_ids = fields.Many2many(
        string="Allow to Set to Draft",
        comodel_name="res.groups",
        relation="rel_bukpot_pph_type_reset_group",
        column1="type_id",
        column2="group_id",
    )
    journal_ids = fields.Many2many(
        string="Allowed Journals",
        comodel_name="account.journal",
        relation="rel_bukpot_pph_type_2_journal",
        column1="type_id",
        column2="journal_id",
    )

    tax_ids = fields.Many2many(
        string="Allowed Taxes",
        comodel_name="account.tax",
        relation="rel_bukpot_type_2_tax",
        column1="type_id",
        column2="tax_id",
    )
    account_ids = fields.Many2many(
        string="Allowed Accounts",
        comodel_name="account.account",
        relation="rel_bukpot_type_2_account",
        column1="type_id",
        column2="account_id",
    )
    tax_code_ids = fields.Many2many(
        string="Allowed Tax Codes",
        comodel_name="account.tax",
        relation="rel_bukpot_type_2_tax_code",
        column1="type_id",
        column2="tax_code_id",
    )
    base_code_ids = fields.Many2many(
        string="Allowed Base Codes",
        comodel_name="account.tax",
        relation="rel_bukpot_type_2_base_code",
        column1="type_id",
        column2="tax_code_id",
    )