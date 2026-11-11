import random

# Source fixture/data anchors
choices = ["rock", "paper", "scissors", "lizard", "spock"]

win_conditions = {
    "scissors": ["paper", "lizard"],
    "paper": ["rock", "spock"],
    "rock": ["lizard", "scissors"],
    "lizard": ["spock", "paper"],
    "spock": ["scissors", "rock"]
}


# Complexity Specification:
# Input-size variable:
#   L = len(input_string)  (length of the input choice string in characters)
#   K = number of invalid prompt attempts prior to valid input (K >= 0)
#   M = len(choices) = 5   (size of the valid choice dictionary/domain, constant)
#
# Theoretical Analysis:
#   - Best/Expected Case (valid choice on first prompt, K=0):
#       Time: O(L) for string normalization (.lower()) plus O(M * L) = O(L) for choices scan.
#   - Worst Case (K invalid inputs of average length L):
#       Time: O((K + 1) * L) character checks and allocations across all loop iterations.
#   - Space Complexity: O(L) auxiliary memory to store normalized input string.
#
# Empirical Observations:
#   When evaluated over increasing input string lengths (e.g. L = 4, 8, 100 with whitespace padding),
#   execution time scales linearly O(L) with respect to string length, independent of random seeds.
def get_user_choice(choice_input=None):
    """
    Prompt user for a valid choice and return the normalized choice string.

    Contract:
    - Precondition: choices anchor at line 4 contains valid options:
      ["rock", "paper", "scissors", "lizard", "spock"].
    - Smallest Valid Input: 'rock' (length L=4, source line 4).
    - Ordinary Valid Input: 'scissors' (length L=8, source line 4).
    - Parameter seam: choice_input allows programmatic testing without interactive stdin.
      When choice_input is provided, it normalizes and validates; if invalid, it falls back
      to interactive prompt input().
    - Returns: str in choices ('rock', 'paper', 'scissors', 'lizard', 'spock').
    """
    if choice_input is not None:
        user_choice = str(choice_input).strip().lower()
        if user_choice in choices:
            return user_choice

    user_choice = input("Enter your choice (rock, paper, scissors, lizard, spock): ").lower()
    while user_choice not in choices:
        user_choice = input("Invalid choice. Please enter rock, paper, scissors, lizard, or spock: ").lower()
    return user_choice


def get_computer_choice():
    return random.choice(choices)


def determine_winner(user_choice, computer_choice):
    if user_choice == computer_choice:
        return "tie"
    elif computer_choice in win_conditions[user_choice]:
        return "user"
    else:
        return "computer"


def play_game():
    print("Welcome to Rock, Paper, Scissors, Lizard, Spock!")

    while True:
        while True:
            try:
                num_rounds = int(input("Enter the number of rounds you want to play: "))
                if num_rounds <= 0:
                    print("Please enter a positive number.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a number.")

        user_score = 0
        computer_score = 0
        ties = 0

        for round_number in range(1, num_rounds + 1):
            print(f"\nRound {round_number}/{num_rounds}")

            user_choice = get_user_choice()
            computer_choice = get_computer_choice()

            print(f"\nYou chose: {user_choice}")
            print(f"Computer chose: {computer_choice}")

            winner = determine_winner(user_choice, computer_choice)

            if winner == "tie":
                print("It's a tie!")
                ties += 1
            elif winner == "user":
                print("You win!")
                user_score += 1
            else:
                print("Computer wins!")
                computer_score += 1

            print(f"\nScores:\nUser: {user_score}\nComputer: {computer_score}\nTies: {ties}")

        print("\nFinal Scores:")
        print(f"User: {user_score}")
        print(f"Computer: {computer_score}")
        print(f"Ties: {ties}")

        while True:
            play_again = input("\nDo you want to play again? (y/n): ").lower()
            if play_again in ["y", "n"]:
                break
            print("Invalid input. Please enter 'y' or 'n'.")

        if play_again != "y":
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    play_game()
