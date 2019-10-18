The ``account_id`` field of the model selected in 'Move lines source'
in the Period form can now be a Many2one
relationship with any model that has a ``code`` field (not only with
``account.account`` model). To this end, the model to be used for Actuals
move lines can be configured on the report template. It can be something else
than move lines and the only constraint is that its ``account_id`` field
as a ``code`` field.
