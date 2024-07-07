import socket
import os

def protocol_header(filename_length, data_length):
    return data_length.to_bytes(4, 'big') + filename_length.to_bytes(1, 'big')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = '127.0.0.1'
server_port = 9001

try:
    sock.connect((server_address, server_port))
except socket.error as err:
    print(f'Connection error: {err}')
    exit(1)

try:
    filepath = input('Type in a mp4 file to upload: ')

    # バイナリモードでファイルを読み込む
    with open(filepath, 'rb') as f:
        f.seek(0, os.SEEK_END)
        filesize = f.tell()
        f.seek(0)

        print(f"Filesize: {filesize}")

        if filesize > pow(2, 32):
            raise Exception('File must be below 4GB.')

        filename = os.path.basename(filepath)
        filename_bits = filename.encode('utf-8')

        # ヘッダ情報の作成
        header = protocol_header(len(filename_bits), filesize)
        print(f"Header: {header}")

        # ヘッダの送信
        sock.send(header)
        print(f"Sent header")

        # ファイル名の送信
        sock.send(filename_bits)
        print(f"Sent filename: {filename}")

        # ファイル内容の送信
        while True:
            data = f.read(1400)
            if not data:
                break
            sock.sendall(data)

        print(f"File {filename} sent successfully.")

    # サーバーからの応答受信
    response = sock.recv(16)
    print(f'Server response: {response.decode("utf-8")}')
except Exception as e:
    print(f'Error: {e}')
finally:
    sock.close()
