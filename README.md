[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/248/10.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-mis-builder-248)
[![Build Status](https://travis-ci.org/OCA/mis-builder.svg?branch=10.0)](https://travis-ci.org/OCA/mis-builder)
[![codecov](https://codecov.io/gh/OCA/mis-builder/branch/10.0/graph/badge.svg)](https://codecov.io/gh/OCA/mis-builder)
[![docs](https://media.readthedocs.org/static/projects/badges/passing.svg)](http://oca-mis-builder.readthedocs.io/en/10.0/)

# MIS Builder

Management Information System reports for [Odoo Business Suite of Applications](https://www.odoo.com):
easily build super fast, beautiful, custom reports such as P&L, Balance Sheets and more.

**This is the 10.0 branch, where new features are been developed, which are then ported
to 9.0 and 11.0.**

This project implements a class of reports where KPI (Key Performance Indicators)
are displayed in rows, and time periods in columns. It focuses on very fast reporting
on accounting data but can also use data from any other Odoo model.

It features the following key characteristics:

- User-friendly configuration: end users can create new report templates without
  development, using simple Excel-like formulas.
- Very fast balance reporting for accounting data, even on million-line databases
  with very complex account charts.
- Reusability: Use the same template for different reports.
- Multi-period comparisons: Compare data over different time periods.
- User-configurable styles: perfectly rendered in the UI as well as in Excel and
  PDF exports.
- Interactive display with drill-down.
- WYSIWYG Export to PDF and Excel.
- A budgeting module.
- KPI Evaluation over various data sources, such as actuals, simulation, committed
  costs (custom developments are required to create the data source).
- Easy-to-use API for developers for the accounting balance computation engine.

All source code of the modules is licensed under [AGPLv3](http://www.gnu.org/licenses/agpl-3.0-standalone.html) and can be found in the [OCA Official Github repository](https://github.com/OCA/mis-builder/).

`MIS Builder` is available for the following versions:

* 8.0,
* 9.0,
* 10.0,
* 11.0
* in both Community and Enterprise Edition.

Here are some presentations:

- Odoo Experience 2017 ([slides](https://www.slideshare.net/acsone/budget-control-with-misbuilder-3-2017), [video](https://youtu.be/0PpxGAf2l-0))
- Odoo Experience 2016 ([slides](https://www.slideshare.net/acsone/misbuilder-2016))
- Odoo Experience 2015 ([slides](https://www.slideshare.net/acsone/misbuilder))


[//]: # (addons)

Available addons
----------------
addon | version | summary
--- | --- | ---
[mis_builder](mis_builder/) | 10.0.3.2.0 | Build 'Management Information System' Reports and Dashboards
[mis_builder_budget](mis_builder_budget/) | 10.0.3.2.0 | Create budgets for MIS reports
[mis_builder_demo](mis_builder_demo/) | 10.0.3.0.0 | Demo addon for MIS Builder

[//]: # (end addons)

Translation Status
------------------
[![Transifex Status](https://www.transifex.com/projects/p/OCA-mis-builder-10-0/chart/image_png)](https://www.transifex.com/projects/p/OCA-mis-builder-10-0)

----

OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.
