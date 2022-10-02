
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/mis-builder&target_branch=16.0)
[![Pre-commit Status](https://github.com/OCA/mis-builder/actions/workflows/pre-commit.yml/badge.svg?branch=16.0)](https://github.com/OCA/mis-builder/actions/workflows/pre-commit.yml?query=branch%3A16.0)
[![Build Status](https://github.com/OCA/mis-builder/actions/workflows/test.yml/badge.svg?branch=16.0)](https://github.com/OCA/mis-builder/actions/workflows/test.yml?query=branch%3A16.0)
[![codecov](https://codecov.io/gh/OCA/mis-builder/branch/16.0/graph/badge.svg)](https://codecov.io/gh/OCA/mis-builder)
[![Translation Status](https://translation.odoo-community.org/widgets/mis-builder-16-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/mis-builder-16-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# MIS Builder

Management Information System reports for Odoo: easily build super fast,
beautiful, custom reports such as P&L, Balance Sheets and more.

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

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Unported addons
---------------
addon | version | maintainers | summary
--- | --- | --- | ---
[mis_builder](mis_builder/) | 15.0.4.1.0 (unported) | [![sbidoul](https://github.com/sbidoul.png?size=30px)](https://github.com/sbidoul) | Build 'Management Information System' Reports and Dashboards
[mis_builder_budget](mis_builder_budget/) | 15.0.4.0.1 (unported) | [![sbidoul](https://github.com/sbidoul.png?size=30px)](https://github.com/sbidoul) | Create budgets for MIS reports
[mis_builder_demo](mis_builder_demo/) | 15.0.3.1.1 (unported) | [![sbidoul](https://github.com/sbidoul.png?size=30px)](https://github.com/sbidoul) | Demo addon for MIS Builder

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA)
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
