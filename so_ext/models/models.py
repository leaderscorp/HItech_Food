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

    _rec_name = 'partner_id'

    partner_id=fields.Many2one('res.partner','Customer')
    bundle_id=fields.Many2one('product.bundle')
    bundle_ids=fields.Many2many('product.bundle',string='Items')
    shipping_charges=fields.Float(string='Shipping Charges',readonly=1,force_save=1)
    delivery_terms=fields.Float(string='Delivery Terms',readonly=1,force_save=1)
    packing_charges=fields.Float(string='Packing Charges',readonly=1,force_save=1)
    state=fields.Selection([('Draft','Draft'),('Confirmed','Confirmed'),('Done','Done')],default='Draft')
    line_ids=fields.One2many('soda.line','soda_id')

    @api.onchange('bundle_ids')
    def OnchangeBudle(self):
        vals=[]
        if self.bundle_ids:
            self.line_ids=False
            print(self.bundle_ids)
            for bundle in self.bundle_ids:
                for line in bundle.product_ids:
                    vals.append((0,0,{'product_id':line.product_id.id,'unit_price':line.unit_price,'qty':line.qty}))
            self.line_ids=vals

    def CreateSO(self):
        self.state='Done'

        SO=self.env['sale.order'].create({'partner_id':self.partner_id.id,'pricelist_id':self.partner_id.property_product_pricelist.id,'soda_id':self.id})
        tax=self.env['account.tax'].search([('soda_tax','=',True)],limit=1)
        for line in self.line_ids:
            self.env['sale.order.line'].create({'order_id':SO.id,'product_id':line.product_id.id,'product_uom':line.uom_id.id,'price_unit':line.unit_so,'product_uom_qty':line.qty,'tax_id':(4,tax.id)})
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
            self.delivery_terms=self.partner_id.delivery_terms

class SodeLines(models.Model):
    _name='soda.line'

    soda_id=fields.Many2one('product.soda')
    product_id=fields.Many2one('product.product','Product')
    qty=fields.Float('Quantity')
    unit_price=fields.Float(string='Soda/Maund')
    net_amount=fields.Float('Net Amount')
    market_value=fields.Float('Market Rate')
    uom_id=fields.Many2one('uom.uom')
    unit_so=fields.Float(string='Per Unit Amount')

    @api.onchange('net_amount')
    def GetSoUnit(self):
        for line in self:
            line.unit_so=(line.net_amount-(line.net_amount*0.17))/line.qty

class InheritPartner(models.Model):
    _inherit='res.partner'

    shipping_charges=fields.Float(string='Shipping Charges')
    packing_charges=fields.Float(string='Packing Charges')


class InheritSaleOrder(models.Model):
    _inherit = 'sale.order'

    soda_id=fields.Many2one('product.soda')

    # @api.onchange('soda_id')
    # def GetProductines(self):
    #     tax=self.env['account.tax'].search([('soda_tax','=',True)],limit=1)
    #     for line in self.soda_id.line_ids:
    #         self.env['sale.order.line'].create({'product_id':line.product_id.id,'product_uom':line.uom_id.id,'price_unit':line.unit_so,'qty':line.qty,'tax_id':(4,tax.id)})

class InheritAccountTax(models.Model):
    _inherit = 'account.tax'

    soda_tax=fields.Boolean()