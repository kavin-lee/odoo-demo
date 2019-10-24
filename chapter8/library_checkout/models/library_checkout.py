from odoo import api, fields, models, exceptions


class Checkout(models.Model):
    _name = 'library.checkout'
    _description = 'Checkout Request'
    member_id = fields.Many2one(
        'library.member',
        required=True
    )
    user_id = fields.Many2one(
        'res.users',
        'Librarian',
        default=lambda s: s.env.uid
    )
    request_date = fields.Date(
        default=lambda s: fields.Date.today()
    )
    line_ids = fields.One2many(
        'library.checkout.line',
        'checkout_id',
        string='Borrowed Books'
    )

    @api.model
    def _default_stage(self):
        Stage = self.env['library.checkout.stage']
        return Stage.search([], limit=1)

    @api.model
    def _group_expand_stage_id(self, stages, domain, order):
        return stages.search([], order=order)

    stage_id = fields.Many2one(
        'library.checkout.stage',
        default=_default_stage,
        group_expand='_group_expand_stage_id'
    )
    state = fields.Selection(related='stage_id.state')


class Checkoutline(models.Model):
    _name = 'library.checkout.line'
    _description = 'Borrow Request Line'
    checkout_id = fields.Many2one('library.checkout')
    book_id = fields.Many2one('library.book')
