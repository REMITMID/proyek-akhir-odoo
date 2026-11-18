from odoo import models, fields, api

class PosOrder(models.Model):
    _inherit = 'pos.order'

    store_id = fields.Many2one('stock.warehouse', string='Store / Toko MR. DIY')
    total_sale = fields.Monetary(string='Total Penjualan')
