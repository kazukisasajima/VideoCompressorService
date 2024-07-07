import cv2
import numpy as np

# 動画ファイルの設定
filename = 'test.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps = 24.0
frame_size = (640, 480)

# 動画ファイル作成
out = cv2.VideoWriter(filename, fourcc, fps, frame_size)

# 1秒分のビデオ（24フレーム）を生成
for _ in range(24):
    # ランダムな色のフレームを生成
    frame = np.random.randint(0, 256, frame_size + (3,), dtype=np.uint8)
    out.write(frame)

# ファイルを閉じる
out.release()
print(f'File {filename} created successfully.')
