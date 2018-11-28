odoo.define('web.MisReportRenderer', function (require) {
    "use strict";

    var BasicRenderer = require('web.BasicRenderer');

    var MisReportRenderer =  BasicRenderer.extend({
        template: 'MisReportView',
        events: _.extend({}, BasicRenderer.prototype.events, {
            'click .mis_builder_drilldown': '_drilldown',
            'click .oe_mis_builder_print': '_print_pdf',
            'click .oe_mis_builder_export': '_export_xls',
            'click .oe_mis_builder_refresh': '_refresh',
        }),

        _getReportData: function (){
            var self = this;
            return this._rpc({
                model: 'mis.report.instance',
                method: 'compute',
                args: [self.instance_id],
                context: self.context,
            }).then(function (result) {
                self.mis_report_data = result;
            });
        },

        _getSettings: function () {
            var self = this;
            return this._rpc({
                model: 'res.users',
                method: 'has_group',
                args: ['account.group_account_user'],
                context: self.instance_context,
            }).then(function (result) {
                self.show_settings = result;
            });
        },

        willStart: function () {
            this.instance_id = this.getParent().initialState.res_ids[0];
            this.instance_context = this.getParent().initialState.context;
            return $.when(
                this._getReportData(),
                this._getSettings(),
                this._super.apply(this, arguments),
            );
        },


        _refresh: function () {
            this.replace();
        },

        _print_pdf: function () {
            var self = this;
            this._rpc({
                model: 'mis.report.instance',
                method: 'print_pdf',
                args: [self.instance_id],
                context: self.instance_context,
            }).then(function (result) {
                self.do_action(result);
            });
        },

        _export_xls: function () {
            var self = this;
            this._rpc({
                model: 'mis.report.instance',
                method: 'export_xls',
                args: [self.instance_id],
                context: self.instance_context,
            }).then(function (result) {
                self.do_action(result);
            });
        },

        _drilldown: function (event) {
            var self = this;
            var drilldown = $(event.target).data("drilldown");
            this._rpc({
                model: 'mis.report.instance',
                method: 'drilldown',
                args: [self.instance_id, drilldown],
                context: self.instance_context,
            }).then(function (result) {
                self.do_action(result);
            });
        },

    });

    return MisReportRenderer;
});
