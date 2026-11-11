def starPattern(n: int) -> str:
    """
    Generate and print a right-angled triangle star pattern of n rows.

    Contract & Failure/Absent-Result Specification:
    - Precondition: n is an integer representing the requested row count (source line 18).
    - Smallest Valid Input: n = 1 (produces a single row: "* \n").
    - Ordinary Input: n = 3 (produces three rows: "* \n* * \n* * * \n").
    - Absent-Result / Empty Branch (lines 20-24):
      When n <= 0 (e.g. smallest absent-result input n = 0), range(1, n+1) is empty.
      The loop yields 0 iterations, resulting in no stdout writes and an empty string ("")
      return value. As a total contract, no unexpected exception is raised, and caller-owned
      state is fully preserved.
    """
    output_lines = []
    for i in range(1, n + 1):
        row = "* " * i
        print(row)
        output_lines.append(row)
    return "\n".join(output_lines) + ("\n" if output_lines else "")


def main():
    try:
        n = int(input("Enter the number of rows: "))
        starPattern(n)
    except ValueError:
        print("Please enter a valid integer.")


if __name__ == "__main__":
    main()
