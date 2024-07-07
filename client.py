import socket
import os
import json

def protocol_header(json_length, media_type_length, payload_length):
    return json_length.to_bytes(2, 'big') + media_type_length.to_bytes(1, 'big') + payload_length.to_bytes(5, 'big')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = '127.0.0.1'
server_port = 9001

try:
    sock.connect((server_address, server_port))
except socket.error as err:
    print(f'Connection error: {err}')
    exit(1)

try:
    filepath = input('Type in a video file to upload: ')
    operation = input('Enter the operation (compress, resolution, aspect_ratio, audio, gif, webm): ')
    options = {}

    if operation == 'resolution':
        options['resolution'] = input('Enter the resolution (e.g., 1280x720): ')
    elif operation == 'aspect_ratio':
        options['aspect_ratio'] = input('Enter the aspect ratio (e.g., 16:9): ')
    elif operation in ['gif', 'webm']:
        options['start_time'] = input('Enter the start time (e.g., 00:00:00): ')
        options['duration'] = input('Enter the duration (in seconds): ')

    json_data = json.dumps({"operation": operation, "options": options}).encode('utf-8')
    json_size = len(json_data)
    media_type = 'mp4'
    media_type_size = len(media_type.encode('utf-8'))

    with open(filepath, 'rb') as f:
        f.seek(0, os.SEEK_END)
        filesize = f.tell()
        f.seek(0)

        print(f"Filesize: {filesize}")

        if filesize > pow(2, 32):
            raise Exception('File must be below 4GB.')

        header = protocol_header(json_size, media_type_size, filesize)
        print(f"Header: {header}")

        sock.send(header)
        sock.send(json_data)
        sock.send(media_type.encode('utf-8'))
        print("Sent header, JSON data, and media type")

        while True:
            data = f.read(1400)
            if not data:
                break
            sock.sendall(data)

        print(f"File {filepath} sent successfully.")

        response_header = sock.recv(8)
        response_json_size = int.from_bytes(response_header[:2], 'big')
        response_media_type_size = response_header[2]
        response_payload_size = int.from_bytes(response_header[3:], 'big')

        response_json_data = sock.recv(response_json_size).decode('utf-8')
        response_media_type = sock.recv(response_media_type_size).decode('utf-8')
        response_payload_data = b''

        if response_payload_size > 0:
            while len(response_payload_data) < response_payload_size:
                response_payload_data += sock.recv(response_payload_size - len(response_payload_data))

        print(f'Server response JSON: {response_json_data}')
        print(f'Server response media type: {response_media_type}')

        if response_payload_size > 0:
            output_filepath = 'output.' + response_media_type
            with open(output_filepath, 'wb') as f:
                f.write(response_payload_data)
            print(f'Processed file saved as {output_filepath}')

except Exception as e:
    print(f'Error: {e}')
finally:
    sock.close()
