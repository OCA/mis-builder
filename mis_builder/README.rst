.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

===========
MIS Builder
===========

This module allows you to build Management Information Systems dashboards.
Such style of reports presents KPI in rows and time periods in columns.
Reports mainly fetch data from account moves, but can also combine data coming
from arbitrary Odoo models. Reports can be exported to PDF, Excel and they
can be added to Odoo dashboards.

Installation
============

Your preferred way to install addons will work with MIS Builder.

An easy way to install it with all its dependencies is using pip:

* ``pip install odoo10-addon-mis_builder odoo-autodiscover``
* then restart Odoo, update the addons list in your database, and install
  the MIS Builder application.

Configuration and Usage
=======================

To configure this module, you need to:

* Go to Accounting > Configuration > Financial Reports > MIS Report Templates where
  you can create report templates by defining KPI's. KPI's constitute the rows of your
  reports. Such report templates are time independent.

.. figure:: static/description/ex_report_template.png
   :scale: 80 %
   :alt: Sample report template

* Then in Accounting > Reporting > MIS Reports you can create report instance by
  binding the templates to time period, hence defining the columns of your reports.

.. figure:: static/description/ex_report.png
   :alt: Sample report configuration

* From the MIS Report view, you can preview the report, add it to and Odoo dashboard,
  and export it to PDF or Excel.

.. figure:: static/description/ex_dashboard.png
   :alt: Sample dashboard view

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/248/10.0

Developer notes
===============

A typical extension is to provide a mechanism to filter reports on analytic dimensions
or operational units. To implement this, you can override _get_additional_move_line_filter
and _get_additional_filter to further filter move lines or queries based on a user
selection. A typical use case could be to add an analytic account field on mis.report.instance,
or even on mis.report.instance.period if you want different columns to show different
analytic accounts.

Known issues / Roadmap
======================

The mis_builder `roadmap <https://github.com/OCA/mis-builder/issues?q=is%3Aopen+is%3Aissue+label%3Aenhancement>`_ 
and `known issues <https://github.com/OCA/mis-builder/issues?q=is%3Aopen+is%3Aissue+label%3Abug>`_ can 
be found on github.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/mis-builder/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Author
------

* Stéphane Bidoul <stephane.bidoul@acsone.eu>

Contributors
------------

* Laetitia Gangloff <laetitia.gangloff@acsone.eu>
* Adrien Peiffer <adrien.peiffer@acsone.eu>
* Alexis de Lattre <alexis.delattre@akretion.com>
* Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
* Jordi Ballester <jordi.ballester@eficent.com>
* Thomas Binsfeld <thomas.binsfeld@gmail.com>
* Giovanni Capalbo <giovanni@therp.nl>
* Marco Calcagni <mcalcagni@dinamicheaziendali.it>
* Sébastien Beau <sebastien.beau@akretion.com>
* Laurent Mignon <laurent.mignon@acsone.eu>
* Luc De Meyer <luc.demeyer@noviat.com>
* Benjamin Willig <benjamin.willig@acsone.eu>
* Martronic SA <info@martronic.ch>  
* nicomacr <nmr@adhoc.com.ar>
* Juan Jose Scarafia <jjs@adhoc.com.ar>
* Richard deMeester <richard@willowit.com.au>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
