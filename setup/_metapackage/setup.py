import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-mis-builder",
    description="Meta package for oca-mis-builder Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-mis_builder',
        'odoo12-addon-mis_builder_budget',
        'odoo12-addon-mis_builder_demo',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
