import socket

IP = '0.0.0.0'
PORT = 3000


def handle_client_connection(client, address, input_func=input):
    """
    Handle a single client communication exchange.

    Contract:
    - Preconditions:
        * TCP Chat Server/server.py:3 establishes IP = '0.0.0.0'
        * TCP Chat Server/server.py:4 establishes PORT = 3000
    - Input: client socket, address tuple (host, port), optional input_func.
    - Receives up to 4096 bytes from client.
    - Decodes data as UTF-8 string.
    - Prompts input_func('Send message> ') and sends UTF-8 encoded response back to client.
    - Returns tuple: (address, decoded_data, response_str).
    """
    data = client.recv(4096)
    decoded_data = data.decode()
    print(decoded_data)

    send = input_func('Send message> ')
    client.send(send.encode())
    return address, decoded_data, send


def main(server_socket=None, max_iterations=None, input_func=input):
    """
    TCP Chat Server main listener loop.

    Contract & Behavior:
    - Sets up socket listening on (IP, PORT) if server_socket is None.
    - If max_iterations is set, loops max_iterations times; otherwise loops indefinitely.
    - Processes incoming connections with handle_client_connection.
    - Returns list of processed session summaries [(address, decoded_data, sent_msg), ...].
    """
    if server_socket is None:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((IP, PORT))
        server.listen(5)
    else:
        server = server_socket

    print(f'Server is listening on {IP}:{PORT}')

    results = []
    count = 0
    while max_iterations is None or count < max_iterations:
        client, address = server.accept()
        print(f'Received a connection from {address[0]}:{address[1]}')
        session = handle_client_connection(client, address, input_func=input_func)
        results.append(session)
        count += 1

    return results


if __name__ == '__main__':
    main()
