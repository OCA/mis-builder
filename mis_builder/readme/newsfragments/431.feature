A mis.report.subreport record is a dependency between a report and a subreport.
ONDELETE is now set on these fields, so that if you delete a mis.report:
(1) If the report depends on other reports, the dependencies will be deleted.
(2) If other reports depend on the report, raise restrict error.
