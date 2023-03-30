import xmlrpc.client
from odoo import models, fields, _
from odoo.exceptions import UserError
import base64
from lxml import etree
import re
from . import api_facturae_sale
import logging
_logger = logging.getLogger(__name__)



url = "http://apps.ferrecocles.com"
db = 'FerreCocles'
username = 'jtapia@accura.pe'
password = '123'



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    invoice_number_from = fields.Char(string='Invoice Number From')
    invoice_number_to = fields.Char(string='Invoice Number To')
    invoice_type_charge = fields.Selection([
        ('sale_invoice', 'Sale Invoice'),
        ('sale_refund', 'Sale Refund'),
        ], string = 'Invoice Type Charge')

    def import_data_sale_invoices(self, invoice_number_from, invoice_number_to,invoice_type_charge):
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        version = common.version()
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        if invoice_type_charge == 'sale_invoice':
            sale_invoices = models.execute_kw(db, uid, password,'account.invoice', 'search_read', [[['type', '=', 'out_invoice'],['number','>=',invoice_number_from], ['number','<=',invoice_number_to],['state','!=','draft'],['xml_comprobante','!=',False]]],
                                               {'fields': ['xml_comprobante', 'partner_id']})

            for sinv in sale_invoices:
                _sale_invoice = self.env['account.move'].create({
                    'move_type': 'out_invoice',
                    'xml_comprobante': sinv['xml_comprobante']
                    })
                if _sale_invoice.xml_comprobante:
                    account = False
                    analytic_account = False
                    product = False

                    sale_journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
                    default_account_id = sale_journal.default_account_id.id
                    if default_account_id:
                        account = self.env['account.account'].search([('id', '=', default_account_id)], limit=1)
                        load_lines = sale_journal.load_lines
                    else:
                        default_account_id = self.env['ir.config_parameter'].sudo().get_param('expense_account_id')
                        load_lines = bool(self.env['ir.config_parameter'].sudo().get_param('load_lines'))
                        if default_account_id:
                            account = self.env['account.account'].search([('id', '=', default_account_id)], limit=1)
                    analytic_account_id = sale_journal.expense_analytic_account_id.id
                    if analytic_account_id:
                        analytic_account = self.env['account.analytic.account'].search(
                            [('id', '=', analytic_account_id)], limit=1)
                    else:
                        analytic_account_id = self.env['ir.config_parameter'].sudo().get_param(
                            'expense_analytic_account_id')
                        if analytic_account_id:
                            analytic_account = self.env['account.analytic.account'].search(
                                [('id', '=', analytic_account_id)],
                                limit=1)
                    product_id = sale_journal.expense_product_id.id
                    if product_id:
                        product = self.env['product.template'].search([('old_code', '=', product_id)], limit=1)
                    else:
                        product_id = self.env['ir.config_parameter'].sudo().get_param('expense_product_id')
                        if product_id:
                            product = self.env['product.template'].search([('old_code', '=', product_id)], limit=1)
                    api_facturae_sale.load_xml_data(_sale_invoice,load_lines,account, product,analytic_account)
        else:
            sale_invoices = models.execute_kw(db, uid, password, 'account.invoice', 'search_read', [[['type', '=', 'out_refund'], ['number', '>=', invoice_number_from],['number', '<=', invoice_number_to], ['state', '!=', 'draft'], ['xml_comprobante', '!=', False]]],
                                              {'fields': ['xml_comprobante', 'partner_id','invoice_id']})



            for sinv in sale_invoices:

                muestra = sinv['invoice_id'][1].strip()
                ref_invoice = self.env['account.move'].search([('move_type', '=', 'out_invoice'),('name', '=', muestra)])
                if not ref_invoice:
                    print("NO HAY FACTURA DE CLIENTE PARA REFERENCIAL")

                _sale_invoice = self.env['account.move'].create({
                    'move_type': 'out_refund',
                    'xml_comprobante': sinv['xml_comprobante'],
                    'invoice_id': ref_invoice.id
                })
                if _sale_invoice.xml_comprobante:
                    account = False
                    analytic_account = False
                    product = False

                    sale_journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
                    default_account_id = sale_journal.default_account_id.id
                    if default_account_id:
                        account = self.env['account.account'].search([('id', '=', default_account_id)], limit=1)
                        load_lines = sale_journal.load_lines
                    else:
                        default_account_id = self.env['ir.config_parameter'].sudo().get_param('expense_account_id')
                        load_lines = bool(self.env['ir.config_parameter'].sudo().get_param('load_lines'))
                        if default_account_id:
                            account = self.env['account.account'].search([('id', '=', default_account_id)], limit=1)
                    analytic_account_id = sale_journal.expense_analytic_account_id.id
                    if analytic_account_id:
                        analytic_account = self.env['account.analytic.account'].search(
                            [('id', '=', analytic_account_id)], limit=1)
                    else:
                        analytic_account_id = self.env['ir.config_parameter'].sudo().get_param(
                            'expense_analytic_account_id')
                        if analytic_account_id:
                            analytic_account = self.env['account.analytic.account'].search(
                                [('id', '=', analytic_account_id)],
                                limit=1)
                    product_id = sale_journal.expense_product_id.id
                    if product_id:
                        product = self.env['product.template'].search([('old_code', '=', product_id)], limit=1)
                    else:
                        product_id = self.env['ir.config_parameter'].sudo().get_param('expense_product_id')
                        if product_id:
                            product = self.env['product.template'].search([('old_code', '=', product_id)], limit=1)
                    api_facturae_sale.load_xml_data(_sale_invoice, load_lines, account, product, analytic_account)