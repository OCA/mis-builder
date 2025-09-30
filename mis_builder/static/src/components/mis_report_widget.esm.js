import {Component, onMounted, onWillStart, useState, useSubEnv} from "@odoo/owl";
import {useBus, useService} from "@web/core/utils/hooks";
import {DateTimeInput} from "@web/core/datetime/datetime_input";
import {Many2OneField} from "@web/views/fields/many2one/many2one_field";
import {SearchBar} from "@web/search/search_bar/search_bar";
import {SearchModel} from "@web/search/search_model";
import {parseDate} from "@web/core/l10n/dates";
import {registry} from "@web/core/registry";

export class MisReportWidget extends Component {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.action = useService("action");
        this.view = useService("view");
        this.dialog = useService("dialog");
        this.JSON = JSON;
        this.state = useState({
            mis_report_data: {header: [], body: []},
            pivot_date: null,
        });
        this.searchModel = new SearchModel(this.env, {
            orm: this.orm,
            view: this.view,
            dialog: this.dialog,
        });
        useSubEnv({searchModel: this.searchModel});
        useBus(this.env.searchModel, "update", async () => {
            await this.env.searchModel.sectionsPromise;
            this.refresh();
        });
        onWillStart(this.willStart);

        onMounted(this._onMounted);
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
                "wide_display_by_default",
            ],
            {context: this.context}
        );

        this.source_aml_model_name = result.source_aml_model_name;
        this.widget_show_filters = result.widget_show_filters;
        this.widget_show_settings_button = result.widget_show_settings_button;
        this.widget_search_view_id = result.widget_search_view_id?.[0];
        this.state.pivot_date = parseDate(result.pivot_date);
        this.widget_show_pivot_date = result.widget_show_pivot_date;

        if (this.showSearchBar) {
            // Initialize the search model
            await this.searchModel.load({
                resModel: this.source_aml_model_name,
                searchViewId: this.widget_search_view_id,
            });
        }

        this.wide_display = result.wide_display_by_default;

        // Compute the report
        this.refresh();
    }

    get showDateRange() {
        return this.props.record.data.id && this.showPivotDate;
    }

    get dateRanges() {
        return {
            relation: "date.range",
            readonly: false,
            name: "date_range_id",
            record: this.props.record,
        };
    }
    async updateDateRange(ev) {
        await this.props.record.update(ev);
        await this.props.record.save();
        this.refresh();
    }

    async _onMounted() {
        this.resize_sheet();
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
        const context = this.props.record.context;
        if (context.active_model === "mis.report.instance") {
            return context.active_id;
        }
    }

    get context() {
        return {
            ...super.context,
            ...(this.showSearchBar && {
                mis_analytic_domain: this.searchModel.searchDomain,
            }),
            ...(this.showPivotDate &&
                this.state.pivot_date && {mis_pivot_date: this.state.pivot_date}),
        };
    }

    async drilldown(event) {
        const drilldown = JSON.parse(event.target.dataset.drilldown);
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

    onDateTimeChanged(ev) {
        this.state.pivot_date = ev;
        this.refresh();
    }

    async toggle_wide_display() {
        this.wide_display = !this.wide_display;
        this.resize_sheet();
    }

    async resize_sheet() {
        var sheet_element = document.getElementsByClassName("o_form_sheet_bg")[0];
        sheet_element.classList.toggle(
            "oe_mis_builder_report_wide_sheet",
            this.wide_display
        );
        var button_resize_element = document.getElementById("icon_resize");
        button_resize_element.classList.toggle("fa-expand", !this.wide_display);
        button_resize_element.classList.toggle("fa-compress", this.wide_display);
    }
}

MisReportWidget.components = {SearchBar, DateTimeInput, Many2OneField};
MisReportWidget.template = "mis_builder.MisReportWidget";

export const misReportWidget = {
    component: MisReportWidget,
};

registry.category("fields").add("mis_report_widget", misReportWidget);
