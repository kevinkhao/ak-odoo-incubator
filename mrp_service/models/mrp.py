# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# ajouter les fournisseurs sur les services


from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class MrpBom(models.Model):
    """ Defines bills of material for a product or a product template """
    _inherit = 'mrp.bom'

    # ajouter un type ?

    # ça peut être une variante ?
    service_id = fields.Many2one(
        'product.product', 'Service',
        domain="[('type', 'in', ['service'])]")


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    service_id = fields.Many2one(
        'product.product',
        'Service',
        readonly=True,
        compute="_compute_service_id",
    )
    service_procurement_id = fields.Many2one(
        'procurement.order',
        'Procurement Service',
        readonly=True,
    )
    wait_for_service = fields.Boolean(
        compute="_compute_wait_for_service",
        store=True)

    service_provider_id = fields.Many2one(
        'res.partner',
        'Provider',
        related="service_procurement_id.purchase_id.partner_id",
        readonly=True,
    )

    @api.depends('service_procurement_id.state')
    def _compute_wait_for_service(self):
        for rec in self:
            if rec.service_procurement_id:
                rec.wait_for_service = (
                    rec.service_procurement_id.state != 'done')
            else:
                rec.wait_for_service = False

    def _compute_service_id(self):
        for rec in self:
            rec.service_id = rec.bom_id.service_id.id

    @api.model
    def create(self, values):
        production = super(MrpProduction, self).create(values)
        production._generate_service_procurement()
        return production

    @api.multi
    def _generate_service_procurement(self):
        if not self.service_id:
            return
        _logger.info('on va generer des procurements')

        procurements = self.env['procurement.order']
        for rec in self:
            vals = rec._prepare_procurement_for_service()
            proc = procurements.create(vals)
            rec.service_procurement_id = proc.id
            procurements |= proc
        if procurements:
            procurements.run()

    def _prepare_procurement_for_service(self):
        return {
            'name': "Service for %s " % self.name,
            'origin': self.name,
            'company_id': self.company_id.id,
            'date_planned': self.date_planned_start,
            'product_id': self.service_id.id,
            'product_qty': self.product_qty,
            'product_uom': self.service_id.uom_po_id.id,
            'production_id': self.id,  # TODO: mettre une autre clef?service_mrp_id ?
            'location_id': self.location_dest_id.id,
            # 'move_dest_id': (
            #    self.procurement_ids and
            #    self.procurement_ids[0].move_dest_id.id or False),
            'group_id': self.procurement_group_id.id,
            # 'route_ids': [], #[(4, x.id) for x in self.route_ids],
            'warehouse_id': (
                self.picking_type_id and
                self.picking_type_id.warehouse_id.id or False),
            'priority': self.priority,
        }

    def _check_procurement(self):
        _logger.info('check si le procurement est ok')
        if self.service_procurement_id.state == 'done':
                return self.availability
        else:
            return 'waiting'  # or waiting service ?

    @api.multi
    @api.depends('service_procurement_id.state')
    def _compute_availability(self):
        _logger.info('_compute_availability only if service procurement.state')
        super(MrpProduction, self)._compute_availability()
        for rec in self:
            if rec.wait_for_service:
                rec.availability = rec._check_procurement()
