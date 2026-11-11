import math


def from_cel(temp: float = None, target_unit: str = None) -> float:
    """
    Convert a Celsius temperature into Fahrenheit or Kelvin.

    Contract & Worked Example:
    - Precondition: Temperature is a valid float (minimum physical: -273.15 °C, source line 28).
    - Unit selector: 'a' for Fahrenheit, any other input (e.g. 'b') for Kelvin.
    - Decisive State Transitions:
      * Fahrenheit branch ('a'):
          intermediate: scaled = x * (9 / 5)
          decisive: final = scaled + 32
          output format: "The temperature is: {final} °F"
      * Kelvin branch ('b'):
          decisive: final = x + 273.15
          output format: "The temperature is: {final} K"

    Worked Examples:
    1. Smallest valid physical input (-273.15 °C to Kelvin):
       Input: temp=-273.15, target_unit='b'
       State calculation: final = -273.15 + 273.15 = 0.0 K
       Displayed Output: "The temperature is: 0.0 K"
    2. Ordinary input (25.0 °C to Fahrenheit):
       Input: temp=25.0, target_unit='a'
       State calculation: scaled = 25.0 * 1.8 = 45.0 -> final = 45.0 + 32 = 77.0 °F
       Displayed Output: "The temperature is: 77.0 °F"
    """
    if temp is None:
        x = float(input("Enter Temperature: "))
    else:
        x = float(temp)

    if target_unit is None:
        y = input("You want to convert it into: \n (a)fahrenheit (b)Kelvin ")
    else:
        y = str(target_unit)

    if y == 'a':
        final = (x * (9 / 5)) + 32
        print(f"The temperature is: {final} °F")
    else:
        final = x + 273.15
        print(f"The temperature is: {final} K")

    return final


def from_fah(temp: float = None, target_unit: str = None) -> float:
    if temp is None:
        x = float(input("Enter Temperature: "))
    else:
        x = float(temp)

    if target_unit is None:
        y = input("You want to convert it into: \n (a)celsius (b)Kelvin ")
    else:
        y = str(target_unit)

    if y == 'a':
        final = (x - 32) * (5 / 9)
        print(f"The temperature is: {final} °C")
    else:
        final = (x - 32) * (5 / 9) + 273.15
        print(f"The temperature is: {final} K")
    return final


def from_Kel(temp: float = None, target_unit: str = None) -> float:
    if temp is None:
        x = float(input("Enter Temperature: "))
    else:
        x = float(temp)

    if target_unit is None:
        y = input("You want to convert it into: \n (a)celsius (b)fahrenheit ")
    else:
        y = str(target_unit)

    if y == 'a':
        final = x - 273.15
        print(f"The temperature is: {final} °C")
    else:
        final = (x - 273.15) * (5 / 9) + 32
        print(f"The temperature is: {final} °F")
    return final


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
        main()


if __name__ == "__main__":
    main()
