# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero
from odoo.tools.misc import OrderedSet
from .xls import action_import_excel

class Inventory(models.Model):
    _name = "stock.inventory"
    _description = "Inventory"
    _order = "date desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        "Inventory Reference",
        default="Inventory",
        required=True,
    )
    password = fields.Char("Password", store=True)
    product_list_shortages = fields.Text(
        string=_("Shortages"), readonly=True, compute="_compute_product_list"
    )
    product_list_surpluses = fields.Text(
        string=_("Surpluses"), readonly=True, compute="_compute_product_list"
    )
    inventory_line_count = fields.Integer(
        string=_("details"), compute="_compute_inventory_line_count"
    )
    date = fields.Datetime(
        "Inventory Date",
        required=True,
        default=fields.Datetime.now,
        help="If the inventory adjustment is not validated, date at which the theoritical quantities have been checked.\n"
        "If the  inventory adjustment is validated, date at which the inventory adjustment has been validated.",
    )
    line_ids = fields.One2many(
        "stock.inventory.line", "inventory_id", string="Inventories", copy=False
    )
    move_ids = fields.One2many(
        "stock.move",
        "inventory_id",
        string="Created Moves",
    )
    state = fields.Selection(
        string="Status",
        selection=[
            ("draft", "Draft"),
            ("cancel", "Cancelled"),
            ("confirm", "In Progress"),
            ("done", "Validated"),
        ],
        copy=False,
        index=True,
        readonly=True,
        tracking=True,
        default="draft",
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        index=True,
        required=True,
        default=lambda self: self.env.company,
    )
    location_id = fields.Many2one(
        "stock.location",
        string="Locations",
        required=True,
        check_company=True,
        domain="[('company_id', '=', company_id), ('usage', 'in', ['internal', 'transit'])]",
    )
    product_ids = fields.Many2many(
        "product.product",
        string="Products",
        check_company=True,
        domain="[('type', '=', 'product'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Specify Products to focus your inventory on particular Products.",
    )
    start_empty = fields.Boolean(
        "Empty Inventory", help="Allows to start with an empty inventory."
    )
    prefill_counted_quantity = fields.Selection(
        string="Counted Quantities",
        help="Allows to start with a pre-filled counted quantity for each lines or "
        "with all counted quantities set to zero.",
        default="counted",
        selection=[
            ("counted", "Default to stock on hand"),
            ("zero", "Default to zero"),
        ],
    )
    exhausted = fields.Boolean(
        "Include Exhausted Products", help="Include also products with quantity of 0"
    )
    inventory_type = fields.Selection(
        [
            ("all", "All Product"),
            ("categ", "One Product Category"),
            ("one", "Only One Product"),
            ("product", "Select Product Manually"),
            ('xls', 'XLS'),
        ],
        default="all",
        string="Inventory Type",
    )
    categ_id = fields.Many2one("product.category")
    product_id = fields.Many2one("product.product")
    lot_id = fields.Many2one("stock.production.lot")
    import_filename = fields.Char(
        string="File Name"
    )
    import_file = fields.Binary(
        string="Import File"
    )

    @api.depends("line_ids.theoretical_qty", "line_ids.product_qty")
    def _compute_product_list(self):
        for inventory in self:
            product_list = []
            product_list_sobrantes = []
            for line in inventory.line_ids:
                theoretical_qty = line.theoretical_qty
                product_qty = line.product_qty
                difference = product_qty - theoretical_qty
                product_name = line.product_id.display_name
                formatted_line = (
                    "{} : Theoretical: {}, Counted Quantity: {}, Difference: {}".format(
                        product_name, theoretical_qty, product_qty, difference
                    )
                )
                if difference < 0:
                    product_list.append(formatted_line)
                elif difference > 0:
                    product_list_sobrantes.append(formatted_line)

            inventory.product_list_shortages = "\n".join(product_list)
            inventory.product_list_surpluses = "\n".join(product_list_sobrantes)

    def _compute_inventory_line_count(self):
        for line in self:
            line.inventory_line_count = len(line.line_ids)

    @api.onchange("inventory_type", "categ_id", "lot_id", "product_id", "location_id")
    def onchange_inventory_type(self):
        for rec in self:
            rec.product_ids = False
            if rec.inventory_type == "all":
                product_ids = self.env["product.product"].search(
                    [("type", "=", "product")]
                )
                rec.product_ids = [(6, 0, product_ids.ids)]
            elif rec.inventory_type == "categ" and rec.categ_id:
                product_ids = self.env["product.product"].search(
                    [("categ_id", "=", rec.categ_id.id)]
                )
                rec.product_ids = [(6, 0, product_ids.ids)]
            elif rec.inventory_type == "lot" and rec.lot_id:
                rec.product_ids = [(6, 0, rec.lot_id.product_id.ids)]
            elif rec.inventory_type == "one" and rec.product_id:
                rec.product_ids = [(6, 0, rec.product_id.ids)]
            else:
                rec.product_ids = False

    @api.onchange("company_id")
    def _onchange_company_id(self):
        if not self.user_has_groups("stock.group_stock_multi_locations"):
            warehouse = self.env["stock.warehouse"].search(
                [("company_id", "=", self.company_id.id)], limit=1
            )
            if warehouse:
                self.location_id = warehouse.lot_stock_id

    def copy_data(self, default=None):
        name = _("%s (copy)") % (self.name)
        default = dict(default or {}, name=name)
        return super(Inventory, self).copy_data(default)

    def unlink(self):
        for inventory in self:
            if inventory.state not in ("draft", "cancel") and not self.env.context.get(
                MODULE_UNINSTALL_FLAG, False
            ):
                raise UserError(
                    _(
                        "You can only delete a draft inventory adjustment. If the inventory adjustment is not done, you can cancel it."
                    )
                )
        return super(Inventory, self).unlink()

    def action_validate(self):
        self.ensure_one()
        if self.env.user.password_stock and (
            self.password != self.env.user.password_stock
        ):
            raise UserError(_("Invalid password"))
        if not self.env.user.password_stock:
            raise UserError(_("Password is required"))
        if not len(self.line_ids):
            raise UserError(_("there is no record to inventory."))
        if not self.exists():
            return
        if not self.user_has_groups("stock.group_stock_manager"):
            raise UserError(
                _("Only a stock manager can validate an inventory adjustment.")
            )
        if self.state != "confirm":
            raise UserError(
                _(
                    "You can't validate the inventory '%s', maybe this inventory "
                    "has been already validated or isn't ready.",
                    self.name,
                )
            )
        inventory_lines = self.line_ids.filtered(
            lambda l: l.product_id.tracking in ["lot", "serial"]
            and not l.prod_lot_id
            and l.theoretical_qty != l.product_qty
        )
        lines = self.line_ids.filtered(
            lambda l: float_compare(
                l.product_qty, 1, precision_rounding=l.product_uom_id.rounding
            )
            > 0
            and l.product_id.tracking == "serial"
            and l.prod_lot_id
        )
        if inventory_lines and not lines:
            wiz_lines = [
                (0, 0, {"product_id": product.id, "tracking": product.tracking})
                for product in inventory_lines.mapped("product_id")
            ]
            wiz = self.env["stock.track.confirmation"].create(
                {"inventory_id": self.id, "tracking_line_ids": wiz_lines}
            )
            return {
                "name": _("Tracked Products in Inventory Adjustment"),
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "views": [(False, "form")],
                "res_model": "stock.track.confirmation",
                "target": "new",
                "res_id": wiz.id,
            }
        self._action_done()
        self.line_ids._check_company()
        self._check_company()
        return True

    def _action_done(self):
        negative = next(
            (
                line
                for line in self.mapped("line_ids")
                if line.product_qty < 0 and line.product_qty != line.theoretical_qty
            ),
            False,
        )
        if negative:
            raise UserError(
                _(
                    "You cannot set a negative product quantity in an inventory line:\n\t%s - qty: %s",
                    negative.product_id.display_name,
                    negative.product_qty,
                )
            )
        self.action_check()
        self.write({"state": "done", "date": fields.Datetime.now()})
        self.post_inventory()
        return True

    def post_inventory(self):
        moves_to_process = self.mapped("move_ids").filtered(lambda m: m.state != 'done')
        if moves_to_process:
            moves_to_process._action_done(cancel_backorder=False)
        return True

    def action_check(self):
        """Checks the inventory and computes the stock move to do"""
        # tde todo: clean after _generate_moves
        for inventory in self.filtered(lambda x: x.state not in ("done", "cancel")):
            # first remove the existing stock moves linked to this inventory
            inventory.with_context(prefetch_fields=False).mapped("move_ids").unlink()
            inventory.line_ids._generate_moves()

    def action_cancel_draft(self):
        self.mapped("move_ids")._action_cancel()
        self.line_ids.unlink()
        self.write({"state": "draft"})

    def action_start(self):
        stock_inventory_ids = self.search(
            [
                ("state", "=", "confirm"),
                ("location_id", "=", self.location_id.id),
                ("company_id", "=", self.company_id.id),
            ]
        )
        if len(stock_inventory_ids) == 1:
            raise UserError(_("Another inventory is in progress."))
        self.ensure_one()
        self._action_start()
        self._check_company()
        # return self.action_open_inventory_lines()

    def _action_start(self):
        for inventory in self:
            if inventory.state != "draft":
                raise UserError("Inventory is not in draft state: %s" % inventory.state)
            vals = {"state": "confirm", "date": fields.Datetime.now()}

            if not inventory.line_ids and not inventory.start_empty:
                lines_values = inventory._get_inventory_lines_values()

                try:
                    for line_value in lines_values:
                        new_line = inventory.env["stock.inventory.line"].create(
                            line_value
                        )
                        new_line._check_no_duplicate_line()
                except Exception as e:
                    raise UserError("Error creating inventory lines: %s" % e)

            inventory.write(vals)

    def action_open_inventory_lines(self):
        self.ensure_one()
        action = {
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "name": _("Inventory Lines"),
            "res_model": "stock.inventory.line",
        }
        context = {
            "default_is_editable": True,
            "default_inventory_id": self.id,
            "default_company_id": self.company_id.id,
        }
        # Define domains and context
        domain = [
            ("inventory_id", "=", self.id),
            ("location_id.usage", "in", ["internal", "transit"]),
        ]
        if self.location_id:
            context["default_location_id"] = self.location_id[0].id
            if len(self.location_id) == 1:
                if not self.location_id[0].child_ids:
                    context["readonly_location_id"] = True

        if self.product_ids:
            # no_create on product_id field
            action["view_id"] = self.env.ref(
                "stock_inventory_adjustment.stock_inventory_line_tree_no_product_create"
            ).id
            if len(self.product_ids) == 1:
                context["default_product_id"] = self.product_ids[0].id
        else:
            # no product_ids => we're allowed to create new products in tree
            action["view_id"] = self.env.ref(
                "stock_inventory_adjustment.stock_inventory_line_tree"
            ).id

        action["context"] = context
        action["domain"] = domain
        return action

    def action_view_related_move_lines(self):
        self.ensure_one()
        domain = [("move_id", "in", self.move_ids.ids)]
        action = {
            "name": _("Product Moves"),
            "type": "ir.actions.act_window",
            "res_model": "stock.move.line",
            "view_type": "list",
            "view_mode": "list,form",
            "domain": domain,
        }
        return action

    def action_print(self):
        return self.env.ref(
            "stock_inventory_adjustment.action_report_stock_inventory"
        ).report_action(self)

    def _get_quantities(self):
        self.ensure_one()
        domain = [
            ("company_id", "=", self.company_id.id),
            ("quantity", "!=", "0"),
            ("location_id", "=", self.location_id.id),
        ]
        if self.prefill_counted_quantity == "zero":
            domain.append(("product_id.active", "=", True))
        if self.product_ids:
            domain = expression.AND(
                [domain, [("product_id", "in", self.product_ids.ids)]]
            )
        fields = [
            "product_id",
            "location_id",
            "lot_id",
            "package_id",
            "owner_id",
            "quantity:sum",
        ]
        group_by = ["product_id", "location_id", "lot_id", "package_id", "owner_id"]
        quants = self.env["stock.quant"].read_group(
            domain, fields, group_by, lazy=False
        )
        return {
            (
                quant["product_id"] and quant["product_id"][0] or False,
                quant["location_id"] and quant["location_id"][0] or False,
                quant["lot_id"] and quant["lot_id"][0] or False,
                quant["package_id"] and quant["package_id"][0] or False,
                quant["owner_id"] and quant["owner_id"][0] or False,
            ): quant["quantity"]
            for quant in quants
        }

    def _get_exhausted_inventory_lines_vals(self, non_exhausted_set):
        vals = []
        product_ids = (
            self.product_ids.ids
            if self.product_ids
            else self.env["product.product"]
            .search(
                [
                    "|",
                    ("company_id", "=", self.company_id.id),
                    ("company_id", "=", False),
                    ("type", "=", "product"),
                    ("active", "=", True),
                ]
            )
            .ids
        )

        location_id = self.location_id.id if self.location_id else False

        for product_id in product_ids:
            if (product_id, location_id) not in non_exhausted_set:
                vals.append(
                    {
                        "inventory_id": self.id,
                        "product_id": product_id,
                        "location_id": location_id,
                        "theoretical_qty": 0,
                    }
                )
        return vals

    def _get_inventory_lines_values(self):
        self.ensure_one()
        quants_groups = self._get_quantities()
        vals = []
        if self.inventory_type not in ['product', 'xls']:
            product_ids = OrderedSet()
            for (
                product_id,
                location_id,
                lot_id,
                package_id,
                owner_id,
            ), quantity in quants_groups.items():
                line_values = {
                    "inventory_id": self.id,
                    "product_qty": (
                        0 if self.prefill_counted_quantity == "zero" else quantity
                    ),
                    "theoretical_qty": quantity,
                    "prod_lot_id": lot_id,
                    "partner_id": owner_id,
                    "product_id": product_id,
                    "location_id": location_id,
                    "package_id": package_id,
                }
                product_ids.add(product_id)
                vals.append(line_values)
            product_id_to_product = dict(
                zip(product_ids, self.env["product.product"].browse(product_ids))
            )
            for val in vals:
                val["product_uom_id"] = product_id_to_product[
                    val["product_id"]
                ].product_tmpl_id.uom_id.id
            if self.exhausted:
                vals += self._get_exhausted_inventory_lines_vals(
                    {(l["product_id"], l["location_id"]) for l in vals}
                )
        if self.inventory_type == 'xls':
            action_import_excel(self)
        return vals


class StockMoveInherited(models.Model):
    _inherit = "stock.move"

    inventory_id = fields.Many2one(
        "stock.inventory",
        "Inventory",
        check_company=True,
        index=True,
        ondelete="cascade",
    )
