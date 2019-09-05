/* Copyright 2014-2018 ACSONE SA/NV (<http://acsone.eu>)
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html). */

odoo.define('mis_builder.widget', function (require) {
"use strict";

    var AbstractField = require('web.AbstractField');
    var field_registry = require('web.field_registry');
    var relational_fields = require('web.relational_fields');
    var BasicModel = require('web.BasicModel');

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
            self.analytic_tag_ids = undefined;
            self.analytic_tag_ids_domain = [];
            self.analytic_tag_ids_label = _t("Analytic Tags");
            self.analytic_tag_ids_m2m = undefined;
            self.has_group_analytic_accounting = false;
            self.hide_analytic_filters = false;
            self.filter_values = {};
            self.init_filter_from_context();
            self.record_model = new BasicModel(self.model);
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
                    field_object.value = filter['value'][0].id;
                    field_object.m2o_value = filter['value'][0].display_name;
                } else if (field_object.formatType == "many2many"){
                    field_object.value.data = [];
                    field_object.value.res_ids = [];
                    _.each(filter.value, function(val) {
                        field_object.value.data.push({
                            data: val,
                            res_id: val.id,
                            id: val.id,
                        });
                        field_object.value.res_ids.push(val.id);
                    })
                }
            }
        },

        init_filter: function(filter_name) {
            var self = this;
            if(self.filter_values[filter_name] === undefined) {
                self.filter_values[filter_name] = {value: []};
            }
        },

        set_m2o_value: function(field_object, attr_name, new_val) {
            var self = this;
            self.init_filter(attr_name);
            self.filter_values[attr_name]['value'] =
                [{id: new_val.id, display_name: new_val.display_name}] || undefined;
        },

        set_m2m_value: function(field_object, attr_name, new_val) {
            var self = this;
            if (self.filter_values[attr_name] === undefined) {
                self.init_filter(attr_name);
            }
            self.filter_values[attr_name]['value'].push(new_val);
        },

        rm_m2m_value: function(field_object, attr_name, new_val) {
            var self = this;
            _.each(new_val, function(val) {
                var found = _.findWhere(self.filter_values[attr_name]['value'], { id: val });
                var index = self.filter_values[attr_name].value.indexOf(found);
                if (index !== -1) self.filter_values[attr_name].value.splice(index, 1);
            });
        },

        add_filters: function () {
            var self = this;
            if (self.hide_analytic_filters || !self.has_group_analytic_accounting) {
                return;
            }
            this.record_model.makeRecord(self.model, [{
                relation: 'account.analytic.account',
                type: 'many2one',
                name: 'filter_analytic_account_id',
            }, {
                relation: 'account.analytic.tag',
                type: 'many2many',
                name: 'filter_analytic_tag_ids',
            }], {})
            .then(function (recordID) {
                self.handleCreateRecord = recordID;
                var record = self.record_model.get(self.handleCreateRecord);

                // Prevent errors with autocomplete
                if (self.analytic_account_id_m2o) {
                    self.analytic_account_id_m2o.destroy();
                }
                if (self.analytic_tag_ids_m2m) {
                    self.analytic_tag_ids_m2m.destroy();
                }

                // Field creation
                self.analytic_account_id_m2o = new relational_fields.FieldMany2One(self,
                    'filter_analytic_account_id',
                    record,
                    {
                        mode: 'edit',
                        attrs: {
                            can_write: false,
                            can_create: false,
                            placeholder: _t("Analytic Account Filter"),
                        },
                    });
                self.init_filter_value(self.analytic_account_id_m2o, 'analytic_account_id');
                self.analytic_tag_ids_m2m = new relational_fields.FormFieldMany2ManyTags(self,
                    'filter_analytic_tag_ids',
                    record,
                    {
                        mode: 'edit',
                        attrs: {
                            can_write: false,
                            can_create: false,
                            placeholder: _t("Analytic Tags Filter"),
                        },
                    });
                self.init_filter_value(self.analytic_tag_ids_m2m, 'analytic_tag_ids');

                // Add fields to view
                self.analytic_account_id_m2o.prependTo(self.get_mis_builder_filter_box());
                self.analytic_account_id_m2o.$external_button.hide();
                self.analytic_tag_ids_m2m.prependTo(self.get_mis_builder_filter_box());
                self.render_m2m();
            });
        },

        render_m2m: function () {
            this.analytic_tag_ids_m2m._renderEdit();
            this.analytic_tag_ids_m2m.many2one.can_create = false;
            this.analytic_tag_ids_m2m.many2one.can_write = false;
            this.analytic_tag_ids_m2m.many2one.attrs.placeholder = _t("Analytic Tags Filter");
        },

        refresh: function () {
            this.replace();
        },

        on_field_changed: function (event) {
            var self = this;
            if (event && event.data.changes) {
                var changes = event.data.changes;
                if (changes['filter_analytic_account_id'] !== undefined) {
                    var field_name = 'analytic_account_id';
                    var new_val = changes['filter_analytic_account_id'];
                    self.set_m2o_value(self.analytic_account_id_m2o, field_name, new_val);
                    self.init_filter_value(self.analytic_account_id_m2o, field_name);
                    self.analytic_account_id_m2o._renderEdit();
                }
                if (changes['filter_analytic_tag_ids'] !== undefined) {
                    var field_name = 'analytic_tag_ids';
                    var new_val = changes['filter_analytic_tag_ids'];
                    if (new_val.operation == 'ADD_M2M'){
                        self.set_m2m_value(self.analytic_tag_ids_m2m, field_name, new_val.ids);
                    } else if (new_val.operation == 'FORGET'){
                        self.rm_m2m_value(self.analytic_tag_ids_m2m, field_name, new_val.ids);
                    }
                    self.init_filter_value(self.analytic_tag_ids_m2m, field_name);
                    self.render_m2m();
                }
                event.stopPropagation();
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
