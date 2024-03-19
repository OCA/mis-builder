/** @odoo-module **/

import {MisReportFormController} from "@mis_builder/views/form/mis_report_form_controller.esm";
import {formView} from "@web/views/form/form_view";
import {registry} from "@web/core/registry";

// The view to use when mounting `mis_report_widget` widget in order to preserve the
// filters when returning from the drill-down views.
export const misReportFormView = {
    ...formView,
    Controller: MisReportFormController,
};

registry.category("views").add("mis_report_form_view", misReportFormView);
