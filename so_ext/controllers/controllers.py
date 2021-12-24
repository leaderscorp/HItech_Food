# -*- coding: utf-8 -*-
# from odoo import http


# class SoExt(http.Controller):
#     @http.route('/so_ext/so_ext/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/so_ext/so_ext/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('so_ext.listing', {
#             'root': '/so_ext/so_ext',
#             'objects': http.request.env['so_ext.so_ext'].search([]),
#         })

#     @http.route('/so_ext/so_ext/objects/<model("so_ext.so_ext"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('so_ext.object', {
#             'object': obj
#         })
