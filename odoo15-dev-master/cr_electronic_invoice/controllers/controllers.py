# -*- coding: utf-8 -*-
# from odoo import http


# class CrElectronicInvoice(http.Controller):
#     @http.route('/cr_electronic_invoice/cr_electronic_invoice', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cr_electronic_invoice/cr_electronic_invoice/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cr_electronic_invoice.listing', {
#             'root': '/cr_electronic_invoice/cr_electronic_invoice',
#             'objects': http.request.env['cr_electronic_invoice.cr_electronic_invoice'].search([]),
#         })

#     @http.route('/cr_electronic_invoice/cr_electronic_invoice/objects/<model("cr_electronic_invoice.cr_electronic_invoice"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cr_electronic_invoice.object', {
#             'object': obj
#         })
