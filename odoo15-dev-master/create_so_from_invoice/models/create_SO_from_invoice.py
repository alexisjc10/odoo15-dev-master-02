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
                'partner_id': sale_id_invoice.partner_id.id,
                'validity_date': sale_id_invoice.invoice_date + timedelta(3),
                'date_order': sale_id_invoice.invoice_date,
                'payment_term_id': '',
                'invoice_ids': sale_id_,
                # 'state': 'sale'
            })

            order_lines_x = []
            for line in sale_id_invoice.invoice_line_ids:
                order_lines_x.append({
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'product_uom_qty': line.quantity,
                    'qty_invoiced': line.quantity,
                    # 'product_uom': line.product_uom_id.id,
                    'price_unit': line.price_unit,
                    'tax_id': line.tax_ids.ids,
                    'discount': line.discount,
                    'invoice_lines': list(line.ids),
                    'qty_delivered': line.quantity,
                })

            for line_x in order_lines_x:
                create_sale_order.order_line = [((0, 0, line_x))]

    def corregir_UDM_invoice(self):

        for inv in self:
            inv.tipo_documento = 'FE'
            for line in inv.invoice_line_ids:
                line.product_uom_id = line.product_id.uom_id

    # def asignar_secuencia_fact_provee(self):
    #     for inv in self:
    #         inv.name = inv.purchase_id.origin

class SaleOrder(models.Model):


    _inherit = 'sale.order'

    def add_product_invoice(self):

        for sale_order in self:
            for line in sale_order.order_line:
                line.move_ids.picking_id.state = 'cancel'

    def confirm_order_change_ware(self):
        for sale_order in self:
            sale_order.state = 'draft'

class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    def asignar_secuencia_fact_provee(self):
        for inv in self:
            inv.invoice_ids.name = inv.origin
