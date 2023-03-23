import xmlrpc.client
from odoo import models, fields, _
from odoo.exceptions import UserError
import base64
from lxml import etree
import re
from . import api_facturae
import logging
_logger = logging.getLogger(__name__)



url = "http://apps.ferrecocles.com"
db = 'FerreCocles'
username = 'jtapia@accura.pe'
password = '123'


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def import_payments(self):
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        version = common.version()
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        invoice_payment = models.execute_kw(db, uid, password,'account.payment', 'search_read',[[['payment_type', '=', 'inbound'],['payment_date', '>=', '01/01/2023'],['payment_date','<=','31/01/2023'],['state','=','posted']]],
                                            {'fields': ['payment_type','partner_id','communication','journal_id','amount', 'payment_date', 'invoice_ids'], 'limit': 5})



        print('PAGOS V10', invoice_payment)

        i = 0
        for pay in invoice_payment:
            list_invoices_reconcilie_v10 = []
            list_invoices_reconcilie_v15 = []
            list_invoices = list(pay['invoice_ids'])
            for rec in list_invoices:
                all_invoices = models.execute_kw(db, uid, password, 'account.invoice', 'search_read',[[['id', '=', rec]]],
                                             {'fields': ['number']})
                number_invoice = all_invoices[0]['number']
                list_invoices_reconcilie_v10.append(number_invoice)
                for num in list_invoices_reconcilie_v10:
                    new_invoice = self.env['account.move'].search([('name','=',num)])
                    list_invoices_reconcilie_v15.append(new_invoice.id)

            amount_pay = invoice_payment[i]['amount']
            date_pay = invoice_payment[i]['payment_date']
            old_partner = invoice_payment[i]['partner_id'][1]
            old_journal = invoice_payment[i]['journal_id'][1]
            abc = old_journal.find('(')
            xyz = old_partner.find(']')
            new_partner_02 = old_partner[xyz+1:].strip()
            new_journal_02 = old_journal[:abc-1].strip()
            get_new_partner = self.env['res.partner'].search([('name','=', new_partner_02)])
            get_new_journal = self.env['account.journal'].search([('name', '=', new_journal_02)])
            invoice_pay = self.env['account.payment'].create({
                'payment_type': 'inbound',
                'partner_id': get_new_partner.id,
                'amount': amount_pay,
                'date': date_pay,
                'journal_id': get_new_journal.id,
                'reconciled_invoice_ids': [(6, 0, [list_invoices_reconcilie_v15])
                ],
                })
            # self.env['account.move.line'].action_reconcile(invoice_pay)
            i += 1