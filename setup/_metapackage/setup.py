import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-mis-builder",
    description="Meta package for oca-mis-builder Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-mis_builder',
        'odoo14-addon-mis_builder_budget',
        'odoo14-addon-mis_builder_demo',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
