from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_booking_order = fields.Boolean(string='Is Booking Order', default=False)
    team = fields.Many2one('service.team', string='Team')
    team_leader = fields.Many2one('res.users', string='Team Leader')
    team_members = fields.Many2many('res.users', string='Team Members')
    booking_start = fields.Datetime(string='Booking Start')
    booking_end = fields.Datetime(string='Booking End')

    @api.onchange('team')
    def _onchange_team(self):
        """Auto-fill Team Leader and Members based on selected Team."""
        if self.team:
            self.team_leader = self.team.team_leader
            self.team_members = self.team.team_members

    @api.model
    def create(self, vals):
        if 'team' in vals:
            team = self.env['service.team'].browse(vals['team'])
            vals['team_leader'] = team.team_leader.id if team.team_leader else False
            vals['team_members'] = [(6, 0, team.team_members.ids)]
        return super(SaleOrder, self).create(vals)

    def write(self, vals):
        if 'team' in vals:
            team = self.env['service.team'].browse(vals['team'])
            vals['team_leader'] = team.team_leader.id if team.team_leader else False
            vals['team_members'] = [(6, 0, team.team_members.ids)]
        return super(SaleOrder, self).write(vals)

    def action_check_team_availability(self):
        """Validasi ketersediaan tim berdasarkan jadwal booking."""
        for order in self:
            if not order.team:
                raise ValidationError("Please select a team before checking availability.")
            
            # Cari Work Order aktif (tidak cancelled) dengan overlap jadwal
            overlapping_work_orders = self.env['work.order'].search([
                ('team', '=', order.team.id),
                ('state', '!=', 'cancelled'),
                ('planned_start', '<=', order.booking_end),
                ('planned_end', '>=', order.booking_start)
            ])
            
            if overlapping_work_orders:
                raise ValidationError("Team already has work orders during this period.")
            self._send_notification("Team is available for booking!")

    def _send_notification(self, message):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': message,
                'type': 'success',
                'sticky': False,
            }
        }





    def action_confirm(self):
        """Override action_confirm untuk validasi ketersediaan tim."""
        for order in self:
            overlapping_work_orders = self.env['work.order'].search([
                ('team', '=', order.team.id),
                ('state', '!=', 'cancelled'),
                ('planned_start', '<=', order.booking_end),
                ('planned_end', '>=', order.booking_start)
            ])
            if overlapping_work_orders:
                raise ValidationError(
                    "Team is not available during this period, already booked on another work order."
                )
        
        work_order_vals = {
            'booking_order_reference': self.id,
            'team': self.team.id,
            'team_leader': self.team_leader.id,
            'team_members': [(6, 0, self.team_members.ids)],
            'planned_start': self.booking_start,
            'planned_end': self.booking_end,
            'state': 'pending',
        }
        self.env['work.order'].create(work_order_vals)
        return super(SaleOrder, self).action_confirm()