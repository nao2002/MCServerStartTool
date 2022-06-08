@echo off

rem ServerStarter 起動用batファイル created by lyomi_project

rem 以下対応引数
rem (startServer.bat) javaパス サーバーディレクトリ サーバーファイル 割り当てメモリ(****M、*G) マイクラver その他引数(nogui等)

title Server

set PATH="%~1";%PATH%

set log4j=-Dlog4j.configurationFile=log4j2_112-116.xml 
if %5 == 17 (
set log4j=-Dlog4j2.formatMsgNoLookups=true 
) else if %5 == 18 (
set log4j=
)

cd /d "%~2"

taskkill /F /IM MCServerStarter.exe > nul

java -Xms%4 -Xmx%4 %log4j%-jar "%~3"%~6

pause

exit 0