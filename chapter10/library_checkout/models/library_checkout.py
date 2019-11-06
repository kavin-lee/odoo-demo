from odoo import api, fields, models, exceptions


class Checkout(models.Model):
    _name = 'library.checkout'
    _description = 'Checkout Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
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

    @api.multi
    def name_get(self):
        names = []
        for rec in self:
            name = '%s/%s' % (rec.member_id, rec.request_date)
            names.append((rec.id, name))
        return names

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

    @api.onchange('member_id')
    def onchange_member_id(self):
        today = fields.Date.today()
        if self.request_date != today:
            self.request_date = fields.Date.today()
            return {
                'warning': {
                    'title': 'Changed Request Date',
                    'message': 'Request date changed to today.'
                }
            }

    # 添加字段，来进行记录进入的open时间以及退出的close的时间
    checkout_date = fields.Date()
    closed_date = fields.Date()

    @api.model
    def create(self, vals):
        # code创建之前：使用 vals 字典
        if 'staged_id' in vals:
            Stage = self.env['library.checkout.stage']
            new_stage = Stage.browse(vals['stage_id']).state
            if new_stage == 'open':
                vals['checkout_date'] = fields.Date.today()
        new_record = super().create(vals)

        # code 创建之后：使用  new_record 创建
        if new_record.state == 'done':
            raise exceptions.UserError(
                'Not allowed to create a checkout in the done state.'
            )
        return new_record

    # 实现对开始时间和关闭时间做一个写的操作
    def write(self, vals):
        # code 在写操作之前： 使用self 来获取 旧值
        if 'stage_id' in vals:
            Stage = self.env['library.checkout.stage']
            new_state = Stage.browse(vals['stage_id']).state
            if new_state == 'open' and self.stage != 'open':
                vals['checkout_date'] = fields.Date.today()
            if new_state == 'done' and self.state != 'done':
                vals['closed_date'] = fields.Date.today()
        super().write(vals)
        # code 在写入之后，可以使用self，获得更新后的值
        return True

    def button_done(self):
        Stage = self.env['library.checkout.stage']
        done_stage = Stage.search(
            ['state', '=', 'done'],
            limit=1)
        for checkout in self:
            checkout.stage_id = done_stage
        return True


class Checkoutline(models.Model):
    _name = 'library.checkout.line'
    _description = 'Borrow Request Line'
    checkout_id = fields.Many2one('library.checkout')
    book_id = fields.Many2one('library.book')
