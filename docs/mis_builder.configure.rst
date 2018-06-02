Access Rights
-------------
User must be included in the group "Accounting / Advisers" to have access to MIS
Builder.

Standard financial MIS Builder menus are located in:

* `Accounting > Report > MIS Builder`
* `Accounting > Report > Configuration > MIS Builder`

Base objects
------------
MIS Reports are based on **KPI** (Sales, Cost, etc.) that needs to be displayed in
certain **Periods** (2018, March, etc.) for certain **Data** (Actual, Budget, etc.):

* **KPI** are defined in the "MIS Report templates"
* **Periods** are defined in the MIS Reports"
* **Actual** Data are coming by default from the standard Odoo Accounting Moves
* **Budget** Data are defined in the "MIS Budgets"

MIS Report Templates
********************
Go to Accounting > Configuration > Financial Reports > MIS Report Templates where
you can create report templates by defining KPI's. KPI's constitute the rows of your
reports. Such report templates are time independent.

.. image:: _static/images/01.png
   :width: 1800

MIS Report
**********
Then in Accounting > Reporting > MIS Reports you can create report instance by binding
the templates to time period, hence defining the columns of your reports.

.. image:: _static/images/02.png
   :width: 1800

.. image:: _static/images/03.png
   :width: 1800
