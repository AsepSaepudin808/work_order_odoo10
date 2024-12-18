from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_booking_order = fields.Boolean(string='Is Booking Order', default=False)
    # team_id = fields.Many2one('service.team', string='Team')
    team_leader = fields.Many2one('res.users', string='Team Leader')
    team_members = fields.Many2many('res.users', string='Team Members')
    booking_start = fields.Datetime(string='Booking Start')
    booking_end = fields.Datetime(string='Booking End')

    @api.model
    def create(self, vals):
        if vals.get('is_booking_order'):
            vals['is_booking_order'] = True
        return super(SaleOrder, self).create(vals)

    @api.multi
    def action_confirm(self):
        for order in self:
            # Cek ketersediaan tim
            overlapping_work_orders = self.env['work.order'].search([
                ('team_id', '=', order.team_id.id),
                ('state', '!=', 'cancelled'),
                ('planned_start', '<', order.booking_end),
                ('planned_end', '>', order.booking_start)
            ])
            if overlapping_work_orders:
                raise UserError("Team is not available during this period, already booked on SOXX. Please book on another date.")
            # Buat work order
            work_order = self.env['work.order'].create({
                'team_id': order.team_id.id,
                'team_leader': order.team_leader.id,
                'team_members': [(6, 0, order.team_members.ids)],
                'planned_start': order.booking_start,
                'planned_end': order.booking_end,
                'booking_order_ref': order.id,
            })
            order.work_order_id = work_order.id
        return super(SaleOrder, self).action_confirm()

