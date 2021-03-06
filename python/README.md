# RPi-GP40用Pythonサンプルファイル

RPi-GP40用Pythonサンプルファイルの使用方法について説明します。  
Raspberry Piは'Raspberry Pi3 ModelB'、OSは'Raspbian Stretch with desktop(NOOBS:2018-03-14)'で説明します。
サンプルファイルは`sampleGp40.py`です。  

  
***
## 準備
### Raspberry PiにRPi-GP40を接続
[README.md](../README.md)を参考に下記の準備をおこなってください。  
- OS(`RASPBIAN`)のインストール
- GPIO40pinのSPI設定
- 'Raspberry Pi'に'RPi-GP40'を接続  
  

### Pythonサンプルファイルを実行するディレクトリを作成
1. 'mkdir'コマンドを使って'RPi-GP40'という名前のディレクトリを作成します。(ディレクトリ名や作成場所は自由です)
    ```
    $ mkdir RPi-GP40  
    ```

1. 'ls'コマンドを実行して'RPi-GP40'ディレクトリが作成されていること確認します。
    ```
    $ ls  
    ```

1. 'cd'コマンドで'RPi-GP40'ディレクトリに移動します。
    ```
    $ cd RPi-GP40  
    ```  
    
### PythonサンプルファイルをGitHubからダウンロード  
GitHubからPythonサンプルファイルをダウンロードします。
1. sampleGp40.pyをダウンロード
    ```
    $ wget https://github.com/ratocsystems/rpi-gp40/raw/master/python/sampleGp40.py  
    ```  

1. `ls`コマンドを実行してPythonサンプルファイル`sampleGp40.py`がダウンロードされていることを確認します。
    ```
    $ ls  
    sampleGp40.py
    ```
  
***
## Pythonサンプルファイルについて
  
`sampleGp40.py`  

アナログ入力やデジタル入出力を制御するPythonサンプルプログラムです。  
サンプルプログラムでは下記の処理を行っています。

1. **RaspberryPi SPI機能設定**  
    SPIとGPIOの初期値を設定します。  
    - SPI(SPI0, CEN0)を使用するためにコネクションオブジェクト取得
    - RPi-GP40を制御するSPIモード設定  
        SPIクロック設定モード:1  
        `CPOL=0[正論理], CPHA=1[H->Lでデータ取り込み]`
    - SPIクロック最大周波数設定  
        SPIクロック最大周波数:17MHz  
        `ただし、2018年4月時点のカーネル仕樣では、指定値より実周波数が低くなります  17MHz→10.5MHz, 10MHz→6.2MHz, 8MHz→5MHz`
    - デジタル出力端子用GPIO番号を設定  
        デフォルトはGPIO12ですが、基板上のジャンパ抵抗JP8をJP7に変更することでGPIO14に設定することができます。
    - デジタル/アラーム入力端子用GPIO番号を設定  
        デフォルトはGPIO13ですが、基板上のジャンパ抵抗JP6をJP5に変更することでGPIO15に設定することができます。
      
1. **RPi-GP40の初期設定 init_GP40()**  
    GPIOの初期設定を行います。  
    ※<u>ハードウェアに依存する設定ですので変更しないでください。</u>  
    - GPIOをGPIO番号で指定するように設定
    - 絶縁回路用電源をONに設定  
        電源ON後、安定するまで待ちます。
    - デジタル出力端子を出力に設定し、初期状態をOFF(オープン)にします。
    - デジタル/アラーム入力端子を入力に設定します。

1. **入力レンジ設定 set_adrange(ch, range)**  
    ch0～ch7の入力レンジを初期値（引数なしの場合は`±10V`）に設定します。  

1. **引数による直接実行形式**  
    引数の指定があれば、指定された間隔で指定回数AD変換を実行し、結果を表示します。  

1. **引数なしの場合はメニュー実行形式**  
    引数の指定がなければ、メニュー実行形式でAD変換を実行します。  

1. **各chの入力レンジ設定値表示**  
    現在設定されている各chの入力レンジを表示します。  

1. **メニュー表示**  
    次のメニューを表示します。  
    `0-7:chレンジ設定, a:単一AD変換, b:連続AD変換, c:アラーム, d:デジタルIO, e:終了 >`

1. **0-7:chレンジ設定 set_adrange(ch, range)**  
    メニューで0～7が入力された場合は、指定chの入力レンジを設定します。  
    `0:±10V 1:±5V 2:±2.5V 3:±1.25V 4:±0.5V 5:0-10V 6:0-5V 7:0-2.5V 8:0-1.25V 9:0-20mA a:無効`  
    から入力レンジを選択します。`[a:無効]`が選択されたchはAD変換を実行しません。

1. **a:単一AD変換 print_adc(0, 1)**  
    間隔0秒で1回AD変換を実行し、結果を表示します。     

