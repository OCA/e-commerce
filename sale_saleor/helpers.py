import base64
import logging
import re
import time
import unicodedata

from bs4 import BeautifulSoup, NavigableString
from markupsafe import Markup
from text_unidecode import unidecode

from odoo import _, api, fields
from odoo.exceptions import UserError


# Borrowed from Django's django.utils.text.slugify
def slugify(value, allow_unicode: bool = False):
    """Convert text to a slug.

    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """

    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def html_to_editorjs(html: str | None) -> dict | None:
    """Convert HTML to an EditorJS JSON structure."""
    html = (html or "").strip()
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    blocks = []

    container = soup.body or soup
    for child in container.children:
        process_child(child, blocks)

    if not blocks:
        return None

    return {
        "time": int(time.time() * 1000),
        "blocks": blocks,
        "version": "2.24.3",
    }


def process_child(child, blocks: list):
    """Process a child element or string."""
    if isinstance(child, NavigableString):
        add_text_block(str(child).strip(), blocks)
        return
    handle_element(child, blocks)


def add_text_block(text: str, blocks: list):
    """Add a paragraph block if text is not empty."""
    if text:
        blocks.append({"type": "paragraph", "data": {"text": text}})


def handle_element(el, blocks: list):
    """Handle HTML element and append corresponding EditorJS block."""
    if getattr(el, "name", None) is None:
        return

    name = el.name.lower()

    if name.startswith("h") and name[1].isdigit():
        add_header_block(el, blocks)
    elif name in {"p", "div"}:
        add_text_block(el.decode_contents().strip(), blocks)
    elif name in {"ul", "ol"}:
        add_list_block(el, blocks)
    elif name == "blockquote":
        add_quote_block(el, blocks)
    else:
        add_text_block(el.decode_contents().strip(), blocks)


def add_header_block(el, blocks: list):
    level = int(el.name[1])
    text = el.get_text(strip=True)
    if text:
        blocks.append({"type": "header", "data": {"text": text, "level": level}})


def add_list_block(el, blocks: list):
    items = [
        li.decode_contents().strip()
        for li in el.find_all("li", recursive=False)
        if li.decode_contents().strip()
    ]
    if items:
        blocks.append(
            {
                "type": "list",
                "data": {
                    "items": items,
                    "style": "ordered" if el.name == "ol" else "unordered",
                },
            }
        )


def add_quote_block(el, blocks: list):
    text = el.decode_contents().strip()
    if text:
        blocks.append({"type": "quote", "data": {"text": text, "alignment": "left"}})


def decode_image_field(
    b64: str | bytes | None, base_filename: str = "category"
) -> tuple[bytes | None, str | None, str]:
    """Decode an Odoo Binary field and guess content-type and filename.

    Returns: (bytes or None, filename or None, content_type)
    """
    if not b64:
        return None, None, "application/octet-stream"
    try:
        raw = base64.b64decode(b64)
    except Exception:
        return None, None, "application/octet-stream"

    filename = base_filename
    content_type = "application/octet-stream"
    if raw.startswith(b"\x89PNG"):
        content_type = "image/png"
        filename += ".png"
    elif raw.startswith(b"\xff\xd8"):
        content_type = "image/jpeg"
        filename += ".jpg"
    elif raw.startswith(b"GIF8"):
        content_type = "image/gif"
        filename += ".gif"
    elif raw.startswith(b"RIFF") and b"WEBP" in raw[0:16]:
        content_type = "image/webp"
        filename += ".webp"
    else:
        # default extension-less filename
        pass

    return raw, filename, content_type


