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
username = 'admin'
password = 'admin'



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    def import_data_purchase_invoices(self):
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        version = common.version()
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        facturas_proveedor = models.execute_kw(db, uid, password,'account.invoice', 'search_read',[[['type', '=', 'in_invoice'],['date_invoice','>=','01/01/2023'],['date_invoice','<=','31/01/2023'],['state','!=','draft'],['xml_supplier_approval','!=',False]]],
                                               {'fields': ['xml_supplier_approval','partner_id'],'limit':2})

        for factura in facturas_proveedor:
            order = self.env['account.move'].create({
                'move_type': 'in_invoice',
                'xml_supplier_approval': factura['xml_supplier_approval']
                })
            if order.xml_supplier_approval:
                account = False
                analytic_account = False
                product = False

                purchase_journal = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
                default_account_id = purchase_journal.expense_account_id.id
                if default_account_id:
                    account = self.env['account.account'].search([('id', '=', default_account_id)], limit=1)
                    load_lines = purchase_journal.load_lines
                else:
                    default_account_id = self.env['ir.config_parameter'].sudo().get_param('expense_account_id')
                    load_lines = bool(self.env['ir.config_parameter'].sudo().get_param('load_lines'))
                    if default_account_id:
                        account = self.env['account.account'].search([('id', '=', default_account_id)], limit=1)
                analytic_account_id = purchase_journal.expense_analytic_account_id.id
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
                product_id = purchase_journal.expense_product_id.id
                if product_id:
                    product = self.env['product.product'].search([('id', '=', product_id)], limit=1)
                else:
                    product_id = self.env['ir.config_parameter'].sudo().get_param('expense_product_id')
                    if product_id:
                        product = self.env['product.product'].search([('id', '=', product_id)], limit=1)
                api_facturae.load_xml_data(order,load_lines, account, product, analytic_account)