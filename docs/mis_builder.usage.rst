Creating New reports
--------------------
Create Styles for your reporting
********************************
Menu accessible here: `Accounting > Configuration > MIS Reporting > MIS Reports Style`

You can create multi-level styles which will be applied to the different lines of reporting:

.. image:: images/06.png
   :width: 1800

The styles are used later in the Template Report definition.

Create a Template Report
************************
Menu accessible here: `Accounting > Configuration > MIS Reporting > MIS Reports Template`

Templates are the base of the reports, defining the KPI structure and calculation
between the elements. They can be found in:

.. image:: images/07.png
   :width: 1800

How to create a template
########################
#. Provide a Description (Name is automatically proposed but can be amended)
#. Value type (Numeric, percentage or string)
#. Comparison Method (Percentage, difference, none)
#. Style: as defined in the Reports Style
#. Style expression: An expression that returns a style depending on the KPI value.
   Such style is applied on top of the row style.
#. Budgetable (if MIS_Budget module is installed): indicates that a budget can be
   provided for the KPI (not needed for calculations)
#. Multi: If True allows to define KPI with multiple values (eg: Initial, Debit,
   Credit, Ending) using Sub-KPI
#. Expression: calculation for the KPI (see below)
#. Display details by account: If set to true will display account details
#. Style for account detail rows: specific style applied to the detailed accounts.

Adding KPI to the current report
################################
KPI are the different element that constitutes the template:

.. image:: images/08.png
   :width: 1800

KPI details:

.. image:: images/09.png
   :width: 1800

Help for the KPI
^^^^^^^^^^^^^^^^
Expressions can be any valid python expressions.

The following special elements are recognized in the expressions to compute accounting
data: {bal|crd|deb}{pieu}[account selecor][journal items domain].

* bal, crd, deb: balance, debit, credit.
* p, i, e: respectivelyl variation over the period, initial balance, ending balance
* The account selector is a like expression on the account code (eg 70%, etc).
* The journal items domain is an Odoo domain filter on journal items.
* balu[]: (u for unallocated) is a special expression that shows the unallocated 
  profit/loss of previous fiscal years.
* Expression can also involve other KPI and query results by name (eg kpi1 + kpi2).

Additionally following variables are available in the evaluation context:

* sum, min, max, len, avg: behave as expected, very similar to the python builtins.
* datetime, datetime, dateutil: the python modules.
* date_from, date_to: beginning and end date of the period.
* AccountingNone: a null value that behaves as 0 in arithmetic operations.

Examples for the KPI
^^^^^^^^^^^^^^^^^^^^
* bal[70]: variation of the balance of account 70 over the period (it is the same as balp[70].
* bali[70,60]: initial balance of accounts 70 and 60.
* bale[1%]: balance of accounts starting with 1 at end of period.
* crdp[40%]: sum of all credits on accounts starting with 40 during the period.
* debp[55%][('journal_id.code', '=', 'BNK1')]: sum of all debits on accounts 55 and
  journal BNK1 during the period.
* balp[('user_type_id', '=', ref('account.data_account_type_receivable').id)][]:
  variation of the balance of all receivable accounts over the period.
* balp[][('tax_line_id.tag_ids', '=', ref('l10n_be.tax_tag_56').id)]: balance of move
  lines related to tax grid 56.

Queries
#######
.. note:: Todo

Sub-KPI
#######
Used when the field `Multi` is set to true for multiple KPI (see `Adding KPI to
the current report`_ and `Trial Balance (sub-KPI)`_). Thanks to this option, one
given KPI can display multiple columns (eg: Initial balance, Debit, Credit and Ending Balance).

Use the Template to create a new Report
***************************************
Menu accessible here: `Accounting > Reports > MIS Reporting > MIS Reports`

Once templates are created, you can use them to display the data for specific
series and dates in order to display the data, compare them and calculate
additional series:

.. image:: images/10.png
   :width: 1800

You can create a new report with different series based on the selected template.

.. image:: images/11.png
   :width: 1800

Create a report
###############

#. Provide a Name
#. Select the Template
#. Select the currency
#. Comparison mode: set to true if you wish to be able to compare data from
   different series or dates.
#. Set your filters: Posted entries or not
#. Base date: important for relative date reports (today by default)
#. Add Columns to your report (if comparison is True)

.. image:: images/12.png
   :width: 1800

Create a new column in the report
#################################

#. Set the label to appear on top of the column as title
#. Select sub-KPI filter if necessary
#. Select the source of the data:

   * Actual: use data from accounting move lines.
   * Actual (Alternative): Use a custom-made series (not accounting moves) with at
     least following fields: initial, debit, credit, ending, dates
   * Sum Columns: Creates a new column sum of others existing in the report
   * Compare Columns: Creates a comparison (percentage) of 2 existing columns
   * MIS Budget (If budget installed): Use Budget Series
#. Dates Mode:

   * Fixed Dates: simply provide the fixed range
   * Relative to report base date: allows to select the period compared with base report date.

     *  `Offset = -1` means previous month.
     *  `Duration = 2` means 2 months from the start of the period

Accessing your Reports
######################
Menu accessible here: `Accounting > Reports > MIS Reports > MIS Reports`

Reports can be displayed from the tree view or the Form view:

.. image:: images/15.png
   :width: 1800

.. image:: images/16.png
   :width: 1800

They can either be (in order of the button):

* Displayed directly in the web interface
* Exported as PDF file
* Exported as Excel File
* Added to a standard Odoo Dashboard

.. note:: When the report is displayed in the web interface user can click on any figure and drill down to the underlying data.

