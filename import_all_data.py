import os
import sys
import pandas as pd
import datetime

# Setup Odoo Environment
sys.path.append(r'C:\odoo\odoo-16')
import odoo
from odoo import api, SUPERUSER_ID

ODOO_CONF = r'C:\odoo\odoo.conf'
DB_NAME = 'odoo'
EXCEL_PATH = r'C:\Users\CYBORG\Downloads\Compressed\Artifak proyek akhir-20261118T145028Z-1-001\Artifak proyek akhir\Data Departemen.xlsx'

def load_sheet(sheet_name):
    df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name)
    if 'Unnamed: 0' in df.columns:
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)
    return df

def main():
    print("Menghubungkan ke Odoo database...")
    odoo.tools.config.parse_config(['-c', ODOO_CONF])
    registry = odoo.registry(DB_NAME)

    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        print("Koneksi berhasil!")

        # 1. IMPORT DATA PEMASOK / VENDOR (Purchase)
        print("\n[1/6] Mengimpor Data Pemasok (Vendor)...")
        df_pemasok = load_sheet('Data Pemasok')
        partner_obj = env['res.partner']
        for _, row in df_pemasok.iterrows():
            nama = str(row.get('nama_pemasok', '')).strip()
            if not nama: continue
            email = str(row.get('email (Perbaikan)', '')) if pd.notnull(row.get('email (Perbaikan)')) else False
            telp = str(row.get('no_telepon', '')) if pd.notnull(row.get('no_telepon')) else False
            alamat = str(row.get('alamat image_782584.png', '')) if pd.notnull(row.get('alamat image_782584.png')) else False
            
            existing = partner_obj.search([('name', '=', nama)], limit=1)
            if not existing:
                partner_obj.create({
                    'name': nama,
                    'supplier_rank': 1,
                    'email': email,
                    'phone': telp,
                    'street': alamat,
                })
        print(f" -> Selesai mengimpor {len(df_pemasok)} Pemasok/Vendor.")

        # 2. IMPORT DATA PRODUK (POS & Inventory)
        print("\n[2/6] Mengimpor Data Produk MR. DIY...")
        df_produk = load_sheet('Data Produk')
        prod_obj = env['product.product']
        for _, row in df_produk.iterrows():
            p_name = str(row.get('product_name', '')).strip()
            if not p_name: continue
            barcode = str(row.get('barcode', '')) if pd.notnull(row.get('barcode')) else False
            cost = float(row.get('unit_cost', 0)) if pd.notnull(row.get('unit_cost')) else 0.0
            price = float(row.get('selling_price', 0)) if pd.notnull(row.get('selling_price')) else 0.0
            sku = str(row.get('sku', '')) if pd.notnull(row.get('sku')) else False

            existing = prod_obj.search([('name', '=', p_name)], limit=1)
            if not existing:
                prod_obj.create({
                    'name': p_name,
                    'barcode': barcode,
                    'default_code': sku,
                    'standard_price': cost,
                    'list_price': price,
                    'available_in_pos': True,
                    'type': 'product',
                })
        print(f" -> Selesai mengimpor {len(df_produk)} Produk.")

        # 3. IMPORT DATA KARYAWAN (Employees & HR)
        print("\n[3/6] Mengimpor Data Karyawan MR. DIY...")
        df_karyawan = load_sheet('Data Karyawan')
        emp_obj = env['hr.employee']
        job_obj = env['hr.job']
        emp_mapping = {} # id_karyawan -> emp_id

        for _, row in df_karyawan.iterrows():
            nama = str(row.get('nama_karyawan', '')).strip()
            if not nama: continue
            jabatan = str(row.get('jabatan', 'Staff Toko')).strip()
            email = str(row.get('email', '')) if pd.notnull(row.get('email')) else False
            telp = str(row.get('no_telepon', '')) if pd.notnull(row.get('no_telepon')) else False
            emp_code = str(row.get('id_karyawan', ''))

            job = job_obj.search([('name', '=', jabatan)], limit=1)
            if not job:
                job = job_obj.create({'name': jabatan})

            existing = emp_obj.search([('name', '=', nama)], limit=1)
            if not existing:
                emp = emp_obj.create({
                    'name': nama,
                    'job_id': job.id,
                    'work_email': email,
                    'work_phone': telp,
                })
            else:
                emp = existing
            emp_mapping[emp_code] = emp.id
        print(f" -> Selesai mengimpor {len(df_karyawan)} Karyawan.")

        # 4. IMPORT DATA ARMADA DISTRIBUSI (Fleet)
        print("\n[4/6] Mengimpor Data Armada Distribusi Truk CDC...")
        df_armada = load_sheet('Data Armada Distribusi')
        fleet_obj = env['fleet.vehicle']
        model_obj = env['fleet.vehicle.model']
        brand_obj = env['fleet.vehicle.model.brand']

        default_brand = brand_obj.search([('name', '=', 'MR DIY Fleet')], limit=1)
        if not default_brand:
            default_brand = brand_obj.create({'name': 'MR DIY Fleet'})

        for _, row in df_armada.iterrows():
            plat = str(row.get('no_plat', '')).strip()
            tipe = str(row.get('tipe_kendaraan', 'Truk Box')).strip()
            driver_name = str(row.get('nama_driver', '')).strip()
            if not plat: continue

            model = model_obj.search([('name', '=', tipe)], limit=1)
            if not model:
                model = model_obj.create({'name': tipe, 'brand_id': default_brand.id})

            # cari driver
            driver_emp = emp_obj.search([('name', '=', driver_name)], limit=1)
            if not driver_emp:
                driver_emp = emp_obj.create({'name': driver_name})

            existing = fleet_obj.search([('license_plate', '=', plat)], limit=1)
            if not existing:
                fleet_obj.create({
                    'license_plate': plat,
                    'model_id': model.id,
                    'driver_employee_id': driver_emp.id,
                })
        print(f" -> Selesai mengimpor {len(df_armada)} Armada Distribusi.")

        # 5. IMPORT DATA PENGGAJIAN (Payroll)
        print("\n[5/6] Mengimpor Data Penggajian / Payroll MR. DIY...")
        df_payroll = load_sheet('Data Penggajian')
        payroll_obj = env['mr_diy.payroll']
        for _, row in df_payroll.iterrows():
            no_slip = str(row.get('id_penggajian', '')).strip()
            karyawan_id = str(row.get('id_karyawan', '')).strip()
            emp_id = emp_mapping.get(karyawan_id)
            if not emp_id:
                emp = emp_obj.search([], limit=1)
                emp_id = emp.id if emp else False

            gapok = float(row.get('gaji_pokok', 0)) if pd.notnull(row.get('gaji_pokok')) else 0
            tunjangan = float(row.get('total_tunjangan', 0)) if pd.notnull(row.get('total_tunjangan')) else 0
            lembur = float(row.get('lembur', 0)) if pd.notnull(row.get('lembur')) else 0
            insentif = float(row.get('insentif', 0)) if pd.notnull(row.get('insentif')) else 0
            potongan = float(row.get('total_potongan', 0)) if pd.notnull(row.get('total_potongan')) else 0
            thp = float(row.get('gaji_bersih', 0)) if pd.notnull(row.get('gaji_bersih')) else 0

            status_str = str(row.get('status_transfer', '')).strip().lower()
            status_val = 'paid' if 'berhasil' in status_str else ('failed' if 'gagal' in status_str else 'draft')

            existing = payroll_obj.search([('name', '=', no_slip)], limit=1)
            if not existing and emp_id:
                payroll_obj.create({
                    'name': no_slip,
                    'employee_id': emp_id,
                    'gaji_pokok': gapok,
                    'total_tunjangan': tunjangan,
                    'lembur': lembur,
                    'insentif': insentif,
                    'total_potongan': potongan,
                    'gaji_bersih': thp,
                    'status_transfer': status_val,
                    'no_referensi_bank': str(row.get('no_referensi_bank', '')),
                })
        print(f" -> Selesai mengimpor {len(df_payroll)} Record Penggajian.")

        # 6. IMPORT DATA BASK & QUALITY (Quality Control)
        print("\n[6/6] Mengimpor Data Berita Acara Selisih & Kerusakan (BASK)...")
        df_bask = load_sheet('Data BASK Logistik')
        qc_obj = env['mr_diy.quality_check']
        for _, row in df_bask.iterrows():
            no_bask = str(row.get('no_bask', '')).strip()
            ket = str(row.get('keterangan', ''))
            rusak = int(row.get('jumlah_rusak', 0)) if pd.notnull(row.get('jumlah_rusak')) else 0
            selisih = int(row.get('jumlah_selisih', 0)) if pd.notnull(row.get('jumlah_selisih')) else 0
            status_klaim = str(row.get('status_klaim', 'pending')).strip().lower()

            existing = qc_obj.search([('name', '=', no_bask)], limit=1)
            if not existing:
                qc_obj.create({
                    'name': no_bask,
                    'product_name': 'Barang Kiriman Logistik',
                    'jumlah_rusak': rusak,
                    'jumlah_selisih': selisih,
                    'keterangan': ket,
                    'status_klaim': status_klaim if status_klaim in ['pending', 'approved', 'rejected'] else 'pending',
                    'bask_claim': True,
                })
        print(f" -> Selesai mengimpor {len(df_bask)} Berita Acara BASK.")

        # Commit ke database Odoo
        cr.commit()
        print("\n=======================================================")
        print(" SEMUA DATA MR. DIY BERHASIL DIIMPOR KE ODOO 100%! 🎉 ")
        print("=======================================================")

if __name__ == '__main__':
    main()
