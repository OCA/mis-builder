[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/248/10.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-mis-builder-248)
[![Build Status](https://travis-ci.org/OCA/mis-builder.svg?branch=10.0)](https://travis-ci.org/OCA/mis-builder)
[![codecov](https://codecov.io/gh/OCA/mis-builder/branch/10.0/graph/badge.svg)](https://codecov.io/gh/OCA/mis-builder)
[![docs](https://media.readthedocs.org/static/projects/badges/passing.svg)](http://oca-mis-builder.readthedocs.io/en/10.0/)

# MIS Builder

Management Information System reports for Odoo: easily build super fast,
beautiful, custom reports such as P&L, Balance Sheets and more.

**This is the 10.0 branch, where we develop new features, which are then ported
to 9.0 and 11.0.**

This project implements a class of reports where KPI (Key Performance Indicators)
are displayed in rows, and time periods in columns. It focuses on very fast reporting
on accounting data but can also use data from any other Odoo model.

It features the following key characteristics:

- User configurable: end users can create new report templates without development,
  using simple Excel-like formulas.
- Very fast balance reporting for accounting data, even on million lines databases
  and very complex account charts.
- Use the same template for different reports.
- Compare data over different time periods.
- User-configurable styles, rendered perfectly in the UI as well as Excel and PDF exports.
- Interactive display with drill-down.
- Export to PDF and Excel.
- A budgeting module.
- Evaluate KPI over various data sources, such as actuals, simulation, committed costs
  (some custom development is required to create the data source).
- For developers, the accounting balance computation engine is exposed as an easy
  to use API.

Here are some presentations:

- Odoo Experience 2017 ([slides](https://www.slideshare.net/acsone/budget-control-with-misbuilder-3-2017), [video](https://youtu.be/0PpxGAf2l-0))
- Odoo Experience 2016 ([slides](https://www.slideshare.net/acsone/misbuilder-2016))
- Odoo Experience 2015 ([slides](https://www.slideshare.net/acsone/misbuilder))


[//]: # (addons)

Available addons
----------------
addon | version | summary
--- | --- | ---
[mis_builder](mis_builder/) | 10.0.3.5.0 | Build 'Management Information System' Reports and Dashboards
[mis_builder_budget](mis_builder_budget/) | 10.0.3.4.0 | Create budgets for MIS reports
[mis_builder_demo](mis_builder_demo/) | 10.0.3.1.0 | Demo addon for MIS Builder

[//]: # (end addons)

Translation Status
------------------
[![Translation status](https://translation.odoo-community.org/widgets/mis-builder-10-0/-/multi-auto.svg)](https://translation.odoo-community.org/engage/mis-builder-10-0/?utm_source=widget)

----

OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.
