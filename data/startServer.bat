@echo off

rem ServerStarter 起動用batファイル created by nao2002_

rem 以下対応引数
rem (startServer.bat) javaパス サーバーディレクトリ サーバーファイル 割り当てメモリ(****M、*G) log4j その他引数(nogui等)

title Server

set PATH="%~1";%PATH%

cd /d %~dp0

set log4j=
if %5 == 17 (
set log4j=-Dlog4j2.formatMsgNoLookups=true 
) else if %5 == 11 (
set log4j=-Dlog4j.configurationFile=log4j2_17-111.xml 
copy /Y log4j2_17-111.xml "%~2" > nul
) else if %5 == 16 (
set log4j=-Dlog4j.configurationFile=log4j2_112-116.xml 
copy /Y log4j2_112-116.xml "%~2" > nul
)

cd /d "%~2"

java -Xms%4 -Xmx%4 %log4j%-jar "%~3"%~6

pause

exit 0