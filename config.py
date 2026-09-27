"Define app-level configurations."

# Default directories
OUTPUTS_DIR: str = "outputs/"
SVG_TEMPLATE_FILE: str = "templates/base_template.svg.tpl"

# -----------------------------------------------------------------------
# Rose Customizations

# Sizes and proportions (see README for more detailed info)
ROSE_ARM_H: float = 0.25
ROSE_ARM_W: float = 0.125

# Colors
MAIN_ROSE_COLOR: str = "E0A84A"
SECONDARY_ROSE_COLOR: str | None = None
