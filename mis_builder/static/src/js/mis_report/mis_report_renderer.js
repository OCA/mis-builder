odoo.define('web.MisReportRenderer', function (require) {
    "use strict";

    var BasicRenderer = require('web.BasicRenderer');

    var MisReportRenderer =  BasicRenderer.extend({
        // className: "o_mis_report_view",
        template: 'MisReportView',
        events: _.extend({}, BasicRenderer.prototype.events, {
            'click .mis_builder_drilldown': '_drilldown',
            'click .oe_mis_builder_print': '_print_pdf',
            'click .oe_mis_builder_export': '_export_xls',
            'click .oe_mis_builder_settings': '_display_settings',
            'click .oe_mis_builder_refresh': '_refresh',
        }),

        _getReportData: function (){
            var self = this;
            var id = this.getParent().initialState.res_id;
            var context = this.getParent().initialState.context;
            return this._rpc({
                model: 'mis.report.instance',
                method: 'compute',
                args: [id],
                context: context,
            }).then(function (result) {
                self.mis_report_data = result;
            });
        },

        _getSettings: function () {
            var self = this;
            var context = this.getParent().initialState.context;
            return this._rpc({
                model: 'res.users',
                method: 'has_group',
                args: ['account.group_account_user'],
                context: context,
            }).then(function (result) {
                self.show_settings = result;
            });
        },

        willStart: function () {
            return $.when(
                this._getReportData(),
                this._getSettings(),
                this._super.apply(this, arguments),
            );
        },

        start: function() {
            this._super.apply(this, arguments);
        },

    });

    return MisReportRenderer;
});
