13.0.3.5.1 (2021-04-06)
~~~~~~~~~~~~~~~~~~~~~~~

**Bugfixes**

- Fix incorrect budget by account multi company security rules. (`#347 <https://github.com/OCA/mis-builder/issues/347>`_)


13.0.3.5.0 (2020-03-28)
~~~~~~~~~~~~~~~~~~~~~~~

**Features**

- Budget by GL account: allow budgeting by GL account in addition to the
  existing mechanism to budget by KPI. Budget items have a begin and end
  date, and when reporting a pro-rata temporis adjustment is made to match
  the reporting period. (`#259 <https://github.com/OCA/mis-builder/issues/259>`_)


13.0.3.4.0 (2020-01-??)
~~~~~~~~~~~~~~~~~~~~~~~

Migration to odoo 13.0.

12.0.3.4.0 (2019-10-26)
~~~~~~~~~~~~~~~~~~~~~~~

**Bugfixes**

- Consider analytic tags too when detecting overlapping budget items.
  Previously only analytic account was considered, and this overlap detection
  mechanism was overlooked when analytic tags were added to budget items. (`#241 <https://github.com/oca/mis-builder/issues/241>`_)


11.0.3.3.0 (2019-01-13)
~~~~~~~~~~~~~~~~~~~~~~~

**Features**

- Support analytic filters. (`#15 <https://github.com/oca/mis-builder/issues/15>`_)


11.0.3.2.1 (2018-06-30)
~~~~~~~~~~~~~~~~~~~~~~~

- [IMP] Support analytic tags in budget items
  (`#100 <https://github.com/OCA/mis-builder/pull/100>`_)

11.0.3.2.0 (2018-05-02)
~~~~~~~~~~~~~~~~~~~~~~~

- [FIX] #NAME error in out-of-order computation of non
  budgetable items in budget columns
  (`#68 <https://github.com/OCA/mis-builder/pull/69>`_)

11.0.3.1.1 (2018-02-04)
~~~~~~~~~~~~~~~~~~~~~~~

Migration to Odoo 11. No new feature.
(`#67 <https://github.com/OCA/mis-builder/pull/67>`_)

10.0.3.1.0 (2017-11-14)
~~~~~~~~~~~~~~~~~~~~~~~

New features:

- [ADD] multi-company record rule for MIS Budgets
  (`#27 <https://github.com/OCA/mis-builder/issues/27>`_)

10.0.1.1.1 (2017-10-01)
~~~~~~~~~~~~~~~~~~~~~~~

First version.
