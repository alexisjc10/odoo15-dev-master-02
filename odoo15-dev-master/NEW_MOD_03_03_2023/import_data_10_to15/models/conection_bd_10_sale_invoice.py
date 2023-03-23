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
username = 'admin'
password = 'admin'



class SaleOrder(models.Model):
    _inherit = 'sale.order'




    def import_data_sale_invoices(self):
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        version = common.version()
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        sale_invoices = models.execute_kw(db, uid, password,'account.invoice', 'search_read',[[['type', '=', 'out_invoice'],['number','<=','00100002010000177433'],['number','>=','00100002010000171839'],['state','!=','draft'],['xml_comprobante','!=',False]]],
                                               {'fields': ['xml_comprobante','partner_id'],'limit':1})

        print("FACTURAS DE CLIENTE", sale_invoices)
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



    # def load_xml_data(self,invoice,load_lines, account_id, product_id=False, analytic_account_id=False):
    #     try:
    #         xml_string = base64.b64decode(invoice.xml_comprobante).decode("utf-8")
    #         # quita saltos de linea
    #         xml_string = xml_string.replace('\n', '')
    #         pattern = re.compile(r'>\s+<')
    #         xml_string = re.sub(pattern, '><', xml_string)
    #         invoice_xml = etree.XML(bytes(bytearray(xml_string, encoding='utf-8')))
    #         document_type = re.search(
    #             'FacturaElectronica|NotaCreditoElectronica|NotaDebitoElectronica|TiqueteElectronico',
    #             invoice_xml.tag).group(0)
    #
    #         if document_type == 'TiqueteElectronico':
    #             raise UserError(_("Los tiquetes electrónicos no son aceptados como gastos"))
    #
    #     except Exception as e:
    #         raise UserError(_("Este xml esta en un formato incorrecto: %s") % e)
    #
    #     namespaces = invoice_xml.nsmap
    #     inv_xmlns = namespaces.pop(None)
    #     namespaces['inv'] = inv_xmlns
    #
    #     # invoice.consecutive_number_receiver = invoice_xml.xpath("inv:NumeroConsecutivo", namespaces=namespaces)[0].text
    #     invoice.sequence_number = invoice_xml.xpath("inv:NumeroConsecutivo", namespaces=namespaces)[0].text
    #
    #     invoice.number_electronic = invoice_xml.xpath("inv:Clave", namespaces=namespaces)[0].text
    #     activity_node = invoice_xml.xpath("inv:CodigoActividad", namespaces=namespaces)
    #     activity = False
    #
    #     invoice.date_issuance = invoice_xml.xpath("inv:FechaEmision", namespaces=namespaces)[0].text
    #     invoice.invoice_date = invoice.date_issuance
    #     invoice.tipo_documento = False
    #
    #     emisor = invoice_xml.xpath("inv:Emisor/inv:Identificacion/inv:Numero", namespaces=namespaces)
    #
    #     receptor_node = invoice_xml.xpath("inv:Receptor/inv:Identificacion/inv:Numero", namespaces=namespaces)[0].text
    #     if emisor:
    #         emisor = emisor[0].text
    #     else:
    #         raise UserError('El emisor no está definido en el xml')  # noqa
    #
    #     if emisor != invoice.company_id.vat:
    #         raise UserError('El emisor no corresponde con la compañía actual con identificación ' +
    #                         emisor + '. Por favor active la compañía correcta.')  # noqa
    #
    #     currency_node = invoice_xml.xpath("inv:ResumenFactura/inv:CodigoTipoMoneda/inv:CodigoMoneda",
    #                                       namespaces=namespaces)
    #
    #     if currency_node:
    #         invoice.currency_id = invoice.env['res.currency'].search([('name', '=', currency_node[0].text)],
    #                                                                  limit=1).id
    #     else:
    #         invoice.currency_id = invoice.env['res.currency'].search([('name', '=', 'CRC')], limit=1).id
    #
    #     partner = invoice.env['res.partner'].search([('vat', '=', receptor_node),
    #                                                  '|',
    #                                                  ('company_id', '=', invoice.company_id.id),
    #                                                  ('company_id', '=', False)],
    #                                                 limit=1)
    #
    #     if partner:
    #         invoice.partner_id = partner
    #     else:
    #         raise UserError(_('El proveedor no existe, por favor creelo antes de cargar este documento'))
    #
    #
    #     payment_method_node = invoice_xml.xpath("inv:MedioPago", namespaces=namespaces)
    #     if payment_method_node:
    #         invoice.payment_methods_id = invoice.env['payment.methods'].search(
    #             [('sequence', '=', payment_method_node[0].text)], limit=1)
    #     else:
    #         invoice.payment_methods_id = partner.payment_methods_id
    #
    #     _logger.debug('FECR - load_lines: %s - account: %s', (load_lines, account_id))
    #
    #     product = False
    #     if product_id:
    #         product = product_id.id
    #
    #     analytic_account = False
    #     if analytic_account_id:
    #         analytic_account = analytic_account_id.id
    #
    #     # if load_lines and not invoice.invoice_line_ids:
    #     if invoice.move_type in ('out_invoice'):
    #         if load_lines:
    #             lines = invoice_xml.xpath("inv:DetalleServicio/inv:LineaDetalle", namespaces=namespaces)
    #             new_lines = invoice.env['account.move.line']
    #
    #             for line in lines:
    #                 cabys = False
    #                 exoneracion = False
    #                 cabys_node = line.xpath("inv:Codigo", namespaces=namespaces)
    #                 if cabys_node:
    #                     cabys = line.xpath("inv:Codigo", namespaces=namespaces)[0].text
    #
    #                 product_uom = invoice.env['uom.uom'].search(
    #                     [('code', '=', line.xpath("inv:UnidadMedida", namespaces=namespaces)[0].text)],
    #                     limit=1).id
    #                 total_amount = float(line.xpath("inv:MontoTotal", namespaces=namespaces)[0].text)
    #
    #                 discount_percentage = 0.0
    #                 discount_note = None
    #
    #                 if total_amount > 0:
    #                     discount_node = line.xpath("inv:Descuento", namespaces=namespaces)
    #                     if discount_node:
    #                         discount_amount_node = discount_node[0].xpath("inv:MontoDescuento", namespaces=namespaces)[
    #                             0]
    #                         discount_amount = float(discount_amount_node.text or '0.0')
    #                         discount_percentage = discount_amount / total_amount * 100
    #                         discount_note = discount_node[0].xpath("inv:NaturalezaDescuento", namespaces=namespaces)[
    #                             0].text
    #                     else:
    #                         discount_amount_node = line.xpath("inv:MontoDescuento", namespaces=namespaces)
    #                         if discount_amount_node:
    #                             discount_amount = float(discount_amount_node[0].text or '0.0')
    #                             discount_percentage = discount_amount / total_amount * 100
    #                             discount_note = line.xpath("inv:NaturalezaDescuento", namespaces=namespaces)[0].text
    #
    #                 total_tax = 0.0
    #                 taxes = []
    #
    #                 tax_nodes = line.xpath("inv:Impuesto", namespaces=namespaces)
    #                 impuesto_tasa = 0.0
    #                 for tax_node in tax_nodes:
    #                     tax_code = re.sub(r"[^0-9]+", "", tax_node.xpath("inv:Codigo", namespaces=namespaces)[0].text)
    #                     tax_amount = float(tax_node.xpath("inv:Tarifa", namespaces=namespaces)[0].text)
    #                     _logger.debug('FECR - tax_code: %s', tax_code)
    #                     _logger.debug('FECR - tax_amount: %s', tax_amount)
    #
    #                     if product_id and product_id.non_tax_deductible:
    #                         tax = invoice.env['account.tax'].search(
    #                             [('tax_code', '=', tax_code),
    #                              ('amount', '=', tax_amount),
    #                              ('type_tax_use', '=', 'sale'),
    #                              ('non_tax_deductible', '=', True),
    #                              ('active', '=', True)],
    #                             limit=1)
    #                     else:
    #                         tax = invoice.env['account.tax'].search(
    #                             [('tax_code', '=', tax_code),
    #                              ('amount', '=', tax_amount),
    #                              ('type_tax_use', '=', 'sale'),
    #                              ('active', '=', True)],
    #                             limit=1)
    #                     if tax:
    #                         total_tax += float(tax_node.xpath("inv:Monto", namespaces=namespaces)[0].text)
    #
    #                         exonerations = tax_node.xpath("inv:Exoneracion", namespaces=namespaces)
    #                         if exonerations:
    #                             for exoneration_node in exonerations:
    #                                 exoneracion_ = invoice.env['exoneration'].create({
    #                                     'date': (
    #                                         exoneration_node.xpath("inv:FechaEmision", namespaces=namespaces)[0].text),
    #                                     'display_name': (
    #                                         exoneration_node.xpath("inv:NumeroDocumento", namespaces=namespaces)[
    #                                             0].text),
    #                                     'exoneration_number': float(
    #                                         exoneration_node.xpath("inv:NumeroDocumento", namespaces=namespaces)[
    #                                             0].text),
    #                                     'name_institution':
    #                                         exoneration_node.xpath("inv:NombreInstitucion", namespaces=namespaces)[
    #                                             0].text,
    #                                     'percentage_exoneration': float(
    #                                         exoneration_node.xpath("inv:PorcentajeExoneracion", namespaces=namespaces)[
    #                                             0].text),
    #                                     'type': exoneration_node.xpath("inv:TipoDocumento", namespaces=namespaces)[
    #                                         0].text,
    #                                 })
    #                                 exoneracion = exoneracion_.id
    #
    #                         taxes.append((4, tax.id))
    #                         impuesto_tasa = tax_amount
    #                     else:
    #                         if product_id and product_id.non_tax_deductible:
    #                             raise UserError(_(
    #                                 'Tax code %s and percentage %s as non-tax deductible is not registered in the system' % (
    #                                     tax_code, tax_amount)))
    #                         else:
    #                             raise UserError(_(
    #                                 'El código de tarifa %s con el impuesto %s no existe en el sistema debe de crearlo' % (
    #                                     tax_code, tax_amount)))
    #
    #                 _logger.debug('FECR - impuestos de linea: %s' % (taxes))
    #
    #                 codigo_articulo_linea = line.xpath("inv:CodigoComercial", namespaces=namespaces)
    #                 codigo_articulo_xml = False
    #                 for codigo in codigo_articulo_linea:
    #                     codigo_articulo_xml = codigo.xpath("inv:Codigo", namespaces=namespaces)[0].text
    #                     break
    #                 product_odoo = invoice.env['product.template'].search(
    #                     [
    #                         ('old_code', '=', codigo_articulo_xml),
    #                     ],
    #                     limit=1)
    #
    #                 if product_odoo:
    #                     invoice_line = invoice.env['account.move.line'].create({
    #                         'name': line.xpath("inv:Detalle", namespaces=namespaces)[0].text,
    #                         'move_id': invoice.id,
    #                         'price_unit': float(line.xpath("inv:PrecioUnitario", namespaces=namespaces)[0].text),
    #                         'quantity': float(line.xpath("inv:Cantidad", namespaces=namespaces)[0].text),
    #                         'product_uom_id': product_uom,
    #                         'sequence': line.xpath("inv:NumeroLinea", namespaces=namespaces)[0].text,
    #                         'discount': discount_percentage,
    #                         'discount_note': discount_note,
    #                         # 'total_amount': total_amount,
    #                         'product_id': product_odoo.product_variant_id.id,
    #                         'account_id': account_id.id,
    #                         'analytic_account_id': analytic_account,
    #                         'price_subtotal': float(line.xpath("inv:SubTotal", namespaces=namespaces)[0].text),
    #                         'total_tax': total_tax,
    #                         # 'economic_activity_id': invoice.economic_activity_id.id,
    #                     })
    #                     invoice_line.tax_ids = taxes
    #                     if exoneracion:
    #                         invoice_line.exoneration_id_info = exoneracion
    #
    #                     # invoice_line.economic_activity_id = activity
    #                     new_lines += invoice_line
    #
    #                     invoice.invoice_line_ids = new_lines
    #                 else:
    #
    #                     # wizard_form = self.env.ref('cr_electronic_invoice.wirzard_from_busqueda_articulo', False)
    #                     # view = self.env.ref('cr_electronic_invoice.wirzard_from_busqueda_articulo')
    #                     xml_descripcion = '[' + codigo_articulo_xml + '] ' + \
    #                                       line.xpath("inv:Detalle", namespaces=namespaces)[0].text
    #                     return {'name': 'Relación código proveedor',
    #                             'view_type': 'form',
    #                             'view_mode': 'form',
    #                             'target': 'new',
    #                             # 'res_model': 'wizard.busqueda.articulo',
    #                             'view_id': view.id,
    #                             'views': [(view.id, 'form')],
    #                             'type': 'ir.actions.act_window',
    #                             'context': {'articulo_xml': xml_descripcion,
    #                                         'cabys': cabys,
    #                                         'proveedor_id': invoice.partner_id.id,
    #                                         'invoice_id': invoice.id,
    #                                         'codigo_producto_xml': codigo_articulo_xml,
    #                                         }
    #                             }
    #
    #                     costo = Decimal(line.xpath("inv:PrecioUnitario", namespaces=namespaces)[0].text)
    #                     imp = Decimal(impuesto_tasa)
    #                     calculo_precio = calcula_precio_venta(costo, imp)
    #                     line.xpath("inv:PrecioUnitario", namespaces=namespaces)[0].text
    #                     product_odoo = invoice.env['product.template'].create(
    #                         {
    #                             'name': line.xpath("inv:Detalle", namespaces=namespaces)[0].text,
    #                             'code_type_id': '4',
    #                             'type': 'product',
    #                             'default_code': codigo_articulo_xml,
    #                             'commercial_measurement': 'Unidad',
    #                             'standard_price': line.xpath("inv:PrecioUnitario", namespaces=namespaces)[0].text,
    #                             'list_price': calculo_precio['precio_sin_iva'],
    #                             'margen_costo': calculo_precio['margen_costo'],
    #                             'precio_ivi': calculo_precio['precio_iva_incluido'],
    #                             'taxes_id': (4, default_iva_ventas),
    #                             'cabys_code': cabys,
    #
    #                         }
    #                     )
    #                     invoice_line.invoice_line_tax_ids = taxes
    #
    #                     new_lines += invoice_line
    #
    #                     invoice.invoice_line_ids = new_lines
    #
    #             invoice.invoice_line_ids = new_lines
    #
    #     invoice.amount_total_electronic_invoice = \
    #         invoice_xml.xpath("inv:ResumenFactura/inv:TotalComprobante", namespaces=namespaces)[0].text
    #
    #     tax_node = invoice_xml.xpath("inv:ResumenFactura/inv:TotalImpuesto", namespaces=namespaces)
    #     if tax_node:
    #         invoice.amount_tax_electronic_invoice = tax_node[0].text
    #     invoice.compute_taxes()
    #     for line in invoice.invoice_line_ids:
    #         if line.invoice_id.type == 'out_invoice':
    #             if not (line.product_id.id == False):
    #                 product = self.env['product.template'].search([['old_code', '=', line.product_id.id]])
    #                 line.precio_venta_compra = product.precio_ivi
    #                 margen = 0.0
    #                 if product.taxes_id.amount > 0:
    #                     costo_unitario = (line.price_subtotal / line.quantity)
    #                     precio_sin_impuesto = product.precio_ivi / (1 + (product.taxes_id.amount / 100))
    #                     line.precio_venta_sin_impuesto = precio_sin_impuesto
    #                     if costo_unitario > 0:
    #                         margen = ((precio_sin_impuesto - costo_unitario) / costo_unitario) * 100
    #                         line.margen_venta_nuevo = margen
    #                     else:
    #                         line.linea_promocion = True
    #                 else:
    #                     costo_unitario = (line.price_subtotal / line.quantity)
    #                     precio_sin_impuesto = product.precio_ivi
    #                     line.precio_venta_sin_impuesto = precio_sin_impuesto
    #                     margen = ((precio_sin_impuesto - costo_unitario) / costo_unitario) * 100
    #                     line.margen_venta_nuevo = margen
