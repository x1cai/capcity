echo * create_report.bat dlCoreId ulCoreId

SET REPORT="report.html"
SET DlCoreId="1231"
SET UlCoreId="1234"
if /I "%1"=="DL" (goto :UPDATECORE) else (if /I "%1" == "" (SET REPORT="report.html") else (SET REPORT=%1))
goto :HB

:UPDATECORE
if /I "%2"=="" (SET DlCoreId="1231") else (SET DlCoreId=%2)
if /I "%3"=="UL" (if /I "%4"=="" (SET UlCoreId="1234") else (SET UlCoreId=%4))
SET REPORT=%5
goto :HB

:HB
cd tools\logs\600UE_tcp\
sicftp.exe -c %DlCoreId% -g mac_slow_1231.bin
sicftp.exe -c %UlCoreId% -g mac_slow_1234.bin

cd ..\..\..\tools
C:\Python27\python HB_report_with_fn.py %REPORT%
mv logs\600UE_tcp\mac_slow_1231.bin ..
mv logs\600UE_tcp\mac_slow_1231.txt ..
mv logs\600UE_tcp\mac_slow_1234.bin ..
mv logs\600UE_tcp\mac_slow_1234.txt ..
mv logs\600UE_tcp\reportdata.txt ..
mv %REPORT% ..

cd ..