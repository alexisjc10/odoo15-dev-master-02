import xmlrpc.client
from odoo import models, fields, _
from odoo.exceptions import UserError
import base64
from lxml import etree
import re
import logging
_logger = logging.getLogger(__name__)




class InsertInvoiceNUmber(models.TransientModel):
    _name = 'insert.invoice.number'

    invoice_number_from_x = fields.Char(string='From Invoice Number', store=True)
    invoice_number_to_x = fields.Char(string='To Invoice Number', store=True)
    invoice_type_charge_x = fields.Selection([
        ('sale_invoice', 'Sale Invoice'),
        ('sale_refund', 'Sale Refund'),
        ], string = 'Invoice Type Charge')

    def import_data_sale(self):

        sale_order = self.env['sale.order']
        number_from = self.invoice_number_from_x
        number_to = self.invoice_number_to_x
        invoice_type_charge = self.invoice_type_charge_x

        sale_order.import_data_sale_invoices(number_from, number_to,invoice_type_charge)

class InsertPurchaseInvoiceNumber(models.TransientModel):
    _name = 'insert.purchase.invoice.number'

    invoice_number_from_y = fields.Char(string='From Invoice Number', store=True)
    invoice_number_to_y = fields.Char(string='To Invoice Number', store=True)
    invoice_type_charge_y = fields.Selection([
        ('purchase_invoice', 'Purchase Invoice'),
        ('purchase_refund', 'Purchase Refund'),
        ], string = 'Invoice Type Charge')

    def import_data_purchase(self):

        purchase_order = self.env['purchase.order']
        number_from_p = self.invoice_number_from_y
        number_to_p = self.invoice_number_to_y
        invoice_type_charge_p = self.invoice_type_charge_y

        purchase_order.import_data_sale_invoices(number_from_p, number_to_p,invoice_type_charge_p)



