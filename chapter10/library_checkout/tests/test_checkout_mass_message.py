from odoo.odoo.tests.common import TransactionCase
from odoo import exceptions


class TestWizard(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestWizard, self).setUp(*args, **kwargs)
        # 此处进行添加测试的代码【配置测试】
        admin_user = self.env.ref('base.user_admin')
        self.Checkout = self.env['library.checkout'].sudo(admin_user)
        self.Wizard = self.env['library.checkout.massmessage'].sudo(admin_user)

        a_member = self.env['library.member'].create({'name': 'John'})
        self.checkout0 = self.Checkout.create({
            'member_id': a_member.id
        })

    def test_button_send(self):
        '''在借阅中，发送按钮应该创建信息'''
        # 此处增加测试代码【编写测试用例】
        msgs_before = len(self.checkout0.message_ids)

        Wizard0 = self.Wizard.with_context(active_ids=self.checkout0.ids)
        wizard0 = Wizard0.create({'message_body': 'Hello'})
        wizard0.button_send()

        msgs_after = len(self.checkout0.message_ids)
        self.assertEqual(
            msgs_after,
            msgs_before + 1,
            'Expected on additional message in the Checkout.'
        )

    def test_button_send_empty_body(self):
        '''发送空的信息体'''
        wizard0 = self.Wizard.create({})
        with self.assertRaises(exceptions.UserError) as e:
            wizard0.button_send()
