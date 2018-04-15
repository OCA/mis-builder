.. |LOGO| image:: https://odoo-community.org/logo.png
   :align: middle
   :width: 100
.. |TITLE| replace:: MIS Builder (OCA Financial report builder)
.. |SOFT| replace:: Odoo 8.0, 9.0, 10.0, 11.0 (CE and EE)
.. |REPO| replace:: https://github.com/OCA/mis-builder
.. |AUTHOR| replace:: Stéphane Bidoul (Acsone, NV)
.. |LICENSE| replace:: AGPLv3

+----------------------+----------------------+----------------------+
|                      | **Title**            | **Version**          |
|                      |                      |                      |
| |LOGO|               | |TITLE|              | |SOFT|               |
+----------------------+----------------------+----------------------+
| **Author**           | **Repository**       | **License**          |
|                      |                      |                      |
| |AUTHOR|             | |REPO|               | |LICENSE|            |
+----------------------+----------------------+----------------------+

.. topic:: Overview

    * This document is a Functional Documentation for Odoo set of modules.
    * Maintainer: `Odoo Community Association <https://odoo-community.org>`_
    * OCA, or the Odoo Community Association, is a nonprofit organization whose
      mission is to support the collaborative development of Odoo features and
      promote its widespread use.
    * To contribute to this documentation, please visit
      https://odoo-community.org/page/Contribute.
    * This document is licensed under a `Creative Commons Attribution 4.0 International
      License <http://creativecommons.org/licenses/by/4.0/>`_.

Introduction
============

MIS Builder is an Odoo module that implements a class of Odoo reports where KPI
(Key Performance Indicators) are displayed in rows, and time periods in columns.
It focuses on very fast reporting on accounting data but can also use data from
any other Odoo model.

It features the following key characteristics:

- User-friendly configuration: end users can create new report templates without
  development, sing simple Excel-like formulas.
- Very fast balance reporting for accounting data, even on million-line databases
  with very complex account charts.
- Reusability: Use the same template for different reports.
- Multi-period comparisons: Compare data over different time periods.
- User-configurable styles: perfectly rendered in the UI as well as in Excel and
  PDF exports.
- Interactive display with drill-down.
- WYSIWYG Export to PDF and Excel.
- A budgeting module.
- KPI Evaluation over various data sources, such as actuals, simulation, committed
  costs (custom developments are required to create the data source).
- Easy-to-use API for developers for the accounting balance computation engine.

Modules information
*******************
`MIS Builder` is a set of modules, part of `Odoo Business Suite of Applications <https://www.odoo.com>`_.

The source code of the modules can be found in the `OCA Official Github repository <https://github.com/OCA/mis-builder/>`_:

The main modules are the following:

* `mis_builder` module installs the "MIS Reports", "MIS Reports Styles" and "MIS
  report Template" menu. This module is the base one and is necessary for any other
  module.
* `mis_builder_budget` module installs the "MIS Budget" menu.
* `mis_builder_demo` module installs the demo data reports in existing MIS.

The repository is licensed under `AGPLv3 <http://www.gnu.org/licenses/agpl-3.0-standalone.html>`_.

`MIS Builder` is available for the following versions (at the time of this document):

* 8.0,
* 9.0,
* 10.0,
* 11.0
* in both Community and Enterprise Edition.

About this documentation
************************
This documentation intends to provide the basic knowledge for the user to create
financial reports from the standard Odoo financial entries.

The user must have standard knowledge of Odoo usability and functions (Accounting).

No development skills are necessary to use the module but some set up parts requires
light technical knowledge.