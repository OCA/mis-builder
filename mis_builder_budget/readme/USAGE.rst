To use this module, you first need to flag at least some KPI in a MIS
report to be budgetable. You also need to configure the accumulation method
on the KPI according to their type.

The accumulation method determines how budgeted values spanning over a
time period are transformed to match the reporting period.

* Sum: values of shorter period are added, values of longest or partially overlapping
  periods are adjusted pro-rata temporis (eg monetary amount such as revenue).
* Average: values of included period are averaged with a pro-rata temporis weight.
  Typically used for values that do not accumulate over time (eg a number of employees).

When KPI are configured, you need to create a budget, then click on the budget items
button to create or import the budgeted amounts for all your KPI and time periods.

Finally, a column (aka period) must be added to a MIS report instance, selecting your
newly created budget as a data source. The data will be adjusted to the reporting period
when displayed. Columns can be compared by adding a column of type "comparison" or "sum".
