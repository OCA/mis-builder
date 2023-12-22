/** @odoo-module **/

import {Component, onWillStart, useState, useSubEnv} from "@odoo/owl";
import {useBus, useService} from "@web/core/utils/hooks";
import {DatePicker} from "@web/core/datepicker/datepicker";
import {Domain} from "@web/core/domain";
import {FilterMenu} from "@web/search/filter_menu/filter_menu";
import {SearchBar} from "@web/search/search_bar/search_bar";
import {SearchModel} from "@web/search/search_model";
import {parseDate} from "@web/core/l10n/dates";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";

export class MisReportWidget extends Component {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.user = useService("user");
        this.action = useService("action");
        this.view = useService("view");
        this.JSON = JSON;
        this.state = useState({
            mis_report_data: {header: [], body: []},
            pivot_date: null,
        });
        this.searchModel = new SearchModel(this.env, {
            user: this.user,
            orm: this.orm,
            view: this.view,
        });
        useSubEnv({searchModel: this.searchModel});
        useBus(this.env.searchModel, "update", async () => {
            await this.env.searchModel.sectionsPromise;
            this.refresh();
        });
        onWillStart(this.willStart);
    }

    // Lifecycle
    async willStart() {
        const [result] = await this.orm.read(
            "mis.report.instance",
            [this._instanceId()],
            [
                "source_aml_model_name",
                "widget_show_filters",
                "widget_show_settings_button",
                "widget_search_view_id",
                "pivot_date",
                "widget_show_pivot_date",
            ],
            {context: this.context}
        );
        this.source_aml_model_name = result.source_aml_model_name;
        this.widget_show_filters = result.widget_show_filters;
        this.widget_show_settings_button = result.widget_show_settings_button;
        this.widget_search_view_id =
            result.widget_search_view_id && result.widget_search_view_id[0];
        this.state.pivot_date = parseDate(result.pivot_date);
        this.widget_show_pivot_date = result.widget_show_pivot_date;
        if (this.showSearchBar) {
            // Initialize the search model
            await this.searchModel.load({
                resModel: this.source_aml_model_name,
                searchViewId: this.widget_search_view_id,
            });
        }

        // Compute the report
        this.refresh();
    }

    get misAnalyticDomainContextKey() {
        return "mis_analytic_domain";
    }

    get showSearchBar() {
        return (
            this.source_aml_model_name &&
            this.widget_show_filters &&
            this.widget_search_view_id
        );
    }

    get showPivotDate() {
        return this.widget_show_pivot_date;
    }

    /**
     * Return the id of the mis.report.instance to which the widget is
     * bound.
     *
     * @returns int
     */
    _instanceId() {
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

    get context() {
        let ctx = this.props.record.context;
        this.setMisAnalyticDomainContextKey(ctx);
        if (this.showSearchBar && this.searchModel.searchDomain) {
            ctx[this.misAnalyticDomainContextKey] = Domain.and([
                ctx[this.misAnalyticDomainContextKey],
                new Domain(this.searchModel.searchDomain),
            ]).toList();
        }
        if (this.showPivotDate && this.state.pivot_date) {
            ctx = {
                ...ctx,
                mis_pivot_date: this.state.pivot_date,
            };
        }
        return ctx;
    }

    async drilldown(event) {
        const drilldown = $(event.target).data("drilldown");
        const action = await this.orm.call(
            "mis.report.instance",
            "drilldown",
            [this._instanceId(), drilldown],
            {context: this.context}
        );
        this.action.doAction(action);
    }

    async refresh() {
        this.state.mis_report_data = await this.orm.call(
            "mis.report.instance",
            "compute",
            [this._instanceId()],
            {context: this.context}
        );
    }

    setMisAnalyticDomainContextKey(context) {
        if (
            this.props.analytic_account_id_field &&
            !(this.misAnalyticDomainContextKey in context)
        ) {
            let analyticAccountId = false;
            const analyticAccountIdFieldType =
                this.props.record.fields[this.props.analytic_account_id_field].type;
            switch (analyticAccountIdFieldType) {
                case "many2one":
                    analyticAccountId =
                        this.props.record.data[this.props.analytic_account_id_field][0];
                    break;
                case "integer":
                    analyticAccountId =
                        this.props.record.data[this.props.analytic_account_id_field];
                    break;
                default:
                    throw new Error(
                        ```Unsupported field type for analytic_account_id: ${analyticAccountIdFieldType}```
                    );
            }
            if (analyticAccountId) {
                context[this.misAnalyticDomainContextKey] = [
                    ["analytic_account_id", "=", analyticAccountId],
                ];
            }
        }
    }

    async printPdf() {
        const action = await this.orm.call(
            "mis.report.instance",
            "print_pdf",
            [this._instanceId()],
            {context: this.context}
        );
        this.action.doAction(action);
    }

    async exportXls() {
        const action = await this.orm.call(
            "mis.report.instance",
            "export_xls",
            [this._instanceId()],
            {context: this.context}
        );
        this.action.doAction(action);
    }

    async displaySettings() {
        const action = await this.orm.call(
            "mis.report.instance",
            "display_settings",
            [this._instanceId()],
            {context: this.context}
        );
        this.action.doAction(action);
    }

    onDateTimeChanged(ev) {
        this.state.pivot_date = ev;
        this.refresh();
    }
}

MisReportWidget.components = {FilterMenu, SearchBar, DatePicker};
MisReportWidget.template = "mis_builder.MisReportWidget";
MisReportWidget.props = {
    ...standardFieldProps,
    analyticAccountIdField: {
        type: String,
        optional: true,
    },
};
MisReportWidget.extractProps = ({attrs}) => ({
    analyticAccountIdField: attrs.analytic_account_id_field,
});

registry.category("fields").add("mis_report_widget", MisReportWidget);
