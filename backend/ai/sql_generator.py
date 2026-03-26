"""
AI SQL Generator — Rule-based natural language to SQL engine.

Uses schema-aware template matching to convert user questions
into valid SQL queries. No LLM required — works entirely offline
with pattern matching and keyword extraction.
"""

import re
from typing import Optional


# ── SQL patterns mapped from natural-language keywords ────────────────

AGGREGATION_KEYWORDS = {
    "total": "SUM",
    "sum": "SUM",
    "average": "AVG",
    "avg": "AVG",
    "mean": "AVG",
    "count": "COUNT",
    "how many": "COUNT",
    "number of": "COUNT",
    "maximum": "MAX",
    "max": "MAX",
    "highest": "MAX",
    "largest": "MAX",
    "top": "MAX",
    "minimum": "MIN",
    "min": "MIN",
    "lowest": "MIN",
    "smallest": "MIN",
}

COMPARISON_PATTERNS = [
    (r"greater than (\d+\.?\d*)", ">"),
    (r"more than (\d+\.?\d*)", ">"),
    (r"above (\d+\.?\d*)", ">"),
    (r"over (\d+\.?\d*)", ">"),
    (r"exceeds? (\d+\.?\d*)", ">"),
    (r"less than (\d+\.?\d*)", "<"),
    (r"below (\d+\.?\d*)", "<"),
    (r"under (\d+\.?\d*)", "<"),
    (r"equals? (\d+\.?\d*)", "="),
    (r"equal to (\d+\.?\d*)", "="),
    (r"at least (\d+\.?\d*)", ">="),
    (r"at most (\d+\.?\d*)", "<="),
]

TIME_KEYWORDS = {
    "daily": "day",
    "weekly": "week",
    "monthly": "month",
    "yearly": "year",
    "annually": "year",
    "quarterly": "quarter",
    "by day": "day",
    "by week": "week",
    "by month": "month",
    "by year": "year",
    "per day": "day",
    "per week": "week",
    "per month": "month",
    "per year": "year",
}

ORDER_KEYWORDS = {
    "top": ("DESC", True),
    "highest": ("DESC", False),
    "largest": ("DESC", False),
    "most": ("DESC", False),
    "best": ("DESC", False),
    "bottom": ("ASC", True),
    "lowest": ("ASC", False),
    "smallest": ("ASC", False),
    "least": ("ASC", False),
    "worst": ("ASC", False),
}


