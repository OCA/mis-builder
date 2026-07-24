#. Open a MIS Report Instance (*Accounting > Reporting > MIS Reporting >
   MIS Reports*) and click the *Check Account Coverage* button, or go to
   *Accounting > Reporting > MIS Reporting > Account Coverage Check* and
   pick the report instance manually.
#. Enter the account code range to check, e.g. ``100000`` to ``599999``.
#. Optionally restrict the periods to check; leave empty to check every
   period column defined on the report instance.
#. Click *Check*. Any account in the range that has postings in a period
   but is not referenced by any KPI expression of the report is listed with
   its debit, credit and balance for that period.
#. Click *View Journal Items* on a line to open the underlying journal
   entries causing that account to appear.

.. note::
   The account range is compared as text (``account.account.code``), so it
   is only reliable when the codes being compared have the same number of
   digits (as is normally the case, e.g. 6-digit Spanish PGC codes). A range
   like ``7`` to ``12`` would not behave as expected since ``"7" <= "12"``
   is false as a string comparison.

.. note::
   Coverage means "referenced by *any* KPI expression of the report",
   including aggregate/rollup KPIs (e.g. a "Result for the year" line that
   nets a whole P&L range like ``6%,7%`` into a single equity figure). That
   is intentional: if an account is correctly summed into such a KPI it does
   not put the report out of balance, so it should not be reported as
   uncovered even though it has no individual detail line of its own.

.. note::
   Without a chart's usual closing/opening entries, a balance-sheet
   account's balance keeps accumulating from postings dated before the
   period being checked. To match how mis_builder itself computes a
   balance-sheet KPI ("ending balance" mode), an uncovered account's
   debit/credit/balance are summed since the beginning of time for
   balance-sheet accounts (asset/liability/equity), and since the start of
   the fiscal year only for P&L accounts (income/expense), which do reset
   every year. So a posting from a previous period can still make an
   account show up as uncovered today.
