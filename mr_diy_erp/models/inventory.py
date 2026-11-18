from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    transfer_type = fields.Selection([
        ('in', 'Transfer-In'),
        ('out', 'Transfer-Out'),
        ('keep', 'Keep-Stock')
    ], string='Tipe Transfer')
    pdt_scan_code = fields.Char(string='Kode Scan PDT')
