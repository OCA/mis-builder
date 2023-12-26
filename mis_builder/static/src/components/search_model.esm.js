/** @odoo-module **/

import {SearchModel} from "@web/search/search_model";
import {useService} from "@web/core/utils/hooks";

export class MisReportSearchModel extends SearchModel {
    /**
     * @override
     */
    setup() {
        this.notificationService = useService("notification");
        super.setup(...arguments);
    }

    /**
     * @override
     */
    deactivateGroup(groupId) {
        // Prevent removing the analytic account filter and let the user know.
        let reactivateAnalyticAccountFilter = false;
        if (this.analyticAccountSearchItem.groupId === groupId) {
            if (
                this.query.filter(
                    (query) => query.searchItemId === this.analyticAccountSearchItem.id
                ).length === 1
            ) {
                this.notificationService.add(
                    this.env._t("The analytic account filter cannot be removed"),
                    {type: "info"}
                );
                return;
            }
            // As there are more than one filter on the analytic account, let
            // super remove them and add it back after.
            reactivateAnalyticAccountFilter = true;
        }
        super.deactivateGroup(groupId);
        if (reactivateAnalyticAccountFilter) {
            this._addAnalyticAccountFilter();
        }
    }

    /**
     * @override
     */
    async load(config) {
        // Store analytic account id in the SearchModel for reuse in other functions.
        this.analyticAccountId = config.analyticAccountId;
        const analyticAccountNamePromise = this._loadAnalyticAccountName();
        await Promise.all([analyticAccountNamePromise, super.load(...arguments)]);
        this._determineAnalyticAccountSearchItem();
        this._addAnalyticAccountFilter();
    }

    /**
     * Add the filter regarding the analytic account in the search model.
     * @private
     */
    _addAnalyticAccountFilter() {
        if (!this.analyticAccountSearchItem || !this.analyticAccountName) {
            return;
        }
        this.addAutoCompletionValues(this.analyticAccountSearchItem.id, {
            label: this.analyticAccountName,
            operator: "=",
            value: this.analyticAccountId,
        });
    }

    /**
     * Find the searchItem that correspond to the analytic account field and store it
     * under analyticAccountSearchItem.
     * @private
     */
    _determineAnalyticAccountSearchItem() {
        // Store analytic account searchItem in the SearchModel for reuse in other functions.
        for (const searchItem of Object.values(this.searchItems)) {
            if (
                searchItem.type === "field" &&
                searchItem.fieldName === "analytic_account_id"
            ) {
                this.analyticAccountSearchItem = searchItem;
                break;
            }
        }
    }

    /**
     * Load the analytic account name and store it under analyticAccountName.
     * @returns {Promise<void>}
     * @private
     */
    async _loadAnalyticAccountName() {
        if (!this.analyticAccountId) {
            return;
        }
        const readResult = await this.orm.read(
            "account.analytic.account",
            [this.analyticAccountId],
            ["display_name"]
        );
        const analyticAccount = readResult[0];
        this.analyticAccountName = analyticAccount.display_name;
    }
}
