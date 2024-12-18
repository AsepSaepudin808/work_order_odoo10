from odoo import models, fields, api

class WorkOrder(models.Model):
    _name = 'work.order'
    _description = 'Work Order'

    name = fields.Char(string='WO Number', required=True, readonly=True, default=lambda self: self.env['ir.sequence'].next_by_code('work.order'))
    booking_order_ref = fields.Many2one('sale.order', string='Booking Order Reference', readonly=True)
    team_id = fields.Many2one('service.team', string='Team', required=True)
    team_leader = fields.Many2one('res.users', string='Team Leader', required=True)
    team_members = fields.Many2many('res.users', string='Team Members')
    planned_start = fields.Datetime(string='Planned Start', required=True)
    planned_end = fields.Datetime(string='Planned End', required=True)
    date_start = fields.Datetime(string='Date Start', readonly=True)
    date_end = fields.Datetime(string='Date End', readonly=True)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    notes = fields.Text(string='Notes')

    @api.multi
    def action_cancel(self):
        for order in self:
            reason = self.env['ir.actions.act_window'].create({
                'name': 'Reason for Cancellation',
                'type': 'ir.actions.act_window',
                'res_model': 'work.order',
                'view_mode': 'form',
                'target': 'new',
            })
            order.notes += "\nCancelled: {}".format(reason)
            order.state = 'cancelled'

