class Array:
    """Base abstraction for doing matrix and vector operations in 2D."""

    def __init__(self, array: list[float | int | list[float | int]]) -> None:
        """
        Initialize a matrix or vector inside an array as an `Array` instance.

        Parameters
        ----------
            array: list[float | int | list[float | int]]
                A list containing a 2D vector (e.g., [-1, 0])
                or a 2D matrix (e.g., [[-1, 0], [0, 1]]).
                Lists with non-numerical elements or for different dimensions
                raise ValueError.
        """
        # Basic input validity checks
        if not isinstance(array, list):
            raise ValueError(
                f"Invalid type for array: {type(array)}. "
                "Expected list."
            )
        if len(array) != 2:
            raise ValueError(
                f"Expected a list of len 2, got {len(array)} instead."
            )

        # Check contents of list
        if isinstance(array[0], (int, float)):  # expects vector
            if not isinstance(array[1], (int, float)):
                raise ValueError(
                    f"Invalid type for second vector element: {type(array[1])}. "
                    "Expected int or float."
                )
            self.object_type = "vector"
            self.object = array
        elif isinstance(array[0], list):
            if not isinstance(array[1], list):
                raise ValueError(
                    f"Invalid value for second array element: {type(array[1])}. "
                    "Expected a list to match first element."
                )
            if not len(array[0]) == 2 or not len(array[1]) == 2:
                raise ValueError(
                    "At least one of the dimension vectors in the 2D "
                    "matrix has an invalid number of elements. Expected 2 each."
                )
            flattened_elements = [  # [[1, 2], [3, 4]] -> [1, 2, 3, 4]
                item for element in array
                for item in element
            ]
            for i in flattened_elements:
                if not isinstance(i, (int, float)):
                    raise ValueError(
                        "Invalid type for at least one item inside the "
                        "2D matrix. Expected int or float."
                    )
            self.object_type = "matrix"
            self.object = array

        else:
            raise ValueError(
                f"Invalid type for first array element: {type(array[0])}. "
                "Expected int, float or list."
                )

    def __add__(self, other: Array | int | float) -> Array:
        """Add an Array element (left) to other (right)."""
        pass

    def __radd__(self, other:  Array | int | float) -> Array:
        """
        Addition rules for when an `Array` element is to the right
        of an operation. Simply defaults to the default behavior of
        __add__.
        """
        return self.__add__(other)