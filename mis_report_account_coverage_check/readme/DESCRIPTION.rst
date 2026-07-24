A MIS Builder report (e.g. a balance sheet) only shows what its KPI
expressions explicitly reference. If an account within the report's range
receives postings during the period but no KPI expression covers it, the
report silently omits it -- typically the symptom is a balance sheet that
does not balance, with no obvious way to find out why.

This module adds a wizard that, given a MIS report instance and an account
code range, finds accounts in that range which have journal entries posted
during the report's period(s) but are not referenced by any KPI expression
of the report (including subreport KPIs). Each uncovered account is shown
with its period debit/credit/balance, with a direct drill-down to the
underlying journal items.
