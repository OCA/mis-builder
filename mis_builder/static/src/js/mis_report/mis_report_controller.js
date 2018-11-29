odoo.define('web.MisReportController', function (require) {
    "use strict";

    var BasicController = require('web.BasicController');
    var core = require('web.core');

    var MisReportController = BasicController.extend({

        update: function (params, options) {
            params = _.extend({viewType: 'mis_report'}, params);
            return this._super(params, options);
        },

        _pushState: function (state) {
            state = state || {};
            var env = this.model.get(this.handle, {env: true});
            state.id = env.currentId;
            this._super(state);
        },

        // getContext: function () {
        //     var state = this.model.get();
        //     return {
        //         state: state,
        //     };
        // },

    });

    return MisReportController;
});
