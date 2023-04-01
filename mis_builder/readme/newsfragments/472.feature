Migration to 16.0

- Addition of a generic filter domain on reports and columns.
- Addition of a search bar to the widget. The corresponding search view is configurable
  per report.
- Huge improvement of the widget style. This was long overdue.
- Removal of analytic fetures because the upstream ``analytic_distribution`` mechanism
  is not compatible; support may be introduced in separate module, depending on use
  cases.
- Abandon the ``mis_report_filters`` context key which had security implication.
  It is replaced by a ``mis_analytic_domain`` context key which is ANDed with other
  report-defined filters.
