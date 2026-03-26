"""
AI Chart Recommender — Heuristic-based chart type selection.

Analyzes query results and the original question to recommend
the best chart type for visualization.
"""


CHART_TYPE_KEYWORDS = {
    "trend": "line",
    "over time": "line",
    "timeline": "line",
    "growth": "line",
    "daily": "line",
    "weekly": "line",
    "monthly": "line",
    "yearly": "line",
    "compare": "bar",
    "comparison": "bar",
    "by category": "bar",
    "by region": "bar",
    "breakdown": "bar",
    "distribution": "bar",
    "proportion": "pie",
    "percentage": "pie",
    "share": "pie",
    "ratio": "pie",
    "makeup": "pie",
    "composition": "pie",
    "scatter": "scatter",
    "correlation": "scatter",
    "relationship": "scatter",
}


class ChartRecommender:
    """Recommends chart types based on query results and question context."""

    def recommend(self, question: str, columns: list, results: list) -> tuple[str, dict]:
        """
        Recommend a chart type and configuration.

        Returns:
            Tuple of (chart_type, chart_config).
        """
        q = question.lower()

        # 1. Keyword-based detection
        for keyword, chart_type in CHART_TYPE_KEYWORDS.items():
            if keyword in q:
                return chart_type, self._build_config(chart_type, columns, results)

        # 2. Heuristic-based detection
        if len(columns) == 1:
            return "metric", self._build_config("metric", columns, results)

        if len(results) == 1 and len(columns) <= 2:
            return "metric", self._build_config("metric", columns, results)

        has_date = any(
            hint in col.lower()
            for col in columns
            for hint in ("date", "time", "period", "month", "year", "day", "week")
        )

        if has_date and len(columns) == 2:
            return "line", self._build_config("line", columns, results)

        if len(results) <= 8 and len(columns) == 2:
            return "pie", self._build_config("pie", columns, results)

        if len(columns) == 2:
            return "bar", self._build_config("bar", columns, results)

        if len(columns) >= 3:
            return "bar", self._build_config("bar", columns, results)

        return "table", self._build_config("table", columns, results)

    def _build_config(self, chart_type: str, columns: list, results: list) -> dict:
        """Build chart configuration for the frontend."""
        if chart_type == "metric":
            value = results[0][columns[-1]] if results else "N/A"
            return {
                "title": columns[-1] if columns else "Result",
                "value": value,
            }

        if chart_type in ("line", "bar", "scatter"):
            x_key = columns[0]
            y_keys = columns[1:3]
            return {
                "xKey": x_key,
                "yKeys": y_keys,
                "data": results[:100],
            }

        if chart_type == "pie":
            return {
                "nameKey": columns[0],
                "valueKey": columns[1] if len(columns) > 1 else columns[0],
                "data": results[:20],
            }

        # Table fallback
        return {"columns": columns, "data": results[:100]}
