from odoo import models, fields, _
from odoo.exceptions import UserError
import base64
from lxml import etree
import re
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    old_code = fields.Char(string='Old Code')



class ProductSupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    operation_supp = fields.Selection([('multiply', 'Multiply'), ('divide', 'Divide')], string='Operacion Conversion',
                                      default='multiply')
    factor_conversion = fields.Float(string='Factor Conversion')

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    xml_supplier_approval = fields.Binary(string="XML Migration", copy=False, attachment=True)

class AccountMove(models.Model):
    _inherit = 'account.move.line'

    old_code_x = fields.Char(related='product_id.old_code')


