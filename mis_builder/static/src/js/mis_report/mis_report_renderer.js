odoo.define('web.MisReportRenderer', function(require) {
    "use strict";

    var BasicRenderer = require('web.BasicRenderer');
    var FieldManagerMixin = require('web.FieldManagerMixin');

    var relational_fields = require('web.relational_fields');
    var Data = require('web.data');
    var Core = require('web.core');
    var Session = require('web.session');
    var _t = Core._t;

    var MisReportRenderer = BasicRenderer.extend(FieldManagerMixin, {
        template: 'MisReportView',
        events: _.extend({}, BasicRenderer.prototype.events, {
            'click .mis_builder_drilldown': '_drilldown',
            'click .oe_mis_builder_print': '_print_pdf',
            'click .oe_mis_builder_export': '_export_xls',
            'click .oe_mis_builder_refresh': '_refresh',
        }),

        _getReportData: function() {
            var self = this;
            return this._rpc({
                model: 'mis.report.instance',
                method: 'compute',
                args: [self.instance_id],
                context: self.context,
            }).then(function(result) {
                self.mis_report_data = result;
            });
        },

        _getSettings: function() {
            var self = this;
            return this._rpc({
                model: 'res.users',
                method: 'has_group',
                args: ['account.group_account_user'],
                context: self.instance_context,
            }).then(function(result) {
                self.show_settings = result;
            });
        },

        init: function(parent, state, params) {
            this.state = state;
            this.instance_id = state.data.id;
            this.instance_context = state.context;
            this._super.apply(this, arguments);
        },

        _checkAccessAnalytic: function() {
            var self = this;
            return Session.user_has_group(
                'analytic.group_analytic_accounting',
            ).then(function(result) {
                self.has_group_analytic_accounting = result;
            });
        },

        _hideAnalyticFilters: function() {
            var self = this;
            return this._rpc({
                model: 'mis.report.instance',
                method: 'read',
                args: [self.instance_id, ['hide_analytic_filters']],
                context: self.instance_context,
            }).then(function(result) {
                var record = result[0];
                self.hide_analytic_filters = record['hide_analytic_filters'];
            });
        },

        willStart: function() {
            this.analytic_account_id = undefined;
            this.analytic_account_id_domain = [];
            this.analytic_account_id_label = _t("Analytic Account");
            this.analytic_account_id_m2o = undefined;
            this.has_group_analytic_accounting = false;
            this.hide_analytic_filters = false;
            this.filter_values = {};
            this.init_filter_from_context();
            return $.when(
                this._getReportData(),
                this._getSettings(),
                this._checkAccessAnalytic(),
                this._hideAnalyticFilters(),
                this._super.apply(this, arguments),
            );
        },

        start: function() {
            this._super();
            this.add_filters();
        },

        init_filter_value: function(field_object, attr_name) {
            var self = this;
            var filter = self.filter_values[attr_name];
            if (filter !== undefined && filter['value'] !== undefined) {
                field_object.set_value(filter['value']);
            }
        },

        init_filter: function(filter_name) {
            var self = this;
            if (self.filter_values[filter_name] === undefined) {
                self.filter_values[filter_name] = {};
            }
        },

        set_filter_value: function(field_object, attr_name) {
            var self = this;
            self.init_filter(attr_name);
            self.filter_values[attr_name]['value'] =
                field_object.value || undefined;
        },

        set_filter_operator: function(operator, attr_name) {
            var self = this;
            self.init_filter(attr_name);
            self.filter_values[attr_name]['operator'] = operator;
        },

        get_filter_operator: function(attr_name) {
            var self = this;
            var operator = undefined;
            if (self.filter_values[attr_name] !== undefined) {
                operator = self.filter_values[attr_name]['operator'] || '=';
            }
            return operator;
        },

        add_filters: function() {
            var self = this;
            if (self.hide_analytic_filters) {
                return;
            }
            self.add_analytic_account_filter();
        },

        init_filter_from_context: function() {
            var self = this;
            var filters = this.instance_context['mis_report_filters'] || {};
            self.filter_values = filters;
        },

        add_analytic_account_filter: function() {
            var self = this;
            if (!self.has_group_analytic_accounting) {
                return;
            }
            if (self.analytic_account_id_m2o) {
                // Prevent errors with autocomplete
                self.analytic_account_id_m2o.destroy();
            }
            var field_name = 'analytic_account_id';
            var record = this.getParent().model.get(this.getParent().handle);
            var analytic_account_id_m2o = new relational_fields.FieldMany2One(self,
                field_name,
                record, {
                    mode: 'edit',
                    attrs: {
                        placeholder: self.analytic_account_id_label,
                        // name: field_name,
                        // type: 'many2one',
                        domain: self.analytic_account_id_domain,
                        // context: {},
                        // modifiers: '{}',
                        options: '{"no_create": true}',
                    },
                }
            );
            self.fields = {
                field_name: analytic_account_id_m2o
            };
            self.init_filter_value(analytic_account_id_m2o, field_name);
            analytic_account_id_m2o.appendTo(self.get_mis_builder_filter_box());
            analytic_account_id_m2o.$input.focusout(function() {
                self.set_filter_value(analytic_account_id_m2o, field_name);
            });
            analytic_account_id_m2o.$external_button.toggle();
            self.analytic_account_id_m2o = analytic_account_id_m2o;
        },

        get_mis_builder_filter_box: function () {
            var self = this;
            return self.$(".oe_mis_builder_analytic_filter_box");
        },

        _refresh: function() {
            this.replace();
        },

        _print_pdf: function() {
            var self = this;
            this._rpc({
                model: 'mis.report.instance',
                method: 'print_pdf',
                args: [self.instance_id],
                context: self.instance_context,
            }).then(function(result) {
                self.do_action(result);
            });
        },

        _export_xls: function() {
            var self = this;
            this._rpc({
                model: 'mis.report.instance',
                method: 'export_xls',
                args: [self.instance_id],
                context: self.instance_context,
            }).then(function(result) {
                self.do_action(result);
            });
        },

        _drilldown: function(event) {
            var self = this;
            var drilldown = $(event.target).data("drilldown");
            this._rpc({
                model: 'mis.report.instance',
                method: 'drilldown',
                args: [self.instance_id, drilldown],
                context: self.instance_context,
            }).then(function(result) {
                self.do_action(result);
            });
        },

    });

    return MisReportRenderer;
});
