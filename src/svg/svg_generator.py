from config import (
    MAIN_ROSE_COLOR,
    SECONDARY_ROSE_COLOR,
    ROSE_ARM_H,
    ROSE_ARM_W
)
from src.linear_algebra import TwoDimArray


class CompassRoseSVGGenerator:
    """
    Utility class containing the core logic for drawing compass
    rose SVGs based on input parameters, as well as fetching and
    formatting SVG files, and creating new ones.

    Notes
    -----
    TODO: Would be nice to generalize for n levels of arm geometry
    without explicitly coding for level parameters.
    TODO: Increase level of flexibility with the generated shapes:
    allow user to specify how many arms to generate for first level
    (normally it's 4, for N-S-W-E) but there's no reason this can't
    change.
    """
    def __init__(self) -> None:
        """Initialize an instance of the CompassRoseSVGGenerator class."""
        

    @staticmethod
    def compute_1st_level_base_arm(
            l: int | float,
            *,
            h: float,
            w: float,
            main_color: str,
            secondary_color: str | None = None
    ) -> list[dict[str, TwoDimArray | str | None]]:
        """
        Solve for the 'N' arm of the first level of the compass
        rose, which is made up of two halves: one on the left and
        another on the right. Assumes coordinates start at (0, 0).

        Parameters
        ----------
        l: int | float
            Arm length for the compass rose.
        h: int | float
            Base edge height for the rose, expressed as a factor of l.
        w: int | float
            Base edge width for the rose, expressed as a factor of l.
        main_color: str
            Hex or other valid color code to use as the main fill color
            for the SVG.
        secondary_color: str | None = None
            Hex or other valid color code to use as the main fill color
            for the SVG. If not provided the secondary color is not filled
            and is instead left as transparent.

        Returns
        -------
        list[dict[str, TwoDimArray | str | None]
            List where each element represents the metadata for an arm half:
            its geometry (represented as a TwoDimArray) + its fill.
        """
        # Pass h and w to full values
        full_h = h * l
        full_w = w * l

        # Store geomtry objects as TwoDimArrays
        left_geom = TwoDimArray([
            [0, 0],
            [-full_w, full_h],
            [0, l]
        ])
        right_geom = TwoDimArray([
            [0, 0],
            [full_w, full_h],  # only change to left_geom is the sign here
            [0, l]
        ])

        # Return a list of dicts with metadata for each half
        result = [
            {
                "geom": left_geom,
                "fill": main_color
            },
            {
                "geom": right_geom,
                "fill": secondary_color
            }
        ]
        return result

    @staticmethod
    def build_full_rose_level(
            initial_arm_metadata: list[dict[str, TwoDimArray | str | None]],
            *,
            n_arms: int,
            inplace: bool = False
    ) -> list[dict[str, TwoDimArray | str | None]]:
        """
        Get the metadata for an initial arm with two halves and use it to
        populate the other arm halves based on the number of arms to have in
        total for the level.

        Parameters
        ----------
        initial_arm_metadata: list[dict[str, TwoDimArray | str | None]]
            List where each element represents the metadata for an arm half:
            its geometry + its fill (see output from `compute_1st_level_base_arm`
            for more context).
        n_arms: int
            The number of arms to generate for the level, including the initial
            arm. The code generates the metadata for the (n_arms - 1) missing
            arms by leveraging the TwoDimArray.rotate() method. Arms are spaced
            out evenly.
        inplace: bool = False
            Whether to write to the original object or to a new one in memory.

        Returns
        -------
        list[dict[str, TwoDimArray | str | None]]
            New list where each element represents the metadata for an arm half:
            its geometry (represented as a TwoDimArray) + its fill.
        """
        # Input Validity checks
        if (
            not isinstance(initial_arm_metadata, list)
            or len(initial_arm_metadata) != 2
            or any(not isinstance(x, dict) for x in initial_arm_metadata)
        ):
            raise ValueError(
                "Expected a list of two elements, where each element "
                "is a dict containing the metadata for an arm half. "
                f"Got {initial_arm_metadata}."
            )

        # Init return object
        if inplace:
            full_arms = initial_arm_metadata  # points to the same object in memory
        else:
            full_arms = initial_arm_metadata.copy()  # points to independent object

        # Solve for rotation value
        rotation_degrees = 360 / n_arms

        # Get arm halves
        left_half_ref = initial_arm_metadata[0]
        right_half_ref = initial_arm_metadata[1]

        # Build new arms iteratively
        for turn in range(rotation_degrees, 360, rotation_degrees):  # start, stop, step
            # Append new left
            new_left_half_geom = left_half_ref["geom"].rotate(turn)
            full_arms.append({
                "geom": new_left_half_geom,
                "fill": left_half_ref["fill"]
            })
            # Append new right
            new_right_half_geom = right_half_ref["geom"].rotate(turn)
            full_arms.append({
                "geom": new_right_half_geom,
                "fill": right_half_ref["fill"]
            })

        return full_arms

    @staticmethod
    def recenter_rose(
        rose_radius: int | float,
        rose_metadata: list[dict[str, TwoDimArray | str | None]],
        inplace: bool = False
    ) -> list[dict[str, TwoDimArray | str | None]]:
        """
        Re-center the coordinates for the rose's geometry based on
        the dimensions for the SVG.

        Coordinates for the rose are initially computed assuming a center
        on (0, 0), whereas SVGs start on (0, 0) in the top left corner and
        increase in value down and to the right, which is why this process
        is needed.

        Parameters
        ----------
        rose_radius: int | float
            The length of a rose arm. The full size of the SVG is assumed to
            be two times this.
        rose_metadata: list[dict[str, TwoDimArray | str | None]]
            The metadata for the rose arms. Does not check how many arms are
            there and assumes they have expected structure. See
            `compute_1st_level_base_arm` for more context on expected schema.
        inplace: bool = False
        """
        # Init return object
        if inplace:
            new_metadata = rose_metadata  # points to the same object in memory
        else:
            new_metadata = rose_metadata.copy()  # points to independent object

        new_center = (rose_radius, rose_radius)
        for element in new_metadata:
            element["geom"] = element["geom"].translate(new_center)

        return new_metadata

    @staticmethod
    def translate_rose_metadata_to_svg(
        rose_metadata: list[dict[str, TwoDimArray | str | None]] 
    ) -> str:
        """
        Translates a list of rose metadata into a string ready to be
        formatted into an SVG template.
        Assumes rose metadata is provided as exemplified in
        `compute_1st_level_base_arm`.
        """

    def write_svg() -> None:
        """
        Assumes placeholders are saved with $placeholder, not {placeholder}
        in order to avoid collisions with native SVG/CSS syntax. 
        """
        raise NotImplementedError

    def run(
            self,
            rose_radius: int,
            rose_arm_h: float = ROSE_ARM_H,
            rose_arm_w: float = ROSE_ARM_W,
            main_color: str = MAIN_ROSE_COLOR,
            secondary_color: str | None = SECONDARY_ROSE_COLOR
    ) -> None:
        """
        Main callable for creating and saving an SVG file with
        specified parameters.

        Parameters
        ----------
        rose_radius: int
            The radius for the rose, i.e., the length
            of the N-S-E-W arms of the rose.
        rose_arm_h: float
            The 'h' parameter for the rose arm, expressed as a factor
            of the rose's radius (see README for more info).
            Must be between 0 and 1.
        rose_arm_w: float
            The 'w' parameter for the rose arm, expressed as a factor
            of the rose's radius (see README for more info).
            Must be between 0 and 1.
        main_color: str
            A hex or other valid color code to use as the main color
            for the rose. This will be used for the rose's outline, as well
            as for the fill in the arms' left sides.
        secondary_color: str | None
            Optional secondary color to fill the rose's right arm side.
            If not provided, it's left empty and transparent to background.
        """
        # -----------------------------------------------------------------------
        # Input consistency checks

        if not isinstance(rose_radius, int) or rose_radius < 0:
            raise ValueError(
                "Invalid value provided for `rose_radius`."
            )
        if not isinstance(main_color, str) or len(main_color) == 0:
            raise ValueError(
                "Invalid value provided for `main_color`."
            )
        if (
            not isinstance(secondary_color, str)
            or len(secondary_color) == 0
        ):
            secondary_color = None

        rose_arm_factors = [rose_arm_h, rose_arm_w]
        for factor in rose_arm_factors:
            if not isinstance(factor, float) or factor <= 0 or factor > 1:
                raise ValueError(
                    "Invalid value provided for either "
                    "`rose_arm_h` or `rose_arm_w`."
                )

        # -----------------------------------------------------------------------
        # Build rose's first level

        # Get metadata for 'N' arm
        first_arm_metadata = self.compute_1st_level_base_arm(
            l=rose_radius,
            h=rose_arm_h,
            w=rose_arm_w,
            main_color=main_color,
            secondary_color=secondary_color
        )

        # Use rotation to build the other three arms
        full_arm_metadata = self.build_full_rose_level(
            first_arm_metadata,
            n_arms=4
        )

        # Re-center arm coordinates for SVG