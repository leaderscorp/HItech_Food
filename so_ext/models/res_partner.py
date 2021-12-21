from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    warehouse_id=fields.Many2one('stock.warehouse','Region')
    location_id=fields.Many2one('stock.location','Town')
    payment_term=fields.Html(string='Payment Term')
    delivery_terms=fields.Html('Delivery Terms')

    def _compute_wl_credit(self):
        for rec in self:
            # Previous Receivable
            credit = rec.credit
            # All Confirm Sale order
            all_partners = self.search([('id', 'child_of', rec.ids)])
            all_partners.read(['parent_id'])

            confirm_so = self.env['sale.order'].search(
                [('partner_id', 'in', all_partners.ids), ('state', '=', 'sale')]
            )

            # confirm_so = self.env['sale.order'].search([
            #                     ('partner_id','=',rec.id),
            #                     ('state','=','sale')
            #                 ])

            confirm_so_amount = 0
            for so in confirm_so:
                so_amount = sum(so.mapped('amount_total'))
                inv_amount = sum(so.invoice_ids.filtered(lambda x: x.state != 'cancel').mapped('amount_total_signed'))
                # Ignore sale order amount if total invoiced amount is greater then sale order amount
                if inv_amount > so_amount:
                    continue
                else:
                    # Get remaining sale order amount
                    confirm_so_amount += so_amount - inv_amount

            # Get draft invoices for credit limit
            account_move_draft = self.env['account.move'].search([
                ('partner_id', 'in', all_partners.ids),
                ('state', '=', 'draft'),
                ('move_type', '=', 'out_invoice')
            ])
            account_move_draft = sum(account_move_draft.mapped('amount_total_signed'))

            # Compute credit limit
            rec.total_credit_used = credit + confirm_so_amount + account_move_draft
            return rec.total_credit_used
    attachment_ids = fields.One2many(
        comodel_name='ir.attachment',
        inverse_name='res_partner_id',
        string='Attachment_ids',
        required=False)
    total_credit_used = fields.Monetary(
        compute='_compute_wl_credit',
        string='Total Credit Used',
        help='Total credit used by the partner')


class Attachment(models.Model):
    _inherit = 'ir.attachment'

    res_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string=' Partner',
        required=False)