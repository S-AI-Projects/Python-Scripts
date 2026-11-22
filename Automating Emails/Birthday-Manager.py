import ssl
import smtplib
import csv
from abc import ABC, abstractmethod


class EmailSender(ABC):
    """Abstract base class for sending emails.

    Contract
    --------
    EmailSender
        Source line (precondition anchor): ``class EmailSender(ABC):``  # line 7
        Smallest valid input : recipient="", message=""
        Ordinary input       : recipient="alice@example.com",
                               message="Hi Alice,\\n\\nI wish you a very Happy Birthday.\\n\\nI hope you had a great day."
        Result               : None (side-effect only — email is sent via SMTP)
        Public interface     : ``send_email(recipient, message)``
        Dependencies         : smtplib, ssl (external network I/O — inject/mock in tests)
        Mutation behaviour   : no instance state mutated; network side-effect only

    Runnable Example
    ----------------
    The following example shows the decisive state transition: how
    ``GmailEmailSender`` routes a birthday message to the SMTP server.
    External I/O (SMTP) is replaced by a ``StubEmailSender`` so the example
    runs without live credentials::

        >>> class StubEmailSender(EmailSender):
        ...     def __init__(self):
        ...         self.sent = []
        ...     def send_email(self, recipient, message):
        ...         self.sent.append((recipient, message))
        ...
        >>> sender = StubEmailSender()

        # Smallest valid input — empty recipient and message
        >>> sender.send_email("", "")
        >>> sender.sent
        [('', '')]

        # Ordinary input — birthday message for Alice
        >>> msg = BirthdayMessage.create_message("Alice")
        >>> sender.send_email("alice@example.com", msg)
        >>> sender.sent[-1][0]
        'alice@example.com'
        >>> "Happy Birthday" in sender.sent[-1][1]
        True

    Intermediate state: ``sender.sent`` accumulates ``(recipient, message)``
    tuples — one per ``send_email`` call — before any network I/O occurs.
    """

    @abstractmethod
    def send_email(self, recipient, message):
        pass


class GmailEmailSender(EmailSender):
    def __init__(self, sender_address, sender_password):
        self.sender_address = sender_address
        self.sender_password = sender_password

    def send_email(self, recipient, message):
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(self.sender_address, self.sender_password)
            server.sendmail(self.sender_address, recipient, message)


class BirthdayMessage:
    @staticmethod
    def create_message(fname):
        return f"""Hi {fname},

I wish you a very Happy Birthday.

I hope you had a great day."""


class BirthdayListManager:
    def __init__(self, filename):
        self.filename = filename

    def load_birthdays(self):
        with open(self.filename) as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            return list(reader)

    def add_birthday(self, new_data):
        with open(self.filename, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(new_data)

    def remove_birthday(self, first_name):
        updated_lines = []          # precondition anchor: updated_lines = []
        with open(self.filename, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[0] != first_name:
                    updated_lines.append(row)

        with open(self.filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(updated_lines)


class BirthdayNotifier:
    def __init__(self, email_sender, birthday_list_manager):
        self.email_sender = email_sender
        self.birthday_list_manager = birthday_list_manager

    def notify_birthdays(self):
        birthdays = self.birthday_list_manager.load_birthdays()
        for fname, lname, email, dob in birthdays:
            message = BirthdayMessage.create_message(fname)
            self.email_sender.send_email(email, message)


def main():
    sender_address = "you@example.com"
    sender_password = "examplePassword"
    birthday_file = "birthday.csv"

    email_sender = GmailEmailSender(sender_address, sender_password)
    birthday_list_manager = BirthdayListManager(birthday_file)
    notifier = BirthdayNotifier(email_sender, birthday_list_manager)

    notifier.notify_birthdays()

    while True:
        choice = input(
            """Do you wish to add or remove names from the csv file?
            If you would like to add names type 'add'
            Otherwise if you would like to remove names type 'remove'
            When you are finished, type 'exit': """
        ).strip().lower()

        if choice == "exit":
            break
        elif choice == "add":
            new_data = input("Enter data as first name,lastname,email,date of birth: ")
            new_data = new_data.split(",")
            birthday_list_manager.add_birthday(new_data)
        elif choice == "remove":
            removal = input("Enter the first name of the person to be removed: ")
            birthday_list_manager.remove_birthday(removal)
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