class SQLGenerator:
    """Generates SQL queries from natural language questions using schema-aware pattern matching."""

    def generate(self, question: str, table_name: str, schema: list, sample_columns: list) -> str:
        """
        Generate a SQL query from a natural language question.

        Args:
            question: The user's natural language question.
            table_name: The Athena table name.
            schema: List of dicts with 'name' and 'type' keys.
            sample_columns: List of column name strings.

        Returns:
            A valid SQL SELECT statement.
        """
        q = question.lower().strip()
        col_map = {col.lower(): col for col in sample_columns}
        type_map = {s["name"].lower(): s["type"] for s in schema}

        # Identify referenced columns
        mentioned_cols = [col for col_lower, col in col_map.items() if col_lower in q]

        # Detect aggregation
        agg_func = None
        for keyword, func in AGGREGATION_KEYWORDS.items():
            if keyword in q:
                agg_func = func
                break

        # Detect numeric columns for aggregation targets
        numeric_cols = [
            s["name"] for s in schema
            if s["type"] in ("int64", "float64", "integer", "float", "BIGINT", "DOUBLE")
        ]

        # Detect grouping columns (non-numeric mentioned cols)
        group_cols = [c for c in mentioned_cols if type_map.get(c.lower()) in ("object", "string", "STRING")]

        # Detect date/time columns
        date_cols = [
            s["name"] for s in schema
            if any(hint in s["name"].lower() for hint in ("date", "time", "timestamp", "created", "updated"))
            or s["type"] in ("datetime64", "TIMESTAMP")
        ]

        # Detect time granularity
        time_granularity = None
        for keyword, granularity in TIME_KEYWORDS.items():
            if keyword in q:
                time_granularity = granularity
                break

        # Detect ordering
        order_direction = None
        wants_limit = False
        for keyword, (direction, limit_flag) in ORDER_KEYWORDS.items():
            if keyword in q:
                order_direction = direction
                wants_limit = limit_flag
                break

        # Extract limit number
        limit_n = None
        limit_match = re.search(r"top (\d+)|bottom (\d+)|first (\d+)|last (\d+)|(\d+) (?:results|rows|records)", q)
        if limit_match:
            limit_n = int(next(g for g in limit_match.groups() if g))

        # Detect WHERE conditions
        where_clauses = self._extract_where_clauses(q, schema, col_map)

        # Build the query
        sql = self._build_query(
            table_name=table_name,
            all_columns=sample_columns,
            mentioned_cols=mentioned_cols,
            numeric_cols=numeric_cols,
            group_cols=group_cols,
            date_cols=date_cols,
            agg_func=agg_func,
            time_granularity=time_granularity,
            order_direction=order_direction,
            limit_n=limit_n,
            wants_limit=wants_limit,
            where_clauses=where_clauses,
        )

        return sql

    def _extract_where_clauses(self, question: str, schema: list, col_map: dict) -> list:
        """Extract WHERE clause conditions from the question."""
        clauses = []

        # Numeric comparisons
        for pattern, operator in COMPARISON_PATTERNS:
            match = re.search(pattern, question)
            if match:
                value = match.group(1)
                numeric_cols = [
                    s["name"] for s in schema
                    if s["type"] in ("int64", "float64", "integer", "float")
                    and s["name"].lower() in question
                ]
                if numeric_cols:
                    clauses.append(f"`{numeric_cols[0]}` {operator} {value}")

        # String equality (e.g., "where category is Electronics")
        for col_lower, col in col_map.items():
            pattern = rf"(?:where|for|in|with) {re.escape(col_lower)} (?:is|=|equals?) ['\"]?(\w+)['\"]?"
            match = re.search(pattern, question)
            if match:
                clauses.append(f"`{col}` = '{match.group(1)}'")

        return clauses

    def _build_query(
        self,
        table_name: str,
        all_columns: list,
        mentioned_cols: list,
        numeric_cols: list,
        group_cols: list,
        date_cols: list,
        agg_func: Optional[str],
        time_granularity: Optional[str],
        order_direction: Optional[str],
        limit_n: Optional[int],
        wants_limit: bool,
        where_clauses: list,
    ) -> str:
        """Assemble the final SQL query from extracted components."""

        # Determine SELECT clause
        if agg_func:
            agg_col = numeric_cols[0] if numeric_cols else "*"
            if agg_func == "COUNT":
                agg_expr = "COUNT(*)"
            else:
                agg_expr = f"{agg_func}(`{agg_col}`)"

            if time_granularity and date_cols:
                date_col = date_cols[0]
                select_parts = [
                    f"DATE_TRUNC('{time_granularity}', CAST(`{date_col}` AS TIMESTAMP)) AS period",
                    f"{agg_expr} AS value",
                ]
                group_by = "GROUP BY 1"
                order_by = "ORDER BY 1"
            elif group_cols:
                select_parts = [f"`{group_cols[0]}`", f"{agg_expr} AS value"]
                group_by = f"GROUP BY `{group_cols[0]}`"
                order_by = f"ORDER BY value {order_direction or 'DESC'}"
            else:
                select_parts = [agg_expr + " AS value"]
                group_by = ""
                order_by = ""
        else:
            if mentioned_cols:
                select_parts = [f"`{c}`" for c in mentioned_cols[:5]]
            else:
                select_parts = [f"`{c}`" for c in all_columns[:6]]
            group_by = ""
            if order_direction and mentioned_cols:
                order_by = f"ORDER BY `{mentioned_cols[0]}` {order_direction}"
            else:
                order_by = ""

        # Assemble
        select_clause = ", ".join(select_parts)
        where_clause = " AND ".join(where_clauses) if where_clauses else ""
        limit_clause = f"LIMIT {limit_n}" if limit_n else ("LIMIT 100" if not agg_func else "")

        parts = [f"SELECT {select_clause}", f"FROM `{table_name}`"]
        if where_clause:
            parts.append(f"WHERE {where_clause}")
        if group_by:
            parts.append(group_by)
        if order_by:
            parts.append(order_by)
        if limit_clause:
            parts.append(limit_clause)

        return "\n".join(parts)
