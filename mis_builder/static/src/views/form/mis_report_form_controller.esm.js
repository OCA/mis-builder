/** @odoo-module */

import {FormController} from "@web/views/form/form_controller";
import {useSubEnv} from "@odoo/owl";

export class MisReportFormController extends FormController {
    setup() {
        super.setup();
        useSubEnv({
            misReportSearchModelState:
                this.props.globalState &&
                this.props.globalState.misReportSearchModelState,
        });
    }
}
