"""Custom template tags and filters for academics app."""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key.

    Usage: {{ dict|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def contrast_text_color(bg_color):
    """Calculate contrasting text color (black or white) for a background color.

    Uses WCAG relative luminance formula to determine readability.

    Usage: {{ tag.color|contrast_text_color }}

    Args:
        bg_color: Hex color string (e.g., "#FF5733" or "FF5733")

    Returns:
        "#000000" for light backgrounds, "#ffffff" for dark backgrounds
    """
    if not bg_color:
        return "#ffffff"

    # Remove # if present
    hex_color = bg_color.lstrip("#")

    # Handle short hex format (#FFF -> #FFFFFF)
    if len(hex_color) == 3:
        hex_color = "".join([c * 2 for c in hex_color])

    # Validate hex color
    if len(hex_color) != 6:
        return "#ffffff"

    try:
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # Calculate relative luminance (WCAG formula)
        # Weights green more heavily as human eye is more sensitive to it
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255

        # Return black for light backgrounds, white for dark backgrounds
        return "#000000" if luminance > 0.5 else "#ffffff"
    except (ValueError, IndexError):
        # If parsing fails, default to white
        return "#ffffff"


@register.inclusion_tag("academics/partials/tag_badge.html")
def tag_badge(tag, size="md", clickable=False, link_to_detail=False):
    """Render a tag badge with automatic contrast.

    Usage:
        {% tag_badge tag %}
        {% tag_badge tag size="sm" %}
        {% tag_badge tag clickable=True %}
        {% tag_badge tag link_to_detail=True %}

    Args:
        tag: Tag model instance
        size: Badge size - "sm", "md", or "lg" (default: "md")
        clickable: Add pointer cursor (default: False)
        link_to_detail: Wrap in link to tag detail page (default: False)

    Returns:
        Rendered badge HTML with proper contrast
    """
    text_color = contrast_text_color(tag.color)

    # Size mappings
    size_classes = {
        "sm": "badge-sm",
        "md": "",
        "lg": "badge-lg",
    }

    return {
        "tag": tag,
        "text_color": text_color,
        "size_class": size_classes.get(size, ""),
        "clickable": clickable,
        "link_to_detail": link_to_detail,
    }
