#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2020-10-23: SPI CS端子をGPIO制御方式へ変更

import sys
import os
import time
import argparse
#import smbus            #I2C制御用
import spidev           #SPI制御用
import RPi.GPIO as GPIO #GPIO制御用


# グローバル変数
rstr = ["±10V","±5V","±2.5V","±1.25V","±0.5V","0-10V","0-5V","0-2.5V","0-1.25V","0-20mA","NONE"]   # レンジ文字列
chn  = [      0,     1,       2,        3,      11,      5,     6,       7,       15,       6,     0]   # レンジ選択レジスタへ書き込む値のテーブル
chu  = [  0x800, 0x800,   0x800,    0x800,   0x800,  0x000, 0x000,   0x000,    0x000,   0x000, 0x000]   # 実値変換減算値 0x800:バイポーラ 0x000:ユニポーラ
chm  = [   5.00,  2.50,    1.25,    0.625,  0.3125,   2.50,  1.25,   0.625,   0.3125,    5.00,   0.0]   # 実値変換乗算値 1LSB[mV](/[uA])
chr  = [0,0,0,0,0,0,0,0]         # ch0-7の入力レンジ初期値
adalarm = 0                      # ADアラーム 0:無効 1:有効
adach = 0                        # ADアラーム発生ch bit0-7=ch0-7 bit8=DIN
adadt = 0                        # デジタル入力検知時のADC ch0値
ADCS = 8                         # AD SPI CS端子のGPIO番号 8

# RPi-GP40初期設定
def init_GP40():
    GPIO.setmode(GPIO.BCM)                                # Use Broadcom pin numbering
    GPIO.setwarnings(False)
    GPIO.setup(ADCS, GPIO.OUT, initial=GPIO.HIGH)         # ADCS はGPIO端子として制御する
    GPIO.setup(27,   GPIO.OUT, initial=GPIO.HIGH )        # RPi-GP40絶縁電源ON
    GPIO.setup(DOUT, GPIO.OUT, initial=GPIO.LOW )         # DOUT端子出力設定 LOW (=OFF:オープン)
    GPIO.setup(DIN,  GPIO.IN,  pull_up_down=GPIO.PUD_OFF) # DIN端子入力設定
    time.sleep(0.5)                                       # 電源安定待ち

# ADCとのSPIデータ転送
# 2020-05-27以降のraspi-osで、SPI CS端子に余分な'L'パルスが発生する現象の対策としてGPIO制御方式へ変更(2020-10-23)
def xfer_spiadc( wd ):
    GPIO.output(ADCS, 0)         # SPI CS0='L' GPIO端子として制御する
    rd = spi.xfer(wd)
    GPIO.output(ADCS, 1)         # SPI CS0='H'
    return rd

# 指定chのレンジ選択レジスタ値を設定
def set_adrange(ch, r):
    wdat = [((5+ch)<<1)|1, r, 0x00, 0x00]     # chの入力レンジ設定
    rdat = xfer_spiadc(wdat)

# 指定chのレンジ選択レジスタ値を取得
def get_adrange(ch):
    wdat = [((5+ch)<<1)|0, 0x00, 0x00, 0x00]  # chの入力レンジ取得
    rdat = xfer_spiadc(wdat)
    return rdat[2]

# 指定chのAD変換データ取得
def get_addata(ch):
    wdat = [0xc0+(ch<<2), 0x00, 0x00, 0x00]   # ch'ch'をAD変換する
    rdat = xfer_spiadc(wdat)                  # ch指定
#   time.sleep(0.1)
    rdat = xfer_spiadc(wdat)                  # ADデータ取得
    adat = (rdat[2]<<4)+(rdat[3]>>4)          # AD変換値
    return adat

