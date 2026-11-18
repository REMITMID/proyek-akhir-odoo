from odoo import models, fields, api

class HrPayslipCustom(models.Model):
    _name = 'mr_diy.payroll'
    _description = 'MR DIY Payroll & Gaji'

    name = fields.Char(string='Nomor Slip Gaji', required=True)
    employee_id = fields.Many2one('hr.employee', string='Karyawan', required=True)
    date_from = fields.Date(string='Periode Dari', default=fields.Date.context_today)
    date_to = fields.Date(string='Periode Sampai', default=fields.Date.context_today)
    gaji_pokok = fields.Monetary(string='Gaji Pokok', currency_field='currency_id')
    total_tunjangan = fields.Monetary(string='Total Tunjangan', currency_field='currency_id')
    lembur = fields.Monetary(string='Uang Lembur', currency_field='currency_id')
    insentif = fields.Monetary(string='Insentif / Bonus', currency_field='currency_id')
    potongan_bpjs = fields.Monetary(string='Potongan BPJS', currency_field='currency_id')
    potongan_pph21 = fields.Monetary(string='Potongan PPh 21', currency_field='currency_id')
    total_potongan = fields.Monetary(string='Total Potongan', currency_field='currency_id')
    gaji_bersih = fields.Monetary(string='Gaji Bersih (Take Home Pay)', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Mata Uang', default=lambda self: self.env.company.currency_id)
    status_transfer = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Disetujui'),
        ('paid', 'Berhasil Transfer'),
        ('failed', 'Gagal Transfer')
    ], string='Status Transfer', default='draft')
    no_referensi_bank = fields.Char(string='No Referensi Bank')
