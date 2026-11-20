def pigeonhole_sort(arr):
    """
    Sort an array of integers in ascending order using Pigeonhole Sort.

    Contract & Failure/Absent-Result Path:
    - Input:
        arr (list of int): Integer list to be sorted.
    - Failure / Absent-Result Handling:
        Line 17: Where the collection is empty (len(arr) == 0) or contains a single element,
        the contract is total: it returns the array as-is without raising exceptions.
    - In-place mutation:
        arr is sorted in-place in ascending order, and returned.
    """
    if len(arr) <= 1:
        return arr

    # Find the minimum and maximum values in the array
    min_val = min(arr)
    max_val = max(arr)
    
    # Calculate the range of values in the array
    range_val = max_val - min_val + 1
    
    # Create a list of "holes" to store counts of each value
    holes = [0] * range_val

    # Count the occurrences of each value and store them in the "holes" list
    for val in arr:
        holes[val - min_val] += 1

    # Reconstruct the sorted array using the counts in the "holes" list
    index = 0
    for i in range(range_val):
        while holes[i] > 0:
            arr[index] = i + min_val
            index += 1
            holes[i] -= 1

    return arr


def main():
    # Example usage:
    input_array = [8, 3, 2, 7, 4, 6, 8]
    pigeonhole_sort(input_array)
    print("Sorted order is:", input_array)


if __name__ == "__main__":
    main()
