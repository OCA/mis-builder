Changelog for mis_builder
-------------------------

.. Future (?)
.. ~~~~~~~~~~
..
.. *

10.0.3.1.1 (2017-11-14)
~~~~~~~~~~~~~~~~~~~~~~~

New features:

* [ADD] month and year relative periods, easier to use than
  date ranges for the most common case.
  (`#2 <https://github.com/OCA/mis-builder/issues/2>`_)
* [ADD] multi-company consolidation support, with currency conversion
  (the conversion rate date is the end of the reporting period)
  (`#7 <https://github.com/OCA/mis-builder/issues/7>`_, 
  `#3 <https://github.com/OCA/mis-builder/issues/3>`_)
* [ADD] provide ref, datetime, dateutil, time, user in the evaluation 
  context of move line domains; among other things, this allows using 
  references to xml ids (such as account types or tax tags) when 
  querying move lines 
  (`#26 <https://github.com/OCA/mis-builder/issues/26>`_).
* [ADD] extended account selectors: you can now select accounts using
  any domain on account.account, not only account codes
  ``balp[('user_type_id', '=', ref('account.data_account_type_receivable').id)]``
  (`#4 <https://github.com/OCA/mis-builder/issues/4>`_).
* [IMP] in the report instance configuration form, the filters are
  now grouped in a notebook page, this improves readability and
  extensibility
  (`#39 <https://github.com/OCA/mis-builder/issues/39>`_).

Bug fixes:

* [FIX] fix error when saving periods in comparison mode on newly 
  created (not yet saved) report instances.
  `#50 <https://github.com/OCA/mis-builder/pull/50>`_
* [FIX] improve display of Base Date report instance view.
  `#51 <https://github.com/OCA/mis-builder/pull/51>`_

Upgrading from 3.0 (breaking changes):

* Alternative move line data sources must have a company_id field.

10.0.3.0.4 (2017-10-14)
~~~~~~~~~~~~~~~~~~~~~~~

Bug fix:

* [FIX] issue with initial balance rounding.
  `#30 <https://github.com/OCA/mis-builder/issues/30>`_

10.0.3.0.3 (2017-10-03)
~~~~~~~~~~~~~~~~~~~~~~~

Bug fix:

* [FIX] fix error saving KPI on newly created reports.
  `#18 <https://github.com/OCA/mis-builder/issues/18>`_

10.0.3.0.2 (2017-10-01)
~~~~~~~~~~~~~~~~~~~~~~~

New features:

* [ADD] Alternative move line source per report column.
  This makes mis buidler accounting expressions work on any model
  that has debit, credit, account_id and date fields. Provided you can
  expose, say, committed purchases, or your budget as a view with
  debit, credit and account_id, this opens up a lot of possibilities
* [ADD] Comparison column source (more flexible than the previous,
  now deprecated, comparison mechanism).
  CAVEAT: there is no automated migration to the new mechanism.
* [ADD] Sum column source, to create columns that add/subtract
  other columns.
* [ADD] mis.kpi.data abstract model as a basis for manual KPI values
  supporting automatic ajustment to the reporting time period (the basis
  for budget item, but could also server other purposes, such as manually
  entering some KPI values, such as number of employee)
* [ADD] mis_builder_budget module providing a new budget data source
* [ADD] new "hide empty" style property
* [IMP] new AEP method to get accounts involved in an expression
  (this is useful to find which KPI relate to a given P&L
  acount, to implement budget control)
* [IMP] many UI improvements
* [IMP] many code style improvements and some refactoring
* [IMP] add the column date_from, date_to in expression evaluation context,
  as well as time, datetime and dateutil modules

Main bug fixes:

