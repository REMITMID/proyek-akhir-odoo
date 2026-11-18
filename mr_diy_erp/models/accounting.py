from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    cash_non_operational_amount = fields.Monetary(
        string='Cash Non‑Operasional',
        help='Pendapatan kas non‑operasional (penjualan karton bekas)')

    audit_type = fields.Selection([
        ('internal', 'Audit Internal'),
        ('external', 'Audit Eksternal')
    ], string='Tipe Audit', default='internal')
