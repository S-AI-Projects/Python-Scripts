from turtle import *
import random
speed(-1)
width(3)
colors = ['sky blue', 'navy', "steel blue", 'cyan']

def main(iterations=102):
    """Draw ``iterations`` circles; the default preserves the original art."""
    for index in range(iterations):
        random.shuffle(colors)
        color(colors[0])
        circle(10 + 2 * index, 100, 2)

if __name__ == '__main__':
    ht()
    main()
    mainloop()
