{
    'name': 'Agregar Grupos de Usuarios',
    'version': '15.0.1.0.0',
    'author': 'Alexis C.',
    'license': 'AGPL-3',
    'website': '',
    'category': 'Account',
    'description':
        '''
        Se agregan nuevos grupos de usuarios:
        -Usuario Caja
        -Usuario Ventas
        -Usuario Contabilidad Externa
        -Usuario Inventario Parcial
        -Usuario Inventario Total
        -Usuario Compras
        -Usuario Contabilidad Interna
        ''',
    'depends':
        [
        ],
    'data':
        [
            'security/security.xml',
        ],
    'installable': True,
}
