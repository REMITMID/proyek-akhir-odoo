from odoo import models, fields, api

class QualityCheckCustom(models.Model):
    _name = 'mr_diy.quality_check'
    _description = 'MR DIY Quality Control & BASK'

    name = fields.Char(string='No QC / BASK', required=True)
    product_name = fields.Char(string='Nama Produk / Sampel')
    tgl_lapor = fields.Date(string='Tanggal Pemeriksaan', default=fields.Date.context_today)
    jumlah_rusak = fields.Integer(string='Jumlah Rusak', default=0)
    jumlah_selisih = fields.Integer(string='Jumlah Selisih', default=0)
    keterangan = fields.Text(string='Keterangan Kerusakan / Uji')
    status_klaim = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved / Lolos'),
        ('rejected', 'Rejected / Gagal')
    ], string='Status Klaim / Uji', default='pending')
    bask_claim = fields.Boolean(string='Klaim BASK', default=False)
    sni_certificate = fields.Char(string='Sertifikat SNI')
