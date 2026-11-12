import {Component, onMounted, onWillStart, useState, useSubEnv} from "@odoo/owl";
import {useBus, useService} from "@web/core/utils/hooks";
import {DateTimeInput} from "@web/core/datetime/datetime_input";
import {SearchBar} from "@web/search/search_bar/search_bar";
import {SearchModel} from "@web/search/search_model";
import {parseDate} from "@web/core/l10n/dates";
import {registry} from "@web/core/registry";
import {AnnotationDialog} from "../annotation_dialog/annotation_dialog.esm";
import {_t} from "@web/core/l10n/translation";

export class MisReportWidget extends Component {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.action = useService("action");
        this.view = useService("view");
        this.dialog = useService("dialog");
        this.JSON = JSON;
        this.state = useState({
            mis_report_data: {header: [], body: [], notes: {}},
            pivot_date: null,
            can_edit_annotation: false,
            can_read_annotation: false,
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
                "user_can_read_annotation",
                "user_can_edit_annotation",
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
        this.state.can_edit_annotation = result.user_can_edit_annotation;
        this.state.can_read_annotation = result.user_can_read_annotation;
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
        /*
         * When the widget is used as a field in a mis.report.instance
         * form view, the record it belongs to is the instance itself.
         * This is the modern owl field API; props.value is kept below
         * as a fallback for legacy call sites.
         */
        if (this.props.record && this.props.record.resId) {
            return this.props.record.resId;
        }

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

    async refresh_annotation() {
        this.state.mis_report_data.notes = await this.orm.call(
            "mis.report.instance",
            "get_notes_by_cell_id",
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

    async _remove_annotation(cell_id) {
        await this.orm.call(
            "mis.report.instance.annotation",
            "remove_annotation",
            [cell_id, this._instanceId()],
            {context: this.context}
        );
        await this.refresh_annotation();
    }

    async _save_annotation(cell_id, text) {
        await this.orm.call(
            "mis.report.instance.annotation",
            "set_annotation",
            [cell_id, this._instanceId(), text],
            {context: this.context}
        );
        await this.refresh_annotation();
    }

    async annotate(event) {
        const cell_id = event.target.dataset.cellId;
        const note = this.state.mis_report_data.notes[cell_id];
        const note_text = (note && note.text) || "";
        this.dialog.add(AnnotationDialog, {
            title: _t("Annotate"),
            annotationText: note_text,
            confirm: async (text) => {
                await this._save_annotation(cell_id, text);
            },
            canRemove: typeof note !== "undefined",
            remove: async () => {
                await this._remove_annotation(cell_id);
            },
        });
    }

    async remove_annotation(event) {
        const cell_id = event.target.dataset.cellId;
        this._remove_annotation(cell_id);
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

MisReportWidget.components = {SearchBar, DateTimeInput};
MisReportWidget.template = "mis_builder.MisReportWidget";

export const misReportWidget = {
    component: MisReportWidget,
};

registry.category("fields").add("mis_report_widget", misReportWidget);
