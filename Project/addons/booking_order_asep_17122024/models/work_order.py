from odoo import models, fields, api

class WorkOrder(models.Model):
    _name = 'work.order'
    _description = 'Work Order'


    wo_number = fields.Char(string='WO Number', readonly=True, copy=False)
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
    ], string='State', default='pending', readonly=True, index=True, track_visibility='onchange')
    notes = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        if vals.get('wo_number', 'New') == 'New':
            vals['wo_number'] = self.env['ir.sequence'].next_by_code('work.order.sequence') or 'WO'
        return super(WorkOrder, self).create(vals)

    @api.onchange('booking_order_reference')
    def _onchange_booking_order_reference(self):
        if self.booking_order_reference:
            self.team = self.booking_order_reference.team
            self.team_leader = self.booking_order_reference.team_leader
            self.team_members = self.booking_order_reference.team_members

    def action_start_work(self):
        self.ensure_one()
        self.state = 'in_progress'
        self.date_start = fields.Datetime.now()
        self.date_end = fields.Datetime.now()

    def action_end_work(self):
        self.ensure_one()
        self.state = 'done'
        self.date_start = fields.Datetime.now()
        self.date_end = fields.Datetime.now()

    def action_reset(self):
        self.ensure_one()
        self.state = 'pending'
        self.date_start = False
        self.date_end = False

    def action_cancel(self):
       return {
           'name': 'Reason for Cancellation',
           'view_mode': 'form',
           'view_id': self.env.ref('booking_order_asep_17122024.view_cancel_reason_form').id,
           'target': 'new',
           'context': {
               'default_work_order_id': self.id,
           },
           'type': 'ir.actions.act_window',
       }
    def name_get(self):
        result = []
        for record in self:
            name = record.wo_number or "Unnamed Work Order"
            result.append((record.id, name))
        return result

class WorkOrderSequence(models.Model):
    _name = 'work.order.sequence'
    _description = 'Work Order Sequence'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)

class WorkOrderCancelReason(models.TransientModel):
    _name = 'work.order.cancel.reason'
    _description = 'Work Order Cancel Reason'

    work_order_id = fields.Many2one('work.order', string='Work Order')
    reason = fields.Text(string='Reason for Cancellation', required=True)

    def action_confirm_cancel(self):
        self.ensure_one()
        self.work_order_id.write({'state': 'cancelled', 'notes': self.reason})
        return {'type': 'ir.actions.act_window_close'}
