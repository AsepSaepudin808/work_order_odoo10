from odoo import models, fields, api

class WorkOrder(models.Model):
    _name = 'work.order'
    _description = 'Work Order'

    name = fields.Char(string='WO Number', readonly=True, required=True, default='New')
    booking_order_reference = fields.Many2one('sale.order', string='Booking Order Reference', readonly=True)
    team = fields.Many2one('service.team', string='Team', required=True)
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
    ], string='State', default='pending')
    notes = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('work.order') or 'New'
        return super(WorkOrder, self).create(vals)

    def action_start_work(self):
        self.write({
            'state': 'in_progress',
            'date_start': fields.Datetime.now()
        })

    def action_end_work(self):
        self.write({
            'state': 'done',
            'date_end': fields.Datetime.now()
        })

    def action_reset(self):
        self.write({
            'state': 'pending',
            'date_start': False
        })

    def action_cancel(self):
        self.write({'state': 'cancelled'})
