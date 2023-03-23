{
    'name': 'Importar Data',
    'version': '15.0.1.0.0',
    'author': 'Alexis C.',
    'license': 'AGPL-3',
    'website': '',
    'category': 'Account',
    'description':
        '''
        Se importara data de facturas de cliente y proveedor desde Odoo 10 hacia Odoo 15
        ''',
    'depends':
        ['product','account','sale','purchase']
    ,
    'data':
        [
            'view/add_button_charge_data.xml',
        ],
    'installable': True,
}
