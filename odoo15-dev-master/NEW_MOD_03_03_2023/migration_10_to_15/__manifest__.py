{
    'name': 'Agregar Codigo Antiguo',
    'version': '15.0.1.0.0',
    'author': 'Alexis C.',
    'license': 'AGPL-3',
    'website': '',
    'category': 'Account',
    'description':
        '''
        Se agregan nuevo campo llamado Codigo Antiguo.
        ''',
    'depends':
        ['product','account','purchase']
    ,
    'data':
        [
            'view/add_field_product_template.xml',
        ],
    'installable': True,
}
