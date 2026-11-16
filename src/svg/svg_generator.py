from pathlib import Path
from string import Template

from config import SVG_TEMPLATE_FILE, SVG_OUTPUT_FILENAME, OUTPUTS_DIR
from src.linear_algebra import TwoDimArray
from src.utils.utils import convert_deg_to_rad


class CompassRoseSVGGenerator:
    """
    Utility class containing the core logic for drawing compass
    rose SVGs based on input parameters, as well as fetching and
    formatting SVG files, and creating new ones.

    Notes
    -----
    TODO: Allow for building a second rose blades level on top
    of the first one.
    TODO: Would be nice to generalize for n levels of blade geometry
    without explicitly coding for each level.
    """
    def __init__(
            self,
            svg_template_file: str = SVG_TEMPLATE_FILE,
            outputs_dir: str = OUTPUTS_DIR
    ) -> None:
        """
        Initialize an instance of the CompassRoseSVGGenerator class.

        Parameters
        ----------
        svg_template_file: str
            The path location inside the project with the SVG template
            file. Outputs take this as reference to format the dynamically-
            generated compass rose SVG.
        outputs_dir: str
            The path inside the project to save new generated SVGs to.
        """
        for param in [svg_template_file, outputs_dir]:
            if not isinstance(param, str):
                raise ValueError(
                    f"Invalid value for parameter `{param}`. "
                    "Expected str."
                )

        self.svg_template_file = svg_template_file
        self.outputs_dir = outputs_dir

    @staticmethod
    def compute_1st_level_base_blade(
            l: int | float,
            *,
            h: float,
            w: float,
            main_color: str,
            secondary_color: str | None = None,
            factors_need_scaling: bool = False
    ) -> list[dict[str, TwoDimArray | str | None]]:
        """
        Solve for the 'N' blade of the first level of the compass
        rose, which is made up of two halves: one on the left and
        another on the right. Assumes coordinates start at (0, 0).

        Parameters
        ----------
        l: int | float
            blade length for the compass rose.
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
        factors_need_scaling: bool = False
            If True, scales the h and w factors by the rose's radius.

        Returns
        -------
        list[dict[str, TwoDimArray | str | None]
            List where each element represents the metadata for an blade half:
            its geometry (represented as a TwoDimArray) + its fill.
        """
        # Pass h and w to full values
        if factors_need_scaling:
            full_h = h * l
            full_w = w * l
        else:
            full_h = h
            full_w = w

        # Store geomtry objects as TwoDimArrays
        right_geom = TwoDimArray([
            [0, 0],
            [-full_w, full_h],
            [0, l]
        ])
        left_geom = TwoDimArray([
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
            initial_blade_metadata: list[dict[str, TwoDimArray | str | None]],
            *,
            n_blades: int,
            inplace: bool = False
    ) -> list[dict[str, TwoDimArray | str | None]]:
        """
        Get the metadata for an initial blade with two halves and use it to
        populate the other blade halves based on the number of blades to have in
        total for the level.

        Parameters
        ----------
        initial_blade_metadata: list[dict[str, TwoDimArray | str | None]]
            List where each element represents the metadata for an blade half:
            its geometry + its fill (see output from `compute_1st_level_base_blade`
            for more context).
        n_blades: int
            The number of blades to generate for the level, including the initial
            blade. The code generates the metadata for the (n_blades - 1) missing
            blades by leveraging the TwoDimArray.rotate() method. blades are spaced
            out evenly.
        inplace: bool = False
            Whether to write to the original object or to a new one in memory.

        Returns
        -------
        list[dict[str, TwoDimArray | str | None]]
            New list where each element represents the metadata for an blade half:
            its geometry (represented as a TwoDimArray) + its fill.
        """
        # Input Validity checks
        if (
            not isinstance(initial_blade_metadata, list)
            or len(initial_blade_metadata) != 2
            or any(not isinstance(x, dict) for x in initial_blade_metadata)
        ):
            raise ValueError(
                "Expected a list of two elements, where each element "
                "is a dict containing the metadata for an blade half. "
                f"Got {initial_blade_metadata}."
            )

        # Init return object
        if inplace:
            full_blades = initial_blade_metadata  # points to the same object in memory
        else:
            full_blades = initial_blade_metadata.copy()  # points to independent object

        # Solve for rotation value
        rotation_degrees = int(360 / n_blades)

        # Get blade halves
        left_half_ref = initial_blade_metadata[0]
        right_half_ref = initial_blade_metadata[1]

        # Build new blades iteratively
        for blade_index in range(1, n_blades):  # start, stop, step
            turn = 360 * blade_index / n_blades
            # Append new left
            new_left_half_geom = left_half_ref["geom"].rotate(turn, unit="degrees")
            full_blades.append({
                "geom": new_left_half_geom,
                "fill": left_half_ref["fill"]
            })
            # Append new right
            new_right_half_geom = right_half_ref["geom"].rotate(turn, unit="degrees")
            full_blades.append({
                "geom": new_right_half_geom,
                "fill": right_half_ref["fill"]
            })

        return full_blades

    @staticmethod
    def recenter_rose(
        rose_radius: int | float,
        rose_metadata: list[dict[str, TwoDimArray | str | None]],
        padding: int = 0,
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
            The length of a rose blade. The full size of the SVG is assumed to
            be two times this.
        rose_metadata: list[dict[str, TwoDimArray | str | None]]
            The metadata for the rose blades. Does not check how many blades are
            there and assumes they have expected structure. See
            `compute_1st_level_base_blade` for more context on expected schema.
        padding: int = 0
            Number of fill pixels on each border of the SVG. Assumes it's applied
            uniformly across all 4 borders of the image.
            Changes the new calculated center.
        inplace: bool = False
        """
        # Init return object
        if inplace:
            new_metadata = rose_metadata  # points to the same object in memory
        else:
            new_metadata = rose_metadata.copy()  # points to independent object

        new_center = (rose_radius + padding, rose_radius + padding)
        for element in new_metadata:
            element["geom"] = element["geom"].translate(new_center)

        return new_metadata

    @staticmethod
    def translate_rose_metadata_to_svg(
        rose_metadata: list[dict[str, TwoDimArray | str | None]],
        *,
        stroke_color: str,
        stroke_width: int
    ) -> str:
        """
        Translates a list of rose metadata into a string ready to be
        formatted into an SVG template.
        Assumes rose metadata is provided as exemplified in
        `compute_1st_level_base_blade`.

        Notes
        -----
        In case of no fill, in SVG it's used fill="none".

        Examples
        --------
        >>> example_metadata = [
            {
                "geom": TwoDimArray([
                    [10, 10],
                    [9.9, 10.15],
                    [10, 11]
                ]),
                "fill": "#E0A84A"
            }
        ]
        >>> svg_example = CompassRoseSVGGenerator().translate_rose_metadata_to_svg(
            example_metadata,
            stroke_color="#999999",
            stroke_width=2
        )
        >>> print(svg_example)
            '<polygon
                points="10,10 9.9,10.15 10,11"
                fill="#E0A84A"
                stroke="#999999"
                stroke-width="2" 
            />'
        """
        template = """<polygon
            points="{points}"
            fill="{fill_color}"
            stroke="{stroke_color}"
            stroke-width="{stroke_width}" 
        />
        """

        polygon_code = ''
        for polygon in rose_metadata:
            new_points = ''
            # Fill out points iteratively
            for point in polygon["geom"].array:  # Access TwoDimArray as list
                if len(new_points) != 0:
                    new_points += ' '  # comma between points
                new_points += f'{point[0]},{point[1]}'

            # Solve for fill color
            fill_color = (
                'none' if polygon["fill"] is None
                else polygon["fill"]
            )
            
            polygon_code += template.format(
                points=new_points,
                fill_color=fill_color,
                stroke_color=stroke_color,
                stroke_width=stroke_width
            )
        return polygon_code

    def write_svg(
            self,
            *,
            contents: str,
            rose_radius: int | float,
            svg_padding: int,
            output_filename: str,
            overwrite: bool = False
    ) -> str:
        """
        Fetches the file from self.svg_template_file, formats
        it with the rose's contents, and saves results to a new file
        in the self.outputs_dir space.

        Assumes three placeholders in the template file: $width, $height,
        $contents. Placeholders are saved with $placeholder, not {placeholder}
        in order to avoid collisions with native SVG/CSS syntax.

        Parameters
        ----------
        contents: str
            String containing the contents for the SVG. In this case, the
            polygons for the rose.
        rose_radius: int
            The length of a single rose blade.
        padding: int
            How many pixels to use to fill each border. Assumes they're
            applied uniformly on each border of the image.
        output_filename: str
            The name of the file to save the output as.
        overwrite: bool = False
            Whether to save new files over existing ones or not.
            If save to false, appends _{integer} to the name to avoid
            collissions.

        Returns
        -------
        str
            The path of the saved SVG file.
        """
        # The rose spans from 0 to twice its radius, with padding on each side.
        height = width = 2 * rose_radius + 2 * svg_padding

        # Fetch template file and format
        template_file = Template(
            Path(self.svg_template_file).read_text(encoding="utf-8")
        )
        svg = template_file.substitute(
            height=height,
            width=width,
            contents=contents,
        )

        # Write new file
        output_dir = Path(self.outputs_dir)
        output_dir.mkdir(parents=True, exist_ok=True)  # create new dir if needed

        target = output_dir / output_filename
        if target.suffix.lower() != ".svg":
            target = target.with_suffix(".svg")

        if not overwrite:
            stem, suffix = target.stem, target.suffix
            counter = 1
            while target.exists():  # while the filename already exists
                target = output_dir / f"{stem}_{counter}{suffix}"
                counter += 1

        target.write_text(svg, encoding="utf-8")
        return target

    @staticmethod
    def get_blade_first_level_dims(
        *,
        rose_radius: int,
        rose_blade_angle: int | float,
        n_blades: int
    ) -> tuple[int | float, int | float]:
        """
        Determine the supporting dimensions for a rose blade,
        based on its length, angle and number of blades.

        This is done in order to ensure all blades take up their
        own space in the SVG and 'fit' each other correctly in their
        borders. Due to aesthetic reasons, blades only match at the
        borders for 4 or more blades.

        Parameters
        ----------
        ...

        Returns
        -------
        tuple[int | float, int | float]
            A tuple with two elements, representing the 'h' and 'w'
            factors needed to build the rose blade geometry
        """
        import math

        # Convert initial angle to radians
        blade_angle_rad = convert_deg_to_rad(rose_blade_angle)

        if n_blades < 4:  # See docstring for explanation
            n_blades = 4

        bisector_angle_deg = 90 - (360 / (n_blades * 2))
        bisector_angle_rad = convert_deg_to_rad(bisector_angle_deg)

        w_factor = (
            rose_radius / (
                math.tan(bisector_angle_rad) + (1 / math.tan(blade_angle_rad))
            )
        )
        h_factor = w_factor * math.tan(bisector_angle_rad)

        return w_factor, h_factor

    def run(
            self,
            rose_radius: int = 110,
            rose_blade_angle: int | float = 15,
            main_fill_color: str = "#E0A84A",
            secondary_fill_color: str | None = None,
            stroke_color: str = "#E0A84A",
            stroke_width: int = 1,
            n_blades_first_level: int = 4,
            padding: int = 10,
            output_filename: str = SVG_OUTPUT_FILENAME,
            overwrite_existing_file: bool = False
    ) -> None:
        """
        Main callable for creating and saving an SVG file with
        specified parameters.

        Parameters
        ----------
        rose_radius: int
            The radius for the rose, i.e., the length
            of the N-S-E-W blades of the rose.
        rose_blade_angle: int | float
            The angle, in degrees, with which the blade opens from the
            top (please see README.md for diagram).
        main_fill_color: str
            A hex or other valid color code to use as the main color
            for the rose. This will be used to fill the rose's left sides
            for each blade.
        secondary_fill_color: str | None
            Optional secondary color to fill the rose's right blade side.
            If not provided, it's left empty and transparent to background.
        stroke_color: str
            The color to use when outlining the rose's shape.
        stroke_width: int
            The thickness of the lines drawing the rose's shape.
        n_blades_first_level: int
            The number of rose blades to display in the first level of the rose.
            Standard value is 4, but there's no reason it can't be different.
        padding: int = 1
            Number of empty pixels to use as image border.
        output_filename: str
            The name of the file to save the output SVG Aas.
        overwrite: bool = False
            Whether to save new files over existing ones or not.
            If save to false, appends _{integer} to the output filename to avoid
            collissions.
        """
        # -----------------------------------------------------------------------
        # Input consistency checks

        if not isinstance(rose_radius, int) or rose_radius < 0:
            raise ValueError(
                "Invalid value provided for `rose_radius`."
            )
        if not isinstance(main_fill_color, str) or len(main_fill_color) == 0:
            raise ValueError(
                "Invalid value provided for `main_fill_color`."
            )
        if not isinstance(stroke_color, str) or len(stroke_color) == 0:
            raise ValueError(
                "Invalid value provided for `stroke_color`."
            )
        if not isinstance(stroke_width, int) or stroke_width <= 0:
            raise ValueError(
                "Invalid value provided for `stroke_width`."
            )
        if not isinstance(n_blades_first_level, int) or n_blades_first_level <= 0:
            raise ValueError(
                "Invalid value provided for `n_blades_first_level`."
            )
        if (
            not isinstance(secondary_fill_color, str)
            or len(secondary_fill_color) == 0
        ):
            secondary_color = None

        # -----------------------------------------------------------------------
        # Build rose's first level

        # Get rose blade h and w from blade angle
        rose_blade_w, rose_blade_h = self.get_blade_first_level_dims(
            rose_radius=rose_radius,
            rose_blade_angle=rose_blade_angle,
            n_blades=n_blades_first_level
        )

        # Get metadata for 'N' blade
        first_blade_metadata: list[dict] = self.compute_1st_level_base_blade(
            l=rose_radius,
            h=rose_blade_h,
            w=rose_blade_w,
            main_color=main_fill_color,
            secondary_color=secondary_fill_color
        )

        # Use rotation to build the other three blades
        full_rose_metadata: list[dict] = self.build_full_rose_level(
            first_blade_metadata,
            n_blades=n_blades_first_level
        )

        # Re-center blade coordinates for SVG
        recentered_metadata: list[dict] = self.recenter_rose(
            rose_radius=rose_radius,
            rose_metadata=full_rose_metadata,
            padding=padding
        )

        # Convert metadata into SVG-ready code
        rose_svg_code: str = self.translate_rose_metadata_to_svg(
            recentered_metadata,
            stroke_color=stroke_color,
            stroke_width=stroke_width
        )

        # Write file
        saved_filename = self.write_svg(
            contents=rose_svg_code,
            rose_radius=rose_radius,
            svg_padding=padding,
            output_filename=output_filename,
            overwrite=overwrite_existing_file
        )

        print(f"File saved successfully to {saved_filename}.")
