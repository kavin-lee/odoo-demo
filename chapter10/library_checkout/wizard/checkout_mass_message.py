from odoo import api, fields, models, exceptions
import logging
from odoo import exceptions

# raise exceptions.ValidationError('验证失败')
# raise exceptions.UserError('业务逻辑错误')

_logger = logging.getLogger(__name__)


# 实现消息的发送类
class CheckoutMassMessage(models.TransientModel):
    _name = 'library.checkout.massmessage'
    _description = 'Send Message to Borrowers'
    checkout_ids = fields.Many2many(
        'library.checkout',
        string='Checkouts'
    )
    message_subject = fields.Char()
    message_body = fields.Html()

    @api.model
    def default_get(self, field_names):
        defaults = super().default_get(field_names)
        checkout_ids = self.env.context.get('active_ids')
        defaults['checkout_ids'] = checkout_ids
        return defaults

    # 向导业务逻辑的书写
    @api.multi
    def button_send(self):
        # 代码一次处理一个向导实例，所以用
        # self.ensure_one()来表示的更加清楚一些
        self.ensure_one()
        if not self.checkout_ids:
            raise exceptions.UserError(
                '请至少选择一条借阅记录来发送消息！'
            )
        if not self.message_body:
            raise exceptions.UserError(
                '请填写要发送的消息体！'
            )
        for checkout in self.checkout_ids:
            checkout.message_post(
                body=self.message_body,
                subject=self.message_subject,
                subtype='mail.mt_comment',
            )
            _logger.debug(
                'Message on %d to followers:%s',
                checkout.id,
                checkout.message_follower_ids
            )
        _logger.info(
            'Posted %d messages to Checkouts: %s',
            len(self.checkout_ids),
            str(self.checkout_ids)
        )
        return True
        # 让方法至少返回一个 True 值是一个很好的编程实践。
        # 主要是因为有些XML-RPC协议不支持 None 值，
        # 所以对于这些协议就用不了那些方法了。在实际工作中，
        # 我们可能不会遇到这个问题，因为网页客户端使用JSON-RPC而不是XML-RPC，
        # 但这仍是一个可遵循的良好实践。
