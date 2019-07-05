/* Copyright 2014-2018 ACSONE SA/NV (<http://acsone.eu>)
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html). */

odoo.define('mis_builder.widget', function (require) {
"use strict";

    var AbstractField = require('web.AbstractField');
    var field_registry = require('web.field_registry');

    var MisReportWidget = AbstractField.extend({

        /*
         * The following attributes are set after willStart() and are available
         * in the widget template:
         * - mis_report_data: the result of mis.report.instance.compute()
         * - show_settings: a flag that controls the visibility of the Settings
         *   button
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

            return $.when(this._super.apply(this, arguments), def1, def2);
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
    });

    field_registry.add("mis_report_widget", MisReportWidget);

    return MisReportWidget;

});
