# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    @api.multi
    def create_invoices(self):
        sales = self.env['sale.order'].search([
            ('id', 'in', self.env.context['active_ids']),
            ('holding_company_id', '!=', False),
        ])
        if sales:
            raise UserError(_('This sale order must be invoiced from holding'))
        return super(SaleAdvancePaymentInv, self).create_invoices()