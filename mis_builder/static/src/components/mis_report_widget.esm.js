/** @odoo-module **/

import {Component, onWillStart, useState, useSubEnv} from "@odoo/owl";
import {SearchBar} from "@web/search/search_bar/search_bar";
import {FilterMenu} from "@web/search/filter_menu/filter_menu";
import {SearchModel} from "@web/search/search_model";
import {registry} from "@web/core/registry";
import {useBus, useService} from "@web/core/utils/hooks";

export class MisReportWidget extends Component {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.user = useService("user");
        this.action = useService("action");
        this.view = useService("view");
        this.JSON = JSON;
        this.state = useState({mis_report_data: {header: [], body: []}});
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
            ],
            {context: this.context}
        );
        this.source_aml_model_name = result.source_aml_model_name;
        this.widget_show_filters = result.widget_show_filters;
        this.widget_show_settings_button = result.widget_show_settings_button;
        this.widget_search_view_id =
            result.widget_search_view_id && result.widget_search_view_id[0];

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

    get showSearchBar() {
        return (
            this.source_aml_model_name &&
            this.widget_show_filters &&
            this.widget_search_view_id
        );
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
        if (this.showSearchBar) {
            return {
                ...super.context,
                mis_analytic_domain: this.searchModel.searchDomain,
            };
        }
        return super.context;
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
}

MisReportWidget.components = {FilterMenu, SearchBar};
MisReportWidget.template = "mis_builder.MisReportWidget";

registry.category("fields").add("mis_report_widget", MisReportWidget);
