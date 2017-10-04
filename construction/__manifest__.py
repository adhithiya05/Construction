{
    'name' : 'Construction Management',
    'version' : '1.1',
    'summary': 'Construction Management',
    'description': """
Construction Management""",
    'category': '',
    'depends' : ['hr','project'],
    'data': [
        # 'security/student_security.xml',
         # 'security/ir.model.access.csv',
        # 'update_xml': ['security/ir.model.access.csv1'], 
        # 'security/ir.model.access.csv',
        'views/construction.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
