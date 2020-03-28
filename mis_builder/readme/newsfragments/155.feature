Access to KPI from other reports in KPI expressions, aka subreports. In a
report template, one can list named "subreports" (other report templates). When
evaluating expressions, you can access KPI's of subreports with a dot-prefix
notation. Example: you can define a MIS Report for a "Balance Sheet", and then
have another MIS Report "Balance Sheet Ratios" that fetches KPI's from "Balance
Sheet" to create new KPI's for the ratios (e.g. balance_sheet.current_assets /
balance_sheet.total_assets).
