def starPattern(n):
    """
    Print a left-aligned star pattern.

    For n = 1, n = 3, and n = 0, the outputs are "* \n",
    "* \n* * \n* * * \n", and "", respectively. The function prints
    directly and returns None.
    """
    for i in range(1, n+1):
        for j in range(1, i+1):
            print("* ", end="")
        print()


if __name__ == "__main__":
    n = int(input("Enter the number of rows: "))
    starPattern(n)