* [FIX] deletion of templates and reports (cascade and retricts) 
  (https://github.com/OCA/account-financial-reporting/issues/281)
* [FIX] copy of reports 
  (https://github.com/OCA/account-financial-reporting/issues/282)
* [FIX] better error message when periods have wrong/missing dates 
  (https://github.com/OCA/account-financial-reporting/issues/283)
* [FIX] xlsx export of string types KPI 
  (https://github.com/OCA/account-financial-reporting/issues/285)
* [FIX] sorting of detail by account
* [FIX] computation bug in detail by account when multiple accounting
  expressions were used in a KPI
* [FIX] permission issue when adding report to dashboard with non admin user

10.0.2.0.3 (unreleased)
~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] more robust behaviour in presence of missing expressions
* [FIX] indent style
* [FIX] local variable 'ctx' referenced before assignment when generating
  reports with no objects
* [IMP] use fontawesome icons
* [MIG] migrate to 10.0
* [FIX] unicode error when exporting to Excel
* [IMP] provide full access to mis builder style for group Adviser.

9.0.2.0.2 (2016-09-27)
~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Add refresh button in mis report preview.
* [IMP] Widget code changes to allow to add fields in the widget more easily.

9.0.2.0.1 (2016-05-26)
~~~~~~~~~~~~~~~~~~~~~~

* [IMP] remove unused argument in declare_and_compute_period()
  for a cleaner API. This is a breaking API changing merged in
  urgency before it is used by other modules.

9.0.2.0.0 (2016-05-24)
~~~~~~~~~~~~~~~~~~~~~~

Part of the work for this release has been done at the Sorrento sprint
April 26-29, 2016. The rest (ie a major refactoring) has been done in
the weeks after.

* [IMP] hide button box in edit mode on the report instance settings form
* [FIX] Fix sum aggregation of non-stored fields 
  (https://github.com/OCA/account-financial-reporting/issues/178)
* [IMP] There is now a default style at the report level
* [CHG] Number display properties (rounding, prefix, suffix, factor) are
  now defined in styles
* [CHG] Percentage difference are rounded to 1 digit instead of the kpi's
  rounding, as the KPI rounding does not make sense in this case
* [CHG] The divider suffix (k, M, etc) is not inserted automatically anymore
  because it is inconsistent when working with prefixes; you need to add it
  manually in the suffix
* [IMP] AccountingExpressionProcessor now supports 'balu' expressions
  to obtain the unallocated profit/loss of previous fiscal years;
  get_unallocated_pl is the corresponding convenience method
* [IMP] AccountingExpressionProcessor now has easy methods to obtain
  balances by account: get_balances_initial, get_balances_end,
  get_balances_variation
* [IMP] there is now an auto-expand feature to automatically display
  a detail by account for selected kpis
* [IMP] the kpi and period lists are now manipulated through forms instead
  of directly in the tree views
* [IMP] it is now possible to create a report through a wizard, such
  reports are deemed temporary and available through a "Last Reports Generated"
  menu, they are garbaged collected automatically, unless saved permanently,
  which can be done using a Save button
* [IMP] there is now a beginner mode to configure simple reports with
  only one period
* [IMP] it is now easier to configure periods with fixed start/end dates
* [IMP] the new sub-kpi mechanism allows the creation of columns
  with multiple values, or columns with different values
* [IMP] thanks to the new style model, the Excel export is now styled
* [IMP] a new style model is now used to centralize style configuration
* [FIX] use =like instead of like to search for accounts, because
  the % are added by the user in the expressions
* [FIX] Correctly compute the initial balance of income and expense account
  based on the start of the fiscal year
* [IMP] Support date ranges (from OCA/server-tools/date_range) as a more
  flexible alternative to fiscal periods
* v9 migration: fiscal periods are removed, account charts are removed,
  consolidation accounts have been removed

8.0.1.0.0 (2016-04-27)
~~~~~~~~~~~~~~~~~~~~~~

* The copy of a MIS Report Instance now copies period.
  https://github.com/OCA/account-financial-reporting/pull/181
* The copy of a MIS Report Template now copies KPIs and queries.
  https://github.com/OCA/account-financial-reporting/pull/177
* Usability: the default view for MIS Report instances is now the rendered preview,
  and the settings are accessible through a gear icon in the list view and
  a button in the preview.
  https://github.com/OCA/account-financial-reporting/pull/170
* Display blank cells instead of 0.0 when there is no data.
  https://github.com/OCA/account-financial-reporting/pull/169
* Usability: better layout of the MIS Report periods settings on small screens.
  https://github.com/OCA/account-financial-reporting/pull/167
* Include the download buttons inside the MIS Builder widget, and refactor
  the widget to open the door to analytic filtering in the previews.
  https://github.com/OCA/account-financial-reporting/pull/151
* Add KPI rendering prefixes (so you can print $ in front of the value).
  https://github.com/OCA/account-financial-reporting/pull/158
* Add hooks for analytic filtering.
  https://github.com/OCA/account-financial-reporting/pull/128
  https://github.com/OCA/account-financial-reporting/pull/131

8.0.0.2.0
~~~~~~~~~

Pre-history. Or rather, you need to look at the git log.
