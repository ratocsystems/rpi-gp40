# RASPBIANの設定

Rapberry Pi用OS RASPBIANの設定について説明します。  
Raspberry Piは'Raspberry Pi3 ModelB'、OSは'Raspbian Stretch with desktop(NOOBS:2018-03-14)'で説明します。  

## Raspbianのインストール  
1) Class10のmicroSD(8～32G)を用意します。  
*64GB以上のSDカードの場合、exFATでフォーマットされます。
RaspbianはexFATに対応していませんので、別のツールを使ってFAT16またはFAT32でフォーマットする必要があります。*

2) SDカード用フォーマッターとユーザーマニュアルをダウンロードします。  
SDアソシエーションのダウンロードページから'SDメモリカードフォーマッター'と'ユーザーマニュアル'をダウンロードします。
https://www.sdcard.org/jp/downloads/formatter_4/index.html

3) 'SDメモリカードフォーマッター'を使って、SDカードをフォーマットします。
ファーマット方法につきましては、ダウンロードしたユーザーマニュアルをご参照ください。

4) Raspberry財団公式ホームページで
https://www.raspberrypi.org/downloads/noobs/  
「NOOBS」(Download ZIP)をPCでダウンロードし解凍します。  
解凍後、フォルダー内のデータ全てをmicroSDにコピーします。

5) microSDをRaspberry Pi基板に接続し起動します。  
   [言語]に「日本語」を選択し、[Raspbian [RECOMMENDED]]にチェックを入れ「インストール」をクリックします。  

   ![01](/install/img/Raspi_01.png)  

6) 警告画面で「はい」をクリックします。

   ![02](/install/img/Raspi_02.png)  

7) インストール成功の画面が表示されますので「OK」をクリックします。

   ![03](/install/img/Raspi_03.png)  


## I2Cの有効設定  

8) OSを起動し、[設定]-[Rapberry Piの設定]をクリックします。  

   ![04](/install/img/Raspi_04.png)  

9) [インターフェース]で"I2C"を有効にし、OSを再起動します。

   ![05](/install/img/Raspi_05.png)  


以上でRaspbianのインストールと設定は完了です。


