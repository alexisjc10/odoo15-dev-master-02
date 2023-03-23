# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class cr_electronic_invoice(models.Model):
#     _name = 'cr_electronic_invoice.cr_electronic_invoice'
#     _description = 'cr_electronic_invoice.cr_electronic_invoice'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
