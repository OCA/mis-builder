Since Odoo 16 a journal item no longer has one analytic account: it has an
`analytic_distribution` that can split it between several accounts. The analytic
filter of a MIS report on journal items keeps the **full** balance of every item
whose distribution contains the analytic account, so a P&L per project, contract or
department is overstated whenever an item is split. Costs that only exist as
analytic lines, such as timesheets, are not seen at all.

This module adds `mis.analytic.move.line`, a SQL view over `account.analytic.line`
with the fields MIS Builder expects from a move lines source (`account_id`,
`company_id`, `date`, `debit`, `credit`, `parent_state`, `analytic_distribution`).
Analytic lines already carry the prorated amount, so a MIS report that uses this
model as its move lines source gives the exact figures per analytic account,
including timesheet costs.

Each analytic line holds one account per root analytic plan. The view exposes them
as one distribution key (`"project_account,department_account"` at 100%), the same
format as journal items, so the analytic filter works for the accounts of every plan
and a line is never counted twice.
