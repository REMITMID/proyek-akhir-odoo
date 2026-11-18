from odoo import models, fields, api

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    driver_employee_id = fields.Many2one('hr.employee', string='Pengemudi (Karyawan MR DIY)')
    fuel_qty = fields.Float(string='Qty BBM (liter)')
    fuel_cost = fields.Monetary(string='Biaya BBM')
    maintenance_date = fields.Date(string='Tanggal Servis')
    maintenance_cost = fields.Monetary(string='Biaya Servis')
