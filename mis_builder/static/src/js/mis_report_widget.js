/* Copyright 2014-2018 ACSONE SA/NV (<http://acsone.eu>)
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html). */

odoo.define('mis_builder.widget', function (require) {
"use strict";

    var AbstractField = require('web.AbstractField');
    var field_registry = require('web.field_registry');
    var relational_fields = require('web.relational_fields');

    var core = require('web.core');
    var session = require('web.session');

    var _t = core._t;

    var MisReportWidget = AbstractField.extend({

        template: "MisReportWidgetTemplate",

        custom_events: _.extend({}, AbstractField.prototype.custom_events, {
            'field_changed': 'on_field_changed',
        }),
        events: _.extend({}, AbstractField.prototype.events, {
            'click .mis_builder_drilldown': 'drilldown',
            'click .oe_mis_builder_print': 'print_pdf',
            'click .oe_mis_builder_export': 'export_xls',
            'click .oe_mis_builder_settings': 'display_settings',
            'click .oe_mis_builder_refresh': 'refresh',
        }),

        /*
         * The following attributes are set after willStart() and are available
         * in the widget template:
         * - mis_report_data: the result of mis.report.instance.compute()
         * - show_settings: a flag that controls the visibility of the Settings
         *   button
         */

        init: function () {
            var self = this;
            self._super.apply(self, arguments);
            self.analytic_account_id_m2o = undefined;
            self.analytic_account_id_domain = [];
            self.analytic_account_id_label = _t("Analytic Account");
            self.has_group_analytic_accounting = false;
            self.hide_analytic_filters = false;
            self.filter_values = {};
            self.init_filter_from_context();
        },

        init_filter_from_context: function() {
            var self = this;
            var filters = self.getParent().state.context['mis_report_filters'] || {};
            self.filter_values = filters;
        },

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

        /**
         * Method called between @see init and @see start. Performs asynchronous
         * calls required by the rendering and the start method.
         */
        willStart: function () {
            var self = this;
            var context = self.getParent().state.context;

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

            return $.when(this._super.apply(this, arguments), def1, def2, def3, def_hide_analytic_filters);
        },

        start: function () {
            var self = this;
            self._super.apply(self, arguments);
            self.add_filters();
        },

        init_filter_value: function(field_object, attr_name) {
            var self = this;
            var filter = self.filter_values[attr_name];
            if (filter !== undefined && filter['value'] !== undefined) {
                if (field_object.formatType == "many2one") {
                    field_object.value = filter['value'][0];
                    field_object.m2o_value = filter['value'][1];
                } else {
                    // TODO (m2m)
                }
            }
        },

        init_filter: function(filter_name) {
            var self = this;
            if(self.filter_values[filter_name] === undefined) {
                self.filter_values[filter_name] = {};
            }
        },

        set_filter_value: function(field_object, attr_name, new_val) {
            var self = this;
            self.init_filter(attr_name);
            if (field_object.formatType == "many2one") {
                self.filter_values[attr_name]['value'] =
                    [new_val.id, new_val.display_name] || undefined;
            } else {
                // TODO (m2m)
            }
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
            if (!self.has_group_analytic_accounting) {
                return;
            }
            if (self.analytic_account_id_m2o) {
                // Prevent errors with autocomplete
                self.analytic_account_id_m2o.destroy();
            }
            var field_name = 'analytic_account_id';
            self.analytic_account_id_m2o = new relational_fields.FieldMany2One(self, "analytic_account_filter_id", self.record, {
                mode: 'edit',
                viewType: self.viewType,
                attrs: {
                    can_write: false,
                    can_create: false,
                },
            });
            self.init_filter_value(self.analytic_account_id_m2o, field_name);

            // Add field to view
            self.analytic_account_id_m2o.prependTo(self.get_mis_builder_filter_box());
            self.analytic_account_id_m2o.$external_button.hide();
        },

        refresh: function () {
            this.replace();
        },

        on_field_changed: function (event) {
            var self = this;
            if (event && event.data.changes) {
                var changes = event.data.changes;
                if (changes['analytic_account_filter_id'] !== undefined) {
                    var field_name = 'analytic_account_id';
                    var new_val = changes['analytic_account_filter_id'];
                    self.set_filter_value(self.analytic_account_id_m2o, field_name, new_val);
                }
            }
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
