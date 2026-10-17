"""
SpaceY Intelligence - Modern Professional Design System & UI Components
Clean white theme, high-contrast professional typography (Plus Jakarta Sans & JetBrains Mono),
differentiated component accents, and high-level gradient vector logo badges.
Guarantees clean HTML rendering without markdown code-block artifacts.
"""

from typing import Optional, Dict
import streamlit as st

# Vector SVG definitions for high-level gradient badges (viewBox="0 0 24 24")
SVG_ICONS: Dict[str, str] = {
    "rocket": '<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09zM12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-3.95 11a22.35 22.35 0 0 1-3.05 2zM9 12l2 2M15 6l3 3"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "compass": '<circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    "flask": '<path d="M10 2v7.31L4.65 19.3A2 2 0 0 0 6.37 22h11.26a2 2 0 0 0 1.72-2.7L14 9.31V2h-4zM8.5 2h7"/>',
    "cpu": '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/>',
    "brain": '<path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2.04zM14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2.04z"/>',
    "dollar": '<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    "book": '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
    "chart": '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
    "database": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>',
    "check": '<polyline points="20 6 9 17 4 12"/>',
    "alert": '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
    "activity": '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    "search": '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    "layers": '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
    "sliders": '<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/>',
    "award": '<circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/>',
}

# Linear gradient color stops for logo badges
GRADIENT_PALETTES: Dict[str, Dict[str, str]] = {
    "blue": {
        "bg": "linear-gradient(135deg, #2563EB 0%, #0284C7 50%, #38BDF8 100%)",
        "shadow": "rgba(37, 99, 235, 0.28)",
        "pill_bg": "#EFF6FF",
        "pill_text": "#1D4ED8",
        "pill_border": "#BFDBFE",
    },
    "emerald": {
        "bg": "linear-gradient(135deg, #059669 0%, #10B981 50%, #34D399 100%)",
        "shadow": "rgba(5, 150, 105, 0.28)",
        "pill_bg": "#ECFDF5",
        "pill_text": "#047857",
        "pill_border": "#A7F3D0",
    },
    "purple": {
        "bg": "linear-gradient(135deg, #7C3AED 0%, #8B5CF6 50%, #C084FC 100%)",
        "shadow": "rgba(124, 58, 237, 0.28)",
        "pill_bg": "#F5F3FF",
        "pill_text": "#6D28D9",
        "pill_border": "#DDD6FE",
    },
    "amber": {
        "bg": "linear-gradient(135deg, #D97706 0%, #F59E0B 50%, #FBBF24 100%)",
        "shadow": "rgba(217, 119, 6, 0.28)",
        "pill_bg": "#FFFBEB",
        "pill_text": "#B45309",
        "pill_border": "#FDE68A",
    },
    "cyan": {
        "bg": "linear-gradient(135deg, #0891B2 0%, #06B6D4 50%, #22D3EE 100%)",
        "shadow": "rgba(8, 145, 178, 0.28)",
        "pill_bg": "#ECFEFF",
        "pill_text": "#0E7490",
        "pill_border": "#A5F3FC",
    },
    "rose": {
        "bg": "linear-gradient(135deg, #DC2626 0%, #EF4444 50%, #F87171 100%)",
        "shadow": "rgba(220, 38, 38, 0.28)",
        "pill_bg": "#FEF2F2",
        "pill_text": "#B91C1C",
        "pill_border": "#FECACA",
    },
    "slate": {
        "bg": "linear-gradient(135deg, #334155 0%, #475569 50%, #64748B 100%)",
        "shadow": "rgba(51, 65, 85, 0.25)",
        "pill_bg": "#F8FAFC",
        "pill_text": "#334155",
        "pill_border": "#CBD5E1",
    },
}


def clean_html(html_str: str) -> str:
    """
    Strips all leading and trailing whitespace from every line to ensure
    CommonMark markdown parsers NEVER interpret HTML as a preformatted code block.
    """
    lines = [line.strip() for line in html_str.strip().splitlines() if line.strip()]
    return "".join(lines)


def get_gradient_icon_html(icon_name: str = "rocket", size: int = 34, variant: str = "blue") -> str:
    """Generates an unindented HTML snippet for a high-level vector gradient logo badge."""
    icon_svg = SVG_ICONS.get(icon_name, SVG_ICONS["rocket"])
    palette = GRADIENT_PALETTES.get(variant, GRADIENT_PALETTES["blue"])
    icon_size = max(16, int(size * 0.52))

    return (
        f'<span style="display:inline-flex;align-items:center;justify-content:center;'
        f'width:{size}px;height:{size}px;border-radius:{int(size * 0.28)}px;'
        f'background:{palette["bg"]};box-shadow:0 4px 12px {palette["shadow"]};'
        f'color:#FFFFFF;vertical-align:middle;flex-shrink:0;margin-right:12px;">'
        f'<svg width="{icon_size}" height="{icon_size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        f'style="display:block;">{icon_svg}</svg></span>'
    )


def get_gradient_pill_html(text: str, variant: str = "blue") -> str:
    """Renders a styled category pill/badge with soft background and crisp border."""
    palette = GRADIENT_PALETTES.get(variant, GRADIENT_PALETTES["blue"])
    return (
        f'<span style="display:inline-block;background-color:{palette["pill_bg"]};'
        f'color:{palette["pill_text"]};border:1px solid {palette["pill_border"]};'
        f'padding:4px 12px;border-radius:9999px;font-family:\'Plus Jakarta Sans\',sans-serif;'
        f'font-size:0.75rem;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;">'
        f'{text}</span>'
    )


