To configure this module, you need to:

- Go to Accounting \> Configuration \> MIS Reporting \> MIS Report
  Templates where you can create report templates by defining KPI's.
  KPI's constitute the rows of your reports. Such report templates are
  time independent.

![](https://raw.githubusercontent.com/OCA/mis-builder/10.0/mis_builder/static/description/ex_report_template.png)

- Then in Accounting \> Reports \> MIS Reporting \> MIS Reports you can
  create report instance by binding the templates to time periods, hence
  defining the columns of your reports.

![](https://raw.githubusercontent.com/OCA/mis-builder/10.0/mis_builder/static/description/ex_report_settings.png)

- From the MIS Reports view, you can preview the report, add it to and
  Odoo dashboard, and export it to PDF or Excel.

![](https://raw.githubusercontent.com/OCA/mis-builder/10.0/mis_builder/static/description/ex_report_preview.png)

- On the MIS Reports view, you can add annotations on each cells (except cells coming from the option "details by account"). Added notes will be pinted when exporting to PDF and Excel. Only users having either the group to read or the group to update annotations can see those annotations.

- In the **Widget** tab of a MIS Report Instance, you can configure interactive widget options:
  - **Show filters box**: Displays an inline search bar to filter report lines. Active search filters and pivot dates are preserved when navigating to drilldown details and returning via breadcrumbs.
  - **Cache report on drilldown**: Caches computed report data in browser memory during drilldown navigation. Returning via breadcrumbs renders the report instantly from memory without triggering a new server computation. Modifying filters or pivot dates automatically invalidates the cache and fetches fresh data.