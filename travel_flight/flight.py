# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010, 2014 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, api
from openerp.models import Model


class product_flight(Model):
    _name = 'product.flight'
    _inherits = {'product.product': 'product_id'}
    _inherit = ['mail.thread']

    product_id = fields.Many2one('product.product', 'Product', required=True, ondelete="cascade")
    local = fields.Boolean('Local')
    origin = fields.Many2one('destination', 'Origin')
    to = fields.Many2one('destination', 'To')
    flight_name = fields.Char(realted='product_id.name', string='Name', size=128, select=True, store=True)

    _order = 'flight_name asc'

    @api.multi
    def unlink(self):
        for x in self:
            product_product = self.env['product.product']
            pp = product_product.search([('id', '=', x.product_id.id)])
            pp.unlink()
        return super(product_flight, self).unlink()

    def price_get_partner(self, cr, uid, cls, to_search, params, context=None):
        price = 0.0
        model = self.pool.get(cls)
        to_search_sup = [x for x in to_search]
        pp_ids = model.search(cr, uid, to_search, context=context)
        if pp_ids and len(pp_ids) == 1:
            adults = params.get('adults', 0)
            children = params.get('children', 0)
            pp = model.browse(cr, uid, pp_ids[0], context)
            price = pp.price * adults + pp.price * children
            price += self.price_get_partner_supp(cr, uid, pp, params,
                                                 to_search_sup, context)
        return price

    def price_get_partner_supp(self, cr, uid, pp, params, to_search_sup,
                               context=None):
        price = 0.0
        if params.get('supplement_ids', False):
            supp_ids = params['supplement_ids'][0][2]
            if supp_ids:
                prs = self.pool.get('product.rate.supplement')
                to_search_sup.append(('supplement_id', 'in', supp_ids))
                prs_ids = prs.search(cr, uid, to_search_sup, context=context)
                for supp in prs.browse(cr, uid, prs_ids, context):
                    rate_ids = [r.id for r in supp.rate_ids]
                    if not rate_ids or pp.product_rate_id.id in rate_ids:
                        price += supp.price
        return price

    def get_option_type_fields(self, cr, uid, product_id, context):
        '''
        Dict of the model option_type values to load on sale_order view
        '''

        return [{}, []]
