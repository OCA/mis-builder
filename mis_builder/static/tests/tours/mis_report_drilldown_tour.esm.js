import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("mis_report_drilldown_tour", {
    steps: () => [
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
            trigger: ".o_list_renderer, .o_list_view",
        },
        {
            trigger: ".breadcrumb .breadcrumb-item a, .breadcrumb .o_back_button",
            run: "click",
        },
        {
            trigger: ".o_searchview_facet",
        },
    ],
});
