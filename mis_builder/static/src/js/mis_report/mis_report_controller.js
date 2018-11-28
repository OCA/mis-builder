odoo.define('web.MisReportController', function (require) {
    "use strict";

    var BasicController = require('web.BasicController');
    var core = require('web.core');

    var MisReportController = BasicController.extend({
        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
        },
    });

    return MisReportController;
});
