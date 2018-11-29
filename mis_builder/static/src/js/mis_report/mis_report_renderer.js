odoo.define('web.MisReportRenderer', function(require) {
    "use strict";

    var BasicRenderer = require('web.BasicRenderer');
    var FieldManagerMixin = require('web.FieldManagerMixin');
    var session = require('web.session');
    var Dialog = require('web.Dialog');
    var Widget = require('web.Widget');

    var relational_fields = require('web.relational_fields');
    var Data = require('web.data');
    var Core = require('web.core');
    var Session = require('web.session');
    var _t = Core._t;

    var MisReportRenderer = BasicRenderer.extend({
        template: 'MisReportView',
        events: _.extend({}, BasicRenderer.prototype.events, {
            'click .mis_builder_drilldown': '_drilldown',
            'click .oe_mis_builder_print': '_print_pdf',
            'click .oe_mis_builder_export': '_export_xls',
            'click .oe_mis_builder_refresh': '_refresh',
        }),
        custom_events: _.extend({}, BasicRenderer.prototype.custom_events, {
            changeFilter: '_onChangeFilter',
        }),

        init: function(parent, state, params) {
            this._super.apply(this, arguments);
            this.state = state;
            this.instance_id = state.data.id;
            this.instance_context = state.context;
        },

        get_instance_id: function () {
            var self = this;
            var context = self.get_context();
            if (this.instance_id) {
                return this.instance_id;
            } else if (context['active_model'] === 'mis.report.instance') {
                return context['active_id'];
            };
        },

        get_context: function () {
            var self = this;
            return _.extend({}, self.instance_context, {
                mis_report_filters: self.filter_values,
            });
        },

        _render: function() {
            var self = this;
            return this._super().then(function() {
                var record = self.getParent().model.get(self.getParent().handle);
                var options = {
                    record: record,
                    fields: self.state.fields,
                    fieldName: 'analytic_account_id',
                };
                var filter = new SidebarFilter(self, options);
                filter.prependTo(self.$el);
            });
        },

        _onChangeFilter: function (event) {
            this.set_filter_value(event.data);
            this._refresh();
        },

        _getReportData: function() {
            var self = this;
            return this._rpc({
                model: 'mis.report.instance',
                method: 'compute',
                args: [self.get_instance_id()],
                context: self.get_context(),
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
                context: self.get_context(),
            }).then(function(result) {
                self.show_settings = result;
            });
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
                args: [self.get_instance_id(), ['hide_analytic_filters']],
                context: self.instance_context,
            }).then(function(result) {
                var record = result[0];
                self.hide_analytic_filters = record['hide_analytic_filters'];
            });
        },

        willStart: function() {
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
            this.model = this.getParent().model;
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

        set_filter_value: function(filter) {
            var self = this;
            self.init_filter(filter.fieldName);
            self.filter_values[filter.fieldName] = filter;
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
            // FIXME
            // self.add_analytic_account_filter();
        },

        init_filter_from_context: function() {
            var self = this;
            var filters = this.instance_context['mis_report_filters'] || {};
            self.filter_values = filters;
        },

        get_mis_builder_filter_box: function () {
            var self = this;
            return self.$(".oe_mis_builder_analytic_filter_box");
        },

        _refresh: function() {
            this.replace();
            this._getReportData();
        },

        _print_pdf: function() {
            var self = this;
            this._rpc({
                model: 'mis.report.instance',
                method: 'print_pdf',
                args: [self.get_instance_id()],
                context: self.get_context(),
            }).then(function(result) {
                self.do_action(result);
            });
        },

        _export_xls: function() {
            var self = this;
            this._rpc({
                model: 'mis.report.instance',
                method: 'export_xls',
                args: [self.get_instance_id()],
                context: self.get_context(),
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
                args: [self.get_instance_id(), drilldown],
                context: self.get_context(),
            }).then(function(result) {
                self.do_action(result);
            });
        },

    });

    var SidebarFilter = Widget.extend(FieldManagerMixin, {
        tagName: 'div',
        custom_events: _.extend({}, FieldManagerMixin.custom_events, {
            field_changed: '_onFieldChanged',
        }),
        /**
        * @constructor
        * @param {Widget} parent
        * @param {Object} options
        * @param {string} options.fieldName
        * @param {Object[]} options.filters A filter is an object with the
        *   following keys: id, value, label, active, avatar_model, color,
        *   can_be_removed
        * @param {Object} [options.favorite] this is an object with the following
        *   keys: fieldName, model, fieldModel
        */
        init: function (parent, options) {
            this._super.apply(this, arguments);
            FieldManagerMixin.init.call(this);

            this.fields = options.fields;
            this.fieldName = options.fieldName;
            this.record = options.record;
        },

        willStart: function () {
            var self = this;

            return this._super().then(function () {
                self.many2one = new relational_fields.FieldMany2One(
                    self,
                    self.fieldName,
                    self.record,
                    {
                        mode: 'edit',
                        can_create: false,
                        viewType: 'mis_report',
                        attrs: {
                            string: 'Analytic Account',
                            type: 'many2one',
                        }
                    }
                );
            });

        },
        start: function () {
            this._super();
            if (this.many2one) {
                this.many2one.appendTo(this.$el);
            }
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
        * @param {OdooEvent} event
        */
        _onFieldChanged: function (event) {
            var self = this;
            event.stopPropagation();
            var value = event.data.changes[this.fieldName].id;
            self.trigger_up('changeFilter', {
                'fieldName': self.fieldName,
                'value': value,
            });
        },
    });

    return MisReportRenderer;
});
