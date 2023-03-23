{
    'name': 'Create SO from Invoice',
    'version': '15.0.1.0.0',
    'author': 'Alexis C.',
    'license': 'AGPL-3',
    'website': '',
    'category': 'Account',
    'description':
        '''
        Permite Crear Orde de Venta desde una factura de cliente.
        ''',
    'depends':
        ['product','account','purchase','sale']
    ,
    'data':
        [
            'view/create_so_from_invoice.xml',
        ],
    'installable': True,
}
