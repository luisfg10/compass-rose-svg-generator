class Array:
    """
    Base abstraction for doing matrix and vector operations in 2D.

    TODO: Improve degree of abstraction to handle matrix addition,
    substraction and multiplication in arbitrary n by m dimensions. Currently
    only supports (1, 2) and (2, 2) matrices.
    TODO: Improve degree of generalization to avoid manually typing the
    solution for specific cases, as it doesn't scale for arbitrary dimensions.
    """
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

        TODO: Even if nested lists are the correct way to display matrices to users,
        they cause friction with vectors, which are not nested inside lists.
        For consistency and better generalization of operations, either nest all
        objects internally or none. The __str__ method can be adapted to separate
        the internal representation of objects vs. the way they're displayed. 
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

        Notes
        -----
        Uses broadcasting only in the case of Array + int | float.
        For Array + Array situations, each instance must have the same shape
        for the operation to be valid.

        __radd__ is intentionally not defined: there's no meaning
        for, say 2 + [2, 1], as it assumes the element on the left "receives"
        the one on the right.      
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
                return Array(
                    self._nest_flattened_matrix(result)
                )

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
                return Array(
                    self._nest_flattened_matrix(result)
                )                
        raise TypeError(
            "Addition/substraction operation not supported "
            f"between Array and {type(other)}."
        )

    def __sub__(self, other: Array | int | float) -> Array:
        """
        Defines behavior for self - other.

        Notes
        -----
        __rsub__ is intentionally not defined, for the same reason as
        exposed for self.__radd__ in the __doc__ notes for self.__add__.
        
        """
        if isinstance(other, (int, float, Array)):
            other *= (-1)
            return self.__add__(other)
        return NotImplemented

    def __mul__(self, other) -> Array:
        """
        Defines behavior for Array * other.

        Notes
        -----
        Follows rules for matrix multiplication:
            * The number of columns of the first element must
            match the number of rows of the second
            * If A is an n by m matrix and b is p by q, then their
            product C is n by q. C_ij is the result of the dot product
            of row i from matrix A and column J from matrix B.
            Applied to the current scope, this means:
            >> Vector (1, 2) * Matrix (2, 2) -> Vector (1, 2)
            >> Matrix (2, 2) * Matrix (2, 2) -> Matrix (2, 2)
            >> Matrix (2, 2) * Vector (1, 2) -> Invalid
            >> Vector (1, 2) * Vector (1, 2) -> Invalid

        Multiplying by a scalar broadcasts to each matrix element individually.
        Following the convention for addition and substraction,
        __rmul__ is intentionally not defined.
        """
        # Multiplication by scalar
        if isinstance(other, (int | float)):
            if self.object_type == "vector":
                return Array([
                    element * other
                    for element in self.object
                ])
            elif self.object_type == "matrix":
                result = [
                    element * other
                    for dimension in self.object
                    for element in dimension
                ]
                return Array(
                    self._nest_flattened_matrix(result)
                )

        # Array * Array
        elif isinstance(other, Array):
            # Vector * Vector
            if (
                self.object_type == "vector"
                and other.object_type == "vector"
            ):
                raise ValueError(
                    "Invalid operation: multiplication between two "
                    "vectors not supported."
                )

            # Matrix * Vector
            if (
                self.object_type == "matrix"
                and other.object_type == "vector"
            ):
                raise ValueError(
                    "Invalid operation: multiplication between "
                    "object of shape (2, 2) and object of shape (1, 2) "
                    "not allowed."
                )

            # Vector (1, 2) * Matrix (2, 2) -> Vector (1, 2)
            # e.g., [1, 0] * [[1, 1], [2, 0]] -> [1, 1]
            if (
                self.object_type == "vector"
                and other.object_type == "matrix"
            ):
                result = []
                for i in range(0, 2):
                    matrix_dim = self._extract_matrix_dim(
                        other.object,
                        dim="col", pos=i+1
                    )
                    result.append(
                        self.object[0] * matrix_dim[0] +
                        self.object[1] * matrix_dim[1]
                    )
                return Array(result)

            # Matrix (2, 2) * Matrix (2, 2) -> Matrix (2, 2)
            if (
                self.object_type == "matrix"
                and other.object_type == "matrix"
            ):
                result = []
                for i in range(0, 2):
                    dim = []
                    for j in range(0, 2):
                        left_row = self._extract_matrix_dim(
                            self.object,
                            dim="row", pos=i+1
                        )
                        right_column = self._extract_matrix_dim(
                            other.object,
                            dim="col", pos=j+1
                        )
                        dim.append(
                            left_row[0] * right_column[0] + 
                            left_row[1] * right_column[1]
                        )
                    result.append(dim)
                return Array(result)    
        
        return NotImplemented

    def __rmul__(self, other):
        pass

    def __str__(self):
        """Defines behavior when printing a class instance."""
        return str(self.object)  # self.object is a list so this works

    @staticmethod
    def _nest_flattened_matrix(
        flattened_array: list[int | float]) -> list[list[int | float]]:
        """Simplify common operation: go from
        [x_11, x_12, x_21, x_22] -> [[x_11, x_12], [x_21, x_22]]
        """
        return [
            [flattened_array[0], flattened_array[1]],
            [flattened_array[2], flattened_array[3]]
        ]

    @staticmethod
    def _extract_matrix_dim(
        matrix: list,
        *,
        dim: str,
        pos: int
    ) -> list:
        """
        Extracts the nth row or column from a matrix into a list.

        Parameters
        ----------
        matrix: Array
            A 2x2 matrix.
        dim: str
            Either "col" (column) or "row".
        pos: int
            The position of the row or column to extract, with
            index starting at 1 to be consistent with math notation.

        Returns
        -------
        list
            A list with all elements of the specified dimension and
            position.
        """
        # Sanity checks
        if dim not in ["row", "col"]:
            raise ValueError(
                f"Invalid value for `dim`: {dim}. "
                "Valid values: 'row', 'col'."
            )
        if pos not in [1, 2]:
            raise ValueError(
                f"Invalid value for `pos`: {pos}. "
                "Valid values: 1, 2."
            )

        if dim == "row":
            return matrix[pos - 1]
        elif dim == "col":
            return [
                element[pos - 1]
                for element in matrix
            ]
