from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_term=fields.Html(string='Payment Term')
    location_id=fields.Many2one('stock.location','Town')
    credit_limit = fields.Float(
        string='Credit Limit', related='partner_id.credit_limit',
        required=False)
    override_credit_limit = fields.Boolean(
        string='Override Credit Limit',
        copy=False,
        tracking=True,
    )
    over_credit = fields.Boolean(
        string='Over Credit',
        copy=False,
        readonly=True
    )
    partners = fields.Many2many('res.partner')

    state = fields.Selection(selection_add=[('revise', 'Revised Limit'), ('sale',)])

    @api.onchange('partner_id')
    def OnchangePartner(self):
        if self.partner_id:
            self.warehouse_id=self.partner_id.warehouse_id.id
            self.location_id=self.partner_id.location_id.id
            self.payment_term=self.partner_id.payment_term

    def action_revise(self):
        for rec in self:
            rec.state = 'revise'

    @api.onchange('pricelist_id')
    def pricelist_id_onchange_method(self):
        for rec in self:
            partner_list = []
            if rec.pricelist_id:
                rec.partners = False
                print("PArtner: ", rec.partners)
                print("PArtner List: ", partner_list)
                partner_list.append(rec.pricelist_id.item_ids.mapped('partner_id').ids)
                partner_list = partner_list[0]
                rec.partners = partner_list
                partner_list = []

    def check_partner_credit_limit(self):
        if not self._context.get('website_order_tx', False):
            prepayment_test = self.env['ir.config_parameter'].sudo().get_param(
                'credit_management.prepayment_test', False)
            no_of_days_overdue_test = self.env['ir.config_parameter'].sudo().get_param(
                'credit_management.no_of_days_overdue_test', False)
            partner = self.partner_id.commercial_partner_id
            for sale in self:
                invoices = sale.invoice_ids.filtered(lambda x: x.state == 'posted')
                invoice_amount_total = sum(invoices.mapped('amount_total_signed'))
                invoice_due_amount = sum(invoices.mapped('amount_residual'))
                paid_amount = invoice_amount_total - invoice_due_amount

                inv_amount = sum(
                    sale.invoice_ids.filtered(lambda x: x.state not in ['cancel', 'draft']).mapped('amount_total'))
                if (partner.credit_limit > 0 or prepayment_test) and not sale.override_credit_limit:
                    # if sale.payment_method_id and not sale.payment_method_id.prepayment_test:
                    #     continue
                    if sale.override_credit_limit or paid_amount >= sale.amount_total:
                        return True
                    else:
                        inv_amount = sum(
                            sale.invoice_ids.filtered(lambda x: x.state != 'cancel').mapped('amount_total_signed'))
                        actual_credit_used = sale.amount_total - inv_amount + partner.total_credit_used
                        if not sale.override_credit_limit and actual_credit_used > partner.credit_limit:
                            raise UserError(
                                _("Over Credit Limit!\n"
                                  "Credit Limit: {0}{1:.2f}\n"
                                  "Total Credit Balance (Previous used): {0}{2:.2f}\n"
                                  "Total this order: {0}{3:.2f}\n"
                                  "Total Credit Use with this order: {0}{4:.2f}\n"
                                  "You Can Use Total Remaining Credit upto this Amount: {0}{5:.2f}".format(
                                    sale.currency_id.symbol,
                                    partner.credit_limit,
                                    partner.total_credit_used,
                                    sale.amount_total,
                                    actual_credit_used,
                                    (partner.credit_limit - partner.total_credit_used),
                                )
                                ))
            return True

    def action_confirm(self):
        for order in self:
            partner = order.partner_id.commercial_partner_id
            # if order.hold_delivery_till_payment:
            #     continue
            try:
                order.over_credit = False
                order.check_partner_credit_limit()

            except UserError as e:
                order.over_credit = True
                return {
                    'name': 'Warning',
                    'type': 'ir.actions.act_window',
                    'res_model': 'partner.credit.limit.warning',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'target': 'new',
                    'context': {'default_message': e.name}
                }
        return super(SaleOrder, self).action_confirm()
