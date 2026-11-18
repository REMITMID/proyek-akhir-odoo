import sys
import random
import pandas as pd
from datetime import datetime, timedelta

sys.path.append(r'C:\odoo\odoo-16')
import odoo
from odoo import api, SUPERUSER_ID

ODOO_CONF = r'C:\odoo\odoo.conf'
DB_NAME = 'odoo'
EXCEL_PATH = r'C:\Users\CYBORG\Downloads\Compressed\Artifak proyek akhir-20261118T145028Z-1-001\Artifak proyek akhir\Data Departemen.xlsx'

def main():
    print("Memulai setup data Invoice, Purchase, dan Dashboard Sourcing MR. DIY...")
    odoo.tools.config.parse_config(['-c', ODOO_CONF])
    registry = odoo.registry(DB_NAME)

    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        idr = env['res.currency'].with_context(active_test=False).search([('name', '=', 'IDR')], limit=1)

        # -------------------------------------------------------------------------
        # 1. PERBAIKI NEGARA VENDOR (UNTUK DASHBOARD "SOURCING BY COUNTRY")
        # -------------------------------------------------------------------------
        print("\n[1/4] Mengupdate Negara Pemasok (Indonesia & China/Tiongkok)...")
        df_pemasok = pd.read_excel(EXCEL_PATH, sheet_name='Data Pemasok')
        country_id = env['res.country'].search([('code', '=', 'ID')], limit=1)
        country_cn = env['res.country'].search([('code', '=', 'CN')], limit=1)

        for _, row in df_pemasok.iterrows():
            nama = str(row.get('nama_pemasok', '')).strip()
            kode_neg = str(row.get('kode_negara', '')).strip()
            target_country = country_cn if kode_neg in ['CH', 'CN'] else country_id

            partner = env['res.partner'].search([('name', '=', nama)], limit=1)
            if partner:
                partner.write({
                    'country_id': target_country.id if target_country else False,
                    'city': str(row.get('city', '')),
                })
        print(" -> Data negara vendor berhasil diupdate!")

        # -------------------------------------------------------------------------
        # 2. IMPORT TRANSAKSI PURCHASE ORDER DARI SPREADSHEET (LENGKAP DENGAN NILAI RP BESAR)
        # -------------------------------------------------------------------------
        print("\n[2/4] Mengimpor Data Real Purchase Order (PO) MR. DIY...")
        df_po = pd.read_excel(EXCEL_PATH, sheet_name='Data Purchase Order')
        df_dpo = pd.read_excel(EXCEL_PATH, sheet_name='Data Detail PO')

        # Hapus RFQ demo bawaan odoo yang aneh (P00001 - P00008)
        demo_pos = env['purchase.order'].search([('name', 'like', 'P000%')])
        if demo_pos:
            demo_pos.button_cancel()
            demo_pos.unlink()
            print(" -> RFQ demo lama yang bernilai aneh berhasil dibersihkan.")

        po_obj = env['purchase.order']
        pol_obj = env['purchase.order.line']
        diy_products = env['product.product'].search([('default_code', 'like', 'DIY%')])
        default_prod = diy_products[0] if diy_products else env['product.product'].search([], limit=1)

        po_created = 0
        for _, row_po in df_po.iterrows():
            no_po = str(row_po.get('no_po', '')).strip()
            nama_vendor = str(row_po.get('nama_pemasok', '')).strip()
            tgl_po = str(row_po.get('tgl_po', ''))[:10]
            status_po = str(row_po.get('status_po', 'Completed')).strip()
            no_bea = str(row_po.get('no_dokumen_bea', ''))

            vendor = env['res.partner'].search([('name', '=', nama_vendor)], limit=1)
            if not vendor:
                vendor = env['res.partner'].create({
                    'name': nama_vendor, 
                    'supplier_rank': 1,
                    'country_id': country_id.id
                })

            existing_po = po_obj.search([('name', '=', no_po)], limit=1)
            if not existing_po:
                order_date = datetime.strptime(tgl_po, '%Y-%m-%d') if tgl_po and tgl_po != 'nan' else datetime.now()
                
                # Buat PO
                po = po_obj.create({
                    'name': no_po,
                    'partner_id': vendor.id,
                    'date_order': order_date,
                    'currency_id': idr.id,
                    'customs_doc_number': no_bea if no_bea != '-' else False,
                    'three_way_match_ok': True if status_po == 'Completed' else False,
                })

                # Cari baris detail PO
                dpo_rows = df_dpo[df_dpo['no_po'] == no_po]
                if not dpo_rows.empty:
                    for _, drow in dpo_rows.iterrows():
                        item_name = str(drow.get('nama_item', ''))
                        qty = float(drow.get('jumlah_pesan', 100))
                        price = float(drow.get('harga_satuan', 25000))

                        # Cari produk yang cocok atau pakai default
                        prod = env['product.product'].search([('name', 'ilike', item_name)], limit=1)
                        if not prod:
                            prod = default_prod

                        pol_obj.create({
                            'order_id': po.id,
                            'product_id': prod.id,
                            'name': item_name,
                            'product_qty': qty,
                            'price_unit': price,
                            'currency_id': idr.id,
                            'date_planned': order_date + timedelta(days=7),
                        })
                else:
                    # Default line jika tidak ada di detail
                    pol_obj.create({
                        'order_id': po.id,
                        'product_id': default_prod.id,
                        'name': 'Pengadaan Barang Rutin MR DIY',
                        'product_qty': random.randint(50, 200),
                        'price_unit': 45000.0,
                        'currency_id': idr.id,
                        'date_planned': order_date + timedelta(days=7),
                    })

                # Konfirmasi PO agar muncul di dashboard Purchase / Sourcing
                po.button_confirm()
                po_created += 1

        print(f" -> Berhasil membuat {po_created} Purchase Order resmi bernilai puluhan/ratusan juta Rupiah!")

        # -------------------------------------------------------------------------
        # 3. BUAT DATA DUMMY INVOICES BERVARIASI (UNTUK GRAFIK NAIK TURUN BULANAN)
        # -------------------------------------------------------------------------
        print("\n[3/4] Membuat Data Invoicing 6 Bulan Terakhir (Grafik Naik-Turun)...")
        # Bersihkan invoice demo lama
        cr.execute("DELETE FROM account_move_line WHERE move_id IN (SELECT id FROM account_move WHERE name LIKE 'INV/2026/000%')")
        cr.execute("DELETE FROM account_move WHERE name LIKE 'INV/2026/000%'")

        cust_list = env['res.partner'].search([('customer_rank', '>', 0)], limit=10)
        if not cust_list:
            cust_list = env['res.partner'].search([], limit=5)

        journal_sale = env['account.journal'].search([('type', '=', 'sale')], limit=1)
        
        # Simulasikan omset invoice per bulan (ada fluktuasi naik-turun yang cantik)
        # Bulan 6: 45 Juta, Bulan 7: 68 Juta, Bulan 8: 52 Juta, Bulan 9: 85 Juta, Bulan 10: 71 Juta, Bulan 11: 94 Juta
        monthly_targets = [
            (5, 5, 45000000),
            (4, 6, 68000000),
            (3, 7, 52000000),
            (2, 8, 89000000),
            (1, 9, 64000000),
            (0, 10, 105000000),
        ]

        inv_count = 0
        for months_ago, inv_qty, total_target in monthly_targets:
            month_date = datetime.now() - timedelta(days=months_ago * 30)
            avg_per_inv = total_target / inv_qty

            for j in range(inv_qty):
                inv_date = month_date + timedelta(days=random.randint(1, 26))
                cust = random.choice(cust_list)
                inv_val = avg_per_inv * random.uniform(0.7, 1.3)

                move = env['account.move'].create({
                    'move_type': 'out_invoice',
                    'partner_id': cust.id,
                    'invoice_date': inv_date,
                    'date': inv_date,
                    'currency_id': idr.id,
                    'journal_id': journal_sale.id,
                    'invoice_line_ids': [(0, 0, {
                        'name': f'Penjualan Retail Perlengkapan MR. DIY (Struk #{random.randint(100000, 999999)})',
                        'quantity': 1,
                        'price_unit': round(inv_val, -2),
                        'currency_id': idr.id,
                    })],
                })
                # Post invoice agar masuk ke grafik dashboard
                move.action_post()
                inv_count += 1

        print(f" -> Berhasil membuat {inv_count} Customer Invoices dengan grafik tren naik-turun!")

        # -------------------------------------------------------------------------
        # 4. REKALKULASI SELURUH CURRENCY DATABASE KE IDR (Rp)
        # -------------------------------------------------------------------------
        print("\n[4/4] Finalisasi mata uang & rekalkulasi...")
        cr.execute("UPDATE purchase_order SET currency_id = %s", (idr.id,))
        cr.execute("UPDATE purchase_order_line SET currency_id = %s", (idr.id,))
        cr.execute("UPDATE account_move SET currency_id = %s", (idr.id,))
        cr.execute("UPDATE account_move_line SET currency_id = %s", (idr.id,))

        cr.commit()
        print("\n=========================================================================")
        print(" SEMUA GRAFIK INVOICE, PURCHASE ORDER & SOURCING BERHASIL DIBUAT (Rp)! 🎉")
        print("=========================================================================")

if __name__ == '__main__':
    main()
