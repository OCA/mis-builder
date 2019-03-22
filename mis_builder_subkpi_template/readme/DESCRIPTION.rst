This module extends the functionality of MIS-Builder to add MIS Report Sub-KPI
templates.

Sub-KPI Templates allows to predefine a set of sub-KPIs to be used in a
MIS Report template.

A move_line_domain field is defined on Sub-KPI Template Lines, and allows to
specifiy an extra domain to be applied on the move lines for this sub-KPI.

When entering a KPI expression, it will not be needed to fill the expressions
for each sub-KPI, as the extra move line domain is applied automatically on
KPI expressions when flagging the KPI as multi.

Moreover, this module adds a sub-KPI filter at the MIS Report Instance level to
select which sub-KPIs should be displayed on the report.
