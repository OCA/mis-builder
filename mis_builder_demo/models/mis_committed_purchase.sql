CREATE OR REPLACE VIEW mis_committed_purchase AS (
	SELECT ROW_NUMBER() OVER() AS id, mis_committed_purchase.* FROM (

        /* /!\ Multi currency is left as an exercise for the reader /!\ */
	
        /* UNINVOICED PURCHASES */
	SELECT
		'uninvoiced purchase' AS line_type,
                pol.company_id AS company_id,
		pol.name AS name,
		po.date_planned as date,
		CASE
		  WHEN (cast(split_part(ip.value_reference, ',', 2) AS INTEGER) IS NOT NULL) THEN cast(split_part(ip.value_reference, ',', 2) AS INTEGER)
		  WHEN (cast(split_part(ipc.value_reference, ',', 2) AS INTEGER) IS NOT NULL) THEN cast(split_part(ipc.value_reference, ',', 2) AS INTEGER)
		  WHEN (cast(split_part(ipd.value_reference, ',', 2) AS INTEGER) IS NOT NULL) THEN cast(split_part(ipd.value_reference, ',', 2) AS INTEGER)
		  ELSE cast(NULL AS INTEGER)
		END AS account_id,
		CASE
		  WHEN (pol.price_unit * (pol.product_qty - pol.qty_invoiced))::decimal(16,2) >= 0.0 THEN (pol.price_unit * (pol.product_qty - pol.qty_invoiced))::decimal(16,2)
		  ELSE 0.0
		END AS debit,
		CASE
		  WHEN (pol.price_unit * (pol.product_qty - pol.qty_invoiced))::decimal(16,2)  < 0 THEN (pol.price_unit * (pol.product_qty - pol.qty_invoiced))::decimal(16,2)
		  ELSE 0.0
		END AS credit
		FROM purchase_order_line pol
			LEFT JOIN purchase_order po on po.id = pol.order_id
			LEFT JOIN product_product pp ON pp.id = pol.product_id
			LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
			LEFT JOIN product_category pc ON pc.id = pt.categ_id
			LEFT JOIN ir_property ip ON ip.name = 'property_account_expense_id' AND ip.type='many2one' AND ip.res_id ='product.template,' || pt.id
			LEFT JOIN ir_property ipc ON ipc.name = 'property_account_expense_categ_id' AND ipc.type='many2one' AND ipc.res_id ='product.category,' || pc.id
			LEFT JOIN ir_property ipd ON ipd.name = 'property_account_expense_categ_id' AND ipd.type='many2one' AND (ipd.res_id IS NULL OR ipd.res_id = '')
		WHERE pol.product_qty > pol.qty_invoiced AND po.state != 'cancel' AND po.state != 'draft'

	UNION ALL

        /* DRAFT INVOICES */
	SELECT
		'draft invoice' AS line_type,
                ail.company_id AS company_id,
		ail.name AS name,
		ail.create_date as date,
		ail.account_id as account_id,
		CASE
		  WHEN (ail.price_subtotal)::decimal(16,2) >= 0.0 THEN (ail.price_subtotal)::decimal(16,2)
		  ELSE 0.0
		END AS debit,
		CASE
		  WHEN (ail.price_subtotal)::decimal(16,2)  < 0 THEN (ail.price_subtotal)::decimal(16,2)
		  ELSE 0.0
		END AS credit
		FROM account_invoice_line ail
			LEFT JOIN account_invoice ai ON ai.id = ail.invoice_id
		WHERE ai.state = 'draft' AND ai.type IN ('in_invoice', 'in_refund')
	) AS mis_committed_purchase
)
