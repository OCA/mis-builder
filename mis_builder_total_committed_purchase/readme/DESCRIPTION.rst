Addon to create a alternative source based on all purchase order lines with MIS Builder : all the purchase orders that are not in draft or cancelled state are taken into account.

The account_id of the committed purchase bases itself on the product's account_id if set

-   If not, it bases itself on the product_category's account_id if set

    -   If not, it bases itself on the first set account_id on five generations of parent_category

        -   If none of them is set, it bases itself on the default value for new resources

            - Finally if it's not set, the account_id is set to 0


**Needed improvement :**

It would be better if the account_id tried to base itself on all the generations of parent_category, as long as it is set.
