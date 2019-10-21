/* Copyright 2014-2019 ACSONE SA/NV (<http://acsone.eu>)
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html). */

odoo.define('mis_builder.widget', function (require) {
"use strict";

    var AbstractField = require('web.AbstractField');
    var StandaloneFieldManagerMixin = require('web.StandaloneFieldManagerMixin');
    var field_registry = require('web.field_registry');
    var relational_fields = require('web.relational_fields');
    var BasicModel = require('web.BasicModel');

    var core = require('web.core');
    var session = require('web.session');

    var _t = core._t;

    var MisReportWidget = AbstractField.extend(StandaloneFieldManagerMixin, {

        template: "MisReportWidgetTemplate",

        events: _.extend({}, AbstractField.prototype.events, {
            'click .mis_builder_drilldown': 'drilldown',
            'click .oe_mis_builder_print': 'print_pdf',
            'click .oe_mis_builder_export': 'export_xls',
            'click .oe_mis_builder_settings': 'display_settings',
            'click .oe_mis_builder_refresh': 'refresh',
        }),

        init: function () {
            var self = this;
            self._super.apply(self, arguments);
            StandaloneFieldManagerMixin.init.call(self);
            self.model = new BasicModel(self);  // for FieldManagerMixin
            self.analytic_account_id_domain = [];  // TODO unused for now
            self.analytic_account_id_label = _t("Analytic Account Filter");
            self.analytic_account_id_m2o = undefined;  // Field widget
            self.analytic_tag_ids_domain = [];  // TODO unused for now
            self.analytic_tag_ids_label = _t("Analytic Tags Filter");
            self.analytic_tag_ids_m2m = undefined;  // Field widget
            self.mis_report_data = undefined;
            self.show_settings = false;
            self.has_group_analytic_accounting = false;
            self.has_group_analytic_tags = false;
            self.hide_analytic_filters = false;
        },

        _get_filter_value: function(name) {
            var filters = this.getParent().state.context['mis_report_filters'] || {};
            var filter = filters[name] || {};
            return filter.value;
        },

        _set_filter_value: function(name, value, operator) {
            var context = this.getParent().state.context;
            var filters;
            if (context['mis_report_filters'] === undefined) {
                filters = {}
                context['mis_report_filters'] = filters;
            } else {
                filters =  context['mis_report_filters'];
            }
            if (value === undefined) {
                filters[name] = {};
                return
            }
            filters[name] = {
                value: value,
                operator: operator,
            };
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

            var def2 = session.user_has_group(
                'analytic.group_account_user'
            ).then(function (result) {
                self.show_settings = result;
            });

            var def3 = session.user_has_group(
                'analytic.group_analytic_accounting'
            ).then(function (result) {
                self.has_group_analytic_accounting = result;
            });

            var def4 = session.user_has_group(
                'analytic.group_analytic_accounting'  // TODO change in v12
            ).then(function (result) {
                self.has_group_analytic_tags = result;
            });

            var def5 = self._rpc({
                model: 'mis.report.instance',
                method: 'read',
                args: [self._instance_id(), ['hide_analytic_filters']],
                context: context,
            }).then(function (result) {
                self.hide_analytic_filters = result[0]['hide_analytic_filters'];
            });

            return $.when(this._super.apply(this, arguments), def1, def2, def3, def4, def5);
        },

        start: function () {
            var self = this;
            self._super.apply(self, arguments);
            self._add_analytic_filters();
        },

        /**
         * Create list of field descriptors to be provided
         * to BasicModel.makeRecord.
         */
        _get_filter_fields: function() {
            var self = this;
            var fields = []
            if (self.has_group_analytic_accounting) {
                fields.push({
                    relation: 'account.analytic.account',
                    type: 'many2one',
                    name: 'filter_analytic_account_id',
                    value: self._get_filter_value('analytic_account_id'),
                });
            }
            if (self.has_group_analytic_tags) {
                fields.push({
                    relation: 'account.analytic.tag',
                    type: 'many2many',
                    name: 'filter_analytic_tag_ids',
                    value: self._get_filter_value('analytic_tag_ids'),
                });
            }
            return fields;
        },

        /**
         * Create fieldInfo structure to be provided
         * to BasicModel.makeRecord.
         */
        _get_filter_fieldInfo: function() {
            return {};
        },

        /**
         * Create analytic filter widgets and add them in the filter box.
         */
        _make_filter_field_widgets: function(record) {
            var self = this;
            
            if (self.has_group_analytic_accounting) {
                self.analytic_account_id_m2o = new relational_fields.FieldMany2One(self,
                    'filter_analytic_account_id',
                    record,
                    {
                        mode: 'edit',
                        attrs: {
                            placeholder: self.analytic_account_id_label,
                            options: {
                                no_create: 'True',
                                no_open: 'True',
                            },
                        },
                    }
                );
                self._registerWidget(record.id, self.analytic_account_id_m2o.name, self.analytic_account_id_m2o);
                self.analytic_account_id_m2o.appendTo(self.get_mis_builder_filter_box());
            }

            if (self.has_group_analytic_tags) {
                self.analytic_tag_ids_m2m = new relational_fields.FieldMany2ManyTags(self,
                    'filter_analytic_tag_ids',
                    record,
                    {
                        mode: 'edit',
                        attrs: {
                            placeholder: self.analytic_tag_ids_label,  // Odoo 11 does not display it
                            options: {
                                no_create: 'True',
                                no_open: 'True',
                            },
                        },
                    }
                );
                self._registerWidget(record.id, self.analytic_tag_ids_m2m.name, self.analytic_tag_ids_m2m);
                self.analytic_tag_ids_m2m.appendTo(self.get_mis_builder_filter_box());
            }
        },

        /**
         * Hack to work around Odoo not fetching display name for
         * x2many used with makeRecord. 
         * 
         * Return a list of deferred
         * to be awaited before creating the widgets.
         */
        _before_create_widgets: function(record) {
            var self = this;
            var defs = []

            if (self.has_group_analytic_tags) {
                var dataPoint = record.data.filter_analytic_tag_ids;
                dataPoint.fieldsInfo.default["display_name"] = {};
                defs.push(self.model.reload(dataPoint.id));
            }

            return defs;
        },

        /**
         * Populate the analytic filters box. 
         * This method is not meant to be overridden.
         */
        _add_analytic_filters: function () {
            var self = this;
            if (self.hide_analytic_filters) {
                return;
            }
            self.model.makeRecord(
                "dummy.model",
                self._get_filter_fields(),
                self._get_filter_fieldInfo(),
            ).then(function (recordId) {
                var record = self.model.get(recordId);
                var defs = self._before_create_widgets(record);
                $.when.apply($, defs).then(function () {
                    record = self.model.get(record.id);
                    self._make_filter_field_widgets(record);
                });
            });
        },

        _confirmChange: function (id, fields, event) {
            var self = this;
            var result = StandaloneFieldManagerMixin._confirmChange.apply(self, arguments);

            if (self.analytic_account_id_m2o !== undefined) {
                if (self.analytic_account_id_m2o.value) {
                    self._set_filter_value('analytic_account_id', self.analytic_account_id_m2o.value.res_id, "=");
                } else {
                    self._set_filter_value('analytic_account_id', undefined);
                }
            }

            if (self.analytic_tag_ids_m2m !== undefined) {
                if (self.analytic_tag_ids_m2m.value && self.analytic_tag_ids_m2m.value.res_ids.length > 0) {
                    self._set_filter_value('analytic_tag_ids', self.analytic_tag_ids_m2m.value.res_ids, "all");
                } else {
                    self._set_filter_value('analytic_tag_ids', undefined);
                }
            }

            return result;
        },

        refresh: function () {
            this.replace();
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
