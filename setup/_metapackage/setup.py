import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-mis-builder",
    description="Meta package for oca-mis-builder Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-mis_builder',
        'odoo11-addon-mis_builder_budget',
        'odoo11-addon-mis_builder_demo',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
