from odoo import models, fields, api

class HREmployee(models.Model):
    _inherit = 'hr.employee'

    department_id = fields.Many2one('hr.department', string='Departemen')
    job_grade = fields.Char(string='Grade Jabatan')
    status = fields.Selection([
        ('active', 'Aktif'),
        ('resigned', 'Resign'),
        ('on_leave', 'Cuti')
    ], string='Status')
