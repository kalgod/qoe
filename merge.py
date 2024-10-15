import random

def api_sort(arr):
    """
    Simulated API function that sorts up to m elements and returns the sorted result.
    """
    return sorted(arr)

def merge_and_sort(arrA, arrB, m):
    """
    Merges two sorted lists arrA and arrB by leveraging the API for sorting.
    Each list contributes m/2 elements at a time.
    """
    lenA, lenB = len(arrA), len(arrB)
    merged = []

    i, j = 0, 0

    while i < lenA or j < lenB:
        # Get the next m/2 elements from arrA
        partA = arrA[i:i + m // 2]
        # Get the next m/2 elements from arrB
        partB = arrB[j:j + m // 2]

        # Sort the combined parts using the API
        combined = api_sort(partA + partB)

        # Select the first m elements from the sorted result
        merged.extend(combined[:m])

        # Update indices based on how many we've taken from arrA and arrB
        taken_from_A = min(len(partA), len(combined) // 2)
        taken_from_B = min(len(partB), len(combined) - taken_from_A)

        i += taken_from_A
        j += taken_from_B
    
    return merged

def merge_sort(arr, m):
    """
    Implements the merge sort algorithm with a custom merge function.
    """
    if len(arr) < m:
        # If the subarray is smaller than m, no need to sort
        return api_sort(arr)

    mid = len(arr) // 2
    left = merge_sort(arr[:mid], m)
    right = merge_sort(arr[mid:], m)

    return merge_and_sort(left, right, m)

# Example usage
if __name__ == "__main__":
    n = 20  # Size of the array
    m = 8   # API limit for sorting
    arr = [random.randint(1, 100) for _ in range(n)]
    
    print("Original array:", arr)
    sorted_array = merge_sort(arr, m)
    print("Sorted array:", sorted_array)