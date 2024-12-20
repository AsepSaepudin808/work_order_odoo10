from odoo import models, fields

class ServiceTeam(models.Model):
    _name = 'service.team'
    _description = 'Service Team'

    team_name = fields.Char(string='Team Name', required=True)
    team_leader = fields.Many2one('res.users', string='Team Leader', required=True)
    team_members = fields.Many2many('res.users', string='Team Members')

    def name_get(self):
       result = []
       for record in self:
           name = record.team_name or "Unnamed Team"
           result.append((record.id, name))
       return result