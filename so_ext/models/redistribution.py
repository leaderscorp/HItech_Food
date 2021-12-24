from odoo import fields,models,api
from datetime import datetime


class InheritAccountMove(models.Model):
    _inherit='account.move'

    bill_to=fields.Many2one('res.partner')

class InheritStockMove(models.Model):
    _inherit='stock.move'

    weight=fields.Float(string='Weight')

    @api.onchange('quantity_done')
    def GetWeightDetail(self):
        for rec in self:
            sale=self.env['sale.order'].search([('name', '=', self.picking_id.origin)])
            rec.quantity_done=0
            for line in sale.order_line.filtered(lambda x:x.product_id==rec.product_id):
                rec.weight=(line.total_weight/line.product_uom_qty)*rec.quantity_done

class InheritStockPicking(models.Model):
    _inherit='stock.picking'

    freight_rate=fields.Float(string='Freight Rate')
    gate_pass_date=fields.Date(string='Gate Pass Date')
    gate_pass_no=fields.Date(string='Gate Pass#')
    bilty_no=fields.Date(string='Bilty#')
    vehicle_no=fields.Date(string='Vehicle#')
    is_from_soda=fields.Boolean(compute='CheckSodaDetail')
    ship_to=fields.Many2one('res.partner')

    def CheckSodaDetail(self):
        self.is_from_soda=False
        for sale in self.env['sale.order'].search([('name','=',self.origin)]):
            if sale.soda_id:
                self.is_from_soda=True


class ReDistribution(models.Model):
    _name='redistribution.claim'

    picking_id=fields.Many2one('stock.picking',required=1)
    date=fields.Date(string='Date')
    name=fields.Char(string='Name')
    location_id=fields.Many2one('stock.location',related='picking_id.location_id',store=True)
    line_ids=fields.One2many('distribution.line','claim_id')
    state=fields.Selection([('Draft','Draft'),('Waiting For Approval','Waiting For Approval'),('Approved','Approved')],default='Draft')

    def submit(self):
        self.state='Waiting For Approval'

    def approved(self):
        self.state='Approved'
        product_id=self.env['product.product'].search([('name', '=', 'Redistribution Claim')], limit=1)
        amount_total=0
        for line in self.line_ids:
            amount_total+=line.amount
        invoice=self.env['account.move'].create({'move_type':'out_refund','partner_id':self.picking_id.partner_id.id,'journal_id':self.env['account.journal'].search([('type','=','sale')],limit=1).id,
                              'invoice_date': datetime.now()})
        print(product_id.property_account_income_id.id)
        vals = [{
             'move_id':invoice.id,
            'name': product_id.name,
            'product_id': product_id.id,
            'account_id': product_id.property_account_income_id.id,
            'partner_id': self.picking_id.partner_id.id,
            'product_uom_id': product_id.uom_id.id,
            'quantity': 1.0,
            'discount': 0.0,
            'price_unit': amount_total,
            'price_subtotal': amount_total,
            'price_total': amount_total,
            # 'tax_ids': cls.product_a.taxes_id.ids,
            'tax_line_id': False,
            # 'currency_id': cls.company_data['currency'].id,
            'amount_currency': amount_total,
            'debit': amount_total,
            'credit': 0.0,
            'date_maturity': False,
            'tax_exigible': True,
        },{
            'exclude_from_invoice_tab':True,
            'move_id':invoice.id,
            'name': product_id.name,
            'product_id': product_id.id,
            'account_id': product_id.property_account_income_id.id,
            'partner_id': self.picking_id.partner_id.id,
            'product_uom_id': product_id.uom_id.id,
            'quantity': 1.0,
            'discount': 0.0,
            'price_unit': amount_total,
            'price_subtotal': amount_total,
            'price_total': amount_total,
            # 'tax_ids': cls.product_b.taxes_id.ids,
            'tax_line_id': False,
            # 'currency_id': cls.company_data['currency'].id,
            'amount_currency':amount_total,
            'credit': amount_total,
            'debit': 0.0,
            'date_maturity': False,
            'tax_exigible': True,
        }]

        self.env['account.move.line'].create(vals)

class InheritStockPickingReturn(models.TransientModel):
    _inherit = 'stock.return.picking.line'

    type_id=fields.Many2one('redistribution.type','Particular Type')

class Redistributionlines(models.Model):
    _name='distribution.line'

    product_id=fields.Many2one('product.product')
    qty=fields.Float()
    claim_id=fields.Many2one('redistribution.claim')
    type_id=fields.Many2one('redistribution.type','Particular Type')
    amount=fields.Float('Amount')
    remarks=fields.Char('Remarks')

class InheritReutnPickingFunction(models.TransientModel):
    _inherit='stock.return.picking'

    def create_returns(self):
        rec=super(InheritReutnPickingFunction, self).create_returns()
        claim_id=self.env['redistribution.claim'].create({'picking_id':self.picking_id.id,'date':datetime.now(),'location_id':self.picking_id.location_id.id,
                                        })
        for line in self.product_return_moves:
            self.env['distribution.line'].create({'product_id':line.product_id.id,'qty':line.quantity,'type_id':line.type_id.id,'claim_id':claim_id.id})
        return rec

class RedistributionType(models.Model):
    _name='redistribution.type'

    name=fields.Char(string='Name')