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

    id_number_from_x = fields.Char(string='From ID Payment', store=True)
    id_number_to_x = fields.Char(string='To ID Payment', store=True)

    payment_date_from_x = fields.Date(string='From Payment Date', store=True)
    payment_date_to_x = fields.Date(string='To Payment Date', store=True)


    def import_payments(self,id_number_from_x,id_number_to_x,payment_date_from_x,payment_date_to_x):
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        version = common.version()
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        invoice_payment = models.execute_kw(db, uid, password,'account.payment', 'search_read',[[['id', '>=', id_number_from_x],['id','<=',id_number_to_x],['payment_date','>=',payment_date_from_x],['payment_date','<=',payment_date_to_x],['state','=','posted']]],
                                            {'fields': ['payment_type','partner_id','communication','journal_id','amount', 'payment_date', 'invoice_ids','name']})



        print('PAGOS V10', invoice_payment)

        i = 0
        for pay in invoice_payment:
            amount_pay = invoice_payment[i]['amount']
            name_v10 = invoice_payment[i]['name']
            date_pay = invoice_payment[i]['payment_date']
            old_partner = invoice_payment[i]['partner_id'][1]
            old_journal = invoice_payment[i]['journal_id'][1]
            abc = old_journal.find('(')
            xyz = old_partner.find(']')
            new_partner_02 = old_partner[xyz+1:].strip()
            new_journal_02 = old_journal[:abc-1].strip()
            payment_type_x = invoice_payment[i]['payment_type']
            get_new_partner = self.env['res.partner'].search([('name','=', new_partner_02),('active','=', True)])
            get_new_journal = self.env['account.journal'].search([('name', '=', new_journal_02)])
            invoice_pay = self.env['account.payment'].create({
                'payment_type': payment_type_x,
                'name': name_v10,
                'partner_id': get_new_partner.id,
                'amount': amount_pay,
                'date': date_pay,
                'journal_id': get_new_journal.id,

                })
            invoice_pay.action_post()
            self.env.cr.commit()
            i += 1

    def reconcile_invoice_with_payment(self):

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        version = common.version()
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        for record in self:
            all_payment = models.execute_kw(db, uid, password, 'account.payment', 'search_read', [[['name', '=', record.name]]],{'fields': ['invoice_ids']})
            for pay in all_payment:
                list_invoices_reconcile_v10 = []
                list_invoices_reconcile_v15 = []
                list_invoices = list(pay['invoice_ids'])
                for rec in list_invoices:
                    all_invoices = models.execute_kw(db, uid, password, 'account.invoice', 'search_read', [[['id', '=', rec]]],
                                                 {'fields': ['number']})
                    number_invoice = all_invoices[0]['number']
                    list_invoices_reconcile_v10.append(number_invoice)
                    for num in list_invoices_reconcile_v10:
                        new_invoice = self.env['account.move'].search([('name', '=', num)])
                        if new_invoice:
                            list_invoices_reconcile_v15.append(new_invoice.id)

                    for invoice in self.env['account.move'].browse(list_invoices_reconcile_v15):
                        invoice.payment_id = record.id
                        payments = invoice.mapped('payment_id')
                        move_lines = payments.line_ids.filtered(lambda line: line.account_internal_type in ('receivable', 'payable'))
                        for line in move_lines:
                            invoice.js_assign_outstanding_line(line.id)




