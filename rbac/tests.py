from django.test import TestCase


# Create your tests here.


class Solution:
    def searchMatrix(self, matrix, target):
        """
        :type matrix: List[List[int]]
        :type target: int
        :rtype: bool
        """
        for line in matrix:
            if target in line:
                return True
        return False
