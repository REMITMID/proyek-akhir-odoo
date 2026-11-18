from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    customs_doc_number = fields.Char(string='Nomor Dokumen Bea Cukai')
    three_way_match_ok = fields.Boolean(
        string='Three‑Way Matching',
        help='Apakah faktur vendor sudah ter‑match dengan PO & penerimaan barang')
