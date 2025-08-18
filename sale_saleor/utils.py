# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json as _json
import logging

import requests

_logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30


class SaleorClient:
    """Lightweight GraphQL client for Saleor.

    Handles auth via tokenCreate (JWT) or pre-provided token.
    """

    def __init__(self, base_url, verify_ssl=True, token=None, timeout=DEFAULT_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.endpoint = f"{self.base_url}/graphql/"
        self.verify_ssl = verify_ssl
        self._token = token
        self.timeout = timeout

    def set_token(self, token):
        self._token = token

    def graphql(self, query, variables=None):
        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"JWT {self._token}"
        payload = {"query": query, "variables": variables or {}}
        resp = requests.post(
            self.endpoint,
            json=payload,
            headers=headers,
            timeout=self.timeout,
            verify=self.verify_ssl,
        )
        if resp.status_code != 200:
            # Try to provide detailed server message to ease debugging
            try:
                err_body = resp.json()
            except Exception:
                err_body = resp.text
            raise Exception(f"Saleor GraphQL HTTP {resp.status_code}: {err_body}")
        data = resp.json()
        if "errors" in data and data["errors"]:
            raise Exception(str(data["errors"]))
        return data["data"]

    def graphql_multipart(self, query, variables, files_map):
        """Perform GraphQL multipart request per spec (for Upload scalar).

        files_map is a dict like {"0": (filename, bytes, content_type, paths)}
        where paths is a list of variable paths e.g. ["variables.image"].
        """
        headers = {}
        if self._token:
            headers["Authorization"] = f"JWT {self._token}"
        operations = {
            "query": query,
            "variables": variables or {},
        }
        # Build map and files payload
        files = {}
        file_map = {}
        for idx, (filename, content, content_type, paths) in files_map.items():
            file_map[idx] = paths
            files[idx] = (filename, content, content_type)
        data = {
            "operations": _json.dumps(operations),
            "map": _json.dumps(file_map),
        }
        resp = requests.post(
            self.endpoint,
            data=data,
            files=files,
            headers=headers,
            timeout=self.timeout,
            verify=self.verify_ssl,
        )
        if resp.status_code != 200:
            try:
                err_body = resp.json()
            except Exception:
                err_body = resp.text
            raise Exception(f"Saleor GraphQL HTTP {resp.status_code}: {err_body}")
        data = resp.json()
        if "errors" in data and data["errors"]:
            raise Exception(str(data["errors"]))
        return data["data"]

    def token_create(self, email, password):
        query = """
        mutation TokenCreate($email: String!, $password: String!) {
          tokenCreate(email: $email, password: $password) {
            token
            errors { field message }
          }
        }
        """
        res = self.graphql(query, {"email": email, "password": password})
        out = res.get("tokenCreate") or {}
        token = out.get("token")
        if not token:
            raise Exception(f"Saleor auth failed: {out.get('errors')}")
        return token

    # --- App management ---
    def app_get_by_id(self, app_id):
        query = """
        query App($id: ID!) {
          app(id: $id) { id name }
        }
        """
        data = self.graphql(query, {"id": app_id})
        return data.get("app")

    def app_create(self, name, permissions=None, is_active=True):
        query = """
        mutation AppCreate($input: AppInput!) {
          appCreate(input: $input) {
            app { id name }
            authToken
            errors { field message }
          }
        }
        """
        variables = {
            "input": {
                "name": name,
                "permissions": permissions or [],
            }
        }
        data = self.graphql(query, variables)
        result = data.get("appCreate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor appCreate errors: {errors}")
        app = result.get("app") or {}
        token = result.get("authToken")
        out = dict(app)
        if token:
            out["authToken"] = token
        _logger.info("Saleor app_create done: %s", out)
        return out

    def app_update(self, app_id, permissions=None, is_active=None, name=None):
        """Update a Saleor App (e.g., permissions).

        Parameters:
        - app_id: ID of the app to update
        - permissions: list of permission codes to set
        - is_active: optional boolean to activate/deactivate
        - name: optional new app name
        """
        query = """
        mutation AppUpdate($id: ID!, $input: AppInput!) {
          appUpdate(id: $id, input: $input) {
            app { id name }
            errors { field message }
          }
        }
        """
        input_payload = {}
        if permissions is not None:
            input_payload["permissions"] = permissions
        if is_active is not None:
            input_payload["isActive"] = bool(is_active)
        if name is not None:
            input_payload["name"] = name

        variables = {"id": app_id, "input": input_payload}
        data = self.graphql(query, variables)
        result = data.get("appUpdate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor appUpdate errors: {errors}")
        _logger.info("Saleor app_update done for app %s", app_id)
        return result.get("app")

    # --- Webhook management ---
    def webhook_get_by_id(self, webhook_id):
        query = """
        query Webhook($id: ID!) {
          webhook(id: $id) {
            id name targetUrl isActive events { eventType }
          }
        }
        """
        data = self.graphql(query, {"id": webhook_id})
        return data.get("webhook")

    def webhook_create(
        self, app_id, target_url, events, secret_key=None, is_active=True, name=None
    ):
        query = """
        mutation WebhookCreate($input: WebhookCreateInput!) {
          webhookCreate(input: $input) {
            webhook { id name targetUrl isActive }
            errors { field message }
          }
        }
        """
        variables = {
            "input": {
                "app": app_id,
                "name": name or "Odoo Webhook",
                "targetUrl": target_url,
                "isActive": bool(is_active),
                "secretKey": secret_key or "",
                # Use asyncEvents for standard webhooks
                "asyncEvents": events or [],
            },
        }
        data = self.graphql(query, variables)
        result = data.get("webhookCreate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor webhookCreate errors: {errors}")
        return result.get("webhook")

    def webhook_update(
        self,
        webhook_id,
        target_url=None,
        events=None,
        secret_key=None,
        is_active=None,
        name=None,
    ):
        query = """
        mutation WebhookUpdate($id: ID!, $input: WebhookUpdateInput!) {
          webhookUpdate(id: $id, input: $input) {
            webhook { id name targetUrl isActive }
            errors { field message }
          }
        }
        """
        input_data = {}
        if target_url is not None:
            input_data["targetUrl"] = target_url
        if is_active is not None:
            input_data["isActive"] = bool(is_active)
        if name is not None:
            input_data["name"] = name
        if secret_key is not None:
            input_data["secretKey"] = secret_key
        if events is not None:
            input_data["asyncEvents"] = events or []
        variables = {"id": webhook_id, "input": input_data}
        data = self.graphql(query, variables)
        result = data.get("webhookUpdate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor webhookUpdate errors: {errors}")
        return result.get("webhook")

    # ---Product variant quantity---
    def product_variant_stocks_update(self, variant_id, warehouse_id, quantity):
        """
        Update stock quantity of a single product variant in a Saleor warehouse.
        """
        query = """
        mutation ProductVariantStocksUpdate(
            $variantId: ID!, $stocks: [StockInput!]!
        ) {
          productVariantStocksUpdate(variantId: $variantId, stocks: $stocks) {
            productVariant {
              id
              sku
              stocks {
                warehouse { id name }
                quantity
              }
            }
            errors {
              field
              message
            }
          }
        }
        """
        variables = {
            "variantId": variant_id,
            "stocks": [{"warehouse": warehouse_id, "quantity": int(quantity)}],
        }
        data = self.graphql(query, variables)
        result = data.get("productVariantStocksUpdate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor productVariantStocksUpdate errors: {errors}")
        return result.get("productVariant")

    def product_variants_list_by_product_id(self, product_id):
        """Return list of variants for a given Saleor product ID.

        Each item: {id, sku, name}
        """
        query = """
        query ProductVariants($id: ID!) {
          product(id: $id) {
            id
            variants {
              id
              sku
              name
            }
          }
        }
        """
        variables = {"id": product_id}
        data = self.graphql(query, variables) or {}
        product = (data or {}).get("product") or {}
        return product.get("variants") or []

    def product_variant_bulk_delete(self, variant_ids):
        """Bulk delete product variants by IDs in Saleor.

        variant_ids: iterable of variant relay IDs.
        """
        ids = list(variant_ids or [])
        if not ids:
            return True
        query = """
        mutation ProductVariantBulkDelete($ids: [ID!]!) {
          productVariantBulkDelete(ids: $ids) {
            count
            errors { field message }
          }
        }
        """
        variables = {"ids": ids}
        data = self.graphql(query, variables) or {}
        result = (data or {}).get("productVariantBulkDelete") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor productVariantBulkDelete errors: {errors}")
        return result.get("count") or True

    def product_variant_stocks_create(self, variant_id, warehouse_id, quantity=0):
        """Create stock entries for a product variant in a Saleor warehouse."""
        query = """
        mutation ProductVariantStocksCreate(
            $variantId: ID!, $stocks: [StockInput!]!
        ) {
          productVariantStocksCreate(variantId: $variantId, stocks: $stocks) {
            productVariant { id sku stocks { warehouse { id name } quantity } }
            errors { field message code }
          }
        }
        """
        variables = {
            "variantId": variant_id,
            "stocks": [{"warehouse": warehouse_id, "quantity": int(quantity)}],
        }
        data = self.graphql(query, variables)
        result = (data or {}).get("productVariantStocksCreate") or {}
        errors = result.get("errors") or []
        non_dup_errors = [
            e for e in errors if (e or {}).get("code") not in {"ALREADY_EXISTS"}
        ]
        if non_dup_errors:
            raise Exception(
                f"Saleor productVariantStocksCreate errors: {non_dup_errors}"
            )
        return result.get("productVariant") or True

    def product_variant_channel_listing_update(self, variant_id, listings):
        """
        Update channel listings for a variant (prices/cost prices per channel).
        """
        query = """
        mutation ProductVariantChannelListingUpdate(
          $id: ID!, $listings: [ProductVariantChannelListingAddInput!]!
        ) {
          productVariantChannelListingUpdate(id: $id, input: $listings) {
            variant { id sku }
            errors { field message }
          }
        }
        """
        variables = {"id": variant_id, "listings": listings or []}
        data = self.graphql(query, variables)
        result = (data or {}).get("productVariantChannelListingUpdate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(
                f"Saleor productVariantChannelListingUpdate errors: {errors}"
            )
        return result.get("variant")

    # --- Customers ---
    def customer_get_by_id(self, customer_id):
        query = """
        query User($id: ID!) {
          user(id: $id) {
            id
            email
            firstName
            lastName
            defaultBillingAddress {
              country { code }
              city
              streetAddress1
              postalCode
              phone
            }
            defaultShippingAddress {
              country { code }
              city
              streetAddress1
              postalCode
              phone
            }
          }
        }
        """
        data = self.graphql(query, {"id": customer_id})
        return data.get("user")

    # Category mutations
    def category_create(
        self,
        input_data,
        filename=None,
        file_bytes=None,
        content_type="application/octet-stream",
    ):
        query = """
        mutation CategoryCreate(
            $name: String!,
            $slug: String!,
            $description: JSONString,
            $seoTitle: String,
            $seoDescription: String,
            $metadata: [MetadataInput!],
            $privateMetadata: [MetadataInput!],
            $parent: ID,
            $backgroundImage: Upload
        ) {
            categoryCreate(
                input: {
                    name: $name,
                    slug: $slug,
                    description: $description,
                    seo: { title: $seoTitle, description: $seoDescription },
                    metadata: $metadata,
                    privateMetadata: $privateMetadata,
                    backgroundImage: $backgroundImage
                },
                parent: $parent
            ) {
                category { id slug }
                errors { field message }
            }
        }
        """
        seo = input_data.get("seo") or {}
        variables = {
            "name": input_data.get("name"),
            "slug": input_data.get("slug"),
            "description": input_data.get("description"),
            "seoTitle": seo.get("title"),
            "seoDescription": seo.get("description"),
            "metadata": input_data.get("metadata") or [],
            "privateMetadata": input_data.get("privateMetadata") or [],
            "parent": input_data.get("parent"),
            "backgroundImage": None,
        }
        if file_bytes:
            files_map = {
                "0": (
                    filename or "image",
                    file_bytes,
                    content_type,
                    ["variables.backgroundImage"],
                ),
            }
            data = self.graphql_multipart(query, variables, files_map)
        else:
            data = self.graphql(query, variables)
        result = data.get("categoryCreate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor categoryCreate errors: {errors}")
        category = result.get("category")
        _logger.info("Saleor category_create done: %s", category)
        return category

    def category_update(
        self,
        category_id,
        input_data,
        filename=None,
        file_bytes=None,
        content_type="application/octet-stream",
    ):
        query = """
        mutation CategoryUpdate(
            $id: ID!,
            $name: String,
            $slug: String,
            $description: JSONString,
            $seoTitle: String,
            $seoDescription: String,
            $metadata: [MetadataInput!],
            $privateMetadata: [MetadataInput!],
            $backgroundImage: Upload
        ) {
            categoryUpdate(
                id: $id,
                input: {
                    name: $name,
                    slug: $slug,
                    description: $description,
                    seo: { title: $seoTitle, description: $seoDescription },
                    metadata: $metadata,
                    privateMetadata: $privateMetadata,
                    backgroundImage: $backgroundImage
                }
            ) {
                category { id slug }
                errors { field message }
            }
        }
        """
        seo = input_data.get("seo") or {}
        variables = {
            "id": category_id,
            "name": input_data.get("name"),
            "slug": input_data.get("slug"),
            "description": input_data.get("description"),
            "seoTitle": seo.get("title"),
            "seoDescription": seo.get("description"),
            "metadata": input_data.get("metadata") or [],
            "privateMetadata": input_data.get("privateMetadata") or [],
            "backgroundImage": None,
        }
        if file_bytes:
            files_map = {
                "0": (
                    filename or "image",
                    file_bytes,
                    content_type,
                    ["variables.backgroundImage"],
                ),
            }
            data = self.graphql_multipart(query, variables, files_map)
        else:
            data = self.graphql(query, variables)
        result = data.get("categoryUpdate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor categoryUpdate errors: {errors}")

        category = result.get("category")
        _logger.info("Saleor category_update done: %s", category)
        return category

    # Queries
    def category_get_by_slug(self, slug):
        query = """
        query CategoryBySlug($slug: String!) {
          category(slug: $slug) {
            id
            slug
          }
        }
        """
        data = self.graphql(query, {"slug": slug})
        return data.get("category")

    # Collection mutations
    def collection_create(
        self,
        input_data,
        filename=None,
        file_bytes=None,
        content_type="application/octet-stream",
    ):
        query = """
        mutation CollectionCreate($input: CollectionCreateInput!) {
            collectionCreate(input: $input) {
                collection { id slug }
                errors { field message }
            }
        }
        """
        variables = {
            "input": {
                "name": input_data.get("name"),
                "slug": input_data.get("slug"),
                "description": input_data.get("description"),
                "seo": input_data.get("seo") or {},
                "metadata": input_data.get("metadata") or [],
                "privateMetadata": input_data.get("privateMetadata") or [],
            }
        }
        if file_bytes:
            files_map = {
                "0": (
                    filename or "image",
                    file_bytes,
                    content_type,
                    ["variables.input.backgroundImage"],
                ),
            }
            data = self.graphql_multipart(query, variables, files_map)
        else:
            data = self.graphql(query, variables)
        result = data.get("collectionCreate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor collectionCreate errors: {errors}")
        collection = result.get("collection")
        _logger.info("Saleor collection_create done: %s", collection)
        return collection

    def collection_update(
        self,
        collection_id,
        input_data,
        filename=None,
        file_bytes=None,
        content_type="application/octet-stream",
    ):
        query = """
        mutation CollectionUpdate($id: ID!, $input: CollectionInput!) {
            collectionUpdate(id: $id, input: $input) {
                collection { id slug }
                errors { field message }
            }
        }
        """
        variables = {
            "id": collection_id,
            "input": {
                "name": input_data.get("name"),
                "slug": input_data.get("slug"),
                "description": input_data.get("description"),
                "seo": input_data.get("seo") or {},
                "metadata": input_data.get("metadata") or [],
                "privateMetadata": input_data.get("privateMetadata") or [],
            },
        }
        if file_bytes:
            files_map = {
                "0": (
                    filename or "image",
                    file_bytes,
                    content_type,
                    ["variables.input.backgroundImage"],
                ),
            }
            data = self.graphql_multipart(query, variables, files_map)
        else:
            data = self.graphql(query, variables)
        result = data.get("collectionUpdate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor collectionUpdate errors: {errors}")
        collection = result.get("collection")
        _logger.info("Saleor collection_update done: %s", collection)
        return collection

    def collection_channel_listing_update(
        self, collection_id, add_channels=None, remove_channels=None
    ):
        """Update channel listings for a collection.

        add_channels: list of dicts, each like
          {"channelId": ID, "isPublished": bool, "publicationDate": str|None}
        remove_channels: list of channel IDs to remove
        """
        query = """
        mutation CollectionChannelListingUpdate(
          $id: ID!, $input: CollectionChannelListingUpdateInput!
        ) {
          collectionChannelListingUpdate(id: $id, input: $input) {
            collection { id slug }
            errors { field message }
          }
        }
        """
        variables = {
            "id": collection_id,
            "input": {
                "addChannels": add_channels or [],
                "removeChannels": remove_channels or [],
            },
        }
        data = self.graphql(query, variables)
        result = data.get("collectionChannelListingUpdate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor collectionChannelListingUpdate errors: {errors}")
        return result.get("collection")

    def collection_add_products(self, collection_id, product_ids):
        """Add products to a collection.
        collection_id: Saleor ID of the collection
        product_ids: list of Saleor Product IDs
        """
        query = """
        mutation CollectionAddProducts($collectionId: ID!, $products: [ID!]!) {
          collectionAddProducts(collectionId: $collectionId, products: $products) {
            collection { id }
            errors { field message }
          }
        }
        """
        variables = {"collectionId": collection_id, "products": product_ids or []}
        data = self.graphql(query, variables)
        result = data.get("collectionAddProducts") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor collectionAddProducts errors: {errors}")
        return result.get("collection")

    def collection_get_by_slug(self, slug):
        query = """
        query CollectionBySlug($slug: String!) {
          collection(slug: $slug) {
            id
            slug
          }
        }
        """
        data = self.graphql(query, {"slug": slug})
        return data.get("collection")

    def collection_channel_listings(self, collection_id):
        """Return list of current channel listings for a collection.
        Each item: { channel: { id }, isPublished, publicationDate }
        """
        query = """
        query CollectionChannels($id: ID!) {
          collection(id: $id) {
            id
            channelListings {
              channel { id }
              isPublished
              publicationDate
            }
          }
        }
        """
        data = self.graphql(query, {"id": collection_id})
        col = (data or {}).get("collection") or {}
        return col.get("channelListings") or []

    # --- Vouchers ---
    def voucher_get_by_id(self, voucher_id):
        query = """
        query VoucherById($id: ID!) {
          voucher(id: $id) {
            id
            name
            type
          }
        }
        """
        data = self.graphql(query, {"id": voucher_id})
        return (data or {}).get("voucher")

    def vouchers_search_by_name(self, name, first=50):
        """Search vouchers and return exact name match if present."""
        query = """
        query Vouchers($first: Int) {
          vouchers(first: $first) {
            edges { node { id name } }
          }
        }
        """
        data = self.graphql(query, {"first": int(first)})
        edges = (((data or {}).get("vouchers") or {}).get("edges")) or []
        exact = None
        for e in edges:
            node = e.get("node") or {}
            if node.get("name") == name:
                exact = node
                break
        return exact

    def voucher_channel_listings_get(self, voucher_id):
        """Return list of channel IDs currently linked to the voucher in Saleor."""
        query = """
        query VoucherChannelListings($id: ID!) {
          voucher(id: $id) {
            id
            channelListings { channel { id } }
          }
        }
        """
        data = self.graphql(query, {"id": voucher_id})
        voucher = (data or {}).get("voucher") or {}
        listings = voucher.get("channelListings") or []
        chan_ids = []
        for listing in listings:
            ch = (listing or {}).get("channel") or {}
            cid = ch.get("id")
            if cid:
                chan_ids.append(cid)
        return chan_ids

    def voucher_create(self, input_data):
        query = """
        mutation VoucherCreate($input: VoucherInput!) {
          voucherCreate(input: $input) {
            voucher { id name }
            errors { field message }
          }
        }
        """
        variables = {"input": input_data or {}}
        data = self.graphql(query, variables)
        result = (data or {}).get("voucherCreate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor voucherCreate errors: {errors}")
        return result.get("voucher")

    def voucher_update(self, voucher_id, input_data):
        query = """
        mutation VoucherUpdate($id: ID!, $input: VoucherInput!) {
          voucherUpdate(id: $id, input: $input) {
            voucher { id name }
            errors { field message }
          }
        }
        """
        variables = {"id": voucher_id, "input": input_data or {}}
        data = self.graphql(query, variables)
        result = (data or {}).get("voucherUpdate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor voucherUpdate errors: {errors}")
        return result.get("voucher")

    def voucher_channel_listing_update(
        self, voucher_id, add_channels=None, remove_channels=None
    ):
        """Update channel listings for a voucher.

        add_channels: list of channel IDs to add
        remove_channels: list of channel IDs to remove
        """
        query = """
        mutation VoucherChannelListingUpdate(
          $id: ID!, $input: VoucherChannelListingInput!
        ) {
          voucherChannelListingUpdate(id: $id, input: $input) {
            voucher { id }
            errors { field message }
          }
        }
        """
        variables = {
            "id": voucher_id,
            "input": {
                "addChannels": add_channels or [],
                "removeChannels": remove_channels or [],
            },
        }
        data = self.graphql(query, variables)
        result = (data or {}).get("voucherChannelListingUpdate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor voucherChannelListingUpdate errors: {errors}")
        return result.get("voucher")

    def voucher_update_add_codes(self, voucher_id, codes):
        """Add codes via voucherUpdate(input: { addCodes }).
        If codes already exist in Saleor, the API returns errors; we log and continue.
        """
        if not codes:
            return True
        query = """
        mutation VoucherUpdateAddCodes($id: ID!, $codes: [String!]!) {
          voucherUpdate(id: $id, input: { addCodes: $codes }) {
            voucher { id }
            errors { field message }
          }
        }
        """
        variables = {"id": voucher_id, "codes": list(codes)}
        data = self.graphql(query, variables)
        result = (data or {}).get("voucherUpdate") or {}
        errors = result.get("errors") or []
        if errors:
            _logger.warning("voucherUpdate(addCodes) returned errors: %s", errors)
        return result.get("voucher") or True

    def voucher_metadata_update(self, voucher_id, metadata):
        """Update public metadata for a voucher via updateMetadata."""
        if not metadata:
            return True
        query = """
        mutation UpdateVoucherMetadata($id: ID!, $input: [MetadataInput!]!) {
          updateMetadata(id: $id, input: $input) {
            item {
              ... on Voucher {
                id
                metadata { key value }
              }
            }
            errors { field message }
          }
        }
        """
        variables = {"id": voucher_id, "input": metadata}
        data = self.graphql(query, variables)
        result = (data or {}).get("updateMetadata") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor updateMetadata (voucher) errors: {errors}")
        return result.get("item") or True

    # --- Orders (Draft) ---
    def draft_order_create(self, input_data):
        query = """
        mutation DraftOrderCreate($input: DraftOrderCreateInput!) {
          draftOrderCreate(input: $input) {
            order { id number }
            errors { field message }
          }
        }
        """
        variables = {"input": input_data or {}}
        data = self.graphql(query, variables)
        result = (data or {}).get("draftOrderCreate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor draftOrderCreate errors: {errors}")
        order = result.get("order") or {}
        return order

    def draft_order_lines_create(self, order_id, lines):
        query = """
        mutation OrderLinesCreate($id: ID!, $input: [OrderLineCreateInput!]!) {
          orderLinesCreate(id: $id, input: $input) {
            order { id }
            errors { field message }
          }
        }
        """
        input_lines = [
            {"variantId": ln.get("variantId"), "quantity": int(ln.get("quantity") or 0)}
            for ln in (lines or [])
        ]
        variables = {"id": order_id, "input": input_lines}
        data = self.graphql(query, variables)
        result = (data or {}).get("orderLinesCreate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor orderLinesCreate errors: {errors}")
        return result.get("order") or True

    def order_update_shipping(self, order_id, shipping_method_id):
        """Set the shipping method on an order using orderUpdateShipping.

        Args:
            order_id (str): Relay ID of the Saleor order
            shipping_method_id (str): Relay ID of the Saleor shipping method
        """
        if not order_id or not shipping_method_id:
            return None
        query = """
        mutation OrderUpdateShipping($order: ID!, $input: OrderUpdateShippingInput!) {
          orderUpdateShipping(order: $order, input: $input) {
            order {
              id
              deliveryMethod {
                __typename
                ... on ShippingMethod { id name type }
              }
            }
            errors { field message }
          }
        }
        """
        variables = {"order": order_id, "input": {"shippingMethod": shipping_method_id}}
        data = self.graphql(query, variables)
        result = (data or {}).get("orderUpdateShipping") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor orderUpdateShipping errors: {errors}")
        return result.get("order")

    def order_available_shipping_methods(self, order_id):
        """Return list of available ShippingMethod nodes for an order.

        Each item has fields: { id, name } where id is of GraphQL type ShippingMethod.
        """
        if not order_id:
            return []
        query = """
        query OrderAvailableShippingMethods($id: ID!) {
          order(id: $id) {
            id
            availableShippingMethods {
              id
              name
            }
          }
        }
        """
        data = self.graphql(query, {"id": order_id})
        order = (data or {}).get("order") or {}
        return order.get("availableShippingMethods") or []

    def order_mark_as_paid(self, order_id, transaction_reference=None):
        """Mark an order as paid in Saleor."""
        if not order_id:
            return None
        query = """
        mutation OrderMarkAsPaid($order: ID!, $transactionReference: String) {
          orderMarkAsPaid(id: $order, transactionReference: $transactionReference) {
            order { id status number }
            errors { field message }
          }
        }
        """
        variables = {"order": order_id, "transactionReference": transaction_reference}
        data = self.graphql(query, variables)
        result = (data or {}).get("orderMarkAsPaid") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor orderMarkAsPaid errors: {errors}")
        return result.get("order")

    def order_get_by_id(self, order_id):
        """Fetch an order by ID with fields used for Odoo upsert behavior."""
        query = """
        query OrderById($id: ID!) {
          order(id: $id) {
            id
            number
            status
            channel { id slug }
            metadata { key value }
            privateMetadata { key value }
            user { id email firstName lastName }
            billingAddress {
              firstName lastName companyName phone
              streetAddress1 streetAddress2 city postalCode
              country { code }
              countryArea
            }
            shippingAddress {
              firstName lastName companyName phone
              streetAddress1 streetAddress2 city postalCode
              country { code }
              countryArea
            }
            shippingMethod { id name }
            shippingPrice {
              net { amount currency }
              gross { amount currency }
            }
            lines {
              id
              quantity
              productName
              variant { id }
              unitPrice { net { amount currency } gross { amount currency } }
            }
            discounts { amount { amount currency } reason }
            payments {
              id
              gateway
              chargeStatus
              total { amount currency }
              capturedAmount { amount currency }
              pspReference
            }
          }
        }
        """
        data = self.graphql(query, {"id": order_id})
        return (data or {}).get("order")

    def draft_order_complete(self, order_id):
        """Complete a draft order using draftOrderComplete mutation."""
        if not order_id:
            return None
        query = """
        mutation DraftOrderComplete($id: ID!) {
          draftOrderComplete(id: $id) {
            order {
              id
              number
              status
            }
            errors { field message }
          }
        }
        """
        data = self.graphql(query, {"id": order_id})
        result = (data or {}).get("draftOrderComplete") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor draftOrderComplete errors: {errors}")
        return result.get("order")

    def draft_order_update(self, order_id, input_data):
        """Update a draft order's base fields (addresses, user/email, channel)."""
        query = """
        mutation DraftOrderUpdate($id: ID!, $input: DraftOrderInput!) {
          draftOrderUpdate(id: $id, input: $input) {
            order { id number }
            errors { field message }
          }
        }
        """
        variables = {"id": order_id, "input": input_data or {}}
        data = self.graphql(query, variables)
        result = (data or {}).get("draftOrderUpdate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor draftOrderUpdate errors: {errors}")
        return result.get("order")

    def order_line_delete(self, order_line_id):
        """Delete a single order line by ID (works for draft orders)."""
        query = """
        mutation OrderLineDelete($id: ID!) {
          orderLineDelete(id: $id) {
            order { id }
            errors { field message }
          }
        }
        """
        data = self.graphql(query, {"id": order_line_id})
        result = (data or {}).get("orderLineDelete") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor orderLineDelete errors: {errors}")
        return result.get("order") or True

    def voucher_catalogues_add(
        self,
        voucher_id,
        products=None,
        collections=None,
        categories=None,
        variants=None,
    ):
        """Attach catalogues to a voucher via voucherCataloguesAdd.
        All params are lists of Saleor IDs. Any empty list is treated as [].
        """
        products = products or []
        collections = collections or []
        categories = categories or []
        variants = variants or []
        if not any([products, collections, categories, variants]):
            return True
        query = """
        mutation VoucherCataloguesAdd(
          $id: ID!,
          $products: [ID!],
          $collections: [ID!],
          $categories: [ID!],
          $variants: [ID!]
        ) {
          voucherCataloguesAdd(
            id: $id,
            input: {
              products: $products,
              collections: $collections,
              categories: $categories,
              variants: $variants
            }
          ) {
            voucher { id }
            errors { field message }
          }
        }
        """
        variables = {
            "id": voucher_id,
            "products": products,
            "collections": collections,
            "categories": categories,
            "variants": variants,
        }
        data = self.graphql(query, variables)
        result = (data or {}).get("voucherCataloguesAdd") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor voucherCataloguesAdd errors: {errors}")
        return result.get("voucher") or True

    def voucher_private_metadata_update(self, voucher_id, private_metadata):
        """Update private metadata for a voucher via updatePrivateMetadata."""
        if not private_metadata:
            return True
        query = """
        mutation UpdateVoucherPrivateMetadata($id: ID!, $input: [MetadataInput!]!) {
          updatePrivateMetadata(id: $id, input: $input) {
            item {
              ... on Voucher {
                id
                privateMetadata { key value }
              }
            }
            errors { field message }
          }
        }
        """
        variables = {"id": voucher_id, "input": private_metadata}
        data = self.graphql(query, variables)
        result = (data or {}).get("updatePrivateMetadata") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor updatePrivateMetadata (voucher) errors: {errors}")
        return result.get("item") or True

    # --- Gift Cards ---
    def gift_card_create(self, input_data):
        """Create a gift card in Saleor and return the giftCard node.

        Expects input_data to conform to GiftCardCreateInput fields, e.g.:
        {
            "isActive": True,
            "balance": {"amount": 10.0, "currency": "USD"},
            "userEmail": "test@example.com",
            "channelId": "...",
            "expiryDate": "YYYY-MM-DD",
            "tags": ["Birthday"],
            "note": "...",
        }
        """
        query = """
        mutation GiftCardCreate($input: GiftCardCreateInput!) {
          giftCardCreate(input: $input) {
            giftCard { id code displayCode }
            errors { field message }
          }
        }
        """
        variables = {"input": input_data or {}}
        data = self.graphql(query, variables)
        result = (data or {}).get("giftCardCreate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor giftCardCreate errors: {errors}")
        return result.get("giftCard")

    def gift_card_update(self, giftcard_id, input_data):
        """Update a gift card in Saleor and return the giftCard node."""
        query = """
        mutation GiftCardUpdate($id: ID!, $input: GiftCardUpdateInput!) {
          giftCardUpdate(id: $id, input: $input) {
            giftCard { id code displayCode }
            errors { field message }
          }
        }
        """
        variables = {"id": giftcard_id, "input": input_data or {}}
        data = self.graphql(query, variables)
        result = (data or {}).get("giftCardUpdate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor giftCardUpdate errors: {errors}")
        return result.get("giftCard")

    def gift_card_metadata_update(self, giftcard_id, metadata):
        """Update public metadata for a gift card via updateMetadata."""
        if not metadata:
            return True
        query = """
        mutation UpdateGiftCardMetadata($id: ID!, $input: [MetadataInput!]!) {
          updateMetadata(id: $id, input: $input) {
            item {
              ... on GiftCard {
                id
                metadata { key value }
              }
            }
            errors { field message }
          }
        }
        """
        variables = {"id": giftcard_id, "input": metadata}
        data = self.graphql(query, variables)
        result = (data or {}).get("updateMetadata") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor updateMetadata (gift card) errors: {errors}")
        return result.get("item") or True

    def gift_card_private_metadata_update(self, giftcard_id, private_metadata):
        """Update private metadata for a gift card via updatePrivateMetadata."""
        if not private_metadata:
            return True
        query = """
        mutation UpdateGiftCardPrivateMetadata($id: ID!, $input: [MetadataInput!]!) {
          updatePrivateMetadata(id: $id, input: $input) {
            item {
              ... on GiftCard {
                id
                privateMetadata { key value }
              }
            }
            errors { field message }
          }
        }
        """
        variables = {"id": giftcard_id, "input": private_metadata}
        data = self.graphql(query, variables)
        result = (data or {}).get("updatePrivateMetadata") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(
                f"Saleor updatePrivateMetadata (gift card) errors: {errors}"
            )
        return result.get("item") or True

    def product_type_metadata_update(self, product_type_id, metadata):
        """Update public metadata for a product type via updateMetadata."""
        if not metadata:
            return True
        query = """
        mutation UpdateProductTypeMetadata($id: ID!, $input: [MetadataInput!]!) {
            updateMetadata(id: $id, input: $input) {
            item {
                ... on ProductType {
                id
                }
            }
            errors {
                field
                message
            }
            }
        }
        """
        variables = {"id": product_type_id, "input": metadata}
        data = self.graphql(query, variables)
        result = (data or {}).get("updateMetadata") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor updateMetadata (product type) errors: {errors}")
        return result.get("item") or True

    def product_type_private_metadata_update(self, product_type_id, private_metadata):
        """Update private metadata for a product type via updatePrivateMetadata."""
        if not private_metadata:
            return True
        query = """
        mutation UpdateProductTypePrivateMetadata($id: ID!, $input: [MetadataInput!]!) {
          updatePrivateMetadata(id: $id, input: $input) {
            item {
              ... on ProductType {
                id
              }
            }
            errors {
              field
              message
            }
          }
        }
        """
        variables = {"id": product_type_id, "input": private_metadata}
        data = self.graphql(query, variables)
        result = (data or {}).get("updatePrivateMetadata") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(
                f"Saleor updatePrivateMetadata (product type) errors: {errors}"
            )
        return result.get("item") or True

    def tax_class_search_by_name(self, name, first=50):
        """Find a TaxClass by exact name."""
        query = """
        query TaxClasses($first: Int) {
          taxClasses(first: $first) {
            edges { node { id name countries { country { code } rate } } }
          }
        }
        """
        variables = {"first": int(first)}
        data = self.graphql(query, variables)
        edges = (((data or {}).get("taxClasses") or {}).get("edges")) or []
        exact = None
        for e in edges:
            node = e.get("node") or {}
            if node.get("name") == name:
                exact = node
                break
        return exact

    def tax_class_create(self, input_data):
        """Create a Tax Class."""
        query = """
        mutation TaxClassCreate($input: TaxClassCreateInput!) {
          taxClassCreate(input: $input) {
            taxClass { id name countries { country { code } rate } }
            errors { field message code }
          }
        }
        """
        variables = {"input": input_data or {}}
        data = self.graphql(query, variables)
        res = (data or {}).get("taxClassCreate") or {}
        errors = res.get("errors") or []
        if errors:
            raise Exception(f"Saleor taxClassCreate errors: {errors}")
        return res.get("taxClass")

    def tax_class_update(self, tax_class_id, input_data):
        query = """
        mutation TaxClassUpdate($id: ID!, $input: TaxClassUpdateInput!) {
          taxClassUpdate(id: $id, input: $input) {
            taxClass { id name countries { country { code } rate } }
            errors { field message code }
          }
        }
        """
        variables = {"id": tax_class_id, "input": input_data or {}}
        data = self.graphql(query, variables)
        res = (data or {}).get("taxClassUpdate") or {}
        errors = res.get("errors") or []
        if errors:
            raise Exception(f"Saleor taxClassUpdate errors: {errors}")
        return res.get("taxClass")

    # --- Attribute helpers ---
    def attribute_get_by_slug(self, slug):
        query = """
        query AttributeBySlug($slug: String!) {
          attribute(slug: $slug) { id slug }
        }
        """
        data = self.graphql(query, {"slug": slug})
        return data.get("attribute")

    def attribute_create(self, input_data):
        query = """
        mutation AttributeCreate($input: AttributeCreateInput!) {
          attributeCreate(input: $input) {
            attribute { id slug }
            errors { field message }
          }
        }
        """
        values = input_data.get("values") or []
        variables = {
            "input": {
                "name": input_data.get("name"),
                "slug": input_data.get("slug"),
                # Saleor requires a non-null type for attribute creation
                "type": "PRODUCT_TYPE",
                # Use DROPDOWN for simple selectable values
                "inputType": "DROPDOWN",
                "values": [{"name": v} for v in values],
            }
        }
        data = self.graphql(query, variables)
        result = data.get("attributeCreate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor attributeCreate errors: {errors}")
        return result.get("attribute")

    def attribute_update(self, attribute_id, input_data):
        query = """
        mutation AttributeUpdate($id: ID!, $input: AttributeUpdateInput!) {
          attributeUpdate(id: $id, input: $input) {
            attribute { id slug }
            errors { field message }
          }
        }
        """
        variables = {
            "id": attribute_id,
            "input": {
                "name": input_data.get("name"),
                "slug": input_data.get("slug"),
                # Do not send metadata/privateMetadata here;
                # not supported in this mutation
            },
        }
        data = self.graphql(query, variables)
        result = data.get("attributeUpdate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor attributeUpdate errors: {errors}")
        return result.get("attribute")

    def attribute_value_create(self, attribute_id, name):
        query = """
        mutation AttributeValueCreate($attribute: ID!, $name: String!) {
          attributeValueCreate(attribute: $attribute, input: {name: $name}) {
            attribute { id }
            errors { field message }
          }
        }
        """
        data = self.graphql(query, {"attribute": attribute_id, "name": name})
        result = data.get("attributeValueCreate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor attributeValueCreate errors: {errors}")
        return result.get("attribute")

    def channel_get_by_slug(self, slug):
        query = """
        query ChannelBySlug($slug: String!) {
          channel(slug: $slug) {
            id
            slug
            name
            isActive
            currencyCode
            defaultCountry { code }
          }
        }
        """
        data = self.graphql(query, {"slug": slug})
        return data.get("channel")

    def channel_get_by_id(self, channel_id):
        query = """
        query ChannelById($id: ID!) {
          channel(id: $id) {
            id
            slug
            name
            isActive
            currencyCode
            defaultCountry { code }
          }
        }
        """
        data = self.graphql(query, {"id": channel_id})
        return data.get("channel")

    def channel_create(self, input_data):
        query = """
        mutation ChannelCreate($input: ChannelCreateInput!) {
          channelCreate(input: $input) {
            channel { id slug name isActive currencyCode defaultCountry { code } }
            errors { field message code }
          }
        }
        """
        variables = {"input": input_data or {}}
        data = self.graphql(query, variables)
        res = (data or {}).get("channelCreate") or {}
        errors = res.get("errors") or []
        if errors:
            raise Exception(f"Saleor channelCreate errors: {errors}")
        return res.get("channel")

    def channel_update(self, channel_id, input_data):
        query = """
        mutation ChannelUpdate($id: ID!, $input: ChannelUpdateInput!) {
          channelUpdate(id: $id, input: $input) {
            channel { id slug name isActive defaultCountry { code } }
            errors { field message code }
          }
        }
        """
        variables = {"id": channel_id, "input": input_data or {}}
        data = self.graphql(query, variables)
        res = (data or {}).get("channelUpdate") or {}
        errors = res.get("errors") or []
        if errors:
            raise Exception(f"Saleor channelUpdate errors: {errors}")
        return res.get("channel")

    def tax_configuration_get_by_channel_id(self, channel_id):
        """Return TaxConfiguration node for a given channel ID, if any."""
        if not channel_id:
            return None
        query = """
        query TaxConfigurationByChannel($id: ID!) {
          channel(id: $id) {
            id
            taxConfiguration {
              id
              pricesEnteredWithTax
            }
          }
        }
        """
        data = self.graphql(query, {"id": channel_id})
        ch = (data or {}).get("channel") or {}
        return ch.get("taxConfiguration")

    def channel_tax_configuration_update(self, channel_id, prices_entered_with_tax):
        """Update tax configuration for a channel identified by its Saleor ID.

        Used by the Odoo connector to control pricesEnteredWithTax on
        Saleor channels so that behavior matches Odoo pricing semantics.
        """
        if not channel_id:
            return None
        cfg = self.tax_configuration_get_by_channel_id(channel_id)
        cfg_id = (cfg or {}).get("id")
        if not cfg_id:
            return None
        query = """
        mutation ChannelTaxConfigUpdate(
          $id: ID!,
          $pricesEnteredWithTax: Boolean!
        ) {
          taxConfigurationUpdate(
            id: $id,
            input: { pricesEnteredWithTax: $pricesEnteredWithTax }
          ) {
            taxConfiguration {
              id
              pricesEnteredWithTax
            }
            errors { field message code }
          }
        }
        """
        variables = {
            "id": cfg_id,
            "pricesEnteredWithTax": bool(prices_entered_with_tax),
        }
        data = self.graphql(query, variables)
        res = (data or {}).get("taxConfigurationUpdate") or {}
        errors = res.get("errors") or []
        if errors:
            raise Exception(f"Saleor taxConfigurationUpdate errors: {errors}")
        return res.get("taxConfiguration")

    def attribute_values_list(self, attribute_id):
        query = """
        query AttributeValues($id: ID!, $first: Int!) {
          attribute(id: $id) {
            id
            choices(first: $first) { edges { node { id name } } }
          }
        }
        """
        data = self.graphql(query, {"id": attribute_id, "first": 200})
        attr = data.get("attribute") or {}
        edges = ((attr.get("choices") or {}).get("edges")) or []
        return [e["node"]["name"] for e in edges]

    # --- Product mutations ---
    def product_create(self, input_data):
        query = """
        mutation ProductCreate($input: ProductCreateInput!) {
          productCreate(input: $input) {
            product { id slug }
            errors { field message }
          }
        }
        """
        variables = {
            "input": {
                "name": input_data.get("name"),
                "slug": input_data.get("slug"),
                "description": input_data.get("description"),
                "seo": input_data.get("seo") or {},
                "metadata": input_data.get("metadata") or [],
                "privateMetadata": input_data.get("privateMetadata") or [],
                "rating": input_data.get("rating"),
                "productType": input_data.get("productType"),
                "category": input_data.get("category"),
                "taxClass": input_data.get("taxClass"),
            }
        }
        data = self.graphql(query, variables)
        result = data.get("productCreate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor productCreate errors: {errors}")
        return result.get("product")

    def product_channel_listings(self, product_id):
        """Return list of current channel listings for a product.
        Each item: { channel: { id }, isPublished, publicationDate }
        """
        query = """
        query ProductChannels($id: ID!) {
          product(id: $id) {
            id
            channelListings {
              channel { id }
              isPublished
              publicationDate
            }
          }
        }
        """
        data = self.graphql(query, {"id": product_id})
        prod = (data or {}).get("product") or {}
        return prod.get("channelListings") or []

    def product_channel_listing_update(
        self, product_id, update_channels=None, remove_channels=None
    ):
        """Update channel listings for a product using delta.

        update_channels: list of dicts, e.g. {"channelId": ID, "isPublished": bool}
        remove_channels: list of channel IDs to remove
        """
        query = """
        mutation ProductChannelListingUpdate(
          $id: ID!, $input: ProductChannelListingUpdateInput!
        ) {
          productChannelListingUpdate(id: $id, input: $input) {
            product { id slug }
            errors { field message }
          }
        }
        """
        variables = {
            "id": product_id,
            "input": {
                "updateChannels": update_channels or [],
                "removeChannels": remove_channels or [],
            },
        }
        data = self.graphql(query, variables)
        result = data.get("productChannelListingUpdate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor productChannelListingUpdate errors: {errors}")
        return result.get("product")

    def product_update(self, product_id, input_data):
        query = """
        mutation ProductUpdate($id: ID!, $input: ProductInput!) {
          productUpdate(id: $id, input: $input) {
            product { id slug }
            errors { field message }
          }
        }
        """
        variables = {
            "id": product_id,
            "input": {
                "name": input_data.get("name"),
                "slug": input_data.get("slug"),
                "description": input_data.get("description"),
                "seo": input_data.get("seo") or {},
                "metadata": input_data.get("metadata") or [],
                "privateMetadata": input_data.get("privateMetadata") or [],
                "rating": input_data.get("rating"),
                "category": input_data.get("category"),
                "taxClass": input_data.get("taxClass"),
            },
        }
        data = self.graphql(query, variables)
        result = data.get("productUpdate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor productUpdate errors: {errors}")
        return result.get("product")

    def product_get_by_slug(self, slug):
        query = """
        query ProductBySlug($slug: String!) {
          product(slug: $slug) { id slug }
        }
        """
        data = self.graphql(query, {"slug": slug})
        return data.get("product")

    def product_media_create(
        self, product_id, filename, file_bytes, content_type="application/octet-stream"
    ):
        query = """
        mutation ProductMediaCreate($product: ID!, $image: Upload!, $alt: String) {
          productMediaCreate(input: { product: $product, image: $image, alt: $alt }) {
            media { id }
            errors { field message }
          }
        }
        """
        variables = {"product": product_id, "image": None, "alt": filename}
        files_map = {
            "0": (filename or "image", file_bytes, content_type, ["variables.image"])
        }
        data = self.graphql_multipart(query, variables, files_map)
        result = data.get("productMediaCreate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor productMediaCreate errors: {errors}")
        return result.get("media")

    def product_media_delete(self, media_id):
        """Delete a product media from Saleor."""
        query = """
        mutation ProductMediaDelete($id: ID!) {
            productMediaDelete(id: $id) {
                product {
                    id
                }
                errors {
                    field
                    message
                }
            }
        }
        """
        try:
            result = self.graphql(query, {"id": media_id})
            media_data = result.get("productMediaDelete") or {}
            errors = media_data.get("errors") or []
            if errors:
                _logger.error("Failed to delete product media %s: %s", media_id, errors)
                return False

            _logger.info("Successfully deleted product media %s", media_id)
            return True

        except Exception as e:
            _logger.error(
                "Error deleting product media %s: %s", media_id, str(e), exc_info=True
            )
            return False

    # --- Product Type helpers ---
    def product_type_search_by_name(self, name):
        """Return first ProductType by name search (case-insensitive)."""
        query = """
        query ProductTypes($first: Int!, $search: String) {
          productTypes(first: $first, filter: {search: $search}) {
            edges { node { id name } }
          }
        }
        """
        data = self.graphql(query, {"first": 5, "search": name})
        edges = (((data or {}).get("productTypes") or {}).get("edges")) or []
        return edges[0]["node"] if edges else None

    # --- Promotion helpers ---
    def promotion_get_by_id(self, promotion_id):
        """Get a Promotion by ID."""
        query = """
        query PromotionById($id: ID!) {
          promotion(id: $id) { id name }
        }
        """
        data = self.graphql(query, {"id": promotion_id})
        return (data or {}).get("promotion")

    def promotion_create(self, input_data):
        query = """
        mutation PromotionCreate($input: PromotionCreateInput!) {
          promotionCreate(input: $input) {
            promotion { id name }
            errors { field message }
          }
        }
        """
        variables = {"input": input_data or {}}
        data = self.graphql(query, variables)
        res = (data or {}).get("promotionCreate") or {}
        errors = res.get("errors") or []
        if errors:
            raise Exception(f"Saleor promotionCreate errors: {errors}")
        return res.get("promotion")

    def promotion_update(self, promotion_id, input_data):
        query = """
        mutation PromotionUpdate($id: ID!, $input: PromotionUpdateInput!) {
          promotionUpdate(id: $id, input: $input) {
            promotion { id name }
            errors { field message }
          }
        }
        """
        variables = {"id": promotion_id, "input": input_data or {}}
        data = self.graphql(query, variables)
        res = (data or {}).get("promotionUpdate") or {}
        errors = res.get("errors") or []
        if errors:
            raise Exception(f"Saleor promotionUpdate errors: {errors}")
        return res.get("promotion")

    def promotion_rules_list(self, promotion_id):
        """List rules for a promotion."""
        query = """
        query PromotionRules($id: ID!) {
          promotion(id: $id) {
            id
            rules { id name }
          }
        }
        """
        data = self.graphql(query, {"id": promotion_id})
        prom = (data or {}).get("promotion") or {}
        return (prom or {}).get("rules") or []

    def promotion_rule_create(self, promotion_id, input_data, channels=None):
        query = """
        mutation PromotionRuleCreate(
          $promotionId: ID!, $input: PromotionRuleCreateInput!
        ) {
          promotionRuleCreate(promotionId: $promotionId, input: $input) {
            promotionRule { id name }
            errors { field message }
          }
        }
        """
        # Merge channels into input if provided
        payload = dict(input_data or {})
        if channels:
            payload["channels"] = list(channels)
        variables = {"promotionId": promotion_id, "input": payload}
        data = self.graphql(query, variables)
        res = (data or {}).get("promotionRuleCreate") or {}
        errors = res.get("errors") or []
        if errors:
            raise Exception(f"Saleor promotionRuleCreate errors: {errors}")
        return res.get("promotionRule")

    def promotion_rule_update(
        self, rule_id, input_data, add_channels=None, remove_channels=None
    ):
        query = """
        mutation PromotionRuleUpdate($id: ID!, $input: PromotionRuleUpdateInput!) {
          promotionRuleUpdate(id: $id, input: $input) {
            promotionRule { id name }
            errors { field message }
          }
        }
        """
        # Merge channel delta into input if provided
        payload = dict(input_data or {})
        if add_channels:
            payload["addChannels"] = list(add_channels)
        if remove_channels:
            payload["removeChannels"] = list(remove_channels)
        variables = {"id": rule_id, "input": payload}
        data = self.graphql(query, variables)
        res = (data or {}).get("promotionRuleUpdate") or {}
        errors = res.get("errors") or []
        if errors:
            raise Exception(f"Saleor promotionRuleUpdate errors: {errors}")
        return res.get("promotionRule")

    def promotion_rule_delete(self, rule_id):
        query = """
        mutation PromotionRuleDelete($id: ID!) {
          promotionRuleDelete(id: $id) {
            errors { field message }
          }
        }
        """
        data = self.graphql(query, {"id": rule_id})
        res = (data or {}).get("promotionRuleDelete") or {}
        errors = res.get("errors") or []
        if errors:
            raise Exception(f"Saleor promotionRuleDelete errors: {errors}")
        return True

    def product_type_create(self, input_data):
        """Create ProductType with a flexible input payload."""
        query = """
        mutation ProductTypeCreate($input: ProductTypeInput!) {
          productTypeCreate(input: $input) {
            productType { id name }
            errors { field message }
          }
        }
        """
        variables = {
            "input": {k: v for k, v in (input_data or {}).items() if v is not None}
        }
        data = self.graphql(query, variables)
        result = (data or {}).get("productTypeCreate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor productTypeCreate errors: {errors}")
        return result.get("productType")

    def product_type_update(self, ptype_id, input_data):
        """Update ProductType by ID."""
        query = """
        mutation ProductTypeUpdate($id: ID!, $input: ProductTypeInput!) {
          productTypeUpdate(id: $id, input: $input) {
            productType { id name }
            errors { field message }
          }
        }
        """
        variables = {
            "id": ptype_id,
            "input": {k: v for k, v in (input_data or {}).items() if v is not None},
        }
        data = self.graphql(query, variables)
        result = (data or {}).get("productTypeUpdate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor productTypeUpdate errors: {errors}")
        return result.get("productType")

    # --- Product Variant helpers ---
    def product_variant_get_by_id(self, variant_id):
        """Fetch a product variant by ID from Saleor."""
        query = """
      query ProductVariant($id: ID!) {
        productVariant(id: $id) {
          id
          name
          sku
          product {
            id
            name
          }
          stocks {
            warehouse { id name }
            quantity
          }
        }
      }
      """
        data = self.graphql(query, {"id": variant_id})
        return data.get("productVariant")

    def product_variant_create(
        self, product_id, sku, name, attributes=None, weight=None
    ):
        """Create a product variant in Saleor."""
        query = """
        mutation ProductVariantCreate($input: ProductVariantCreateInput!) {
          productVariantCreate(input: $input) {
            productVariant {
              id
              sku
              name
            }
            errors {
              field
              message
            }
          }
        }
        """

        variables = {
            "input": {
                "product": product_id,
                "sku": sku,
                "name": name,
                "attributes": attributes or [],
                "trackInventory": True,
            }
        }
        # Include weight only if provided and positive
        try:
            if weight is not None:
                w = float(weight)
                if w > 0:
                    variables["input"]["weight"] = w
        except Exception as e:
            # Log and skip invalid weight to keep mutation robust
            _logger.debug(
                "product_variant_create: invalid weight '%s' for SKU %s: %s",
                weight,
                sku,
                e,
            )

        data = self.graphql(query, variables)
        result = data.get("productVariantCreate", {})

        if result.get("errors"):
            error_messages = [
                e.get("message", "Unknown error") for e in result["errors"]
            ]
            raise Exception(", ".join(error_messages))

        return result.get("productVariant")

    def product_variant_update(self, variant_id, payload):
        """Update an existing product variant in Saleor.

        Args:
            variant_id (str): The Saleor variant ID
            payload (dict): The update payload

        Returns:
            dict: The updated variant data
        """
        query = """
        mutation ProductVariantUpdate($id: ID!, $input: ProductVariantInput!) {
          productVariantUpdate(id: $id, input: $input) {
            productVariant {
              id
              sku
              name
            }
            errors {
              field
              message
            }
          }
        }
        """

        variables = {"id": variant_id, "input": payload}

        data = self.graphql(query, variables)
        result = data.get("productVariantUpdate", {})

        if result.get("errors"):
            error_messages = [
                e.get("message", "Unknown error") for e in result["errors"]
            ]
            raise Exception(", ".join(error_messages))

        return result.get("productVariant")

    def shipping_zone_create(self, input_data):
        query = """
        mutation ShippingZoneCreate($input: ShippingZoneCreateInput!) {
          shippingZoneCreate(input: $input) {
            shippingZone {
              id
              name
              description
              default
              countries { code }
              warehouses { id name }
              channels { id slug }
            }
            errors {
              field
              code
              message
              warehouses
              channels
            }
          }
        }
        """
        variables = {"input": input_data or {}}
        data = self.graphql(query, variables)
        result = data.get("shippingZoneCreate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor shippingZoneCreate errors: {errors}")
        zone = result.get("shippingZone")
        _logger.info("Saleor shipping_zone_create done: %s", zone)
        return zone

    def shipping_zone_update(self, zone_id, input_data):
        query = """
        mutation ShippingZoneUpdate($id: ID!, $input: ShippingZoneUpdateInput!) {
          shippingZoneUpdate(id: $id, input: $input) {
            shippingZone {
              id
              name
              description
              default
              countries { code }
              warehouses { id name }
              channels { id slug }
            }
            errors {
              field
              code
              message
              warehouses
              channels
            }
          }
        }
        """
        variables = {"id": zone_id, "input": input_data or {}}
        data = self.graphql(query, variables)
        result = data.get("shippingZoneUpdate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor shippingZoneUpdate errors: {errors}")
        zone = result.get("shippingZone")
        _logger.info("Saleor shipping_zone_update done: %s", zone)
        return zone

    def shipping_zone_get_by_id(self, zone_id):
        """Fetch a shipping zone strictly by ID (Relay ID)."""
        query = """
        query ShippingZoneById($id: ID!) {
          shippingZone(id: $id) {
            id
            name
            description
            default
            countries { code }
            warehouses { id name }
            channels { id slug }
          }
        }
        """
        data = self.graphql(query, {"id": zone_id})
        zone = data.get("shippingZone")
        return (zone and zone.get("id")) or None

    def shipping_method_create(self, zone_id, input_data):
        """Create a shipping method (price/weight based) within a shipping zone."""
        # Use the shippingZoneId approach which seems to be the correct way
        query = """
        mutation ShippingPriceCreate($input: ShippingPriceInput!) {
          shippingPriceCreate(input: $input) {
            shippingMethod {
              id
              name
              type
              minimumDeliveryDays
              maximumDeliveryDays
            }
            errors {
              field
              code
              message
            }
          }
        }
        """
        supported_fields = {
            "name",
            "type",
            "description",
            "minimumDeliveryDays",
            "maximumDeliveryDays",
            "minimumOrderWeight",
            "maximumOrderWeight",
            "taxClass",
        }
        input_payload = {
            key: value
            for key, value in (input_data or {}).items()
            if key in supported_fields
        }

        # Add the shipping zone ID - this seems to be required
        input_payload["shippingZone"] = zone_id

        variables = {"input": input_payload}
        _logger.debug("shipping_method_create variables: %s", variables)

        data = self.graphql(query, variables)
        result = data.get("shippingPriceCreate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor shippingPriceCreate errors: {errors}")

        method = result.get("shippingMethod")
        method_id = method.get("id") if method else None

        if method_id and input_data:
            try:
                # Handle postal code rules via update
                update_payload = {}
                if "inclusionType" in input_data or "addPostalCodeRules" in input_data:
                    if "inclusionType" in input_data:
                        update_payload["inclusionType"] = input_data["inclusionType"]
                    if "addPostalCodeRules" in input_data:
                        update_payload["addPostalCodeRules"] = input_data[
                            "addPostalCodeRules"
                        ]

                if update_payload:
                    self.shipping_method_update(method_id, update_payload)

                # Handle metadata separately using metadata update mutations
                if "metadata" in input_data and input_data["metadata"]:
                    self.shipping_method_metadata_update(
                        method_id, input_data["metadata"]
                    )

                if "privateMetadata" in input_data and input_data["privateMetadata"]:
                    self.shipping_method_private_metadata_update(
                        method_id, input_data["privateMetadata"]
                    )

            except Exception as e:
                _logger.warning(
                    "Failed to update shipping method %s with additional fields: %s",
                    method_id,
                    e,
                )

        _logger.info("Saleor shipping_method_create done: %s", method)
        return method

    # --- Warehouses ---
    def warehouse_create(self, input_data):
        """Create a Warehouse in Saleor.
        Expected minimal input: { name: str }
        """
        query = """
        mutation WarehouseCreate($input: WarehouseCreateInput!) {
          createWarehouse(input: $input) {
            warehouse { id name slug }
            errors { field code message }
          }
        }
        """
        variables = {"input": input_data or {}}
        data = self.graphql(query, variables)
        # The mutation is named createWarehouse; parse that key
        result = data.get("createWarehouse") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor warehouseCreate errors: {errors}")
        return result.get("warehouse")

    def warehouse_update(self, warehouse_id, input_data):
        """Update a Warehouse in Saleor by ID."""
        query = """
        mutation WarehouseUpdate($id: ID!, $input: WarehouseUpdateInput!) {
          updateWarehouse(id: $id, input: $input) {
            warehouse { id name slug }
            errors { field code message }
          }
        }
        """
        variables = {"id": warehouse_id, "input": input_data or {}}
        data = self.graphql(query, variables)
        # The mutation is named updateWarehouse; parse that key
        result = data.get("updateWarehouse") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor warehouseUpdate errors: {errors}")
        return result.get("warehouse")

    def warehouse_get_by_id(self, warehouse_id):
        """Fetch a Warehouse by its Relay ID from Saleor.

        Returns the warehouse dict on success, or None if not found.
        """
        query = """
        query WarehouseById($id: ID!) {
          warehouse(id: $id) {
            id
            name
            slug
          }
        }
        """
        variables = {"id": warehouse_id}
        data = self.graphql(query, variables)
        # For consistency with other helpers, return the dict or None
        return data.get("warehouse")

    def shipping_method_metadata_update(self, method_id, metadata):
        """Update metadata for a shipping method."""
        query = """
        mutation UpdateMetadata($id: ID!, $input: [MetadataInput!]!) {
          updateMetadata(id: $id, input: $input) {
            item {
              ... on ShippingMethodType {
                id
                metadata {
                  key
                  value
                }
              }
            }
            errors {
              field
              code
              message
            }
          }
        }
        """
        variables = {"id": method_id, "input": metadata}
        data = self.graphql(query, variables)
        result = data.get("updateMetadata") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor updateMetadata errors: {errors}")
        _logger.info(
            "Saleor shipping_method_metadata_update done for method %s", method_id
        )
        return result.get("item")

    def shipping_method_private_metadata_update(self, method_id, private_metadata):
        """Update private metadata for a shipping method."""
        query = """
        mutation UpdatePrivateMetadata($id: ID!, $input: [MetadataInput!]!) {
          updatePrivateMetadata(id: $id, input: $input) {
            item {
              ... on ShippingMethodType {
                id
                privateMetadata {
                  key
                  value
                }
              }
            }
            errors {
              field
              code
              message
            }
          }
        }
        """
        variables = {"id": method_id, "input": private_metadata}
        data = self.graphql(query, variables)
        result = data.get("updatePrivateMetadata") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor updatePrivateMetadata errors: {errors}")
        _logger.info(
            "Saleor shipping_method_private_metadata_update done for method %s",
            method_id,
        )
        return result.get("item")

    def shipping_method_update(self, method_id, input_data):
        """Update a shipping method (price/weight based)."""
        query = """
        mutation ShippingPriceUpdate($id: ID!, $input: ShippingPriceInput!) {
          shippingPriceUpdate(id: $id, input: $input) {
            shippingMethod {
              id
              name
              type
              minimumDeliveryDays
              maximumDeliveryDays
            }
            errors {
              field
              code
              message
            }
          }
        }
        """
        # Filter input_data to only include fields supported by ShippingPriceInput
        supported_fields = {
            "name",
            "description",
            "minimumDeliveryDays",
            "maximumDeliveryDays",
            "inclusionType",
            "addPostalCodeRules",
            "deletePostalCodeRules",
            "minimumOrderWeight",
            "maximumOrderWeight",
            "addProducts",
            "removeProducts",
            "taxClass",
        }
        input_payload = {
            key: value
            for key, value in (input_data or {}).items()
            if key in supported_fields
        }

        variables = {"id": method_id, "input": input_payload}
        data = self.graphql(query, variables)
        result = data.get("shippingPriceUpdate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor shippingPriceUpdate errors: {errors}")
        method = result.get("shippingMethod")
        _logger.info("Saleor shipping_method_update done: %s", method)
        return method

    def shipping_method_channel_listing_update(
        self, method_id, add_channels=None, remove_channels=None
    ):
        """Update channel listings for a shipping method."""
        query = """
        mutation ShippingMethodChannelListingUpdate(
            $id: ID!, $input: ShippingMethodChannelListingInput!
        ) {
          shippingMethodChannelListingUpdate(id: $id, input: $input) {
            shippingMethod {
              id
              name
              type
              minimumDeliveryDays
              maximumDeliveryDays
            }
            errors {
              field
              code
              message
            }
          }
        }
        """
        input_obj = {}
        if add_channels:
            input_obj["addChannels"] = add_channels
        if remove_channels:
            input_obj["removeChannels"] = remove_channels

        variables = {"id": method_id, "input": input_obj}
        data = self.graphql(query, variables)
        result = data.get("shippingMethodChannelListingUpdate") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(
                f"Saleor shippingMethodChannelListingUpdate errors: {errors}"
            )
        method = result.get("shippingMethod")
        _logger.info("Saleor shipping_method_channel_listing_update done: %s", method)
        return method

    def shipping_method_get_postal_codes(self, method_id):
        """Get existing postal code rules for a shipping method
        by searching through shipping zones."""
        try:
            # Get all shipping zones and search for the method
            zones_query = """
            query ShippingZones($first: Int!) {
              shippingZones(first: $first) {
                edges {
                  node {
                    id
                    shippingMethods {
                      id
                      postalCodeRules {
                        id
                        start
                        end
                        inclusionType
                      }
                    }
                  }
                }
              }
            }
            """
            zones_data = self.graphql(zones_query, {"first": 100})
            edges = (((zones_data or {}).get("shippingZones") or {}).get("edges")) or []

            # Search for the method in all zones
            for edge in edges:
                zone = edge.get("node", {})
                methods = zone.get("shippingMethods", [])
                for method in methods:
                    if method.get("id") == method_id:
                        postal_rules = method.get("postalCodeRules", [])
                        _logger.debug(
                            "Found %d existing postal code rules for method %s",
                            len(postal_rules),
                            method_id,
                        )
                        return postal_rules

            _logger.debug("No postal code rules found for method %s", method_id)
            return []

        except Exception as e:
            _logger.warning(
                "Failed to get postal codes for method %s: %s", method_id, e
            )
            return []

    def shipping_method_get_excluded_products(self, method_id):
        """Get existing excluded products for a shipping method
        by searching through shipping zones."""
        try:
            # First, try to get excluded products using the documented API
            zones_query = """
            query ShippingZones($first: Int!) {
              shippingZones(first: $first) {
                edges {
                  node {
                    id
                    shippingMethods {
                      id
                      excludedProducts(first: 100) {
                        edges {
                          node {
                            id
                            name
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
            """
            zones_data = self.graphql(zones_query, {"first": 100})
            edges = (((zones_data or {}).get("shippingZones") or {}).get("edges")) or []

            # Search for the method in all zones
            for edge in edges:
                zone = edge.get("node", {})
                methods = zone.get("shippingMethods", [])
                for method in methods:
                    if method.get("id") == method_id:
                        excluded_products_data = method.get("excludedProducts", {})
                        excluded_edges = excluded_products_data.get("edges", [])
                        excluded_products = [
                            edge.get("node", {}) for edge in excluded_edges
                        ]
                        _logger.debug(
                            "Found %d existing excluded products for method %s",
                            len(excluded_products),
                            method_id,
                        )
                        return excluded_products

            _logger.debug("No excluded products found for method %s", method_id)
            return []

        except Exception as e:
            _logger.warning(
                "Failed to get excluded products for method %s: %s",
                method_id,
                e,
            )
            # Return empty list if excludedProducts field is not supported
            return []

    def shipping_method_sync_postal_codes(
        self, method_id, desired_rules, inclusion_type="INCLUDE"
    ):
        """Sync postal code rules for a shipping method
        by comparing existing vs desired rules."""
        try:
            # Get existing postal codes from Saleor
            existing_rules = self.shipping_method_get_postal_codes(method_id)

            # Create mappings for comparison
            def normalize_rule(rule):
                return (rule.get("start", ""), rule.get("end", ""))

            # Map existing rules: (start, end) -> rule_id
            existing_map = {
                normalize_rule(rule): rule.get("id") for rule in existing_rules
            }
            existing_set = set(existing_map.keys())
            desired_set = {(rule["start"], rule["end"]) for rule in desired_rules}

            # Calculate what to add and remove
            to_add = desired_set - existing_set
            to_remove = existing_set - desired_set

            _logger.debug(
                "Postal code sync for method %s: %d to add, %d to remove",
                method_id,
                len(to_add),
                len(to_remove),
            )

            # Prepare update payload
            update_payload = {}

            if to_add:
                add_rules = [{"start": start, "end": end} for start, end in to_add]
                update_payload["addPostalCodeRules"] = add_rules
                update_payload["inclusionType"] = inclusion_type
                _logger.info(
                    "Adding %d postal code rules to method %s",
                    len(add_rules),
                    method_id,
                )

            if to_remove:
                # Use postal code rule IDs for deletion, not the postal code data
                remove_rule_ids = [
                    existing_map[(start, end)]
                    for start, end in to_remove
                    if existing_map.get((start, end))
                ]
                if remove_rule_ids:
                    update_payload["deletePostalCodeRules"] = remove_rule_ids
                    _logger.info(
                        "Removing %d postal code rules from method %s (IDs: %s)",
                        len(remove_rule_ids),
                        method_id,
                        remove_rule_ids,
                    )

            # Apply changes if needed
            if update_payload:
                self.shipping_method_update(method_id, update_payload)
                _logger.info(
                    "Successfully synced postal codes for method %s", method_id
                )
            else:
                _logger.debug("No postal code changes needed for method %s", method_id)

        except Exception as e:
            _logger.warning(
                "Failed to sync postal codes for method %s: %s", method_id, e
            )
            raise

    def shipping_method_sync_excluded_products(self, method_id, desired_product_ids):
        """Sync excluded products for a shipping method
        by comparing existing vs desired products."""
        try:
            # Get existing excluded products from Saleor
            existing_products = self.shipping_method_get_excluded_products(method_id)

            # Create sets for comparison using Saleor product IDs
            existing_product_ids = {
                product.get("id") for product in existing_products if product.get("id")
            }
            desired_product_ids_set = set(desired_product_ids or [])

            # Calculate what to add and remove
            to_add = desired_product_ids_set - existing_product_ids
            to_remove = existing_product_ids - desired_product_ids_set

            _logger.debug(
                "Excluded products sync for method %s: %d to add, %d to remove",
                method_id,
                len(to_add),
                len(to_remove),
            )

            # Prepare update payload
            update_payload = {}

            if to_add:
                # Add products to exclusion list
                add_product_ids = list(to_add)
                update_payload["addProducts"] = add_product_ids
                _logger.info(
                    "Adding %d excluded products to method %s (IDs: %s)",
                    len(add_product_ids),
                    method_id,
                    add_product_ids,
                )

            if to_remove:
                # Remove products from exclusion list
                remove_product_ids = list(to_remove)
                update_payload["removeProducts"] = remove_product_ids
                _logger.info(
                    "Removing %d excluded products from method %s (IDs: %s)",
                    len(remove_product_ids),
                    method_id,
                    remove_product_ids,
                )

            # Apply changes using dedicated mutations
            if to_add:
                try:
                    add_product_ids = list(to_add)
                    self.shipping_method_exclude_products(method_id, add_product_ids)
                    _logger.info(
                        "Successfully added %d excluded products to method %s",
                        len(add_product_ids),
                        method_id,
                    )
                except Exception as e:
                    _logger.warning(
                        "Failed to add excluded products to method %s: %s", method_id, e
                    )

            if to_remove:
                try:
                    remove_product_ids = list(to_remove)
                    self.shipping_method_remove_excluded_products(
                        method_id, remove_product_ids
                    )
                    _logger.info(
                        "Successfully removed %d excluded products from method %s",
                        len(remove_product_ids),
                        method_id,
                    )
                except Exception as e:
                    _logger.warning(
                        "Failed to remove excluded products from method %s: %s",
                        method_id,
                        e,
                    )

            if not to_add and not to_remove:
                _logger.debug(
                    "No excluded products changes needed for method %s", method_id
                )

        except Exception as e:
            _logger.warning(
                "Failed to sync excluded products for method %s: %s", method_id, e
            )
            raise

    def shipping_method_exclude_products(self, method_id, product_ids):
        """Add products to shipping method exclusion
        list using shippingPriceExcludeProducts mutation."""
        query = """
        mutation ShippingMethodExcludeProducts(
          $id: ID!, $input: ShippingPriceExcludeProductsInput!
        ) {
          shippingPriceExcludeProducts(id: $id, input: $input) {
            shippingMethod {
              id
              name
            }
            errors {
              field
              code
              message
            }
          }
        }
        """
        variables = {"id": method_id, "input": {"products": product_ids}}
        data = self.graphql(query, variables)
        result = data.get("shippingPriceExcludeProducts") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor shippingPriceExcludeProducts errors: {errors}")
        method = result.get("shippingMethod")
        _logger.info("Saleor shipping_method_exclude_products done: %s", method)
        return method

    def shipping_method_remove_excluded_products(self, method_id, product_ids):
        """Remove products from shipping method
        exclusion list using shippingPriceRemoveProductFromExclude mutation."""
        query = """
        mutation ShippingMethodRemoveExcludedProducts($id: ID!, $products: [ID!]!) {
          shippingPriceRemoveProductFromExclude(id: $id, products: $products) {
            shippingMethod {
              id
              name
            }
            errors {
              field
              code
              message
            }
          }
        }
        """
        variables = {"id": method_id, "products": product_ids}
        data = self.graphql(query, variables)
        result = data.get("shippingPriceRemoveProductFromExclude") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(
                f"Saleor shippingPriceRemoveProductFromExclude errors: {errors}"
            )
        method = result.get("shippingMethod")
        _logger.info("Saleor shipping_method_remove_excluded_products done: %s", method)
        return method

    def shipping_zone_metadata_update(self, zone_id, metadata):
        """Update metadata for a shipping zone using updateMetadata mutation."""
        query = """
        mutation UpdateShippingZoneMetadata($id: ID!, $input: [MetadataInput!]!) {
          updateMetadata(id: $id, input: $input) {
            item {
              ... on ShippingZone {
                id
                name
              }
            }
            errors {
              field
              code
              message
            }
          }
        }
        """
        variables = {"id": zone_id, "input": metadata}
        data = self.graphql(query, variables)
        result = data.get("updateMetadata") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(f"Saleor updateMetadata (shipping zone) errors: {errors}")
        item = result.get("item")
        _logger.info("Saleor shipping_zone_metadata_update done: %s", item)
        return item

    def shipping_zone_private_metadata_update(self, zone_id, private_metadata):
        """Update private metadata for a shipping zone
        using updatePrivateMetadata mutation."""
        query = """
        mutation UpdateShippingZonePrivateMetadata(
          $id: ID!, $input: [MetadataInput!]!
        ) {
          updatePrivateMetadata(id: $id, input: $input) {
            item {
              ... on ShippingZone {
                id
                name
              }
            }
            errors {
              field
              code
              message
            }
          }
        }
        """
        variables = {"id": zone_id, "input": private_metadata}
        data = self.graphql(query, variables)
        result = data.get("updatePrivateMetadata") or {}
        errors = result.get("errors") or []
        if errors:
            raise Exception(
                f"Saleor updatePrivateMetadata (shipping zone) errors: {errors}"
            )
        item = result.get("item")
        _logger.info("Saleor shipping_zone_private_metadata_update done: %s", item)
        return item

    def shipping_method_get_by_id(self, method_id):
        """Fetch a shipping method by its Relay ID by scanning shipping zones."""
        # 1) Get shipping zone IDs (basic page of zones)
        zones_query = """
        query ShippingZones($first: Int!) {
          shippingZones(first: $first) {
            edges { node { id } }
          }
        }
        """
        zones_data = self.graphql(zones_query, {"first": 100})
        edges = (((zones_data or {}).get("shippingZones") or {}).get("edges")) or []
        zone_ids = [
            edge.get("node", {}).get("id")
            for edge in edges
            if edge.get("node", {}).get("id")
        ]
        _logger.debug(
            "Discovered %s shipping zones while searching for method %s",
            len(zone_ids),
            method_id,
        )

        # 2) For each zone, fetch shipping methods and search for the ID
        zone_query = """
        query ZoneMethods($id: ID!) {
          shippingZone(id: $id) {
            id
            shippingMethods { id }
          }
        }
        """
        for zid in zone_ids:
            try:
                zdata = self.graphql(zone_query, {"id": zid})
                zone = zdata.get("shippingZone") or {}
                methods = zone.get("shippingMethods") or []
                for m in methods:
                    if m.get("id") == method_id:
                        _logger.info(
                            "shipping_method_get_by_id found in zone %s: %s",
                            zid,
                            method_id,
                        )
                        return True
            except Exception as e:
                _logger.warning(
                    "Failed fetching shipping methods for zone %s: %s", zid, e
                )
                continue
        return False
