# -*- coding: utf-8 -*-
# Copyright 2026 KLO Ingeniería Informática S.L.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api

_logger = logging.getLogger(__name__)


def _post_init_migrate_analytic_account(env):
    """Copia account_id -> analytic_account_id en project.project.

    Solo migra proyectos con analytic_account_id vacío y account_id informado.
    No borra columnas ni elimina campos (account_id nativo se conserva como backup).
    """
    if not isinstance(env, api.Environment):
        _logger.warning("KLO migración analítica: env no es api.Environment, se continúa igualmente.")

    Project = env["project.project"].with_context(active_test=False)

    env.cr.execute("SELECT COUNT(*) FROM project_project WHERE account_id IS NOT NULL")
    count_native = env.cr.fetchone()[0]
    env.cr.execute("SELECT COUNT(*) FROM project_project WHERE analytic_account_id IS NOT NULL")
    count_new = env.cr.fetchone()[0]
    env.cr.execute(
        "SELECT COUNT(*) FROM project_project "
        "WHERE analytic_account_id IS NULL AND account_id IS NOT NULL"
    )
    count_pending = env.cr.fetchone()[0]
    _logger.info(
        "KLO migración analítica (backup conteos): account_id informados=%s, "
        "analytic_account_id informados=%s, pendientes de migrar=%s.",
        count_native, count_new, count_pending,
    )

    to_migrate = Project.search(
        [("analytic_account_id", "=", False), ("account_id", "!=", False)]
    )
    _logger.info("KLO migración analítica: proyectos a migrar (ORM)=%s.", len(to_migrate))
    for project in to_migrate:
        project.write({"analytic_account_id": project.account_id.id})
    _logger.info("KLO migración analítica: migrados=%s.", len(to_migrate))

    conflicts = Project.search(
        [("analytic_account_id", "!=", False), ("account_id", "!=", False)]
    )
    for project in conflicts:
        if project.analytic_account_id.id != project.account_id.id:
            _logger.warning(
                "KLO migración analítica: conflicto proyecto %s (id %s): "
                "account_id=%s vs analytic_account_id=%s. No se sobrescribe; "
                "revisar manualmente.",
                project.display_name, project.id,
                project.account_id.id, project.analytic_account_id.id,
            )

    conflict_75_82 = Project.search(
        ["|", ("account_id", "in", [75, 82]), ("analytic_account_id", "in", [75, 82])]
    )
    for project in conflict_75_82:
        _logger.warning(
            "KLO migración analítica: proyecto %s (id %s) toca cuentas 75/82: "
            "account_id=%s analytic_account_id=%s.",
            project.display_name, project.id,
            project.account_id.id if project.account_id else False,
            project.analytic_account_id.id if project.analytic_account_id else False,
        )

    project_2735 = Project.search(
        ["|", ("name", "ilike", "2735"), ("id", "=", 2735)], limit=10
    )
    for project in project_2735:
        _logger.warning(
            "KLO migración analítica caso 2735: proyecto %s (id %s): "
            "account_id=%s analytic_account_id=%s. Conflicto conocido 75 vs 82: "
            "usar account_id=75 como valor correcto, no se borran columnas.",
            project.display_name, project.id,
            project.account_id.id if project.account_id else False,
            project.analytic_account_id.id if project.analytic_account_id else False,
        )
