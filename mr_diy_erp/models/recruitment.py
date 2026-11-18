from odoo import models, fields, api

class RecruitmentJob(models.Model):
    _inherit = 'hr.job'

    source = fields.Selection([
        ('website', 'Website Karir MR DIY'),
        ('referral', 'Referral Internal'),
        ('agency', 'Agency / Bursa Kerja')
    ], string='Sumber Lowongan', default='website')

class HRApplicant(models.Model):
    _inherit = 'hr.applicant'

    interview_score = fields.Float(string='Skor Interview')
    offer_letter = fields.Binary(string='Surat Penawaran / Offering')
