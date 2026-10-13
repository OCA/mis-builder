1. In the MIS report template, set *Move lines source* to *Analytic line as MIS
   move line*.
2. Use the analytic filter of the report instance, or an analytic domain per column.
3. Expressions can also filter on the origin of the line, for example
   `balp[5%][('line_origin', '=', 'timesheet')]` or
   `-balp[6%][('category', '=', 'invoice')]`.

The sign follows journal items: a positive analytic amount (revenue) is a credit and
a negative one (cost) is a debit, so the usual `-balp[...]` expressions for income
keep working.