def upsert_tax_class(client, tax, payload: dict) -> str | None:
    """Create or update a Saleor TaxClass from an Odoo tax record.

    Returns the Saleor TaxClass ID (str) or None.
    """
    # Update by existing ID
    if getattr(tax, "saleor_tax_class_id", None):
        update_payload = dict(payload)
        update_payload.pop("createCountryRates", None)
        if payload.get("createCountryRates"):
            update_payload["updateCountryRates"] = payload["createCountryRates"]
        res = client.tax_class_update(tax.saleor_tax_class_id, update_payload)
        return (res or {}).get("id") or tax.saleor_tax_class_id

    # Otherwise try find by name, then update
    existing = client.tax_class_search_by_name(payload.get("name"))
    if existing and existing.get("id"):
        update_payload = dict(payload)
        update_payload.pop("createCountryRates", None)
        if payload.get("createCountryRates"):
            update_payload["updateCountryRates"] = payload["createCountryRates"]
        res = client.tax_class_update(existing["id"], update_payload)
        return (res or {}).get("id") or existing["id"]

    # Finally create new
    res = client.tax_class_create(payload)
    return (res or {}).get("id")


# -------- Discount Rule helpers --------
def compute_merged_description_editorjs(
    rule_html: str | None, cond_html_parts: list[str] | None
) -> dict | None:
    """Merge rule and conditions descriptions (HTML) and convert to EditorJS.

    Returns EditorJS payload or None.
    """
    rule_html = rule_html or ""
    cond_html_parts = [p for p in (cond_html_parts or []) if p]

    merged_html: str | None = None
    if rule_html and cond_html_parts:
        merged_html = f"{rule_html}<hr/>" + "".join(
            [f"<p>{p}</p>" for p in cond_html_parts]
        )
    elif cond_html_parts:
        merged_html = "".join([f"<p>{p}</p>" for p in cond_html_parts])
    elif rule_html:
        merged_html = rule_html
    if not merged_html:
        return None
    return html_to_editorjs(merged_html)


def build_catalogue_predicate(conditions, env) -> dict:
    """Aggregate IDs per condition type, validate missing Saleor IDs,
    and build the `cataloguePredicate` dict.

    - conditions: iterable of `discount.rule.condition`
    - env: Odoo environment for translations
    """
    ids = {
        "product_ids": [],
        "variant_ids": [],
        "collection_ids": [],
        "category_ids": [],
    }
    missing = {
        "missing_products": [],
        "missing_variants": [],
        "missing_collections": [],
        "missing_categories": [],
    }

    for cond in conditions:
        _collect_ids_for_condition(cond, ids, missing)

    _raise_missing_catalogue_errors(env, conditions, missing)

    cp: dict = {}
    predicate_map = [
        ("product_ids", "productPredicate"),
        ("variant_ids", "variantPredicate"),
        ("collection_ids", "collectionPredicate"),
        ("category_ids", "categoryPredicate"),
    ]
    for ids_key, pred_key in predicate_map:
        if ids[ids_key]:
            cp[pred_key] = {"ids": sorted(set(ids[ids_key]))}
    return cp


def _collect_ids_for_condition(cond, ids: dict, missing: dict) -> None:
    """Collect Saleor IDs per condition type into ids/missing dicts."""
    ctype = getattr(cond, "catalogue_predicate_type", None)
    mappings = [
        (
            "product",
            "product_template_ids",
            "saleor_product_id",
            "product_ids",
            "missing_products",
        ),
        (
            "variant",
            "product_variant_ids",
            "saleor_variant_id",
            "variant_ids",
            "missing_variants",
        ),
        (
            "collection",
            "product_collection_ids",
            "saleor_collection_id",
            "collection_ids",
            "missing_collections",
        ),
        (
            "category",
            "product_category_ids",
            "saleor_category_id",
            "category_ids",
            "missing_categories",
        ),
    ]
    for t, rel, saleor_field, ids_key, miss_key in mappings:
        if ctype != t:
            continue
        recs = getattr(cond, rel, None)
        if not recs:
            continue
        for rec in recs:
            sid = getattr(rec, saleor_field, None)
            (ids[ids_key] if sid else missing[miss_key]).append(sid or rec.display_name)


