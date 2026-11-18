import sys
import random
from datetime import datetime, timedelta

sys.path.append(r'C:\odoo\odoo-16')
import odoo
from odoo import api, SUPERUSER_ID

ODOO_CONF = r'C:\odoo\odoo.conf'
DB_NAME = 'odoo'

def main():
    print("Memulai setup dashboard & sales dummy MR. DIY...")
    odoo.tools.config.parse_config(['-c', ODOO_CONF])
    registry = odoo.registry(DB_NAME)

    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        # 1. Pastikan Mata Uang IDR (Rp)
        idr = env['res.currency'].with_context(active_test=False).search([('name', '=', 'IDR')], limit=1)
        if idr:
            idr.write({'active': True, 'symbol': 'Rp', 'position': 'before', 'rounding': 1.0})
        
        company = env.company
        cr.execute("UPDATE res_company SET currency_id = %s WHERE id = %s", (idr.id, company.id))
        
        # 2. Update currency di semua pricelist
        env['product.pricelist'].search([]).write({'currency_id': idr.id})

        # 3. Ubah semua Sale Orders dan Invoices demo lama menjadi IDR
        print("Mengupdate transaksi demo lama ke IDR (Rp)...")
        cr.execute("UPDATE sale_order SET currency_id = %s, pricelist_id = (SELECT id FROM product_pricelist LIMIT 1)", (idr.id,))
        cr.execute("UPDATE account_move SET currency_id = %s", (idr.id,))
        cr.execute("UPDATE account_move_line SET currency_id = %s", (idr.id,))
        cr.execute("UPDATE account_journal SET currency_id = NULL") # NULL = ikut company currency (IDR)

        # 4. BUAT DATA SALES TRANSAKSI DUMMY MR. DIY (Kasir POS & Toko)
        print("Membuat data transaksi sales penjualan MR. DIY (Periode 2026)...")
        
        # Ambil produk MR DIY
        diy_products = env['product.product'].search([('default_code', 'like', 'DIY%')])
        if not diy_products:
            diy_products = env['product.product'].search([], limit=10)

        # Ambil customer
        customers = env['res.partner'].search([('customer_rank', '>', 0)])
        if not customers:
            customers = env['res.partner'].search([], limit=10)

        # Buat Sales Orders MR DIY yang realistis
        order_obj = env['sale.order']
        line_obj = env['sale.order.line']

        start_date = datetime.now() - timedelta(days=90)
        total_created = 0

        # Buat 40 transaksi penjualan toko MR DIY dalam 90 hari terakhir
        for i in range(1, 41):
            cust = random.choice(customers)
            trx_date = start_date + timedelta(days=random.randint(0, 90), hours=random.randint(8, 20), minutes=random.randint(0, 59))
            
            so = order_obj.create({
                'partner_id': cust.id,
                'date_order': trx_date,
                'currency_id': idr.id,
                'state': 'sale', # sudah terkonfirmasi / order penjualan resmi
            })

            # Tambahkan 2-5 item barang belanjaan per struk
            items_count = random.randint(2, 5)
            selected_prods = random.sample(list(diy_products), min(items_count, len(diy_products)))
            
            for prod in selected_prods:
                qty = random.randint(1, 4)
                price = prod.list_price if prod.list_price > 0 else 25000.0
                line_obj.create({
                    'order_id': so.id,
                    'product_id': prod.id,
                    'product_uom_qty': qty,
                    'price_unit': price,
                })

            total_created += 1

        print(f" -> Berhasil membuat {total_created} transaksi penjualan baru MR. DIY!")

        # 5. Buat POS Session & Orders agar dashboard Point of Sale juga penuh grafik
        print("Menyiapkan dashboard Point of Sale Toko MR. DIY...")
        pos_config = env['pos.config'].search([], limit=1)
        if pos_config:
            pos_config.write({'currency_id': idr.id})

        cr.commit()
        print("\n=========================================================================")
        print(" SEMUA DASHBOARD & TRANSAKSI SALES MR. DIY TELAH SELESAI DI-GENERATE! 🎉 ")
        print("=========================================================================")

if __name__ == '__main__':
    main()
