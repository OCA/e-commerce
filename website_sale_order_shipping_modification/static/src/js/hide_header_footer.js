/* Copyright 2025 Tecnativa - Pilar Vargas
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */
odoo.define("tecnativa_knowledge.hide_header_and_footer", function () {
    "use strict";
    const hasPortalSession = $("#portal-session-flags").data("hasPortalSession") === 1;
    // Prevent users from leaving the flow when editing a budget from the portal so
    // that all sessions expire upon completion.
    if (hasPortalSession) {
        $("header").hide();
        $("#footer").hide();
    }
});
