@echo off

rem ServerStarter 起動用batファイル created by lyomi_project

rem 以下対応引数
rem (startServer.bat) javaパス サーバーディレクトリ サーバーファイル 割り当てメモリ(****M、*G) マイクラver その他引数(nogui等)

title Server

set PATH="%~1";%PATH%

cd /d %~dp0

set log4j=
if %7 == 17 (
set log4j=-Dlog4j2.formatMsgNoLookups=true 
) else if %7 == 11 (
set log4j=-Dlog4j.configurationFile=log4j2_17-111.xml 
copy /Y log4j2_17-111.xml "%~2" > nul
) else if %7 == 16 (
set log4j=-Dlog4j.configurationFile=log4j2_112-116.xml 
copy /Y log4j2_112-116.xml "%~2" > nul
)

cd /d "%~2"

taskkill /F /IM MCServerStarter.exe > nul

java -Xms%4 -Xmx%4 %log4j%-jar "%~3"%~6

pause

exit 0