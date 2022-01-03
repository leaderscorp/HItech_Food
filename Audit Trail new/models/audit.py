from odoo import api, models, fields, _


class audittrail(models.Model):
    _name = 'audit.trail'
    _description = 'Audit Trail'

    name = fields.Char("Name")
    contract_no = fields.Char("Contract")
    contract_account= fields.Char("Contract Account")
    consumer_number= fields.Char("Consumer Number")
    ibc_name= fields.Char("IBC Name")
    agency_name= fields.Char("Agency")
    cell_no= fields.Char("Cell No.")
    latitude_no= fields.Char("Latitude")
    longitude_no= fields.Char("Longitude")
    attempt_date1= fields.Datetime("Attempt 1 Date")
    attempt_date2= fields.Datetime("Attempt 2 Date")
    attempt_date3= fields.Datetime("Attempt 3 Date")
    call_date1= fields.Datetime("Calls Date 1")
    call_date2= fields.Datetime("Calls Date 2")
    attempt_smsdate1= fields.Datetime("Attempt SMS Date 1")
    attempt_smsdate2= fields.Datetime("Attempt SMS Date 2")
    no_roattempts= fields.Char("No. of RO Attempts")
    no_callattempts= feilds.Char("No. of Call Attempts")
    no_smsattempts= fields.Char("No. of SMS Attempts")
    remarks_1= fields.Char("Remarks 1")
    remarks_2= fields.Char("Remarks 2")
    remarks_3= fields.Char("Remarks 3")
    consumer_name_new= fields.Char("Consumer Name")
    name_agent_physical= fields.Char("Name of Agent (Physical Attempt)")
    name_agent_sms_attempt= fields.Char("Name of Agent Call/SMS Attempt")
    reason_notpaying= fields.Char("Reason for not Paying (Summary)")
    
    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('audit.trail')
        result = super(audittrail, self).create(vals)
        return result