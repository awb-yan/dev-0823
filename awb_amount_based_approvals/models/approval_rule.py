# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ApprovalRule(models.Model):
    _name = 'approval.rule'
    _description = 'Approval Rules'

    name = fields.Char('Name', required=True, index=True,
                       copy=False, compute='_compute_name')
    category = fields.Many2one('approval.category', required=True, String='Category')
    currency = fields.Many2one('res.currency', String='Currency')
    min_amount = fields.Float('Minimum Amount', default=0, tracking=True)
    max_amount = fields.Float('Maximum Amount', default=0, tracking=True)
    active = fields.Boolean('Active', index=True, default=True, tracking=True)
    approval_type = fields.Selection([('amount', 'Amount'),('none','None')], string='Approval Type', default='amount', tracking=True)
    department = fields.Many2one('hr.department', String='Department')
    manager_id = fields.Boolean('Manager', default=False, tracking=True)
    operation_head_id = fields.Boolean('Operations Head', default=False, tracking=True)
    approver_ids = fields.One2many('approval.rule.line','approval_id', String='Approvers')
    company_id = fields.Many2one('res.company', 'Company', index=True, default=lambda self: self.env.company)

    @api.depends('min_amount', 'max_amount', 'department')
    def _compute_name(self):
        for rule in self:
            category_name = rule.category.name if rule.category.name else ''
            currency_name = rule.currency.name if rule.currency.name else ''
            department_name = f'{rule.department.name}:' if rule.department.name else ''
            rule.name = f'{department_name} {category_name} Amount: {currency_name} {rule.min_amount} - {rule.max_amount}'

    @api.constrains('min_amount', 'max_amount')
    def _check_amount(self):
        for record in self:
            if record.approval_type == 'amount':
                if record.min_amount < 0 or record.max_amount < 0:
                    raise UserError(_('Amount must be greater than 0'))
                elif record.min_amount >= record.max_amount:
                    raise UserError(_('Maximum Amount must be greater than Minimum Amount'))

class ApprovalRuleLine(models.Model):
    _name = "approval.rule.line"
    _description = "Approval Rules Line"
    _order = "sequence asc, id asc"

    sequence = fields.Integer(string="Sequence", required=True, default=1)
    approval_condition = fields.Selection([('and', 'AND'), ('or', 'OR')], string='Condition', default='and')
    approved_by = fields.Many2many('res.users', string='Approved By')
    approval_id = fields.Many2one('approval.rule', String="Approval")
