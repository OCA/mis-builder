odoo.define('mis_builder.widget', function(require) {
"use strict";

var AbstractField = require('web.AbstractField');
var core = require('web.core');
var registry = require('web.field_registry');

var _t = core._t;

var MisBuilderWidget = AbstractField.extend({
    events: _.extend({}, AbstractField.prototype.events, {
        'click .mis_builder_drilldown': 'drilldown',
        'click .oe_mis_builder_print': 'print',
        'click .oe_mis_builder_export': 'export',
        'click .oe_mis_builder_settings': 'display_settings',
        'click .oe_mis_builder_generate_content': 'generate_content',
    }),
    description: "",

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @override
     * it should always be displayed, whatever its value
     */
    isSet: function () {
        return true;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     * @private
     */
    _render: function () {
        var self = this;
        var context = self.getParent().state.context;
        var rec_id = this.recordData.id || self.getParent().state.context.active_id;
        self._rpc({
            model: 'mis.report.instance',
            method: 'get_mis_report_view_html',
            args: [parseInt(rec_id, 10)],
            context: context,
        }).then(function (val) {
            self.$el.html(val);
            self._rpc({
                model: 'res.users',
                method: 'has_group',
                args: ['account.group_account_user'],
                context: context,
            }).then(function (result) {
                if (result) {
                    self.$(".oe_mis_builder_settings").show();
                }
            });
        });
    },

    print: function() {
        var self = this;
        var context = self.getParent().state.context;
        this._rpc({
            model: 'mis.report.instance',
            method: 'print_pdf',
            args: [context.active_id],
            context: context,
        }).then(function(result){
            self.do_action(result);
        });
    },
    export: function() {
        var self = this;
        var context = self.getParent().state.context;
        this._rpc({
            model: 'mis.report.instance',
            method: 'export_xls',
            args: [context.active_id],
            context: context,
        }).then(function(result){
            self.do_action(result);
        });
    },
    display_settings: function() {
        var self = this;
        var context = self.getParent().state.context;
        this._rpc({
            model: 'mis.report.instance',
            method: 'display_settings',
            args: [context.active_id],
            context: context,
        }).then(function(result){
            self.do_action(result);
        });
    },
    generate_content: function() {
        var self = this;
        return self._render();
    },
    drilldown: function(event) {
        var self = this;
        var context = self.getParent().state.context;
        var drilldown = $(event.target).data("drilldown");
        drilldown = drilldown.replace(/\'/g, '\"');
        var drilldown_json = JSON.parse(drilldown);
        this._rpc({
                model: 'mis.report.instance',
                method: 'drilldown',
                args: [context.active_id, drilldown_json],
                context: context,
            }).then(function(result){
                self.do_action(result);
            });
    },
});

registry.add("mis_builder_widget", MisBuilderWidget);

});
