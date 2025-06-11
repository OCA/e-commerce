/** Copyright 2025 Kencove - Mohamed Alkobrosli
 License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {useEnv, useState} from "@odoo/owl";

export function useStore() {
    const env = useEnv();
    return useState(env.store);
}
