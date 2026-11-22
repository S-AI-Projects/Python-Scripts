import math


def from_cel():
    """
    Ask for a Celsius temperature and print its Fahrenheit or Kelvin result.

    Worked example 1 - Celsius to Kelvin:
      Input temperature: -273.15
      Conversion choice: b (Kelvin)
      Intermediate calculation: -273.15 + 273.15 = 0.0
      Final output: The temperature is: 0.0 K

    Worked example 2 - Celsius to Fahrenheit:
      Input temperature: 25
      Conversion choice: a (Fahrenheit)
      Intermediate calculation: 25 * (9 / 5) = 45.0
      Then add 32: 45.0 + 32 = 77.0
      Final output: The temperature is: 77.0 °F

    Runnable with mocked input:
      >>> from unittest.mock import patch
      >>> with patch("builtins.input", side_effect=["-273.15", "b"]):
      ...     from_cel()
      The temperature is: 0.0 K
      >>> with patch("builtins.input", side_effect=["25", "a"]):
      ...     from_cel()
      The temperature is: 77.0 °F
    """
    x = float(input("Enter Temperature: "))
    y = input("You want to convert it into: \n (a)fahrenheit (b)Kelvin ")

    if y == 'a':
        final = (x * (9 / 5)) + 32
        print(f"The temperature is: {final} °F")
    else:
        final = x + 273.15
        print(f"The temperature is: {final} K")


def from_fah():
    x = float(input("Enter Temperature: "))
    y = input("You want to convert it into: \n (a)celsius (b)Kelvin ")

    if y == 'a':
        final = (x - 32) * (5 / 9)
        print(f"The temperature is: {final} °C")
    else:
        final = (x - 32) * (5 / 9) + 273.15
        print(f"The temperature is: {final} K")


def from_Kel():
    x = float(input("Enter Temperature: "))
    y = input("You want to convert it into: \n (a)celsius (b)fahrenheit ")

    if y == 'a':
        final = x - 273.15
        print(f"The temperature is: {final} °C")
    else:
        final = (x - 273.15) * (5 / 9) + 32
        print(f"The temperature is: {final} °F")


def get_temp():
    global t
    t = input("What would you like to convert from? (input no.): \n (1)Celsius (2)fahrenheit (3)Kelvin ")


def main():
    get_temp()

    if t == "1":
        from_cel()
    elif t == '2':
        from_fah()
    elif t == '3':
        from_Kel()
    else:
        print("please enter a correct input")
        get_temp()


if __name__ == "__main__":
    main()
