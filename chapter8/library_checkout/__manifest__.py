{
    'name': 'Library Book Borrowing',
    'description': 'Member can borrow books from the Library.',
    'author': 'Kaivn Lee',
    'depends': ['library_member', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/library_menu.xml',
        'views/checkout_view.xml',
        'data/library_checkout_stage.xml',
        'wizard/checkout_mass_message_wizard.xml',
    ],
}