def _raise_missing_catalogue_errors(env, conditions, missing: dict) -> None:
    """Raise a single UserError if any target records are missing Saleor IDs."""
    msg_specs = [
        ("missing_products", "Products not synced to Saleor: %s"),
        ("missing_variants", "Variants not synced to Saleor: %s"),
        ("missing_collections", "Collections not synced to Saleor: %s"),
        ("missing_categories", "Categories not synced to Saleor: %s"),
    ]
    missing_msgs: list[str] = []
    for key, fmt in msg_specs:
        values = missing.get(key) or []
        if values:
            missing_msgs.append(_(fmt, ", ".join(sorted(set(values)))))
    if not missing_msgs:
        return

    rule_name = (
        getattr(conditions, "discount_rule_id", None)
        and conditions.discount_rule_id.display_name
    ) or ""
    raise UserError(
        _(
            "Cannot sync discount rule '%(rule_name)s'"
            " to Saleor because some condition targets are not synced."
            "\n%(missing)s"
        )
        % {"rule_name": rule_name, "missing": "\n".join(missing_msgs)}
    )


def prepare_unique_slug(slug: str, slug_values):
    """Prepare unique slug value based on provided list of existing slug values.

    Mirrors Saleor's ``prepare_unique_slug`` logic but works on a simple
    iterable of slug strings.
    """
    unique_slug = slug
    extension = 1

    existing = {v for v in slug_values if v}
    while unique_slug in existing:
        extension += 1
        unique_slug = f"{slug}-{extension}"

    return unique_slug


def generate_unique_slug(
    instance,
    slugable_value: str,
    slug_field_name: str = "slug",
    *,
    additional_search_domain=None,
) -> str:
    slug = slugify(unidecode(slugable_value))

    if slug == "":
        slug = "-"

    domain = [
        (slug_field_name, "!=", False),
        ("id", "!=", instance.id or 0),
    ]
    if additional_search_domain:
        domain.extend(additional_search_domain)

    candidates = instance.search(domain)
    slug_values = []
    base = slug
    prefix = f"{base}-"
    for rec in candidates:
        value = getattr(rec, slug_field_name, None)
        if not value:
            continue
        if value == base:
            slug_values.append(value)
            continue
        if value.startswith(prefix) and value[len(prefix) :].isdigit():
            slug_values.append(value)

    unique_slug = prepare_unique_slug(slug, slug_values)
    return unique_slug


def apply_reward_mapping(
    input_data: dict, reward_type: str | None, reward_unit: str | None, reward_value
) -> None:
    """Populate reward fields in input_data according to rule configuration.

    - reward_type: expects "sub" for subtotal discount to be applicable
    - reward_unit: "percent" or "currency"
    - reward_value: numeric value (0 allowed)
    """
    if reward_type != "sub":
        return
    if reward_unit == "percent":
        input_data["rewardValueType"] = "PERCENTAGE"
    elif reward_unit == "currency":
        input_data["rewardValueType"] = "FIXED"
    if "rewardValueType" in input_data:
        input_data["rewardValue"] = float(reward_value or 0.0)


# -------- Datetime helpers --------
def to_saleor_datetime(dt):
    """Return ISO8601 string with 'T' separator and 'Z' suffix for UTC.

    Ensures compatibility with Saleor GraphQL DateTime inputs.
    Accepts Odoo datetime (string) or python datetime.
    """
    if not dt:
        return None
    py_dt = fields.Datetime.to_datetime(dt)
    if not py_dt:
        return None
    iso = py_dt.replace(microsecond=0).isoformat()
    if "T" not in iso:
        iso = iso.replace(" ", "T")
    if "+" not in iso and iso.rfind("-") <= 10 and not iso.endswith("Z"):
        iso = iso + "Z"
    return iso


# -------- Account helpers --------
def get_active_saleor_account(env, raise_if_missing: bool = True):
    """Return all active Saleor accounts.

    If none found and raise_if_missing is True, raise a UserError.
    """
    account = env["saleor.account"].search([("active", "=", True)], limit=1)
    if not account and raise_if_missing:
        raise UserError(_("No active Saleor account configured."))
    return account


def format_batch_errors_message(title, items):
    changes = Markup("\n").join(
        [
            Markup(
                """
                <li>
                    <span
                        class='o-mail-Message-trackingNew me-1 fw-bold text-info'
                        >%(name)s</span>
                    <span
                        class='o-mail-Message-trackingField ms-1 fst-italic text-muted'
                        >%(reason)s</span>
                </li>
                """
            )
            % {"name": name, "reason": reason}
            for (name, reason) in items
        ]
    )
    body = Markup("<p> %(title)s </p><ul class='mb-0 ps-4'>%(changes)s</ul>") % {
        "title": title,
        "changes": changes,
    }
    return body