1. **b:連続AD変換 print_adc(interval, cnt)**  
    指定した間隔と回数でAD変換を実行し、結果を表示します。`[CTRL]+[C]` で中断します。

1. **c:アラーム　ene_adalarm(), set_adalarm(ch, hist, hth, lth)**  
    アラームのしきい値設定とコールバック関数の設定を行ないます。`[b:連続AD変換]`を実行中にここで指定されたしきい値をまたいだときにアラームのコールバックが実行されます。  
    - アラームメニュー  
    `アラーム 0-7:有効[ch], a:無効 >`  
    で、アラーム設定するchを指定します。`[a:無効]`が選択された場合はアラームのコールバックを解除設定します。  
    `ヒステリシス 0-15[LSB] >`  
    で、しきい値のヒステリシス間隔をLSBで指定します。  
    `上限/下限しきい値(HEX) 000-FFF >`  
    で、しきい値を3桁のHEXで指定します。

1. **d:デジタル入出力**  
    デジタル入力とデジタル出力を行ないます。  
    デジタル入力は、入力の`H->L`への変化を検知するとデジタル入力のコールバックが実行されます。  
    デジタル出力は、出力状態を  
    `デジタル出力 1:ON(Low) 0:OFF(High) a:戻る >`  
    で指定します。`[a:戻る]`が選択されるとデジタル入力のコールバックを解除してからメニューに戻ります。
  
1. **e:終了**  
    `[e:終了]`が選択されるとプログラムを終了します。  
      


***
## Pythonサンプルファイルの使い方
サンプルファイルの前に、`python3`をつけて実行します。

引数を付けてPythonサンプルファイル`sampleGp40.py`を実行すると、直接形式でAD変換を実行します。  
`例) ヘルプ表示後に、ch0を±5V, ch1を0-10V, その他を±10Vに設定し、1秒間隔で10回AD変換を実行する場合`  
~~~
$ python3 sampleGp40.py -h
usage: メニュー形式でRPi-GP40を制御します

引数を指定することで直接実行が可能です

optional arguments:
  -h, --help            show this help message and exit
  -r [R] [R] [R] [R] [R] [R] [R] [R], --range [R] [R] [R] [R] [R] [R] [R] [R]
                        [R]= 0:±10V 1:±5V 2:±2.5V 3:±1.25V 4:±0.5V 5:0-10V
                        6:0-5V 7:0-2.5V 8:0-1.25V 9:0-20mA 以外:無効
                        チャンネル0-7の入力レンジ(0-9)を指定 例: -r 0 0 5 5 6 6 6 9
  -t [T], --time [T]    [T]= AD変換間隔(1-1000)[秒]を指定 例: -t 1
  -c [C], --cnt [C]     [C]= AD変換回数(1-1000)[回]を指定 例: -c 100

--------------------------------------------------------------------------
$ python3 sampleGp40.py -r 1 5 0 0 0 0 0 0 -t 1 -c 10
     ±5V ch0:  0.0825[821]
   0-10V ch1:  0.0800[020]
    ±10V ch2:  0.0750[80F]
    ±10V ch3:  0.0650[80D]
    ±10V ch4:  0.0550[80B]
    ±10V ch5:  0.0450[809]
    ±10V ch6:  0.0300[806]
    ±10V ch7:  0.0150[803]
   10/10

pi@raspberrypi:~ $
~~~

引数をつけずにPythonサンプルファイル`sampleGp40.py`を実行すると、メニュー形式でAD変換を実行します。  
~~~
$ python3 sampleGp40.py
ch:レンジ= 0:±10V, 1:±10V, 2:±10V, 3:±10V, 4:±10V, 5:±10V, 6:±10V, 7:±10V
0-7:chレンジ設定, a:単一AD変換, b:連続AD変換, c:アラーム, d:デジタルIO, e:終了 >
~~~  

- **chレンジを設定する**  
    ch0～7の入力レンジを設定するには、設定するch番号を入力し、入力レンジを指定します。  
    `a:無効` を選択した場合はそのchはAD変換を行ないません。  
    `例) ch0を±5V, ch1を0-10Vに設定する場合`  
    ~~~
    0-7:chレンジ設定, a:単一AD変換, b:連続AD変換, c:アラーム, d:デジタルIO, e:終了 >0
    入力レンジ 0:±10V 1:±5V 2:±2.5V 3:±1.25V 4:±0.5V 5:0-10V 6:0-5V 7:0-2.5V 8:0-1.25V 9:0-20mA a:無効
    ch0 入力レンジ >1
    ch:レンジ= 0:±5V, 1:±10V, 2:±10V, 3:±10V, 4:±10V, 5:±10V, 6:±10V, 7:±10V
    0-7:chレンジ設定, a:単一AD変換, b:連続AD変換, c:アラーム, d:デジタルIO, e:終了 >1
    入力レンジ 0:±10V 1:±5V 2:±2.5V 3:±1.25V 4:±0.5V 5:0-10V 6:0-5V 7:0-2.5V 8:0-1.25V 9:0-20mA a:無効
    ch0 入力レンジ >5
    ch:レンジ= 0:±5V, 1:0-10V, 2:±10V, 3:±10V, 4:±10V, 5:±10V, 6:±10V, 7:±10V
    0-7:chレンジ設定, a:単一AD変換, b:連続AD変換, c:アラーム, d:デジタルIO, e:終了 >
    ~~~  

