To use this module, you need to:

Create a query with SQL BI Editor:

- Use the BI SQL Editor to create your query.
- Make sure your query includes the required fields: `x_credit`, `x_debit`, `x_account_id`, `x_date` and `x_company_id`.
- Optionally, you can include the `x_analytic_account_id` field for analytical account support.

Field Requirements:

- `x_credit`: Must have type float.
- `x_debit`: Must have type float.
- `x_date`: Must have the date type.
- `x_account_id`: Must have the type many2one and be associated with the `account.account` model.
- `x_company_id`: Must have the type many2one and be associated with the `res.company` model.
- `x_analytic_account_id` (optional): Must have the type many2one and be associated with the `account.analytic.account` model.

Activate MIS Builder in the query model:

- Once your query meets the above requirements, click the “Activate MIS Builder” button.
- This will signal that the query should be used in the "Refresh MIS Builder BI SQL Lines" cron.
- Refreshing materialized view will also create new lines in the model (if there are new lines).

Remove MIS Builder in the query model:

- If you no longer need MIS Builder compatibility, click the "Remove MIS Builder" button.
- This will delete the rows and columns related to your BI SQL model.

Create MIS Builder report:

- When creating a MIS Builder Report, select "BI SQL MIS Builder Line" as the source.
- Afterwards, select the BI SQL View you want to use (The view must have MIS Builder activated).
- When creating kpis for this report, you can use MIS expressions to filter the fields in your query.
- To do this, it is necessary to use the name of the BI SQL View.
- Example: `bal[][('x_bi_sql_view_mis.x_name', '=', 'test')]`.
- This will filter out the lines in your query that have the `x_name` field with "test" as the value.
