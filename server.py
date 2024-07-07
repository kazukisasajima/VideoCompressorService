import socket
import os

# サーバーの設定
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = '0.0.0.0'
server_port = 9001
sock.bind((server_address, server_port))
sock.listen(1)

upload_dir = 'upload_files'
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

while True:
    connection, client_address = sock.accept()
    try:
        print(f'Connection from {client_address}')

        # ヘッダの受信（32バイト）
        header = connection.recv(32)
        print(f"Received header: {header}")
        filesize = int.from_bytes(header[:4], 'big')
        filename_length = header[4]
        print(f"Filesize: {filesize}, Filename length: {filename_length}")

        # ファイル名の受信
        filename = connection.recv(filename_length).decode('utf-8')
        print(f"Filename: {filename}")

        # ファイルの保存先
        filepath = os.path.join(upload_dir, filename)
        print(f"Saving file to: {filepath}")

        # ファイル内容の受信
        with open(filepath, 'wb') as f:
            remaining = filesize
            while remaining:
                chunk_size = 1400 if remaining >= 1400 else remaining
                chunk = connection.recv(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                remaining -= len(chunk)
                print(f"Remaining bytes: {remaining}")

        print(f'File {filename} received successfully.')

        # ステータス応答の送信
        status_message = "File received successfully".encode('utf-8')
        connection.sendall(status_message.ljust(16)[:16])
    except Exception as e:
        print(f'Error: {e}')
    finally:
        connection.close()
