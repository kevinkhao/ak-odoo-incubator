# coding: utf-8
# © 2015 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _

# Duplicate from module project_model_to_task
# to create an external_task instead of a project_task

# generated by print ''.join([str(ord(x)) for x in 'project_model_to_task'])
UNIQUE_ACTION_ID = (
    11211411110610199116951091111001011089511611195116971151071)


class IrValues(models.Model):
    _inherit = 'ir.values'

    @api.model
    def get_actions(self, action_slot, model, res_id=False):
        """ Add an action to all Model objects of the ERP """
        res = super(IrValues, self).get_actions(
            action_slot, model, res_id=res_id)
        if UNIQUE_ACTION_ID in [x[0] for x in res]:
            # Be careful the original fonction is cached in the ORM
            # this method will return a list (mutable object)
            # So if we call once this inherited method we will inject
            # the action in the mutable object and so in the cache
            # If the action is already here no need to add it again
            return res
        else:
            if action_slot == 'client_action_multi'\
                    and model != 'external.task':
                action = self.set_external_task_action(model, res_id=res_id)
                if action:
                    value = (UNIQUE_ACTION_ID, 'external_project', action)
                    res.insert(0, value)
            return res

    @api.model
    def set_external_task_action(self, model, res_id=False):
        action = self.env.ref('project_api_client.task_from_elsewhere')
        return {
            'id': action.id,
            'name': _('Create a Ticket'),
            'res_model': u'external.task',
            'src_model': model,
            'type': u'ir.actions.act_window',
            'target': 'current',
        }
