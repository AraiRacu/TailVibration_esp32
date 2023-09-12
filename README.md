# TailViberation_esp32

## 概要

VRChatのOSC通信機能を利用し，VRC内で尻尾を掴まれたら，腰に設置したESP32を経由して，振動子が振動することで，掴まれていることを気づけるハプティックデバイスです．

VRChatのOSC通信はローカルPC上のPythonで受け取り，ESP32へOSC通信を行う2段構成になっています．

デバイス自体の説明は今後追加する予定です．

## 導入方法

### 環境構築

1. ArduinoIDEの導入<br>
以下のURLを参照し，インストールしてください．<br>
https://kanpapa.com/today/2022/12/esp32-otafab-study-arduino.html

2. Pythonの導入<br>
以下のURLを参照し，インストールしてください．<br>
https://www.javadrive.jp/python/install/index1.html

### ライブラリ追加

1. ArduinoOSCの導入<br>
ESP32でOSC通信ができるように"ArduinoOSC"を導入します．<br>
ArduinoIDEのライブラリマネージャーから"ArduinoOSC"を検索し，インストールしてください．<br>
<img src="image/arduinoosc.png" width="400">

1. python-oscの導入<br>
PythonでOSC通信ができるように"python-osc"を導入します．<br>
コマンドプロンプトを開き，以下のコマンドを入力します．<br>
`pip install python-osc`<br>
インストールが成功後，以下のコマンドを入力し，インストール済みのライブラリを表示します．<br>
その中に"python-osc"が含まれていれば成功です．<br>
`python -m pip freeze`<br>

参考：https://pypi.org/project/python-osc/

### VRChatアバター設定(WIP : 触れると振動する設定は今後追加予定)

1. Unityでの設定<br>
画像のように尻尾に追加したPhysBoneの"Option"に任意のパラメータを入力してください．<br>
`[ここで設定したパラメータ名]_IsGrabbed`が今回用いるパラメータになります．<br>
入力後，アバターをアップロードしてください．<br>
※デフォルトは"Tail"です．任意のパラメータ名にするとPythonのコードを書き換える必要があります．<br>
<br>
<img src="image/vrc1.png" width="400">

