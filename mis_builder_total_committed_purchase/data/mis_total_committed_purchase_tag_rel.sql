CREATE OR REPLACE VIEW mis_total_committed_purchase_tag_rel AS(
    SELECT
        po_mcp.id AS mis_total_committed_purchase_id,
        po_rel.account_analytic_tag_id AS account_analytic_tag_id
        FROM account_analytic_tag_purchase_order_line_rel AS po_rel
        INNER JOIN mis_total_committed_purchase AS po_mcp ON
            po_mcp.res_id = po_rel.purchase_order_line_id
        WHERE po_mcp.res_model = 'purchase.order.line'
    UNION ALL
    SELECT
        inv_mcp.id AS mis_total_committed_purchase_id,
        inv_rel.account_analytic_tag_id AS account_analytic_tag_id
        FROM account_analytic_tag_account_move_line_rel AS inv_rel
        INNER JOIN mis_total_committed_purchase AS inv_mcp ON
            inv_mcp.res_id = inv_rel.account_move_line_id
        WHERE inv_mcp.res_model = 'account.move.line'
)
