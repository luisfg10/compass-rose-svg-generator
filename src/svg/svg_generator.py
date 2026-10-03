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
            rose_arm_h: float = ROSE_ARM_H,
            rose_arm_w: float = ROSE_ARM_W,
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
        rose_arm_h: float
            The 'h' parameter for the rose arm, expressed as a factor
            of the rose's radius (see README for more info).
            Must be between 0 and 1.
        rose_arm_w: float
            The 'w' parameter for the rose arm, expressed as a factor
            of the rose's radius (see README for more info).
            Must be between 0 and 1.
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
        # Input consistency checks
        if not isinstance(rose_radius, int) or rose_radius < 0:
            raise ValueError(
                "Invalid value provided for `rose_radius`."
            )
        if not isinstance(main_rose_color, str) or len(main_rose_color) == 0:
            raise ValueError(
                "Invalid value provided for `main_rose_color`."
            )
        rose_arm_factors = [rose_arm_h, rose_arm_w]
        for factor in rose_arm_factors:
            if not isinstance(factor, float) or factor <= 0 or factor > 1:
                raise ValueError(
                    "Invalid value provided for either "
                    "`rose_arm_h` or `rose_arm_w`."
                )

        # Save SVG colors
        self.colors = {
            "main": main_rose_color,
            "secondary": secondary_rose_color
        }

        # Save relevant SVG positional data
        svg_side_len = int(rose_radius * 2)
        self.measurements = {
            "arm_len": rose_radius,
            "size": (svg_side_len, svg_side_len),
            "center": (rose_radius, rose_radius),
            "h": rose_arm_h,
            "w": rose_arm_w
        }
