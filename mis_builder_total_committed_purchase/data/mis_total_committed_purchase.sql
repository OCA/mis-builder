CREATE OR REPLACE VIEW mis_total_committed_purchase AS (
    SELECT ROW_NUMBER() OVER() AS id, mis_total_committed_purchase.* FROM (
        WITH currency_rate as (
            SELECT
              r.currency_id,
              COALESCE(r.company_id, c.id) as company_id,
              r.rate,
              r.name AS date_start,
              (SELECT name FROM res_currency_rate r2
              WHERE r2.name > r.name AND
                    r2.currency_id = r.currency_id AND
                    (r2.company_id is null or r2.company_id = c.id)
               ORDER BY r2.name ASC
               LIMIT 1) AS date_end
            FROM res_currency_rate r
              JOIN res_company c ON (r.company_id is null or r.company_id = c.id)
        )

        /* ALL CONFIRMED PURCHASES */
    SELECT
        pol.company_id AS company_id,
        pol.name AS name,
        po.date_planned::date as date,
        pol.account_analytic_id as analytic_account_id,
        pol.id AS res_id,
        'purchase.order.line' AS res_model,
        CASE
          WHEN (cast(split_part(ip.value_reference, ',', 2) AS INTEGER) IS NOT NULL) THEN cast(split_part(ip.value_reference, ',', 2) AS INTEGER)
          WHEN (cast(split_part(ipc1.value_reference, ',', 2) AS INTEGER) IS NOT NULL) THEN cast(split_part(ipc1.value_reference, ',', 2) AS INTEGER)
          WHEN (cast(split_part(ipc2.value_reference, ',', 2) AS INTEGER) IS NOT NULL) THEN cast(split_part(ipc2.value_reference, ',', 2) AS INTEGER)
          WHEN (cast(split_part(ipc3.value_reference, ',', 2) AS INTEGER) IS NOT NULL) THEN cast(split_part(ipc3.value_reference, ',', 2) AS INTEGER)
          WHEN (cast(split_part(ipc4.value_reference, ',', 2) AS INTEGER) IS NOT NULL) THEN cast(split_part(ipc4.value_reference, ',', 2) AS INTEGER)
          WHEN (cast(split_part(ipc5.value_reference, ',', 2) AS INTEGER) IS NOT NULL) THEN cast(split_part(ipc5.value_reference, ',', 2) AS INTEGER)
          WHEN (cast(split_part(ipd.value_reference, ',', 2) AS INTEGER) IS NOT NULL) THEN cast(split_part(ipd.value_reference, ',', 2) AS INTEGER)
          ELSE cast(NULL AS INTEGER)
        END AS account_id,
        CASE
          WHEN (pol.price_unit / COALESCE(cur.rate, 1.0) * pol.product_qty)::decimal(16,2) >= 0.0 THEN (pol.price_unit / COALESCE(cur.rate, 1.0) * pol.product_qty)::decimal(16,2)
          ELSE 0.0
        END AS debit,
        CASE
          WHEN (pol.price_unit / COALESCE(cur.rate, 1.0) * pol.product_qty)::decimal(16,2)  < 0 THEN (pol.price_unit / COALESCE(cur.rate, 1.0) * pol.product_qty)::decimal(16,2)
          ELSE 0.0
        END AS credit
        FROM purchase_order_line pol
            LEFT JOIN purchase_order po on po.id = pol.order_id
            LEFT JOIN product_product pp ON pp.id = pol.product_id
            LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
            LEFT JOIN product_category pc1 ON pc1.id = pt.categ_id
            LEFT JOIN product_category pc2 ON pc2.id = pc1.parent_id
            LEFT JOIN product_category pc3 ON pc3.id = pc2.parent_id
            LEFT JOIN product_category pc4 ON pc4.id = pc3.parent_id
            LEFT JOIN product_category pc5 ON pc5.id = pc4.parent_id
            LEFT JOIN ir_property ip ON ip.name = 'property_account_expense_id' AND ip.type='many2one' AND ip.res_id ='product.template,' || pt.id
            LEFT JOIN ir_property ipc1 ON ipc1.name = 'property_account_expense_categ_id' AND ipc1.type='many2one' AND ipc1.res_id ='product.category,' || pc1.id
            LEFT JOIN ir_property ipc2 ON ipc2.name = 'property_account_expense_categ_id' AND ipc2.type='many2one' AND ipc2.res_id ='product.category,' || pc2.id
            LEFT JOIN ir_property ipc3 ON ipc3.name = 'property_account_expense_categ_id' AND ipc3.type='many2one' AND ipc3.res_id ='product.category,' || pc3.id
            LEFT JOIN ir_property ipc4 ON ipc4.name = 'property_account_expense_categ_id' AND ipc4.type='many2one' AND ipc4.res_id ='product.category,' || pc4.id
            LEFT JOIN ir_property ipc5 ON ipc5.name = 'property_account_expense_categ_id' AND ipc5.type='many2one' AND ipc5.res_id ='product.category,' || pc5.id
            LEFT JOIN ir_property ipd ON ipd.name = 'property_account_expense_categ_id' AND ipd.type='many2one' AND (ipd.res_id IS NULL OR ipd.res_id = '') AND ipd.company_id=po.company_id
            LEFT JOIN currency_rate cur on (cur.currency_id = po.currency_id and
                cur.company_id = po.company_id and
                cur.date_start <= coalesce(po.date_order, now()) and
                (cur.date_end is null or cur.date_end > coalesce(po.date_order, now())))
        WHERE po.state != 'cancel' AND po.state != 'draft'
    ) AS mis_total_committed_purchase
)
