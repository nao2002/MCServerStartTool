@echo off

rem 以下対応引数
rem (checkServerVer.bat) javaパス サーバーディレクトリ サーバーファイル

title checking_version...

set PATH="%~1";%PATH%

cd /d "%~2"

java -Xms512M -Xmx1G -jar "%~3" nogui

exit 0