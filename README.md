[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/248/8.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-mis-builder-248)
[![Build Status](https://travis-ci.org/OCA/mis-builder.svg?branch=8.0)](https://travis-ci.org/OCA/mis-builder)
[![codecov](https://codecov.io/gh/OCA/mis-builder/branch/8.0/graph/badge.svg)](https://codecov.io/gh/OCA/mis-builder)

# MIS Builder

Management Information System reports for Odoo: easily build super fast, 
beautiful, custom reports such as P&L, Balance Sheets and more.

**This is the 8.0 branch, which is not actively maintained. New features are
added in the 9.0 branch and forward ported. If you need new features for the 8.0
series, please consider helping with a 
[backport of the 9.0 branch](https://github.com/OCA/mis-builder/issues/13) first.**

This project implements a class of reports where KPI (Key Performance Indicators) 
are displayed in row, and time periods in columns. It focuses on very fast reporting
on accounting data but can also use data from any other Odoo model.

It features the following key characteristics:

- User configurable: end users can create new report templates without development,
  using simple Excel-like formulas.
- Very fast balance reporting for accounting data, even on million lines databases
  and very complex account charts.
- Use the same template for different reports.
- Compare data over different time periods.
- User-configurable styles (CSS).
- Interactive display with drill-down.
- Export to PDF and Excel.


[//]: # (addons)

Available addons
----------------
addon | version | summary
--- | --- | ---
[mis_builder](mis_builder/) | 8.0.1.0.2 | Build 'Management Information System' Reports and Dashboards
[mis_builder_analytic_filter](mis_builder_analytic_filter/) | 8.0.1.0.0 | Add analytic filters to MIS Reports
[mis_builder_demo](mis_builder_demo/) | 8.0.1.0.0 | Demo data for the mis_builder module

[//]: # (end addons)

Translation Status
------------------
[![Transifex Status](https://www.transifex.com/projects/p/OCA-mis-builder-8-0/chart/image_png)](https://www.transifex.com/projects/p/OCA-mis-builder-8-0)

----

OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.