def format_note(env, template, *args):
    text = _(template, *args)
    return Markup("<p>%s</p>") % text


def format_kv_list(title, items):
    lis = Markup("\n").join(
        [
            Markup("<li><b>%s</b>: %s</li>") % (k, (v if v is not None else "-"))
            for (k, v) in items
        ]
    )
    return Markup("<p>%s</p><ul class='mb-0 ps-4'>%s</ul>") % (title, lis)


def post_to_current_job_committed(
    env, record, body, subject=None, message_type="comment"
):
    """Post to current queue.job chatter in a separate transaction and commit."""
    _logger = logging.getLogger(__name__)
    try:
        registry = env.registry
        with registry.cursor() as cr:
            env2 = api.Environment(cr, env.uid, dict(env.context or {}))
            # resolve job in the new env
            ctx = env2.context or {}
            job = None
            job_id = ctx.get("job_id")
            if job_id:
                job = env2["queue.job"].browse(job_id)
                job = job if job and job.exists() else None
            if job is None:
                job_uuid = ctx.get("job_uuid")
                if job_uuid:
                    job = (
                        env2["queue.job"]
                        .sudo()
                        .search([("uuid", "=", job_uuid)], limit=1)
                        or None
                    )
            target = job
            if target is None and record is not None:
                target = env2[record._name].browse(record.id)
            if target is None:
                return
            try:
                target.message_post(
                    body=body, subject=subject, message_type=message_type
                )
            except Exception as e:
                _logger.warning(
                    "Failed to post message (committed) to %s: %s",
                    getattr(target, "_name", "unknown"),
                    e,
                )
    except Exception as e:
        _logger.debug("Committed post failed: %s", e)


# -------- Saleor dashboard link helpers --------
def saleor_dashboard_links(
    base_url: str | None,
    kind: str,
    *,
    object_id: str | None = None,
    number: str | None = None,
    zone_id: str | None = None,
    product_id: str | None = None,
    **kwargs,
) -> tuple[str | None, str | None]:
    """Return (dashboard_url, object_url) for Saleor Dashboard."""
    base = (base_url or "").rstrip("/")
    if not base:
        return None, None
    dashboard = f"{base}/dashboard"
    path = None
    id_val = object_id or kwargs.get("id")

    if kind == "channel":
        ident = id_val
        path = f"/channels/{ident}" if ident else None
    elif kind == "shipping_zone":
        path = f"/shipping/{id_val}" if id_val else None
    elif kind == "shipping_method":
        if zone_id and id_val:
            path = f"/shipping/{zone_id}/{id_val}"
        else:
            path = f"/shipping/{id_val}" if id_val else None
    elif kind == "product":
        path = f"/products/{id_val}" if id_val else None
    elif kind == "product_variant":
        if product_id and id_val:
            path = f"/products/{product_id}/variant/{id_val}"
        else:
            path = (
                f"/products/{product_id or id_val}" if (product_id or id_val) else None
            )
    elif kind == "collection":
        path = f"/collections/{id_val}" if id_val else None
    elif kind == "attribute":
        path = f"/attributes/{id_val}" if id_val else None
    elif kind == "tax":
        path = f"/taxes/tax-classes/{id_val}" if id_val else None
    elif kind == "order":
        ident = id_val
        path = f"/orders/{ident}" if ident else None
    elif kind == "voucher":
        path = f"/discounts/vouchers/{id_val}" if id_val else None
    elif kind == "gift_card":
        path = f"/gift-cards/{id_val}" if id_val else "/gift-cards"

    return dashboard, (dashboard + path) if path else dashboard


def make_link(text: str, href: str | None) -> Markup:
    href = href or "#"
    safe_text = text or href
    return Markup('<a href="%s" target="_blank" rel="noopener">%s</a>') % (
        href,
        safe_text,
    )
