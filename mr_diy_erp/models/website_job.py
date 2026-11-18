from odoo import models, fields, api

class WebsiteJobPost(models.Model):
    _name = 'website.job.post'
    _description = 'Lowongan Kerja di Website MR DIY'

    name = fields.Char(string='Judul Lowongan', required=True)
    description = fields.Html(string='Deskripsi Pekerjaan')
    location = fields.Char(string='Lokasi Cabang / Toko')
    department_id = fields.Many2one('hr.department', string='Departemen')
    posted_date = fields.Datetime(string='Tanggal Posting', default=fields.Datetime.now)
    apply_url = fields.Char(string='URL Pendaftaran')
