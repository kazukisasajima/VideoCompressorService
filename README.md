# Video Compressor Service

## 概要

このサービスは、ユーザーが動画ファイルをアップロードして、サーバのリソースを使ってさまざまな動画処理を行えるように設計されています。ユーザーは、圧縮や解像度・アスペクト比の調整、音声変換、GIF や WEBM の作成などを、クライアントインターフェースから実行できます。このサービスでは、[FFMPEG](https://ffmpeg.org/about.html) ライブラリを用いてタスクを実行します。<br>
このプロジェクトはコンピュータサイエンス学習サービス[Recursion](https://recursion.example.com)の課題で取り組みました。


## 機能

- 動画ファイルの圧縮
  - このサービスは動画ファイルをユーザーに代わって圧縮し、自動的に最適な圧縮方法を選びます。サービスは、大きなファイルサイズの削減を実現しながらも、オリジナルに近い画質を維持した動画を返す必要があります。

- 動画の解像度の変更
  - ユーザーが動画をアップロードし、望む解像度を選ぶと、その解像度に変換された動画が返されます。

- 動画のアスペクト比の変更
  - ユーザーが動画をアップロードし、望むアスペクト比を選ぶと、そのアスペクト比に変換された動画が返されます。

- 動画をオーディオに変換
  - ユーザーが動画ファイルをアップロードすると、その動画から音声だけを抽出した MP3 バージョンが返されます。

- 時間範囲での GIF と WEBM の作成
  - ユーザーが動画をアップロードし、時間範囲を指定すると、その部分を切り取り、GIF または WEBM 形式に変換して返します。


## インストール
以下の手順でffmpegをインストール

1.FFMPEGの公式サイトからバイナリをダウンロード
```sh
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
```

2.ダウンロードしたファイルを解凍
```sh
tar -xvf ffmpeg-release-amd64-static.tar.xz
```

3.ffmpegバイナリを適切なディレクトリに移動（例: /usr/local/bin）
```sh
sudo mv ffmpeg-*-amd64-static/ffmpeg /usr/local/bin/
```
```sh
sudo mv ffmpeg-*-amd64-static/ffprobe /usr/local/bin/
```


## 実行方法

- 以下のコマンドを使用して、実行できます。

```sh
python3 server.py
```
```sh
python3 client.py
```

クライアント側のターミナルでは以下の手順で入力を行います。

- アップロードするファイルを入力します
```sh
Type in a video file to upload:
```

- 実行したい操作を入力します
```sh
Enter the operation (compress, resolution, aspect_ratio, audio, gif, webm):
```

- 動画を圧縮する (compress)  
この操作には追加のオプションは必要ありません。optionsを空にしてEnterを押してください。
```sh
Enter the options for the operation: 
```

- 動画の解像度を変更する (resolution)  
希望する解像度を入力します。例えば、720pに変更する場合：
```sh
Enter the resolution (e.g., 1280x720):
```

- 動画のアスペクト比を変更する (aspect_ratio)  
希望するアスペクト比を入力します。例えば、16:9に変更する場合：
```sh
Enter the aspect ratio (e.g., 16:9):
```

- 動画を音声に変換する (audio)  
この操作には追加のオプションは必要ありません。optionsを空にしてEnterを押してください。
```sh
Enter the options for the operation: 
```

- 指定した時間範囲で GIF や WEBM を作成 (gif)  
開始時間と終了するまでの時間を入力します。：
```sh
Enter the start time (e.g., 00:00:00):
Enter the duration (in seconds):
```



### 注意
- 名前付きパイプ（UNIXソケット）を使用しているため、Windowsの標準的なコマンドプロンプトやPowerShellでは動作しません。
- このアプリケーションはLinuxまたはWSL（Windows Subsystem for Linux）環境で動作します。
