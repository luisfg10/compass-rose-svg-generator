# `compass-rose-svg-generator`  

This is a small side-project for generating compass rose SVGs from a set of dynamic parameters. It requires no dependencies other than Python 3.14, and it generates the files right on your local directory.

## Examples

<p align="center">
  <img src="examples/compass_rose.svg" alt="Four-blade gold compass rose" width="180">
  <img src="examples/compass_rose_2.svg" alt="Eight-blade blue and white compass rose" width="180">
  <img src="examples/compass_rose_3.svg" alt="Sixteen-blade red and black compass rose" width="180">
  <img src="examples/compass_rose_4.svg" alt="Three-blade black and white compass rose" width="180">
</p>

## Parameters

`CompassRoseSVGGenerator.run()` accepts these parameters:

- `rose_radius` (`110`): Length of each cardinal blade, in pixels.
- `rose_blade_angle` (`15`): Blade opening angle from the top into its connection with the adjacent blade, measured in degrees. The bigger, the "chubbier" each blade looks.
- `main_fill_color` (`"#E0A84A"`): Fill color for the left side of each blade.
- `secondary_fill_color` (`None`): Optional fill color for the right side; it is transparent by default.
- `stroke_color` (`"#E0A84A"`): Outline color for the blades.
- `stroke_width` (`1`): Thickness of the blade outlines, in pixels.
- `n_blades_first_level` (`4`): Number of blades in the rose. Typically it's 4 blades, but there's no reason to not add more!
- `padding` (`10`): Empty space around each edge of the SVG, in pixels.
- `output_filename` (`"compass_rose.svg"`): Name of the generated SVG file.
- `overwrite_existing_file` (`False`): Replace an existing file with the same name; otherwise, a numbered suffix is added to the outputs/ directory.

## How to run

From the project directory, run the generator with Python and pass parameters as command-line flags:

```shell
python main.py --rose-radius 200
```

For example, `--rose-radius` sets `rose_radius`; other parameters can be passed as flags in the same way.