2. jsonファイルの追記<br>
PhysBoneで設定したパラメータがOSCとして送信されるように設定します．<br>
VRChatの一時フォルダを開きます．(一時フォルダを変更している場合は変更先を参照してください)<br>
`C:\Users\(ユーザ名)\AppData\LocalLow\VRChat\VRChat\OSC\(ユーザID)\Avatars\`<br>
この中から，適用したいアバターのjsonファイルを探し，テキストエディタで開きます．<br>
`(アバター名)_(アバターID).json`<br>
ファイルを開いたら，以下のコードを追記します．(`<!--ここから-->, <!--ここまで-->`は含めないでください)<br>
PhysBoneで設定したパラメータが"Tail"ではない場合，コード内の"Tail"を設定したパラメータ名に書き換えてください．<br>
追記後，保存して閉じてください．<br>
```json
{
  "id": "[アバターID]",
  "name": "[アバター名]",
  "parameters": [
    <!--ここから-->
    {
      "name": "Tail_Stretch",
      "input": {
        "address": "/avatar/parameters/Tail_Stretch",
        "type": "Float"
      },
      "output": {
        "address": "/avatar/parameters/Tail_Stretch",
        "type": "Float"
      }
    },
    {
      "name": "Tail_Angle",
      "input": {
        "address": "/avatar/parameters/Tail_Angle",
        "type": "Float"
      },
      "output": {
        "address": "/avatar/parameters/Tail_Angle",
        "type": "Float"
      }
    },
    {
      "name": "Tail_IsGrabbed",
      "input": {
        "address": "/avatar/parameters/Tail_IsGrabbed",
        "type": "Bool"
      },
      "output": {
        "address": "/avatar/parameters/Tail_IsGrabbed",
        "type": "Bool"
      }
    },
    <!--ここまで-->
    {
      "name": "VRCFaceBlendH",
      "input": {
        "address": "/avatar/parameters/VRCFaceBlendH",
        "type": "Float"
      },
      "output": {
        "address": "/avatar/parameters/VRCFaceBlendH",
        "type": "Float"
      }
    },
    ︙
```
参考：https://note.com/33linn/n/n2f60b5155ee3

### ソースコードのダウンロード

本システムのコードをダウンロードします．<br>
リポジトリをクローンするか，直接ダウンロードしてください．<br>
ダウンロード後，ファイルを任意の場所に開きます．

<img src="image/downloadcode.png" width="600">

### Python側設定

OSCSendArduino_V2.pyをテキストエディタで開きます．<br>
10行目以降のコードに対して，それぞれ，
- esp32IP : ESP32のIPアドレスを設定します．任意のアドレスを設定できますが，使用していないアドレスを使ってください．
- targetPort : ESP32のポート番号を設定します．番号は任意ですが，予約されている番号は利用しないほうが無難です．

設定完了後は保存してください．
```Python
esp32IP = "192.168.XX.XX" # デバイスのIPアドレス
targetPort = XXXX #接続するポート番号
```

### ESP32側設定

VibeTail_esp32.inoをArduinoIDEで開きます．<br>

まず，コードの設定を入力します．<br>
8行目以降のコードに対して，それぞれ，
- ssid : WifiルータのSSIDを入力します．
- pass : Wifiルータのパスワードを入力します．
- ip : OSCSendArduino_V2.pyで設定したIPアドレスを入力します．
- gateway : ネットワークのデフォルトゲートウェイを入力します．※
- subnet : ネットワークのサブネットマスクを入力します．※
- pc_addr : 送信元のPCのIPアドレスを入力します．※
- pc_port : OSCSendArduino_V2.pyで設定したポート番号を入力します．

設定し終えたら，一旦保存してください．<br>
※PCのネットワークの各パラメータはコマンドプロンプト上で`ipconfig`を入力すると一覧で表示されます． <br>
参考：https://youtm-log.com/setting/windows-setting/ipadress_check/

```C++
const char* ssid = "SSID"; //WiFIのSSIDを入力
const char* pass = "Pass"; // WiFiのパスワードを入力

const IPAddress ip(192, 168, XX, XX); //自身のIPアドレス
const IPAddress gateway(192, 168, XX, XX); //デフォルトゲートウェイ
const IPAddress subnet(255, 255, XX, XX); //サブネットマスク

const char *pc_addr = "192.168.XX.XX";  //送信元のPCのIPアドレス
const int pc_port = XXXX; //受信先のポート
```

次に，書き込む対象を設定するために，左上の"ボードを選択"をクリックします．<br>
表示されるいくつかの「不明 COM...」の内，ESP32を付けたり外したりして変化があるものを選択してください．<br>
開いたポップアップに対して，今回使用するボード(今回はESP32 Dev Module)とESP32が繋がっているUSBポートを選択します．

<img src="image/selectBoard1.png" width="500">

<img src="image/buildArduino.png" width="500">

設定後，左上の書き込みボタンを押し，ESP32に書き込んでください．<br>
ArduinoIDEのコンソール画面に以下のようなログが表示されれば書き込み完了です．<br>
この状態になれば，デバイスを繋いでいるUSBを抜いても問題ありません．<br>
<img src="image/compile.png" width="500">

```
Writing at 0x000dc5db... (94 %)
Writing at 0x000e1b2f... (97 %)
Writing at 0x000e734c... (100 %)
Wrote 894880 bytes (566332 compressed) at 0x00010000 in 8.7 seconds (effective 824.9 kbit/s)...
Hash of data verified.

Leaving...
Hard resetting via RTS pin...
```


## 起動方法

モバイルバッテリーを繋いだ状態でESP32のLEDが光るとデバイスの準備完了です．<br>
VRChatを動かすPC上でOSCSendArduino_V2.pyをダブルクリックし，起動させてください．<br>
コマンドプロンプトが表示され，以下の表示がされたら準備完了です．<br>
その後，VRChatを起動し，対応したアバターに変更すると尻尾を掴んだ際に，デバイスが振動するようになります．<br>
※VRChat，Python，デバイスはどれから起動しても問題ありません．<br>
<img src="image/pythonStart.png" width="300">