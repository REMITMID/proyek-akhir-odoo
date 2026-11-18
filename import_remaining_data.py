import os
import sys
import pandas as pd
from datetime import datetime

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
    print("Menghubungkan ke Odoo untuk pelengkap data presensi & rekrutmen...")
    odoo.tools.config.parse_config(['-c', ODOO_CONF])
    registry = odoo.registry(DB_NAME)

    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})

        # 1. IMPORT DATA PRESENSI (Attendance)
        print("\n[1/3] Mengimpor Data Presensi / Absensi Karyawan...")
        df_presensi = load_sheet('Data Presensi')
        att_obj = env['hr.attendance']
        emp_obj = env['hr.employee']

        imported_att = 0
        for _, row in df_presensi.iterrows():
            nama = str(row.get('nama_karyawan', '')).strip()
            tgl = str(row.get('tanggal', ''))[:10]
            jam_masuk = str(row.get('jam_masuk', ''))
            jam_pulang = str(row.get('jam_pulang', ''))
            terlambat = int(row.get('menit_terlambat', 0)) if pd.notnull(row.get('menit_terlambat')) else 0

            emp = emp_obj.search([('name', '=', nama)], limit=1)
            if emp and tgl and jam_masuk and jam_masuk != 'nan':
                try:
                    check_in_str = f"{tgl} {jam_masuk}"
                    check_in = datetime.strptime(check_in_str, "%Y-%m-%d %H:%M:%S")
                    check_out = None
                    if jam_pulang and jam_pulang != 'nan':
                        check_out_str = f"{tgl} {jam_pulang}"
                        check_out = datetime.strptime(check_out_str, "%Y-%m-%d %H:%M:%S")

                    # hitung denda jika terlambat (misal Rp 1.000 per menit)
                    penalty = terlambat * 1000.0

                    att_obj.create({
                        'employee_id': emp.id,
                        'check_in': check_in,
                        'check_out': check_out,
                        'penalty_amount': penalty,
                    })
                    imported_att += 1
                except Exception as e:
                    pass
        print(f" -> Selesai mengimpor {imported_att} Data Presensi Karyawan.")

        # 2. IMPORT DATA REKRUTMEN (Recruitment)
        print("\n[2/3] Mengimpor Data Pelamar & Rekrutmen...")
        df_rekrutmen = load_sheet('Data Rekrutmen')
        applicant_obj = env['hr.applicant']
        job_obj = env['hr.job']

        imported_rec = 0
        for _, row in df_rekrutmen.iterrows():
            nama_pelamar = str(row.get('nama_lengkap', '')).strip()
            posisi = str(row.get('posisi_dilamar', 'Staff Toko')).strip()
            status_kandidat = str(row.get('status_kandidat', ''))

            if not nama_pelamar or nama_pelamar == 'nan': continue

            job = job_obj.search([('name', '=', posisi)], limit=1)
            if not job:
                job = job_obj.create({'name': posisi})

            existing = applicant_obj.search([('partner_name', '=', nama_pelamar)], limit=1)
            if not existing:
                applicant_obj.create({
                    'name': f"Lamaran {posisi} - {nama_pelamar}",
                    'partner_name': nama_pelamar,
                    'job_id': job.id,
                    'interview_score': 85.0 if 'Setuju' in status_kandidat else 60.0,
                })
                imported_rec += 1
        print(f" -> Selesai mengimpor {imported_rec} Data Pelamar Rekrutmen.")

        # 3. IMPORT DATA LOWONGAN WEBSITE (Website Careers)
        print("\n[3/3] Mengimpor Lowongan Karir Website MR. DIY...")
        web_job_obj = env['website.job.post']
        posisi_unik = df_rekrutmen['posisi_dilamar'].dropna().unique()
        for pos in posisi_unik:
            p_str = str(pos).strip()
            if not p_str: continue
            existing = web_job_obj.search([('name', '=', p_str)], limit=1)
            if not existing:
                web_job_obj.create({
                    'name': f"Lowongan {p_str} (Store Crew)",
                    'location': "Seluruh Gerai MR. DIY Indonesia",
                    'description': f"<p>Bergabunglah bersama keluarga besar PT Daya Intiguna Yasa Tbk sebagai <b>{p_str}</b>.</p>",
                    'apply_url': "https://www.mrdiy.com/id/career",
                })
        print(f" -> Selesai mengimpor {len(posisi_unik)} Lowongan Website MR. DIY.")

        cr.commit()
        print("\nSEMUA MODUL & DATA TAMBAHAN SELESAI 100%! 🎉")

if __name__ == '__main__':
    main()
