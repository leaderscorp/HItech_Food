from odoo import models, fields, api

class BundleModel(models.Model):
    _name = 'product.bundle'

    name=fields.Char(string='Name')
    product_ids=fields.One2many('product.line','bundle_id')

class ProductLines(models.Model):
    _name = 'product.line'

    bundle_id=fields.Many2one('product.bundle')
    product_id=fields.Many2one('product.product')
    qty=fields.Float(string='Quantity')
    unit_price=fields.Float(string='Unit Price')
    uom_id=fields.Many2one('uom.uom')

class ProductSoda(models.Model):
    _name='product.soda'

    partner_id=fields.Many2one('res.partner','Customer')
    bundle_id=fields.Many2one('product.bundle',required=1)
    shipping_charges=fields.Float(string='Shipping Charges',readonly=1,force_save=1)
    packing_charges=fields.Float(string='Packing Charges',readonly=1,force_save=1)
    state=fields.Selection([('Draft','Draft'),('Confirmed','Confirmed'),('Done','Done')],default='Draft')
    line_ids=fields.One2many('soda.line','soda_id')

    @api.onchange('bundle_id')
    def OnchangeBudle(self):
        vals=[]
        for line in self.bundle_id.line_ids:
            vals.append({'product_id':line.product_id.id,'unit_price':self.unit_price,'qty':line.qty})
        return

    def CreateSO(self):
        self.state='Done'

        SO=self.env['sale.order'].create({'partner_id':self.partner_id.id,'pricelist_id':self.partner_id.property_product_pricelist.id})
        for line in self.line_ids:
            self.env['sale.order.line'].create({'product_id':self.product_id.id,'product_uom_qty':self.uom_id.id})
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': SO.id,
        }

    def SetConfirmed(self):
        self.state='Confirmed'

    @api.onchange('partner_id')
    def OnchangePartner(self):
        self.shipping_charges=0
        self.packing_charges=0
        if self.partner_id:
            self.shipping_charges=self.partner_id.shipping_charges
            self.packing_charges=self.partner_id.packing_charges

class SodeLines(models.Model):
    _name='soda.line'

    soda_id=fields.Many2one('product.soda')
    product_id=fields.Many2one('product.product','Product')
    qty=fields.Float('Quantity')
    unit_price=fields.Float(string='Unit Price')
    net_amount=fields.Float('Net Amount')
    market_value=fields.Float('Market Value')
    uom_id=fields.Many2one('uom.uom')

class InheritPartner(models.Model):
    _inherit='res.partner'

    shipping_charges=fields.Float(string='Shipping Charges')
    packing_charges=fields.Float(string='Packing Charges')


class InheritSaleOrder(models.Model):
    _inherit = 'sale.order'

    soda_id=fields.Many2one('product.soda')