# ch0-7のAD変換実行と結果表示
def print_adc(intv, cnt):                     # intv:表示間隔[sec] cnt:表示回数[回]
    global adach
    for i in range(cnt):                      # 表示回数繰り返し
        for adc in range(8):                  # ch0-7
            if( chr[adc]>9 ):                 # 無効chなら、
                print("%8s ch%d:        [---]" % 
                    (rstr[chr[adc]], adc) )   # AD変換なし
            else:                             # 有効chなら、
                adat = get_addata(adc)        # ch'adc'をAD変換する
                volt = (adat-chu[chr[adc]])*chm[chr[adc]]/1000  # 入力レンジでの実値算出 = (AD変換値-減算値)x乗算値
                print("%8s ch%d:%8.4f[%03X]" % 
                    (rstr[chr[adc]], adc, volt, adat) )         # 結果表示
        if( adach == 0 ):                     # アラームなしで、
            if( cnt>1 ):                      # 複数回なら、
                print("%5d/%d" %(i+1, cnt))   # 回数表示
            if( i<(cnt-1) ):
                time.sleep(intv)              # 表示間隔待ち
                sys.stdout.write("\033[9F")   # カーソルを9行上に移動
                sys.stdout.flush()
        else:                                 # アラームありなら、
            print(" アラーム検知！ ch7-0:{0:08b} " .format(adach), end="" )
            wdat = [(0x11<<1), 0x00, 0x00, 0x00]
            rdat1 = xfer_spiadc(wdat)         # アラーム ch0-3変化 レジスタ読み込み
            wdat = [(0x12<<1), 0x00, 0x00, 0x00]
            rdat2 = xfer_spiadc(wdat)         # アラーム ch0-3状態 レジスタ読み込み
            wdat = [(0x13<<1), 0x00, 0x00, 0x00]
            rdat3 = xfer_spiadc(wdat)         # アラーム ch4-7変化 レジスタ読み込み
            wdat = [(0x14<<1), 0x00, 0x00, 0x00]
            rdat4 = xfer_spiadc(wdat)         # アラーム ch4-7状態 レジスタ読み込み
            print( " ch0-3Trip:%02X/Active:%02X, ch4-7Trip:%02X/Active:%02X " %
                ( rdat1[2], rdat2[2], rdat3[2], rdat4[2] ) )
            adach = 0                         # アラームクリア
            break                             # 計測中断

    print("")


# アラームの設定
def set_adalarm(ch, hist, hth, lth):          # ch:アラーム設定ch, hist:ヒステリシス, hth/lth:しきい値上限/下限
    reg = 0x15+(ch*5)                         # アラームレジスタベースアドレス ch0=0x15 ～ ch7=0x38
    reg = (reg<<1)|1                          # レジスタへの書き込み
    wdat = [reg, hist<<4, 0x00, 0x00]
    rdat = xfer_spiadc(wdat)                  # ヒステリシス設定
    wdat = [reg+2, hth>>4, 0x00, 0x00]
    rdat = xfer_spiadc(wdat)                  # 上限しきい値上位8bit設定
    wdat = [reg+4, (hth&0x0f)<<4, 0x00, 0x00]
    rdat = xfer_spiadc(wdat)                  # 上限しきい値下位4bit設定
    wdat = [reg+6, lth>>4, 0x00, 0x00]
    rdat = xfer_spiadc(wdat)                  # 下限しきい値上位8bit設定
    wdat = [reg+8, (lth&0x0f)<<4, 0x00, 0x00]
    rdat = xfer_spiadc(wdat)                  # 下限しきい値下位4bit設定

# アラーム有効
def ena_adalarm(en):                          # 0:アラーム無効 1:アラーム有効
    global adalarm
    wdat = [(0x03<<1), 0x00, 0x00, 0x00]
    rdat = xfer_spiadc(wdat)                  # フィーチャーセレクトレジスタ読み込み
    wdat = [(0x03<<1)|1, (rdat[2]&0xef)|((en&1)<<4), 0x00, 0x00]
    rdat = xfer_spiadc(wdat)                  # アラーム機能有効/無効設定
    adalarm = en&1                            # アラーム状態保持

