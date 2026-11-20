import pygame
import random
import math


def GenerateRandomColorValue(min_val=0, max_val=255):
    """
    Generate a random RGB color value as an (r, g, b) tuple within [min_val, max_val].

    Contract:
    - Preconditions:
        0 <= min_val <= max_val <= 255 (integers).
        Default range is [0, 255] (standard 8-bit RGB color depth).
        Source fixture / data anchors:
          RGBTextRect.center = (width // 2, height // 2 - 20) (RandColorGen.py line 60)
          hexTextRect.center = (width // 2, height // 2 + 20) (RandColorGen.py line 65)
    - Returns:
        tuple (r, g, b) where each component is an integer in [min_val, max_val].
    - Mutation:
        Pure function: does not mutate any input argument or global state.
    """
    if not (isinstance(min_val, int) and isinstance(max_val, int)):
        raise TypeError("min_val and max_val must be integers")
    if not (0 <= min_val <= max_val <= 255):
        raise ValueError(
            f"Invalid range: 0 <= min_val <= max_val <= 255 required, got min_val={min_val}, max_val={max_val}"
        )

    r = random.randint(min_val, max_val)
    g = random.randint(min_val, max_val)
    b = random.randint(min_val, max_val)

    return (r, g, b)


def ReturnTextColor(colorValue):
    r = colorValue[0]
    g = colorValue[1]
    b = colorValue[2]
    colors = [r, g, b]

    i = 0
    for c in colors:
        c = c / 255.0
        if c <= 0.04045:
            c = c / 12.92
        else:
            c = math.pow(((c + 0.055) / 1.055), 2.4)
        colors[i] = c
        i += 1

    r = colors[0]
    g = colors[1]
    b = colors[2]

    L = 0.2126 * r + 0.7152 * g + 0.0722 * b

    shouldBeWhite = L > 0.179
    # shouldBeWhite = (r * 0.299 + g * 0.587 + b * 0.114) > 186
    
    if shouldBeWhite:
        return (0, 0, 0)
    else:
        return (255, 255, 255)


height = 500
width = 500


def main():
    pygame.init()

    canvas = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Random Color Generator!")
    isExit = False
    canvas.fill((255, 255, 255))

    font = pygame.font.Font(pygame.font.get_default_font(), 32)

    # RGB Value
    RGBText = font.render("RGB Value: (255, 255, 255)", True, (0, 0, 0))
    RGBTextRect = RGBText.get_rect()
    RGBTextRect.center = (width // 2, height // 2 - 20)

    # Hex Value
    hexText = font.render("Hex Value: #ffffff", True, (0, 0, 0))
    hexTextRect = hexText.get_rect()
    hexTextRect.center = (width // 2, height // 2 + 20)
    hexTextRect.left = RGBTextRect.left

    while not isExit:
        canvas.blit(RGBText, RGBTextRect)
        canvas.blit(hexText, hexTextRect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isExit = True
            if event.type == pygame.MOUSEBUTTONUP:
                color = GenerateRandomColorValue()
                RGBString = "RGB Value: " + str(color)
                hexString = "Hex Value: " + str("#%02x%02x%02x" % color)
                TextColor = ReturnTextColor(color)
                RGBText = font.render(RGBString, True, TextColor)
                hexText = font.render(hexString, True, TextColor)
                print(RGBString + "; " + hexString)

                canvas.fill(color)

        pygame.display.flip()


if __name__ == "__main__":
    main()
