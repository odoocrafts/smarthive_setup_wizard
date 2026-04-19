/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class SupportSystray extends Component {
    static template = "smarthive_setup_wizard.SupportSystray";
}

export const systrayItem = {
    Component: SupportSystray,
};

// Add to systray registry
// Use a sequence that places it near the chatter/activity menu (usually sequence around 20-50).
registry.category("systray").add("SupportSystray", systrayItem, { sequence: 35 });
