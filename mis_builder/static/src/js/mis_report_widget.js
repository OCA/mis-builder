/* Copyright 2014-2018 ACSONE SA/NV (<http://acsone.eu>)
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html). */

odoo.define('mis_builder.widget', function (require) {
"use strict";

    var AbstractField = require('web.AbstractField');
    var field_registry = require('web.field_registry');
    var core = require('web.core');
    var data = require('web.data');
    var session = require('web.session');

    var relational_fields = require('web.relational_fields');
    var FieldMany2One = relational_fields.FieldMany2One;
    // var FieldMany2One = core.form_widget_registry.get('many2one');
    var _t = core._t;

    var MisReportWidget = AbstractField.extend({

        /*
         * The following attributes are set after willStart() and are available
         * in the widget template:
         * - mis_report_data: the result of mis.report.instance.compute()
         * - show_settings: a flag that controls the visibility of the Settings
         *   button
         * - has_group_analytic_accounting
         * - hide_analytic_filters: a flag that controls the visibility of the
         *   analytic filters box
         */

        template: "MisReportWidgetTemplate",

        events: _.extend({}, AbstractField.prototype.events, {
            'click .mis_builder_drilldown': 'drilldown',
            'click .oe_mis_builder_print': 'print_pdf',
            'click .oe_mis_builder_export': 'export_xls',
            'click .oe_mis_builder_settings': 'display_settings',
            'click .oe_mis_builder_refresh': 'refresh',
        }),


        /**
         * Return the id of the mis.report.instance to which the widget is
         * bound.
         */
        _instance_id: function () {
            if (this.value) {
                return this.value;
            }

            /*
             * This trick is needed because in a dashboard the view does
             * not seem to be bound to an instance: it seems to be a limitation
             * of Odoo dashboards that are not designed to contain forms but
             * rather tree views or charts.
             */
            var context = this.getParent().state.context;
            if (context['active_model'] === 'mis.report.instance') {
                return context['active_id'];
            }
        },

        init_filter_from_context: function(context) {
            var self = this;
            var filters = context['mis_report_filters'] || {};
            if (filters) {
                for (var filter_name in filters) {
                    self.filter_values[filter_name] = filters[filter_name];
                }
            }
        },
        /**
         * Method called between @see init and @see start. Performs asynchronous
         * calls required by the rendering and the start method.
         */
        willStart: function () {
            var self = this;
            var context = self.getParent().state.context;
            self.analytic_account_id = undefined;
            self.analytic_account_id_domain = [];
            self.analytic_account_id_label = _t("Analytic Account");
            self.analytic_account_id_m2o = undefined;
            self.has_group_analytic_accounting = false;
            self.hide_analytic_filters = false;
            self.filter_values = {};
            self.init_filter_from_context(context);

            var def1 = self._rpc({
                model: 'mis.report.instance',
                method: 'compute',
                args: [self._instance_id()],
                context: context,
            }).then(function (result) {
                self.mis_report_data = result;
            });

            var def2 = self._rpc({
                model: 'res.users',
                method: 'has_group',
                args: ['account.group_account_user'],
                context: context,
            }).then(function (result) {
                self.show_settings = result;
            });

            var def3 = session.user_has_group(
                'analytic.group_analytic_accounting'
            ).then(function(result) {
                self.has_group_analytic_accounting = result;
            });

            var def_hide_analytic_filters = self._rpc({
                model: 'mis.report.instance',
                method: 'read',
                args: [self._instance_id(), ['hide_analytic_filters']],
                context: context,
            }).then(function (result) {
                var record = result[0];
                self.hide_analytic_filters = record['hide_analytic_filters'];
            });

            return $.when(
                this._super.apply(this, arguments),
                def1, def2, def3, def_hide_analytic_filters
            );
        },

        start: function () {
            var self = this;
            self._super.apply(self, arguments);
            self.add_filters();
        },

        init_filter_value: function(field_object, attr_name) {
            var self = this;
            var filter_value = self.filter_values[attr_name];
            if (filter_value !== undefined) {
                field_object.set_value(filter_value);
            }
        },

        set_filter_value: function(field_object, attr_name) {
            var self = this;
            self.filter_values[attr_name] = field_object.get_value();
        },

        add_filters: function () {
            var self = this;
            if (self.hide_analytic_filters) {
                return;
            }
            self.add_analytic_account_filter();
        },

        add_analytic_account_filter: function () {
            var self = this;
            // if (!self.has_group_analytic_accounting) {
            //     return;
            // }
            // if (self.analytic_account_id_m2o) {
            //     // Prevent errors with autocomplete
            //     self.analytic_account_id_m2o.destroy();
            // }
            // var field_name = 'analytic_account_id';
            // // var dfm_object = {};
            // // dfm_object[field_name] = {
            // //     relation: 'account.analytic.account',
            // // };
            // // self.dfm.extend_field_desc(dfm_object);
            // var analytic_account_id_m2o = new FieldMany2One(self, {
            //     attrs: {
            //         placeholder: self.analytic_account_id_label,
            //         name: field_name,
            //         type: 'many2one',
            //         relation: 'account.analytic.account',
            //         domain: self.analytic_account_id_domain,
            //         context: {},
            //         modifiers: '{}',
            //     },
            // });
            // self.init_filter_value(analytic_account_id_m2o, field_name);
            // analytic_account_id_m2o.prependTo(self.get_mis_builder_filter_box());
            // analytic_account_id_m2o.$input.focusout(function () {
            //     self.set_filter_value(analytic_account_id_m2o, field_name);
            // });
            // analytic_account_id_m2o.$follow_button.toggle();
            // self.analytic_account_id_m2o = analytic_account_id_m2o;
        },

        refresh: function () {
            this.replace();
        },

        get_context: function () {
            var self = this;
            var context = new data.CompoundContext(
                self.view.dataset.get_context(), {
                    mis_report_filters: self.filter_values,
                }
            );
            return context;
        },

        print_pdf: function () {
            var self = this;
            var context = self.getParent().state.context;
            this._rpc({
                model: 'mis.report.instance',
                method: 'print_pdf',
                args: [this._instance_id()],
                context: context,
            }).then(function (result) {
                self.do_action(result);
            });
        },

        export_xls: function () {
            var self = this;
            var context = self.getParent().state.context;
            this._rpc({
                model: 'mis.report.instance',
                method: 'export_xls',
                args: [this._instance_id()],
                context: context,
            }).then(function (result) {
                self.do_action(result);
            });
        },

        display_settings: function () {
            var self = this;
            var context = self.getParent().state.context;
            this._rpc({
                model: 'mis.report.instance',
                method: 'display_settings',
                args: [this._instance_id()],
                context: context,
            }).then(function (result) {
                self.do_action(result);
            });
        },

        drilldown: function (event) {
            var self = this;
            var context = self.getParent().state.context;
            var drilldown = $(event.target).data("drilldown");
            this._rpc({
                model: 'mis.report.instance',
                method: 'drilldown',
                args: [this._instance_id(), drilldown],
                context: context,
            }).then(function (result) {
                self.do_action(result);
            });
        },

        get_mis_builder_filter_box: function () {
            var self = this;
            return self.$(".oe_mis_builder_analytic_filter_box");
        },
    });

    field_registry.add("mis_report_widget", MisReportWidget);

    return MisReportWidget;

});
