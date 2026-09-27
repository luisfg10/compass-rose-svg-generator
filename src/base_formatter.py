class BaseTemplateFormatter:
    """
    Utility class for fetching and formatting SVG templates and outputting
    SVG files.

    Assumes placeholders are saved with $placeholder, not {placeholder}
    in order to avoid collisions with native SVG/CSS syntax.    
    """
