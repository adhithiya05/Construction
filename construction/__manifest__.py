{
    'name' : 'Construction Management',
    'version' : '1.1',
    'author' : 'Datayaan',
    'summary': 'Construction Management',
    'description': """
Construction Management""",
    'category': '',
    'depends' : ['hr','purchase'],
    'data': [
        # 'security/student_security.xml',
         # 'security/ir.model.access.csv',
        # 'update_xml': ['security/ir.model.access.csv1'],
        'data/ir_sequence_data.xml', 
        'security/ir.model.access.csv',
        'report/project_setup.xml',
        'report/reports.xml',
        'views/construction.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
