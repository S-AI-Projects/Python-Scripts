try:
    from model.model import predict   # import model
except (ImportError, Exception):
    predict = None


def main(password: str = None, predict_fn=None):
    """
    Check and classify the strength of a given password.

    Contract:
    - Preconditions:
        - password (str, optional): Password string to evaluate. If omitted or None,
          prompts via `input()` (line 4 in original source).
        - predict_fn (callable, optional): Prediction callable taking password and returning
          class 0, 1, or 2. Defaults to `predict` from `model.model`.
    - Output:
        - Prints classification result: `Password strength classification: {predicted_class} / 2`
          (0 = weak, 1 = moderate, 2 = strong).
        - Returns int: `predicted_class`.

    Decisive State Transitions:
    1. Input Acquisition:
       Raw input password string is obtained (e.g. "a" or "MyP@ssw0rd!2026").
    2. Model Evaluation / Inference:
       Features are evaluated to yield the argmax class index (0 for weak, 1 for moderate, 2 for strong).
    3. Classification Display & Return:
       Formatted classification message printed to standard output and integer class returned.

    Runnable Worked Examples:
    Example 1: Smallest Valid Input (Weak password: single character "a")
    >>> main(password="a", predict_fn=lambda p: 0)
    Password strength classification: 0 / 2
    0

    Example 2: Ordinary Valid Input (Strong password: "MyP@ssw0rd!2026")
    >>> main(password="MyP@ssw0rd!2026", predict_fn=lambda p: 2)
    Password strength classification: 2 / 2
    2
    """
    if predict_fn is None:
        predict_fn = predict

    if password is None:
        password_to_test = input("Enter a password to check its strength: ")   # get password from terminal
    else:
        password_to_test = str(password)

    predicted_class = int(predict_fn(password_to_test))   # evaluate password strength
    print(f"Password strength classification: {predicted_class} / 2")   # output 0 - weak, 1 - moderate, or 2 - strong
    return predicted_class


if __name__ == "__main__":
    main()
