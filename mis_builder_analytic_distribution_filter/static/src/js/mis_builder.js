/* © 2016 ACSONE SA/NV
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). 
 */

openerp.mis_builder_analytic_distribution_filter = function(instance) {
    var _t = instance.web._t;

    instance.mis_builder.MisReport.include({

        init: function() {
            this._super.apply(this, arguments);
            this.analytic_distribution_id = false;
            this.distribution_initialized = false;
        },
        get_context: function() {
            var self = this;
            context = this._super.apply(this, arguments);
            context['analytic_distribution_id'] = this.analytic_distribution_id;
            return context
        },
        init_fields: function() {
            var self = this;
            var had_dfm = !!self.dfm;
            this._super.apply(this, arguments);
            if (self.had_dfm)
                return;
            self.dfm.extend_field_desc({
                distribution: {
                    relation: "account.analytic.plan.instance",
                },
            });
            self.distribution_m2o = new instance.web.form.FieldMany2One(self.dfm, {
                attrs: {
                    placeholder: _t("Analytic Distribution"),
                    name: "distribution",
                    type: "many2one",
                    domain: [],
                    context: {},
                    modifiers: '{}',
                },
            });
            if (this.distribution_initialized) {
                self.distribution_m2o.set('value', this.analytic_distribution_id);
            } else {
                val = self.getParent().dataset.context.analytic_distribution_id;
                if (val) {
                    self.distribution_m2o.set('value', val);
                    this.analytic_distribution_id = val
                }
                this.distribution_initialized = true;
            }
            self.distribution_m2o.prependTo(self.$(".oe_mis_builder_analytic_axis"));
            self.distribution_m2o.$input.focusout(function(){
                self.analytic_distribution_id = self.distribution_m2o.get_value();
            });
        },
    });
}
