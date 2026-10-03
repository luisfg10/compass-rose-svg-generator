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

        Notes
        -----
        In a 2D matrix, elements are treated as [[x_11, x_12], [x_13, x_14]], where
        the first element of the index is the row number and the second is the column
        number. Conversely, on a vector they're treated as [x_11, x_12].
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
        """
        Defines behavior for Array + other.

        Uses broadcasting only in the case of Array + int | float.
        For Array + Array situations, each instance must have the same shape
        for the operation to be valid.        
        """
        # Array + scalar
        if isinstance(other, (int | float)):
            if self.object_type == "vector":
                return Array([
                    element + other
                    for element in self.object
                ])
            elif self.object_type == "matrix":
                result = [  # [x_11, x_12, x_21, x_22]
                   element + other
                   for dimension in self.object
                   for element in dimension
                ]
                return Array([
                    [result[0], result[1]],
                    [result[2], result[3]]
                ])

        # Array + Array
        elif isinstance(other, Array):
            # Check that types match: no broadcasting supported
            if self.object_type != other.object_type:
                raise ValueError(
                    "Invalid operation: can only add two "
                    "elements of the same type together, got "
                    "a vector and a matrix."
                )
            # vector + vector
            if self.object_type == "vector":
                return Array([
                    self.object[i] + other.object[i]
                    for i in range(0, 2)
                ])
            elif self.object_type == "matrix":
                result = [
                    self.object[i][j] + other.object[i][j]
                    for i in range(0, 2)
                    for j in range(0, 2)
                ]
                return Array([
                    [result[0], result[1]],
                    [result[2], result[3]]
                ])                
        return NotImplemented

    def __radd__(self, other:  Array | int | float) -> Array:
        """
        Defines behavior for other + Array,
        in case other.__add__ returns NotImplemented.

        Simply defaults to self.__add__.
        """
        return self.__add__(other)

    def __sub__(self, other):
        pass

    def __rsub__(self, other):
        pass

    def __str__(self):
        """Defines behavior when printing a class instance."""
        return str(self.object)