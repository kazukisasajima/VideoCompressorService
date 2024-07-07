import socket
import os
import json
import subprocess

def protocol_header(json_length, media_type_length, payload_length):
    return json_length.to_bytes(2, 'big') + media_type_length.to_bytes(1, 'big') + payload_length.to_bytes(5, 'big')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = '0.0.0.0'
server_port = 9001
sock.bind((server_address, server_port))
sock.listen(1)

upload_dir = 'upload_files'
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

def run_ffmpeg_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f'FFmpeg error: {e}')
        return False
    return True

while True:
    connection, client_address = sock.accept()
    try:
        print(f'Connection from {client_address}')

        # ヘッダの受信（8バイト）
        header = connection.recv(8)
        print(f"Received header: {header}")
        json_size = int.from_bytes(header[:2], 'big')
        media_type_size = header[2]
        payload_size = int.from_bytes(header[3:], 'big')
        print(f"JSON size: {json_size}, Media type size: {media_type_size}, Payload size: {payload_size}")

        # JSONデータの受信
        json_data = connection.recv(json_size).decode('utf-8')
        print(f"Received JSON data: {json_data}")

        # メディアタイプの受信
        media_type = connection.recv(media_type_size).decode('utf-8')
        print(f"Received media type: {media_type}")

        request = json.loads(json_data)
        operation = request.get('operation')
        options = request.get('options')

        # ファイルの保存
        filepath = os.path.join(upload_dir, 'uploaded_file.' + media_type)
        with open(filepath, 'wb') as f:
            remaining = payload_size
            while remaining:
                chunk_size = 1400 if remaining >= 1400 else remaining
                chunk = connection.recv(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                remaining -= len(chunk)
                print(f"Remaining bytes: {remaining}")

        print(f'File {filepath} received successfully.')

        # 処理されたファイルのパス
        output_filepath = os.path.join(upload_dir, 'processed_file.' + media_type)
        ffmpeg_command = ""

        if operation == 'compress':
            output_filepath = os.path.join(upload_dir, 'compressed_' + os.path.basename(filepath))
            ffmpeg_command = f"ffmpeg -i {filepath} -vcodec libx264 {output_filepath}"
        elif operation == 'resolution':
            resolution = options.get('resolution', '640x480')
            ffmpeg_command = f"ffmpeg -i {filepath} -vf scale={resolution} {output_filepath}"
        elif operation == 'aspect_ratio':
            aspect_ratio = options['aspect_ratio']
            width, height = map(float, aspect_ratio.split(':'))
            aspect_ratio_value = width / height
            output_filepath = os.path.join(upload_dir, f"aspect_ratio_{os.path.basename(filepath)}")
            ffmpeg_command = f"ffmpeg -i {filepath} -vf \"scale='if(gt(a,{aspect_ratio_value}),iw,-1)':'if(gt(a,{aspect_ratio_value}),-1,ih)',pad='max(iw,ih*{aspect_ratio_value})':'max(iw/{aspect_ratio_value},ih)'\" {output_filepath}"
        elif operation == 'audio':
            output_filepath = os.path.join(upload_dir, 'audio_' + os.path.basename(filepath).replace('.mp4', '.mp3'))
            ffmpeg_command = f"ffmpeg -i {filepath} -q:a 0 -map a {output_filepath}"
        elif operation == 'gif':
            start_time = options.get('start_time', '00:00:00')
            duration = options.get('duration', '5')
            output_filepath = os.path.join(upload_dir, 'clip_' + os.path.basename(filepath).replace('.mp4', '.gif'))
            ffmpeg_command = f"ffmpeg -i {filepath} -ss {start_time} -t {duration} -vf 'fps=10,scale=320:-1:flags=lanczos' {output_filepath}"
        elif operation == 'webm':
            start_time = options.get('start_time', '00:00:00')
            duration = options.get('duration', '5')
            output_filepath = os.path.join(upload_dir, 'clip_' + os.path.basename(filepath).replace('.mp4', '.webm'))
            ffmpeg_command = f"ffmpeg -i {filepath} -ss {start_time} -t {duration} -c:v libvpx -crf 10 -b:v 1M -c:a libvorbis {output_filepath}"

        if ffmpeg_command:
            print(f'Running FFmpeg command: {ffmpeg_command}')
            success = run_ffmpeg_command(ffmpeg_command)
            if success and os.path.exists(output_filepath):
                with open(output_filepath, 'rb') as f:
                    processed_data = f.read()
                response_json = json.dumps({"status": "success"}).encode('utf-8')
                response_header = protocol_header(len(response_json), len(media_type), len(processed_data))
                connection.sendall(response_header)
                connection.sendall(response_json)
                connection.sendall(media_type.encode('utf-8'))
                connection.sendall(processed_data)
            else:
                error_message = {"error": "Processing failed"}
                error_message = json.dumps(error_message).encode('utf-8')
                response_header = protocol_header(len(error_message), len('json'), 0)
                connection.sendall(response_header)
                connection.sendall(error_message)
                connection.sendall(b'json')
        else:
            error_message = {"error": "Invalid operation"}
            error_message = json.dumps(error_message).encode('utf-8')
            response_header = protocol_header(len(error_message), len('json'), 0)
            connection.sendall(response_header)
            connection.sendall(error_message)
            connection.sendall(b'json')
    except Exception as e:
        print(f'Error: {e}')
    finally:
        connection.close()
