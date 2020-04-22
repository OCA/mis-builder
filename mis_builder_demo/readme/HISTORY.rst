13.0.3.1.2 (2020-04-22)
~~~~~~~~~~~~~~~~~~~~~~~

**Bugfixes**

- Fix currency rate in uninvoiced purchases. (`#274 <https://github.com/OCA/mis-builder/issues/274>`_)


13.0.3.1.0 (2020-01-??)
~~~~~~~~~~~~~~~~~~~~~~~

Migration to odoo 13.0.

12.0.3.1.0 (2019-10-26)
~~~~~~~~~~~~~~~~~~~~~~~

**Features**

- Handle multi currency for commited purchase view. The amount in this
  view are now converted to the base currency (the one with rate 1),
  so summing them has some meaning. As a consequence, this view has
  less usefulness if the company currency is not the one with rate 1,
  Debit and credit being assumed to be in company currency.

  Add the M2M to account.analytic.tag in the commited purchase view.

  Fix sign issue in commited purchase view.

  Include customer invoice in commited purchase view. The view is therefore
  not only about purchases anymore. This should not be an issue because
  GL accounts are differents for purchases and income anyway and generally
  used in different KPI.

  These are breaking changes. Change the status of ``mis_builder_demo`` to alpha,
  since it is a demo module and it's content can change at any time without
  any compatibility guarantees. (`#222 <https://github.com/oca/mis-builder/issues/222>`_)


**Bugfixes**

- Fix date casting error on committed expenses drilldown. (`#185 <https://github.com/oca/mis-builder/issues/185>`_)
