import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("mis_report_back_button_tour", {
    steps: () => [
        {
            trigger: ".o_data_row:contains('Test Instance Drilldown')",
        },
        {
            trigger:
                ".o_data_row:contains('Test Instance Drilldown') button[name='preview']",
            run: "click",
        },
        {
            trigger: ".o_searchview_input",
            run: "click",
        },
        {
            trigger: ".o_searchview_input",
            run: "edit Line",
        },
        {
            trigger:
                ".o_searchview_autocomplete .dropdown-item, .o_searchview_autocomplete a",
            run: "click",
        },
        {
            trigger: ".o_searchview_facet",
        },
        {
            trigger: "a.mis_builder_drilldown",
            run: "click",
        },
        {
            trigger: "tr.o_data_row td:contains('Line 1')",
            run: () => {
                window.history.back();
            },
        },
        {
            trigger: ".o_searchview_facet",
        },
        {
            trigger: "a.mis_builder_drilldown",
        },
    ],
});