def render_page_header(
    title: str,
    subtitle: str,
    badge_text: str = "MISSION INTELLIGENCE",
    icon: str = "rocket",
    variant: str = "blue",
):
    """Renders a top page header featuring a high-level gradient logo badge and typography."""
    icon_html = get_gradient_icon_html(icon_name=icon, size=46, variant=variant)
    pill_html = get_gradient_pill_html(text=badge_text, variant=variant)

    raw_html = f"""
    <div style="margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid #E2E8F0;">
    <div style="margin-bottom:8px;">{pill_html}</div>
    <div style="display:flex;align-items:center;margin-top:4px;">
    {icon_html}
    <h1 style="margin:0;font-family:'Plus Jakarta Sans',sans-serif;font-size:2.15rem;font-weight:800;letter-spacing:-0.025em;color:#0F172A;line-height:1.2;">{title}</h1>
    </div>
    <p style="margin-top:8px;margin-bottom:0;margin-left:58px;font-family:'Plus Jakarta Sans',sans-serif;font-size:1.0rem;color:#64748B;font-weight:400;line-height:1.5;">{subtitle}</p>
    </div>
    """
    st.markdown(clean_html(raw_html), unsafe_allow_html=True)


def render_section_header(
    title: str,
    subtitle: Optional[str] = None,
    icon: str = "target",
    variant: str = "blue",
    badge: Optional[str] = None,
):
    """Renders a standardized section header with a gradient vector icon and clean typography."""
    icon_html = get_gradient_icon_html(icon_name=icon, size=32, variant=variant)
    badge_html = f" {get_gradient_pill_html(badge, variant)}" if badge else ""
    sub_html = f'<p style="margin:4px 0 0 44px;color:#64748B;font-size:0.88rem;">{subtitle}</p>' if subtitle else ""

    raw_html = f"""
    <div style="margin-top:24px;margin-bottom:14px;">
    <div style="display:flex;align-items:center;">
    {icon_html}
    <h3 style="margin:0;font-family:'Plus Jakarta Sans',sans-serif;font-size:1.3rem;font-weight:700;letter-spacing:-0.015em;color:#0F172A;">{title}</h3>
    {badge_html}
    </div>
    {sub_html}
    </div>
    """
    st.markdown(clean_html(raw_html), unsafe_allow_html=True)


def render_callout(message_html: str, variant: str = "blue"):
    """Renders a styled callout box without markdown indentation issues."""
    palette = GRADIENT_PALETTES.get(variant, GRADIENT_PALETTES["blue"])
    raw_html = f"""
    <div style="background:{palette['pill_bg']};border:1px solid {palette['pill_border']};border-left:4px solid {palette['pill_text']};border-radius:8px;padding:14px 18px;margin-bottom:16px;color:#0F172A;font-family:'Plus Jakarta Sans',sans-serif;">
    {message_html}
    </div>
    """
    st.markdown(clean_html(raw_html), unsafe_allow_html=True)


def render_card(body_html: str, title: Optional[str] = None, border_left_color: Optional[str] = None):
    """Renders a clean white card container."""
    border_style = f"border-left: 4px solid {border_left_color};" if border_left_color else ""
    title_html = f'<div style="font-family:\'Plus Jakarta Sans\',sans-serif;font-size:0.85rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:#2563EB;margin-bottom:8px;">{title}</div>' if title else ""
    raw_html = f"""
    <div style="background:#FFFFFF;border:1px solid #E2E8F0;{border_style}border-radius:12px;padding:20px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,0.04);">
    {title_html}
    {body_html}
    </div>
    """
    st.markdown(clean_html(raw_html), unsafe_allow_html=True)


def apply_spacey_theme():
    """Applies clean white background, modern Google fonts, and differentiated color tokens."""
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* Global Base */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    .stApp {
        background-color: #FFFFFF;
        color: #0F172A;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 1px solid #E2E8F0 !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stSidebarNav"] span {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        color: #334155 !important;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #0F172A !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }

    /* Metric Cards - Multi-line wrapping and crisp alignment */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        min-height: 110px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #CBD5E1 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
    }
    div[data-testid="stMetricLabel"] {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
        line-height: 1.25 !important;
    }
    div[data-testid="stMetricLabel"] p {
        color: #64748B !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
        margin: 0 !important;
        white-space: normal !important;
        line-height: 1.25 !important;
    }
    div[data-testid="stMetricValue"] {
        color: #0F172A !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 800 !important;
        font-size: 1.65rem !important;
        letter-spacing: -0.02em !important;
        white-space: nowrap !important;
    }

    /* Telemetry Cards */
    .telemetry-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
        transition: all 0.2s ease;
    }
    .telemetry-card:hover {
        border-color: #CBD5E1;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
    }

    .telemetry-title {
        color: #2563EB;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 8px;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        padding: 9px 18px !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%) !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4) !important;
        transform: translateY(-1px);
    }

    /* Tables */
    div[data-testid="stDataFrame"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        color: #64748B !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #2563EB !important;
        border-bottom-color: #2563EB !important;
    }

    /* Dividers */
    hr {
        border-color: #E2E8F0 !important;
        margin: 20px 0 !important;
    }
    </style>
    """
    st.markdown(clean_html(custom_css), unsafe_allow_html=True)
