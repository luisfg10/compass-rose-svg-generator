class TwoDimArray:
    """
    Base abstraction for doing matrix and vector operations in 2D.

    Notes
    -----
    TODO: Add a minimal test suite to confirm methods behave as expected.
    TODO: Generalize matrix and vector rotation in order to allow anti-clockwise
    rotations (simple, as 30° anticlockwise is equivalent to 330° clockwise), as
    well as rotations about a point different than the origin.
    TODO: Add a method for dot product multiplication between self and other =
    TwoDimArray, and use to generalize the dot product operation used in __mul__.
    TODO: Add a method by which an instance can receive more rows (vectors).
    """

    def __init__(self, array: list[float | int | list[float | int]]) -> None:
        """
        Initialize a matrix or vector inside an array as a
        `TwoDimArray` instance.

        Parameters
        ----------
        array: list[float | int | list[float | int]]
            A list containing n 2-dimensional lists, which are treated as (n, 2)
            matrices.

        Notes
        -----
        Matrix elements are indexed internally as
            [
                [x_11, x_12],
                [x_21, x_22],
                ...,
                [x_n1, x_n2]
            ]
        where the first value of the index is the row number and the second
        is the column number. In the special case of n = 1 (a vector), initial value
        can be accepted as either [x, y] or [[x, y]].
        """
        # Basic input validity checks
        if not isinstance(array, list):
            raise ValueError(
                f"Invalid type for array: {type(array)}. Expected list.")

        # Check special case of vector - a (1, 2) matrix
        if all(isinstance(x, (int, float)) for x in array):
            # 2-dim check
            if len(array) != 2:
                raise ValueError(
                    "Expected array as either a list of n nested 2-element lists, "
                    f"or a 2-element list with only int or float. Got instead {array}."
                )
            self.array = [array]
            self.shape = (1, 2)

        # General case of (n, 2) matrices
        elif all(isinstance(x, list) for x in array):
            # All elements inside must be 2-dim
            if any(len(x) != 2 for x in array):
                raise ValueError(
                    "All nested vectors inside the general array must "
                    "have 2 and only 2 elements."
                )
            # All elements must be numeric
            flattened_list = [
                cell
                for row in array
                for cell in row
            ]
            if any(not isinstance(x, (int, float)) for x in flattened_list):
                raise ValueError(
                    "All cell values inside the array must be numeric."
                )
            self.array = array
            self.shape = (len(array), 2)

        else:
            raise ValueError(
                "Expected array as either a list of n nested 2-element lists, "
                f"or a 2-element list with only int or float. Got instead {array}."
            )


    def __add__(self, other: TwoDimArray | int | float) -> TwoDimArray:
        """
        Defines behavior for TwoDimArray + other.

        Notes
        -----
        Uses broadcasting only in the case of TwoDimArray + int | float.
        For TwoDimArray + TwoDimArray situations, uses piecewise addition and
        both elements must have the same shape for the operation to be valid.

        __radd__ is intentionally not defined: there's no meaning for, say
        2 + [2, 1], as it assumes the element on the left "receives" the one
        on the right.      
        """
        # other is scalar
        if isinstance(other, (int, float)):
            flat_matrix = [
                cell + other
                for dim in self.array
                for cell in dim
            ]
            return self._nest_flattened_matrix(flat_matrix)

        # other is TwoDimArray
        elif isinstance(other, TwoDimArray):
            # Check shapes are compatible
            if self.shape != other.shape:
                raise ValueError(
                    "Matrix addition and subtraction is only supported "
                    "for elements of the same size. "
                    f"Got {self.shape} and {other.shape}."
                )
            flat_matrix = [
                self.array[i][j] + other.array[i][j]
                for i in range(self.shape[0])
                for j in range(self.shape[1])
            ]
            return self._nest_flattened_matrix(flat_matrix)

        # Raise for invalid object type
        raise TypeError(
            "Addition/subtraction operation not supported between "
            f"TwoDimArray and {type(other)}."
        )


    def __sub__(self, other: TwoDimArray | int | float) -> TwoDimArray:
        """
        Defines behavior for TwoDimArray - other.

        Notes
        -----
        __rsub__ is intentionally not defined, for the same reason as
        noted for self.__radd__ in the notes for self.__add__.
        
        """
        if isinstance(other, (int, float, TwoDimArray)):
            other *= (-1)
            return self.__add__(other)

        # Raise for invalid object type
        raise TypeError(
            "Addition/subtraction operation not supported between "
            f"TwoDimArray and {type(other)}."
        )

    def __mul__(
            self,
            other: TwoDimArray | int | float,
            num_decimals: int = 4
    ) -> TwoDimArray:
        """
        Defines behavior for TwoDimArray * other.

        Parameters
        ----------
        ...
        num_decimals: int = 4
            The max number of decimals to round each resulting element
            off to.

        Notes
        -----
        Follows rules for matrix multiplication:
        * The number of columns of the first element must
        match the number of rows of the second
        * If A is an (n, m) matrix and b is (m, q), then their
        product C is of dimensions (n, q).
        * C_ij = sum over m (A_im * B_mj). In other words,
        C_ij is the result of the piecewise sum of the dot products
        of row i from matrix A and column J from matrix B.

        Multiplying by a scalar broadcasts to each matrix element individually.

        Following the convention for addition and substraction, __rmul__ is
        intentionally not defined.
        """
        # other is scalar
        if isinstance(other, (int, float)):
            flat_matrix = [
                round(cell * other, num_decimals)
                for row in self.array
                for cell in row
            ]
            return self._nest_flattened_matrix(flat_matrix)

        # other is TwoDimArray
        elif isinstance(other, TwoDimArray):
            # Check dimension compatibility
            if self.shape[1] != other.shape[0]:
                raise ValueError(
                    "For matrix multiplication to be possible, "
                    "the number of columns in the first element must be "
                    "equal to the number of rows of the second. "
                    f"Got {self.shape[1]} and {other.shape[0]}."
                )
            # Populate resulting matrix iteratively
            matrix_c = []
            for i in range(self.shape[0]):  # equals result_matrix.shape[0]
                row_a = self.array[i]  # row from matrix A (self)
                row_c = []  # resulting row to be built
                for j in range(other.shape[1]):  # equals result_matrix.shape[1]
                    col_b = [  # row from matrix B (self)
                        row[j] for row in other.array
                    ]
                    # Perform dot product addition between row_a and col_b
                    cell = 0
                    for x in range(len(row_a)):
                        cell += row_a[x] * col_b[x]
                    row_c.append(round(cell, num_decimals))
                matrix_c.append(row_c)

            return TwoDimArray(matrix_c)

        # Raise for invalid object type
        raise TypeError(
            "Multiplication operation not supported between "
            f"TwoDimArray and {type(other)}."
        )

    def __str__(self):
        """Defines behavior when printing a class instance."""
        # self.array is a list so defaults to list.__str__
        return str(self.array)

    def _nest_flattened_matrix(
            self,
            flattened_array: list[int | float]
    ) -> TwoDimArray:
        """
        Internal method to simplify common data operation from a flattened
        list to a nested one.
        e.g., go from
            [x_11, x_12, x_21, x_22]
        to
            [[x_11, x_12], [x_21, x_22]]
        """
        result = []
        for i in range(0, len(flattened_array), 2):
            result.append(
                [flattened_array[i], flattened_array[i + 1]]
            )

        return TwoDimArray(result)

    def rotate(
            self,
            angle: int | float,
            *,
            unit="radians"
        ) -> TwoDimArray:
        """
        Rotate a matrix by a specified angle clockwise with respect
        to the origin, either in radians or degrees.

        If rotating an (n, 2) matrix, each row in the original matrix
        is rotated individually of the other rows, conserving its
        magnitude and position in the original matrix.
        """
        import math  # lazy import just for this module

        if unit == "degrees":  # convert from degrees to radians
            angle *= math.pi / 180

        rotation_matrix = TwoDimArray([
            [math.cos(angle), -math.sin(angle)],
            [math.sin(angle), math.cos(angle)]
        ])
        return self.__mul__(rotation_matrix)
