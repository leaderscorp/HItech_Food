from odoo import fields,models,api

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
                               })
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



class Redistributionlines(models.Model):
    _name='distribution.line'

    claim_id=fields.Many2one('redistribution.claim')
    type_id=fields.Many2one('redistribution.type','Particular Type')
    amount=fields.Float('Amount')
    remarks=fields.Char('Remarks')

class RedistributionType(models.Model):
    _name='redistribution.type'

    name=fields.Char(string='Name')