# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.exceptions import Warning

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    is_booking_order = fields.Boolean(string='Is Booking Order')
    team = fields.Many2one('service.team', string='Team')
    team_leader = fields.Many2one('res.users', string='Team Leader')
    team_members = fields.Many2many('res.users', string='Team Members')
    booking_start = fields.Datetime(string='Booking Start')
    booking_end = fields.Datetime(string='Booking End')
    booking_count = fields.Integer(string='Booking Order', compute='_compute_booking_count')

    @api.multi
    @api.depends('state')
    def _compute_booking_count(self):
        for order in self:
            wo = order.env['work.order'].search([('booking_order_reference', '=', order.id)])
            if wo:
                order.booking_count = 1
    
    @api.multi
    def action_view_booking(self):
                
        action = self.env.ref('action_work_order').read()[0]
        return action


    @api.multi
    def action_confirm(self):
        for rec in self:
            res = super(SaleOrderInherit, self).action_confirm() if super(SaleOrderInherit, self).action_confirm else True
            if rec.check_availability():
                work_order = rec.env['work.order'].create({
                                'team' : rec.team.id,
                                'team_leader': rec.team_leader.id,
                                'planned_start' : rec.booking_start,
                                'planned_end': rec.booking_end,
                                'booking_order_reference': rec.id
                            })
                work_order.write({
                    'team_members': [(6, 0, rec.team_members.ids)]
                })
                # rec.action_view_work_orders()
                
                return res
            raise UserError(_('Team is not available during this period, already booked on %s. Please book on another date.') % (rec.name))
        return res
    
    def action_view_work_orders(self):
        print('sssssssssssssssss')
        self.ensure_one()
        action = self.env.ref('booking_order_asep_17122024.action_work_order')
        result = action.read()[0]
        result['domain'] = [('booking_order_reference', '=', self.id)]
        result['context'] = {
            'default_booking_order_reference': self.id,
            'default_team': self.team.id,
            'default_team_leader': self.team_leader.id,
            'default_team_members': [(6, 0, self.team_members.ids)],
            'default_planned_start': self.booking_start,
            'default_planned_end': self.booking_end,
        }
  
        print(result)
        return result

    @api.onchange('team')
    def _onchange_team(self):
        if not self.team:
            self.team_leader = False
            self.team_members = False
        self.team_leader = self.team.team_leader.id
        self.team_members = [(6, 0, self.team.team_members.ids)]

    @api.multi
    def check_availability(self):
        for rec in self:
            wo = rec.env['work.order'].search([
                '|',
                ('team', '=', rec.team.id),
                ('team_leader', '=', rec.team_leader.id),
                ('state', '!=', 'cancelled')
            ])
            for data in wo:
                if rec.booking_start <= data.planned_end and rec.booking_end >= data.planned_start:
                    return False
                else:
                    return True
            return True

    @api.multi
    def action_check_work_order(self):
        for rec in self:
            if self.check_availability():
                raise Warning(_('Team is available for booking'))
            raise UserError(_('Team already has work order during that period on %s.') % (rec.name))