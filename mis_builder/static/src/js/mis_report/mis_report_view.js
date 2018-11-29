odoo.define('web.MisReportView', function(require) {
    "use strict";

    var BasicView = require('web.BasicView');
    var Context = require('web.Context');
    var MisReportController = require('web.MisReportController');
    var MisReportRenderer = require('web.MisReportRenderer');
    var view_registry = require('web.view_registry');
    var core = require('web.core');
    var _lt = core._lt;

    var MisReportView = BasicView.extend({
        display_name: _lt('Mis Report Preview'),
        icon: 'fa-tasks',
        multi_record: false,
        searchable: false,
        viewType: 'mis_report',
        config: _.extend({}, BasicView.prototype.config, {
            Controller: MisReportController,
            Renderer: MisReportRenderer,
        }),

        init: function (viewInfo, params) {
            this._super.apply(this, arguments);
            this.loadParams.type = 'record';
            this.rendererParams.foo = 'bar';
        },

    });

    view_registry.add('mis_report', MisReportView);
    return MisReportView;
});
