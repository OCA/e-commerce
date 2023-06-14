import re

from psycopg2 import sql

from odoo import api, models
from odoo.osv.expression import AND, OR, get_unaccent_wrapper


class Website(models.Model):
    _inherit = "website"

    @api.model
    def _get_similar_records(self, model, fields, search, found_already):
        domain: list[str | tuple] = []
        model_fields = [[(f, "%", search)] for f in fields]
        domain += OR(model_fields)
        if found_already:
            domain += AND([[("id", "not in", found_already.ids)]])
        found = model.search(domain)
        return found, len(found)

    def _search_with_fuzzy(
        self, search_type, search, limit, order, options
    ) -> (int, list, int):
        if search:
            search = search.strip()
        total_count, all_results, fuzzy_term = super()._search_with_fuzzy(
            search_type, search, limit, order, options
        )
        search_details = self._search_get_details(search_type, order, options)
        if search and " " in search and options.get("allowFuzzy"):
            for search_detail in search_details:
                str_model = search_detail["model"]
                model = self.env[str_model]
                if search_detail.get("requires_sudo"):
                    model = model.sudo()
                search_fields = search_detail["search_fields"]
                found_already = [r for r in all_results if r["model"] == str_model][0][
                    "results"
                ]
                results, count = self._get_similar_records(
                    model, search_fields, search, found_already
                )
                all_results_filtered = [
                    r for r in all_results if r["model"] == str_model
                ]
                if all_results_filtered:
                    all_results_section = all_results_filtered[0]
                    all_results_section["results"] += results
                    all_results_section["count"] += count
                    total_count += count
                else:
                    search_detail["results"] = results
                    total_count += count
                    search_detail["count"] = count
                    all_results.append(search_detail)

        return total_count, all_results, fuzzy_term

    def _direct_postgres_similarity(self, word1, word2):
        if abs(len(word1) - len(word2)) >= 100:
            return 0
        query = sql.SQL("SELECT similarity({word1}, {word2})").format(
            word1=sql.Placeholder(), word2=sql.Placeholder()
        )
        self.env.cr.execute(query, (word1, word2))
        score = self.env.cr.fetchall()
        return score[0][0]

    def _search_find_fuzzy_term(
        self, search_details, search, limit=1000, word_list=None
    ) -> str:
        best_word: str = super()._search_find_fuzzy_term(
            search_details, search, limit, word_list
        )
        best_score: int = 0
        if (
            self.env.registry.has_trigram
            and " " in search
            and len(search) >= 4
            and len(re.findall(r"\d", search)) / len(search) < 0.8
        ):
            enumerated_words = self._trigram_enumerate_words_w_spaces(
                search_details, search, limit
            )
            for word in word_list or enumerated_words:
                search = search.lower()
                # sql.tool.similarity doesn't work as we want it to
                # So we use postgres pg_trgm.similarity() directly
                similarity = self._direct_postgres_similarity(search, word)
                # if multi-word is more similar to "traditional" best word return it
                if similarity > best_score:
                    best_score = similarity
                    best_word = word

        return best_word

    # because of the way website._trigram_enumerate_words() is structured
    # a big chunk of the original function has to be copied as it is
    # in order to make it work for multi-word keyword
    # this version, like the original one, tries to find the closest result
    # that will be suggested to the user under the search bar
    def _trigram_enumerate_words_w_spaces(self, search_details, search, limit):
        lang = self.env.lang or "en_US"
        self.env.cr.execute(sql.SQL("SELECT show_limit()"))
        db_similarity = self.env.cr.fetchall()[0][0]

        for search_detail in search_details:
            # save model and fields, check if sudo is required, copy domain
            model_name, fields = search_detail["model"], search_detail["search_fields"]
            model = self.env[model_name]
            if search_detail.get("requires_sudo"):
                model = model.sudo()
            domain = search_detail["base_domain"].copy()
            # create set with the required fields
            fields = set(fields).intersection(model._fields)

            unaccent = get_unaccent_wrapper(self.env.cr)
            # data structure with all inherited {inherits_model_fname: {table: _, fname: _}}
            inherits_fields = {
                inherits_model_fname: {
                    "table": self.env[inherits_model_name]._table,
                    "fname": inherits_field_name,
                }
                for inherits_model_name, inherits_field_name in model._inherits.items()
                for inherits_model_fname in self.env[inherits_model_name]._fields.keys()
                if inherits_model_fname in fields
            }
            similarities = []
            for field in fields:
                # Field might belong to another model (`inherits` mechanism)
                table = (
                    inherits_fields[field]["table"]
                    if field in inherits_fields
                    else model._table
                )
                similarities.append(
                    sql.SQL("word_similarity({search}, {field})").format(
                        search=unaccent(sql.Placeholder("search")),
                        field=unaccent(
                            sql.SQL("{table}.{field}").format(
                                table=sql.Identifier(table), field=sql.Identifier(field)
                            )
                        )
                        if not model._fields[field].translate
                        else unaccent(
                            # selected language if exists, otherwise use default en_US
                            sql.SQL(
                                "COALESCE({table}.{field}->>{lang}, {table}.{field}->>'en_US')"
                            ).format(
                                table=sql.Identifier(table),
                                field=sql.Identifier(field),
                                lang=sql.Literal(lang),
                            )
                        ),
                    )
                )

            best_similarity = sql.SQL("GREATEST({similarities})").format(
                similarities=sql.SQL(", ").join(similarities)
            )

            from_clause = sql.SQL("FROM {table}").format(
                table=sql.Identifier(model._table)
            )
            # Specific handling for fields being actually part of another model
            # through the `inherits` mechanism.
            for table_to_join in {
                field["table"]: field["fname"] for field in inherits_fields.values()
            }.items():  # Removes duplicate inherits model
                from_clause = sql.SQL(
                    """
                    {from_clause}
                    LEFT JOIN {inherits_table} ON {table}.{inherits_field} = {inherits_table}.id
                """
                ).format(
                    from_clause=from_clause,
                    table=sql.Identifier(model._table),
                    inherits_table=sql.Identifier(table_to_join[0]),
                    inherits_field=sql.Identifier(table_to_join[1]),
                )
            query = sql.SQL(
                """
                SELECT {table}.id, {best_similarity} AS _best_similarity
                {from_clause}
                ORDER BY _best_similarity desc
                LIMIT 1000
            """
            ).format(
                table=sql.Identifier(model._table),
                best_similarity=best_similarity,
                from_clause=from_clause,
            )
            self.env.cr.execute(query, {"search": search})
            ids = {
                row[0]
                for row in self.env.cr.fetchall()
                if row[1] and row[1] >= db_similarity
            }
            domain.append([("id", "in", list(ids))])
            domain = AND(domain)
            records = model.search_read(domain, fields, limit=limit)

            for record in records:
                for _, value in record.items():
                    if isinstance(value, str):
                        value = value.lower()
                        yield value
