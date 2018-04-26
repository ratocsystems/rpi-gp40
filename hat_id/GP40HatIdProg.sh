#!/bin/bash
# RPi-GP40 HAT ID　EEPROM書き込み用スクリプト

rm ./hats/eepromutils/RPi-GP40_eeprom.eep
rm ./hats/eepromutils/buf.eep

echo " "
echo "#########################"
echo "HAT IDデータを作成"
echo "#########################"
./hats/eepromutils/eepmake ./hats/eepromutils/RPi-GP40_eeprom.txt ./hats/eepromutils/RPi-GP40_eeprom.eep

if [ ! -e ./hats/eepromutils/RPi-GP40_eeprom.eep ]; then
echo "HAT IDデータの作成に失敗しました"
exit 1
fi

echo " "
echo "#########################"
echo "HAT IDデータを書き込みます"
echo "#########################"

sudo ./hats/eepromutils/eepflash.sh -w -f=./hats/eepromutils/RPi-GP40_eeprom.eep -t=24c32
echo " "
echo "#########################"
echo "HAT IDデータを読み込み比較します"
echo "#########################"
sudo ./hats/eepromutils/eepflash.sh -r -f=./hats/eepromutils/buf.eep -t=24c32

echo " "
echo "#########################"
cmp ./hats/eepromutils/RPi-GP40_eeprom.eep ./hats/eepromutils/buf.eep
echo "#########################"

exit 1