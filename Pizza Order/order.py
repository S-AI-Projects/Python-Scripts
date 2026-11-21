# purpose of order.py is the front end for users to submit their order
"""
Pizza Order Front-End Ordering Module.

Supported Boundaries and Domain Contract:
- Initial state / Precondition anchors:
    pizza_lst = [] (line 33)
    pizza_lst_current = [] (line 34)
- Order confirmation domain:
    Affirmative: ["Yes", "yes", "Y", "y", "YES"] (line 37)
    Negative / Exit sentinels: ["No", "no", "Q", "NO", "N", "n"] (line 38)
    Smallest valid input (boundary): negative sentinel ("No" / "Q") -> 0 pizzas ordered, pizza_lst = [].
- Pizza Size domain:
    Valid domain: {"S", "M", "L", "XL"} (line 42, case-insensitive)
    Smallest valid size boundary: "S" (Base price: $7.99)
    Upper size boundary: "XL" (Base price: $13.99)
    Interior valid sizes: "M" ($9.99), "L" ($11.99)
- Toppings domain:
    Valid toppings: TOPPINGS tuple (15 items)
    Topping control sentinels: "X" (finish toppings), "LIST" (display toppings)
    Lower topping boundary: 0 toppings ("X" immediately) -> no extra topping fee
    Included topping threshold: exactly 3 toppings -> included in base price (extra fee = $0.00)
    Extra topping boundary: >= 4 toppings -> extra fee applies per topping above 3:
      - S: +$0.50 per extra topping
      - M: +$0.75 per extra topping
      - L: +$1.00 per extra topping
      - XL: +$1.25 per extra topping
"""
from pizzaReceipt import *  # asks to import all functions found in the pizzaReceipt.py file

# set all initial variables before beginning (Precondition data anchors)
size = ""
pizza_lst = []
pizza_lst_current = []
toppings_lst = []  # list to be a parameter for generateReceipt function
list_order_yes = ["Yes", "yes", "Y", "y", "YES"]
list_order_no = ["No", "no", "Q", "NO", "N", "n"]
TOPPINGS = (
    "ONION", "TOMATO", "GREEN PEPPER", "MUSHROOM", "OLIVE",
    "SPINACH", "BROCCOLI", "PINEAPPLE", "HOT PEPPER", "PEPPERONI",
    "HAM", "BACON", "GROUND BEEF", "CHICKEN", "SAUSAGE"
)


def order_pizzas(input_func=input, print_func=print):
    """
    Execute the interactive ordering loop and return the list of ordered pizzas.

    Contract:
    - Precondition anchors: pizza_lst = [] | pizza_lst_current = []
    - Returns: list of tuples in format (size: str, toppings: list[str])
    - Boundary behavior:
        - If initial order is negative, returns [] without mutating pizza_lst.
        - Sizes normalized to uppercase ('S', 'M', 'L', 'XL').
        - Toppings captured up to 'X' sentinel.
    """
    global pizza_lst, pizza_lst_current, size, toppings_lst
    pizza_lst = []
    pizza_lst_current = []

    order = input_func("Do you want to order a pizza? ")

    # case for when an invalid input is submitted
    while (order not in list_order_yes) and (order not in list_order_no):
        order = input_func("Do you want to order a pizza? ")

    # ask for size
    if order in list_order_yes:
        size = input_func("Choose a size: ")

        # case for when a user inputs invalid size
        while size.upper() not in ["S", "M", "L", "XL"]:
            size = input_func("Choose a size: ")

    # entire loop to repeat if user wants to order more than one pizza
    while order in list_order_yes:
        toppings_lst = []
        topping = input_func(
            'Type in one of our toppings to add it to your pizza. To see the list of toppings, enter "LIST". '
            'When you are done adding toppings, enter "X" '
        )

        # case for when a user places an invalid input for this question
        while (topping.upper() != "X") and (topping.upper() != "LIST") and (topping.upper() not in TOPPINGS):
            topping = input_func(
                'Type in one of our toppings to add it to your pizza. To see the list of toppings, enter "LIST". '
                'When you are done adding toppings, enter "X" '
            )

        print_func()
        # toppings while loop which ask for toppings selection or list view, multiple times until user enters X
        while topping.upper() != "X":
            if topping.upper() == "LIST":
                print_func(topping.upper())
                print_func(TOPPINGS)
                topping = input_func(
                    'Type in one of our toppings to add it to your pizza. To see the list of toppings, enter "LIST". '
                    'When you are done adding toppings, enter "X" \n \n'
                )
            elif topping.upper() in TOPPINGS:
                print_func(topping.upper())
                print_func("Added", topping.upper(), "to your pizza")
                toppings_lst.append(topping.upper())
                topping = input_func(
                    'Type in one of our toppings to add it to your pizza. To see the list of toppings, enter "LIST". '
                    'When you are done adding toppings, enter "X" \n \n'
                )

        # add the size and toppings list as a tuple to pizza_lst
        pizza_lst.append((size.upper(), toppings_lst))
        print_func(pizza_lst)

        # ask whether they want to continue ordering
        order = input_func("Do you want to continue ordering? ")

        # case for when user types invalid input
        while (order not in list_order_yes) and (order not in list_order_no):
            order = input_func("Do you want to order a pizza? ")

        # if they say no, break the loop and go through the last line of the code
        if order in list_order_no:
            break
        elif order in list_order_yes:
            size = input_func("Choose a size: ")

        # case for when user types invalid input
        while size.upper() not in ["S", "M", "L", "XL"]:
            size = input_func("Choose a size: ")

    pizza_lst_current = list(pizza_lst)
    return pizza_lst


def main():
    orders = order_pizzas()
    generateReceipt(orders)


if __name__ == "__main__":
    main()
