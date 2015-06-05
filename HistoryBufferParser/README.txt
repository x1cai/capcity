Usage:
1. keep RAD parameter ERadSwDomainLteMac_TRdCnpStatsOutputEnable is 1
	pscli.exe --setrd -T 1231,1234 ERadSwDomainLteMac_TRdCnpStatsOutputEnable=1
	Note: for on-target test, RAD parameter is set in test script
2. run create_report.bat to generate report
	create_report.bat // 1231 1234 as default target core, report.html as default output
	create_report.bat report_name.html
	create_report.bat DL dlCoreId UL ulCoreId report_name.html//create_report.bat 1232 1234

3. report.html as default report file
