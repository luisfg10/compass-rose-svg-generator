from config import (
    BASE_SVG_TEMPLATE_DIR,
    MAIN_ROSE_COLOR,
    SECONDARY_ROSE_COLOR,
    ROSE_ARM_H,
    ROSE_ARM_W
)

class CompassRoseSVGGenerator:
    """Utility class for generating compass rose SVG code."""

    def __init__(
            self,
            rose_radius: int,
            main_rose_color: str = MAIN_ROSE_COLOR,
            secondary_rose_color: str | None = SECONDARY_ROSE_COLOR
    ) -> None:
        """
        Initiallize the CompassRoseSVGGenerator class.

        Parameters
        ----------
        rose_radius: int
            The radius for the rose, or equivalently, the length
            of the N-S-E-W arms of the rose.
        
        main_rose_color: str
            A hex or other valor color code to use as the main color
            for the compass rose. This color will be used for the rose's
            outline, as well as for alternatively filling out the polygons
            inside.
        secondary_rose_color: str | None
            Optional secondary color to fill the rose's alternative leaf
            sides. Leave empty to make the rose transparent and take in its
            background's color.
        

        """
        # Sanity checks
        if not isinstance(rose_radius, int) or rose_radius < 0:
            raise ValueError(
                "Invalid value provided for `rose_radius`."
            )
        if not isinstance(main_rose_color, str) or len(main_rose_color) == 0:
            raise ValueError(
                "Invalid value provided for `main_rose_color`."
            )

        # Save SVG colors
        self.colors = {
            "main": main_rose_color,
            "secondary": secondary_rose_color
        }

        # Save relevant SVG positional data
        svg_side_len = int(rose_radius * 2)
        self.measurements = {
            "size": (svg_side_len, svg_side_len),
            "center": (rose_radius, rose_radius)
        }
