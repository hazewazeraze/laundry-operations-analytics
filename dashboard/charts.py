"""Shared Altair chart helpers — one visual language across all pages.

Colours are picked to stay readable on both light and dark Streamlit
themes: mid-tone fills for marks, theme-aware text for value labels.
"""

import altair as alt
import pandas as pd
import streamlit as st

PRIMARY = "#4C9BE8"  # dashboard blue
ACCENT = "#D95F4F"  # emphasis / weak-link red
POSITIVE = "#3ECF8E"  # matches the Supported verdict
HIGHLIGHT = "#FFC94F"  # matches the Inconclusive verdict
MUTED = "#9AA4B2"

SEGMENT_COLORS = {
    "Premium Customer": PRIMARY,
    "High-Value Occasional": POSITIVE,
    "Regular Customer": HIGHLIGHT,
    "Low Frequency Customer": MUTED,
}


def _text_color() -> str:
    return "#E9EEF5" if st.get_option("theme.base") == "dark" else "#1B2733"


def bars_v(
    data: pd.DataFrame,
    x: str,
    y: str,
    *,
    title_y: str | None = None,
    fmt: str = ".1f",
    tooltip_fmt: str | None = None,
    height: int = 300,
    highlight: str | None = None,
    labels: bool = True,
    y_max: float | None = None,
    sort: list | None = None,
):
    """Vertical bars with rounded tops, value labels and an optional
    highlighted category (painted in ACCENT)."""
    domain_max = y_max if y_max is not None else float(data[y].max()) * 1.15
    y_scale = alt.Scale(domain=[0, domain_max])
    color = (
        alt.condition(
            alt.datum[x] == highlight,
            alt.value(ACCENT),
            alt.value(PRIMARY),
        )
        if highlight
        else alt.value(PRIMARY)
    )
    bars = (
        alt.Chart(data)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X(f"{x}:N", title=None, sort=sort),
            y=alt.Y(f"{y}:Q", title=title_y, scale=y_scale),
            color=color,
            tooltip=[
                alt.Tooltip(f"{x}:N"),
                alt.Tooltip(f"{y}:Q", format=tooltip_fmt or fmt),
            ],
        )
        .properties(height=height)
    )
    if not labels:
        return bars
    text = (
        alt.Chart(data)
        .mark_text(
            align="center",
            baseline="bottom",
            dy=-4,
            color=_text_color(),
            fontSize=11,
        )
        .encode(
            x=alt.X(f"{x}:N", sort=sort),
            y=alt.Y(f"{y}:Q", scale=y_scale),
            text=alt.Text(f"{y}:Q", format=fmt),
        )
        .properties(height=height)
    )
    return bars + text


def bars_h(
    data: pd.DataFrame,
    y: str,
    x: str,
    *,
    title_x: str | None = None,
    fmt: str = ".1f",
    height: int = 300,
    labels: bool = True,
    color_field: str | None = None,
    x_max: float | None = None,
    sort: list | None = None,
):
    """Horizontal bars; colour by category when color_field maps to
    SEGMENT_COLORS, otherwise a single PRIMARY fill."""
    domain_max = x_max if x_max is not None else float(data[x].max()) * 1.15
    x_scale = alt.Scale(domain=[0, domain_max])
    if color_field and set(data[color_field].unique()) <= set(SEGMENT_COLORS):
        keys = [k for k in SEGMENT_COLORS if k in set(data[color_field].unique())]
        color_enc = alt.Color(
            f"{color_field}:N",
            scale=alt.Scale(domain=keys, range=[SEGMENT_COLORS[k] for k in keys]),
            legend=None,
        )
    else:
        color_enc = alt.value(PRIMARY)
    bars = (
        alt.Chart(data)
        .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
        .encode(
            y=alt.Y(f"{y}:N", title=None, sort=sort),
            x=alt.X(f"{x}:Q", title=title_x, scale=x_scale),
            color=color_enc,
            tooltip=[
                alt.Tooltip(f"{y}:N"),
                alt.Tooltip(f"{x}:Q", format=fmt),
            ],
        )
        .properties(height=height)
    )
    if not labels:
        return bars
    text = (
        alt.Chart(data)
        .mark_text(
            align="left",
            baseline="middle",
            dx=4,
            color=_text_color(),
            fontSize=11,
        )
        .encode(
            y=alt.Y(f"{y}:N", sort=sort),
            x=alt.X(f"{x}:Q", scale=x_scale),
            text=alt.Text(f"{x}:Q", format=fmt),
        )
        .properties(height=height)
    )
    return bars + text


def line_area(
    data: pd.DataFrame,
    x: str,
    y: str,
    *,
    title_y: str | None = None,
    height: int = 300,
    fmt: str = ",.0f",
):
    """Time line with a soft filled area underneath."""
    base = alt.Chart(data)
    area = base.mark_area(color=PRIMARY, opacity=0.16).encode(
        x=alt.X(f"{x}:T", title=None),
        y=alt.Y(f"{y}:Q", title=title_y),
        y2=alt.value(0),
        tooltip=[
            alt.Tooltip(f"{x}:T", format="%d %b %Y"),
            alt.Tooltip(f"{y}:Q", format=fmt),
        ],
    )
    line = base.mark_line(color=PRIMARY, strokeWidth=2).encode(
        x=alt.X(f"{x}:T"),
        y=alt.Y(f"{y}:Q"),
    )
    return (area + line).properties(height=height)


def scatter_segments(
    data: pd.DataFrame,
    *,
    x: str,
    y: str,
    title_x: str | None = None,
    title_y: str | None = None,
    height: int = 300,
):
    """Customer scatter coloured by segment, with a legend and tooltips."""
    present = [k for k in SEGMENT_COLORS if k in set(data["segment"].unique())]
    return (
        alt.Chart(data)
        .mark_point(filled=True, size=64, opacity=0.9)
        .encode(
            x=alt.X(f"{x}:Q", title=title_x),
            y=alt.Y(f"{y}:Q", title=title_y),
            color=alt.Color(
                "segment:N",
                scale=alt.Scale(
                    domain=present, range=[SEGMENT_COLORS[k] for k in present]
                ),
                legend=alt.Legend(title="Segment", symbolSize=90),
            ),
            tooltip=[
                alt.Tooltip("customer_id:N", title="Customer"),
                alt.Tooltip(f"{x}:Q", title=title_x, format=",.0f"),
                alt.Tooltip(f"{y}:Q", title=title_y, format=",.0f"),
                alt.Tooltip("segment:N", title="Segment"),
            ],
        )
        .properties(height=height)
    )
