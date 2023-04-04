import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-mis-builder",
    description="Meta package for oca-mis-builder Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-mis_builder>=16.0dev,<16.1dev',
        'odoo-addon-mis_builder_budget>=16.0dev,<16.1dev',
        'odoo-addon-mis_builder_demo>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
