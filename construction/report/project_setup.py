# -*- coding: utf-8 -*-
# This file is part of OpenERP. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

from odoo import api, models


class ProjectSetupReport(models.AbstractModel):
    _name = 'report.construction.project_setup_report'

    def render_html(self, docids, data=None):
        rcs = self.with_context(translatable=True)
        report_obj = rcs.env['report']
        project_obj = self.env['project.setup'].browse(docids)
        report = report_obj._get_report_from_name(
            'construction.project_setup_report')

        docargs = {}
        docargs.update({
            'doc_ids': docids,
            'doc_model': 'project.setup',
            'docs': project_obj,
        })
        return report_obj.render(
            'construction.project_setup_report',
            docargs)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: