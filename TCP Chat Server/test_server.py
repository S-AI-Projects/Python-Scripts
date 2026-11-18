import os
import sys
import unittest
from unittest.mock import MagicMock

# Ensure TCP Chat Server directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import server as chat_server


def independent_oracle_session(raw_bytes: bytes, reply_str: str, address=("127.0.0.1", 5000)):
    """
    Independent reference oracle for TCP chat message exchange.
    Calculates expected decoded incoming string and outgoing encoded bytes independently.
    """
    decoded = raw_bytes.decode("utf-8")
    sent_bytes = reply_str.encode("utf-8")
    return {
        "address": address,
        "decoded": decoded,
        "reply": reply_str,
        "sent_bytes": sent_bytes,
        "tuple": (address, decoded, reply_str),
    }


class TestTcpChatServer(unittest.TestCase):
    """
    Focused cross-check tests for TCP Chat Server (server.py).
    Precondition source lines:
      - server.py:3 establishes IP = '0.0.0.0'
      - server.py:4 establishes PORT = 3000
      - server.py:7 establishes handle_client_connection
      - server.py:27 establishes main listener
    """

    def test_preconditions(self):
        self.assertEqual(chat_server.IP, "0.0.0.0")
        self.assertEqual(chat_server.PORT, 3000)

    def test_smallest_valid_input(self):
        # Smallest valid input: empty byte string and empty reply
        mock_client = MagicMock()
        mock_client.recv.return_value = b""
        address = ("127.0.0.1", 50001)

        addr, decoded, send = chat_server.handle_client_connection(
            mock_client, address, input_func=lambda prompt: ""
        )
        self.assertEqual(addr, address)
        self.assertEqual(decoded, "")
        self.assertEqual(send, "")
        mock_client.send.assert_called_once_with(b"")

    def test_ordinary_valid_input(self):
        # Ordinary input: standard greetings
        mock_client = MagicMock()
        mock_client.recv.return_value = b"Hello from client"
        address = ("192.168.1.10", 42000)

        addr, decoded, send = chat_server.handle_client_connection(
            mock_client, address, input_func=lambda prompt: "Hello from server"
        )
        self.assertEqual(addr, address)
        self.assertEqual(decoded, "Hello from client")
        self.assertEqual(send, "Hello from server")
        mock_client.send.assert_called_once_with(b"Hello from server")

    def test_oracle_cross_check_25_inputs(self):
        # Generate 25 distinct test cases cross-checked against independent oracle
        test_cases = [
            (b"", ""),
            (b"a", "b"),
            (b"123", "456"),
            (b"ping", "pong"),
            (b"hello world", "goodbye world"),
            (b"test message 001", "ack 001"),
            (b"special chars !@#$%", "reply ^&*()"),
            (b"multiline\nfirst line\nsecond line", "multiline\nresponse"),
            (b"spaces   and   tabs\t\t", "trimmed or raw"),
            (b"json-like {\"key\": \"value\"}", "{\"status\": \"ok\"}"),
            (b"unicode: \xe2\x9c\x93 checkmark", "unicode reply: \xe2\x9c\x94"),
            (b"upper CASE text", "lower case text"),
            (b"numeric 9876543210", "numeric 0123456789"),
            (b"boolean True", "boolean False"),
            (b"null byte inside text \x00 middle", "handled null byte \x00"),
            (b"http GET / HTTP/1.1", "HTTP/1.1 200 OK"),
            (b"repeat a" * 20, "repeat b" * 20),
            (b"long prefix " + b"x" * 100, "long ack " + "y" * 100),
            (b"emoji test: \xf0\x9f\x98\x80", "emoji response: \xf0\x9f\x91\x8d"),
            (b"boundary length 1", "response length 1"),
            (b"csv,col1,col2,col3", "ack,row1,row2"),
            (b"python code: x = 10", "python exec: pass"),
            (b"quit", "bye"),
            (b"exit", "closing connection"),
            (b"final 25th payload", "final ack 25"),
        ]
        self.assertEqual(len(test_cases), 25)

        for idx, (raw_in, reply_in) in enumerate(test_cases):
            addr = ("10.0.0." + str(idx + 1), 6000 + idx)
            mock_client = MagicMock()
            mock_client.recv.return_value = raw_in

            # Actual execution
            act_addr, act_decoded, act_send = chat_server.handle_client_connection(
                mock_client, addr, input_func=lambda prompt, r=reply_in: r
            )

            # Oracle calculation
            oracle = independent_oracle_session(raw_in, reply_in, address=addr)

            # Compare actual with oracle
            self.assertEqual(act_addr, oracle["address"])
            self.assertEqual(act_decoded, oracle["decoded"])
            self.assertEqual(act_send, oracle["reply"])
            mock_client.send.assert_called_once_with(oracle["sent_bytes"])

    def test_main_controlled_loop(self):
        # Verify main executes loop under controlled socket mock
        mock_server = MagicMock()
        mock_client = MagicMock()
        mock_client.recv.return_value = b"test payload"
        mock_server.accept.return_value = (mock_client, ("127.0.0.1", 9999))

        sessions = chat_server.main(
            server_socket=mock_server,
            max_iterations=2,
            input_func=lambda prompt: "server reply",
        )
        self.assertEqual(len(sessions), 2)
        self.assertEqual(sessions[0], (("127.0.0.1", 9999), "test payload", "server reply"))
        self.assertEqual(sessions[1], (("127.0.0.1", 9999), "test payload", "server reply"))


if __name__ == "__main__":
    unittest.main()
