from odoo import models, fields, _
from odoo.exceptions import UserError
import base64
from lxml import etree
import re
import logging
from datetime import datetime, date, timedelta
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def create_sale_order_from_invoice(self):

        for sale_id_invoice in self:
            sale_id_ = sale_id_invoice.id
            
            create_sale_order = self.env['sale.order'].create({
                'partner_id':sale_id_invoice.partner_id.id,
                'validity_date': sale_id_invoice.invoice_date + timedelta(3),
                'date_order': sale_id_invoice.invoice_date,
                'payment_term_id': '',
                'invoice_ids': sale_id_,
                'line_ids': [(0, 0, {vals0})]
                })
            for line in sale_id_invoice.line_ids:
                vals0 = {
                    'product_id': line.product_id,
                    'name': line.name,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.product_uom_id,
                    'price_unit': line.price_unit,
                    'tax_id': line.tax_ids,
                    'discount': line.discount
                }