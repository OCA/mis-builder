Introdution
===========

MIS Builder is an Odoo module that implements a class of Odoo reports where KPI 
(Key Performance Indicators)
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

