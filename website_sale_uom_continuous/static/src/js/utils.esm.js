// Copyright 2026 Camptocamp (http://www.camptocamp.com).
// @author Iván Todorovich <ivan.todorovich@gmail.com>
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

/**
 * Call `fn` with `parseInt` replaced by `parseFloat`, only while its synchronous
 * part runs, i.e. until the first request is sent.
 *
 * Core parses quantities with `parseInt`, which drops their decimals.
 * The server keeps integer quantities for UoMs that are not continuous.
 *
 * @param {Function} fn
 * @returns {*} the result of `fn`
 */
export function withDecimals(fn) {
    const originalParseInt = globalThis.parseInt;
    globalThis.parseInt = (value) => parseFloat(value);
    try {
        return fn();
    } finally {
        globalThis.parseInt = originalParseInt;
    }
}
