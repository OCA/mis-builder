/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const { Component, onWillStart, useState } = owl;

export class MisReportWidget extends Component {
    setup() {
        super.setup();
        this.orm = useService('orm');
        this.user = useService("user");
        this.action = useService("action");
        this.JSON = JSON;
        this.user_context = Component.env.session.user_context;
        this.state = useState({ mis_report_data: {} });
        onWillStart(this.willStart);
    }
    // Lifecycle
    async willStart() {
        this.state.mis_report_data = await this.orm.call(
                "mis.report.instance",
                "compute",
                [this._instanceId()],
                {context: this.user_context}
        );

        this.props.show_settings = await this.user.hasGroup("account.group_account_user");


        this.props.has_group_analytic_accounting = await this.user.hasGroup("analytic.group_analytic_accounting");

        var result = await this.orm.call(
                "mis.report.instance",
                "read",
                [this._instanceId(), ["hide_analytic_filters"]],
                {context: this.user_context},
            )
        this.props.hide_analytic_filters = result && result[0].hide_analytic_filters;

    }
    /**
     * Return the id of the mis.report.instance to which the widget is
     * bound.
     *
     * @returns int
     */
    _instanceId () {
        if (this.props.value) {
            return this.props.value;
        }

        /*
            * This trick is needed because in a dashboard the view does
            * not seem to be bound to an instance: it seems to be a limitation
            * of Odoo dashboards that are not designed to contain forms but
            * rather tree views or charts.
            */
        var context = this.props.record.context;
        if (context.active_model === "mis.report.instance") {
            return context.active_id;
        }
    }
    async drilldown (event) {
        const drilldown = $(event.target).data("drilldown");
        const action = await this.orm.call(
            "mis.report.instance",
            "drilldown",
            [this._instanceId(), drilldown],
            {context: this.user_context},
        )
        this.action.doAction(action);
    }
    async refresh () {
        this.state.mis_report_data = await this.orm.call(
            "mis.report.instance",
            "compute",
            [this._instanceId()],
            {context: this.user_context}
        );
    }

    async printPdf () {
        const action = await this.orm.call(
            "mis.report.instance",
            "print_pdf",
            [this._instanceId()],
            {context: this.user_context},
        )
        this.action.doAction(action);
    }

    async exportXls() {
        const action = await this.orm.call(
            "mis.report.instance",
            "export_xls",
            [this._instanceId()],
            {context: this.user_context},
        )
        this.action.doAction(action);
    }

    async displaySettings() {
        const action = await this.orm.call(
            "mis.report.instance",
            "display_settings",
            [this._instanceId()],
            {context: this.user_context},
        )
        this.action.doAction(action);
    }
}
MisReportWidget.template = "mis_builder.MisReportWidget";
MisReportWidget.defaultProps = {
        analytic_distribution: undefined, // Field widget
        mis_report_data: undefined,
        show_settings: false,
        has_group_analytic_accounting: false,
        hide_analytic_filters: false,
};

registry.category("fields").add("mis_report_widget", MisReportWidget);
