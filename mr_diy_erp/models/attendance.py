from odoo import models, fields, api

class Attendance(models.Model):
    _inherit = 'hr.attendance'

    penalty_amount = fields.Float(
        string='Denda Tidak Hadir (Rp)',
        help='Jumlah denda apabila tidak hadir tanpa izin')
