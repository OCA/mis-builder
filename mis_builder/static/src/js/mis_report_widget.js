/* Copyright 2014-2018 ACSONE SA/NV (<http://acsone.eu>)
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html). */

odoo.define('mis_builder.widget', function (require) {
    "use strict";

    var FormCommon = require('web.form_common');
    var Model = require('web.DataModel');
    var AbstractField = FormCommon.AbstractField;

    var core = require('web.core');
    var session = require('web.session');

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

        init: function (field_manager, node) {
            var self = this;
            self._super(field_manager, node);
            self.MisReportInstance = new Model('mis.report.instance');
        },

        /**
         * Return the id of the mis.report.instance to which the widget is
         * bound.
         */
        _instance_id: function () {
            var self = this;
            var value = self.get('value');
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
            var context = self.get_context();

            var def1 = self.MisReportInstance.call(
                'compute',
                [self._instance_id()],
                {'context': context}
            ).then(function (result) {
                self.mis_report_data = result;
            });

            var def2 = session.user_has_group(
                'account.group_account_user'
            ).then(function (result) {
                self.show_settings = result;
            });

            return $.when(this._super.apply(this, arguments), def1, def2);
        },

        refresh: function () {
            this.replace();
        },

        get_context: function () {
            var self = this;
            return self.view.dataset.get_context();
        },

        print_pdf: function () {
            var self = this;
            var context = self.get_context();
            self.MisReportInstance.call(
                'print_pdf',
                [self._instance_id()],
                {'context': context}
            ).then(function (result) {
                self.do_action(result);
            });
        },

        export_xls: function () {
            var self = this;
            var context = self.get_context();
            self.MisReportInstance.call(
                'export_xls',
                [self._instance_id()],
                {'context': context}
            ).then(function (result) {
                self.do_action(result);
            });
        },

        display_settings: function () {
            var self = this;
            var context = self.get_context();
            self.MisReportInstance.call(
                'display_settings',
                [self._instance_id()],
                {'context': context}
            ).then(function (result) {
                self.do_action(result);
            });
        },

        drilldown: function (event) {
            var self = this;
            var context = self.get_context();
            var drilldown = $(event.target).data("drilldown");
            self.MisReportInstance.call(
                'drilldown',
                [self._instance_id(), drilldown],
                {'context': context}
            ).then(function (result) {
                self.do_action(result);
            });
        },
    });

    core.form_widget_registry.add('mis_report_widget', MisReportWidget);

    return MisReportWidget;

});
