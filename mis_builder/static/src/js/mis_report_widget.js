/* Copyright 2014-2018 ACSONE SA/NV (<http://acsone.eu>)
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html). */

odoo.define("mis_builder.widget", function (require) {
    "use strict";

    var FormCommon = require("web.form_common");
    var Model = require("web.DataModel");
    var AbstractField = FormCommon.AbstractField;

    var core = require("web.core");
    var data = require("web.data");
    var session = require("web.session");

    var FieldMany2One = core.form_widget_registry.get("many2one");
    var FieldMany2ManyTags = core.form_widget_registry.get("many2many_tags");
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
            "click .mis_builder_drilldown": "drilldown",
            "click .oe_mis_builder_print": "print_pdf",
            "click .oe_mis_builder_export": "export_xls",
            "click .oe_mis_builder_settings": "display_settings",
            "click .oe_mis_builder_refresh": "refresh",
        }),

        init: function (field_manager, node) {
            var self = this;
            self._super(field_manager, node);
            self.MisReportInstance = new Model("mis.report.instance");
            self.dfm = new FormCommon.DefaultFieldManager(self);
            self.analytic_account_id = undefined;
            self.analytic_account_id_domain = [];
            self.analytic_account_id_label = _t("Analytic Account Filter");
            self.analytic_account_id_m2o = undefined;
            self.analytic_tag_ids = undefined;
            self.analytic_tag_ids_domain = [];
            self.analytic_tag_ids_label = _t("Analytic Tags Filter");
            self.analytic_tag_ids_m2m = undefined;
            self.has_group_analytic_accounting = false;
            self.hide_analytic_filters = false;
            self.filter_values = {};
            self.init_filter_from_context();
        },

        init_filter_from_context: function () {
            var self = this;
            var filters = self.getParent().dataset.context.mis_report_filters || {};
            self.filter_values = filters;
        },

        /**
         * Return the id of the mis.report.instance to which the widget is
         * bound.
         *
         * @returns int
         */
        _instance_id: function () {
            var self = this;
            var value = self.get("value");
            if (value) {
                return value;
            }

            /*
             * This trick is needed because in a dashboard the view does
             * not seem to be bound to an instance: it seems to be a limitation
             * of Odoo dashboards that are not designed to contain forms but
             * rather tree views or charts.
             */
            var context = self.get_context();
            if (context.active_model === "mis.report.instance") {
                return context.active_id;
            }
        },

        /**
         * Method called between @see init and @see start. Performs asynchronous
         * calls required by the rendering and the start method.
         *
         * @returns Promise
         */
        willStart: function () {
            var self = this;
            var context = self.get_context();

            var def1 = self.MisReportInstance.call("compute", [self._instance_id()], {
                context: context,
            }).then(function (result) {
                self.mis_report_data = result;
            });

            var def2 = session
                .user_has_group("account.group_account_user")
                .then(function (result) {
                    self.show_settings = result;
                });

            var def3 = session
                .user_has_group("analytic.group_analytic_accounting")
                .then(function (result) {
                    self.has_group_analytic_accounting = result;
                });

            var def_hide_analytic_filters = self.MisReportInstance.call(
                "read",
                [self._instance_id(), ["hide_analytic_filters"]],
                {context: context}
            ).then(function (result) {
                var record = result[0];
                self.hide_analytic_filters = record.hide_analytic_filters;
            });

            return $.when(
                this._super.apply(this, arguments),
                def1,
                def2,
                def3,
                def_hide_analytic_filters
            );
        },

        start: function () {
            var self = this;
            self._super.apply(self, arguments);
            self.add_filters();
        },

        init_filter_value: function (field_object, attr_name) {
            var self = this;
            var filter = self.filter_values[attr_name];
            if (filter !== undefined && filter.value !== undefined) {
                field_object.set_value(filter.value);
            }
        },

        init_filter: function (filter_name) {
            var self = this;
            if (self.filter_values[filter_name] === undefined) {
                self.filter_values[filter_name] = {};
            }
        },

        set_filter_value: function (field_object, attr_name) {
            var self = this;
            var value = field_object.get_value() || undefined;
            if (value === undefined) {
                self.filter_values[attr_name] = undefined;
                return;
            }
            self.init_filter(attr_name);
            self.filter_values[attr_name].value = value;
        },

        set_filter_operator: function (operator, attr_name) {
            var self = this;
            self.init_filter(attr_name);
            self.filter_values[attr_name].operator = operator;
        },

        get_filter_operator: function (attr_name) {
            var self = this;
            var operator = undefined; // eslint-disable-line no-undef-init
            if (self.filter_values[attr_name] !== undefined) {
                operator = self.filter_values[attr_name].operator || "=";
            }
            return operator;
        },

        add_filters: function () {
            var self = this;
            if (self.hide_analytic_filters) {
                return;
            }
            self.add_analytic_account_filter();
            self.add_analytic_tag_filter();
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
            var field_name = "analytic_account_id";
            var dfm_object = {};
            dfm_object[field_name] = {
                relation: "account.analytic.account",
            };
            self.dfm.extend_field_desc(dfm_object);
            var analytic_account_id_m2o = new FieldMany2One(self.dfm, {
                attrs: {
                    placeholder: self.analytic_account_id_label,
                    name: field_name,
                    type: "many2one",
                    domain: self.analytic_account_id_domain,
                    context: {},
                    modifiers: "{}",
                    options: '{"no_create": true, "no_open": true}',
                },
            });
            self.init_filter_value(analytic_account_id_m2o, field_name);
            analytic_account_id_m2o.appendTo(self.get_mis_builder_filter_box());
            analytic_account_id_m2o.$input.focusout(function () {
                self.set_filter_value(analytic_account_id_m2o, field_name);
            });
            analytic_account_id_m2o.$follow_button.toggle();
            self.analytic_account_id_m2o = analytic_account_id_m2o;
        },

        add_analytic_tag_filter: function () {
            var self = this;
            if (!self.has_group_analytic_accounting) {
                return;
            }
            if (self.analytic_tag_ids_m2m) {
                // Prevent errors with autocomplete
                self.analytic_tag_ids_m2m.destroy_content();
                self.analytic_tag_ids_m2m.destroy();
            }
            var field_name = "analytic_tag_ids";
            var dfm_object = {};
            dfm_object[field_name] = {
                relation: "account.analytic.tag",
            };
            self.dfm.extend_field_desc(dfm_object);
            var analytic_tag_ids_m2m = new FieldMany2ManyTags(self.dfm, {
                attrs: {
                    placeholder: self.analytic_tag_ids_label,
                    name: field_name,
                    type: "many2many",
                    domain: self.analytic_tag_ids_domain,
                    context: {},
                    modifiers: "{}",
                    options: '{"no_create": true}',
                    help: _t(
                        "This filter returns the journal entries " +
                            "that have all the selected tags."
                    ),
                },
            });
            self.init_filter_value(analytic_tag_ids_m2m, field_name);
            analytic_tag_ids_m2m.appendTo(self.get_mis_builder_filter_box());
            analytic_tag_ids_m2m.on("change:value", this, function () {
                self.set_filter_value(analytic_tag_ids_m2m, field_name);
                self.set_filter_operator("all", field_name);
            });
            self.analytic_tag_ids_m2m = analytic_tag_ids_m2m;
        },

        refresh: function () {
            this.replace();
        },

        get_context: function () {
            var self = this;
            var context = new data.CompoundContext(self.view.dataset.get_context(), {
                mis_report_filters: self.filter_values,
            });
            return context;
        },

        print_pdf: function () {
            var self = this;
            var context = self.get_context();
            self.MisReportInstance.call("print_pdf", [self._instance_id()], {
                context: context,
            }).then(function (result) {
                self.do_action(result);
            });
        },

        export_xls: function () {
            var self = this;
            var context = self.get_context();
            self.MisReportInstance.call("export_xls", [self._instance_id()], {
                context: context,
            }).then(function (result) {
                self.do_action(result);
            });
        },

        display_settings: function () {
            var self = this;
            var context = self.get_context();
            self.MisReportInstance.call("display_settings", [self._instance_id()], {
                context: context,
            }).then(function (result) {
                self.do_action(result);
            });
        },

        drilldown: function (event) {
            var self = this;
            var context = self.get_context();
            var drilldown = $(event.target).data("drilldown");
            self.MisReportInstance.call("drilldown", [self._instance_id(), drilldown], {
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

    core.form_widget_registry.add("mis_report_widget", MisReportWidget);

    return MisReportWidget;
});