# アラームコールバック
def callback_adalarm(din):
    global adach
    global adadt
    wdat = [(0x10<<1), 0x00, 0x00, 0x00]
    rdat = xfer_spiadc(wdat)                  # アラーム要因レジスタ読み込み
    if( rdat[2]==0 ):                         # アラームなし＝DIN入力(H→L変化)あり
        adach = 0x100                         # bit8:DIN
        adadt = get_addata(0)                 # ch0のAD変換値保存
        print("！デジタル入力DIN(H→L変化)検知！ ch0[%03X]" % adadt )    # 検知時のch0 ADCデータ表示
    else:
        adach = rdat[2]                       # bit7-0:ch7-0

# main
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                prog='sampleGp40.py',                       #プログラムファイル名
                usage='メニュー形式でRPi-GP40を制御します', #使用方法
                description='引数を指定することで直接実行が可能です',
                epilog=     '--------------------------------------------------------------------------',
                add_help=True,
                )
    #引数
    parser.add_argument('-r', '--range', metavar='[R]'  , nargs=8, \
                        help='[R]= 0:±10V 1:±5V 2:±2.5V 3:±1.25V 4:±0.5V 5:0-10V 6:0-5V 7:0-2.5V 8:0-1.25V 9:0-20mA 以外:無効 ' + \
                             'チャンネル0-7の入力レンジ(0-9)を指定 例: -r 0 0 5 5 6 6 6 9')
    parser.add_argument('-t', '--time',  metavar='[T]'   , nargs=1, \
                        help='[T]= AD変換間隔(1-1000)[秒]を指定 例: -t 1')
    parser.add_argument('-c', '--cnt',  metavar='[C]'   , nargs=1, \
                        help='[C]= AD変換回数(1-1000)[回]を指定 例: -c 100')
    args = parser.parse_args()  #引数確認

    interval = 0                # 表示間隔 0:1回 1～1000[秒]

    try:
        # 引数取得
        if( args.range ):           # 入力レンジ
            for adc in range(8):
                chr[adc] = int(args.range[adc], 16)
        if( args.time ):            # AD変換間隔
            interval = int(args.time[0],10)
        if( args.cnt ):             # AD変換回数
            cnt = int(args.cnt[0],10)

        # RaspberryPi SPI機能設定
        spi  = spidev.SpiDev()      # RPi-GP40はSPIを使用
        spi.open(0, 0)              #  SPI0, CEN0 でオープン
        spi.no_cs = True            #  CSはspidevではなくGPIOとして制御する Ra
        spi.mode = 1                #  SPIクロック設定 CPOL=0(正論理), CPHA=1(H->Lでデータ取り込み)
        spi.max_speed_hz = 10000000 #  SPIクロック最大周波数(17MHz指定)
                                    #   ただし、2018年4月時点のカーネル仕樣では、指定値より実周波数が低くなる
                                    #   17MHz→10.5MHz, 10MHz→6.2MHz, 8MHz→5MHz, 28MHz→15.6MHz
        DOUT = 12                   # デジタル出力 GPIO12(JP8:Default) / GPIO14(JP7)
        DIN  = 13                   # デジタル入力 GPIO13(JP6:Default) / GPIO15(JP5)

        # RPi-GP40初期設定
        init_GP40()

        # 入力レンジ設定
        for adc in range(8):
            if( chr[adc]<=9 ):      # 有効chなら、
                set_adrange(adc, chn[chr[adc]])     # ch'c'の入力レンジ設定

        # 引数による直接実行形式
        if( interval != 0 ):        # 引数指定があれば、
            print_adc(interval,cnt) # interval間隔でcnt回AD変換値表示
            GPIO.output(27, False)  # RPi-GP40の絶縁電源OFF
            GPIO.cleanup()
            sys.exit()

        # 引数なしのメニュー実行形式
        while True:

            # 各chの入力レンジ設定値表示
            print("ch:レンジ= 0:%s, 1:%s, 2:%s, 3:%s, 4:%s, 5:%s, 6:%s, 7:%s" % 
                (rstr[chr[0]], rstr[chr[1]], rstr[chr[2]], rstr[chr[3]], rstr[chr[4]], rstr[chr[5]], rstr[chr[6]], rstr[chr[7]]) )

            # メニュー表示
            menu = input("0-7:chレンジ設定, a:単一AD変換, b:連続AD変換, c:アラーム, d:デジタルIO, e:終了 >")
            c = int(menu, 16)

            # '0'～'7' ch入力レンジ設定
            if( (c>=0)and(c<=7) ):  
                print("入力レンジ 0:±10V 1:±5V 2:±2.5V 3:±1.25V 4:±0.5V 5:0-10V 6:0-5V 7:0-2.5V 8:0-1.25V 9:0-20mA a:無効")
                d = input("ch%d 入力レンジ >" % c )
                chr[c] = int(d, 16)
                if( chr[c] <= 9 ):
                    set_adrange(c, chn[chr[c]])     # ch'c'の入力レンジ設定

            # 'a' 単一AD変換
            if( c==10 ):            
                print_adc(0, 1)     # 間隔0で1回AD変換値表示

            # 'b' 連続AD変換
            if( c==11 ):            
                i = input(" 連続AD変換 間隔 1-1000[秒] >")
                interval = int(i)
                i = input(" 連続AD変換 回数 1-1000[回] >")
                cnt = int(i)
                print_adc(interval, cnt) # interval間隔でcnt回AD変換値表示

            # 'c' アラーム
            if( c==12 ):            
                i = input(" アラーム 0-7:有効[ch], a:無効 >")
                if( i=='a' ):       # 無効なら、
                    ena_adalarm( 0 )                    # アラーム無効
                    if( adalarm==1 ):
                        GPIO.remove_event_detect(DIN)   # ALARM割り込み解除
                    print("アラーム解除しました。")
                else:               # アラーム設定値入力
                    ch = int(i) & 0x07
                    i = input(" ヒステリシス 0-15[LSB]    >")
                    hist = int(i) & 0x0f
                    i = input(" 上限しきい値(HEX) 000-FFF >")
                    hth = int(i,16) & 0xfff
                    i = input(" 下限しきい値(HEX) 000-FFF >")
                    lth = int(i,16) & 0xfff
                    set_adalarm(ch, hist, hth, lth)     # アラーム設定
                    if( adalarm==1 ):
                        GPIO.remove_event_detect(DIN)   # ALARM割り込み解除
                    adach = 0                           # アラームクリア
                    GPIO.add_event_detect(DIN, GPIO.FALLING, callback=callback_adalarm, bouncetime=200)  # ALARM/DIN割り込みコールバック設定
                    ena_adalarm( 1 )                    # アラーム有効
                    print("アラーム設定しました。連続AD変換中にアラーム検知で計測を中断します。")
                print("")

            # 'd' デジタル入出力
            if( c==13 ):            
                if( adalarm==1 ):
                    GPIO.remove_event_detect(DIN)   # ALARM割り込み解除
                GPIO.add_event_detect(DIN, GPIO.FALLING, callback=callback_adalarm, bouncetime=200)  # ALARM/DIN割り込みコールバック設定
                while True:
                    i = input(" デジタル出力 1:ON(Low) 0:OFF(High) a:戻る >")
                    if( i=='a' ):   # 戻るで、
                        break       # メニューに戻る
                    else:
                        d = int(i,16) & 1
                        GPIO.output(DOUT, d)        # DOUT設定
                GPIO.remove_event_detect(DIN)       # ALARM/DIN割り込み解除

            # 'e' 終了
            if( c==14 ):            
                break

    # 例外処理
    except KeyboardInterrupt:       # CTRL-C キーが押されたら、
         print( "中断しました" )    # 中断
    except Exception:               # その他の例外発生時
         print( "エラー" )          # エラー
    GPIO.output(27, False)          # RPi-GP40の絶縁電源OFF
    GPIO.cleanup()
    sys.exit()