- **単一AD変換を行なう**  
    単一AD変換を行なう場合は `a:単一AD変換` を選択します。  
    ch0からch7を設定されたレンジで計測して、算出した電圧(電流)結果を表示します。
    ~~~
    0-7:chレンジ設定, a:単一AD変換, b:連続AD変換, c:アラーム, d:デジタルIO, e:終了 >a
     ±5V ch0:  1.9700[B14]
    ±10V ch1:  2.2250[9BD]
    ±10V ch2:  2.2250[9BD]
    ±10V ch3:  2.2250[9BD]
    ±10V ch4:  2.2250[9BD]
    ±10V ch5:  2.2250[9BD]
    ±10V ch6:  2.2250[9BD]
    ±10V ch7:  2.2250[9BD]
    ~~~  


- **連続AD変換を行なう**  
    連続AD変換を行なう場合は `b:連続AD変換` を選択します。  
    ch0からch7を設定されたレンジで計測して、算出した電圧(電流)結果を、指定された間隔[秒]で指定回数[回]連続して表示します。  
    連続AD変換中にアラームを検知した場合は、検知内容を表示して連続計測を中断します。
    ~~~
    0-7:chレンジ設定, a:単一AD変換, b:連続AD変換, c:アラーム, d:デジタルIO, e:終了 >b
     連続AD変換 間隔 1-1000[秒] >1
     連続AD変換 回数 1-1000[回] >10
     ±5V ch0:  2.7850[C5A]
    ±10V ch1: 10.2350[FFF]
    ±10V ch2:  2.0900[9A2]
    ±10V ch3:  1.7450[95D]
    ±10V ch4:  1.4000[918]
    ±10V ch5:  1.0500[8D2]
    ±10V ch6:  0.7000[88C]
    ±10V ch7:  0.3500[846]
    アラーム検知！ ch7-0:00000001  ch0-3Trip:40/Active:40, ch4-7Trip:00/Active:00
    ~~~  

- **アラームのしきい値を設定する**  
    アラームのしきい値を設定する場合は `c:アラーム` を選択します。  
    アラームを設定するch、ヒステリシス値、上限しきい値、下限しきい値を設定します。  
    連続AD変換中にしきい値を超えたときにアラーム状態となります。  
    `a:無効` を選択した場合はアラームを無効にします。  
    `例) ch0のアラーム設定を、ヒステリシス3[LSB],上限しきい値900[HEX],下限しきい値000[HEX]に設定する場合`  
    ~~~
    0-7:chレンジ設定, a:単一AD変換, b:連続AD変換, c:アラーム, d:デジタルIO, e:終了 >c
     アラーム 0-7:有効[ch], a:無効 >0
     ヒステリシス 0-15[LSB]    >3
     上限しきい値(HEX) 000-FFF >900
     下限しきい値(HEX) 000-FFF >000
    アラーム設定しました。連続AD変換中にアラーム検知で計測を中断します。
    ~~~  

- **デジタル入出力**  
    デジタル入出力を制御する場合は `d:デジタルIO` を選択します。  
    デジタル入力は、入力の`H->L`への変化を検知するとデジタル入力のコールバックが実行されます。  
    デジタル出力は、出力状態を指定します。  
    `a:戻る` が選択されるとデジタル入力のコールバックを解除してからメニューに戻ります。
    ~~~
    0-7:chレンジ設定, a:単一AD変換, b:連続AD変換, c:アラーム, d:デジタルIO, e:終了 >d
     デジタル出力 1:ON(Low) 0:OFF(High) a:戻る >1
     デジタル出力 1:ON(Low) 0:OFF(High) a:戻る >0
     デジタル出力 1:ON(Low) 0:OFF(High) a:戻る >
     ！デジタル入力DIN(H→L変化)検知！ ch0[C52]
     0
     デジタル出力 1:ON(Low) 0:OFF(High) a:戻る >a
    ch:レンジ= 0:±5V, 1:±10V, 2:±10V, 3:±10V, 4:±10V, 5:±10V, 6:±10V, 7:±10V
    ~~~  

- **終了**  
    終了する場合は `e:終了` を選択します。  
    ~~~
    0-7:chレンジ設定, a:単一AD変換, b:連続AD変換, c:アラーム, d:デジタルIO, e:終了 >e
    $
    ~~~
