#!/usr/bin/python
#==============================================================
#       Function:       Get TC9902 case CNP data
#       Author:         Yu Qiyan
#       Time:           05/02/2013
#*  *********************************
#*  *   Script description:
#*  *********************************
#       1. read Histroy Buffer data
#       2. process CNP data
#       3. write CNP data to html  
#==============================================================
#FileName:HB_report.py

import os
import re
import sys
import logging

class ReportGenerator(object):
    _header ='''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
    <title>report detail</title>
    <style type=text/css media=all>
        p.title{text-align: center;color: #800080;padding-bottom: 10px;font-family: sans-serif;font-size: 20pt;font-style: italic;font-weight: bold;}
        p.subtitle{text-align: center;color: #800080;padding-top: 6px;font-family: sans-serif;font-size: 14pt;font-style: italic;font-weight: bold;}
        p.ruler{background-color: #800080;}
        table {
            width: 90%;
            border-collapse:collapse;
        }
        .statics_table tr{
            background-color: #DDDDFF;
        }
        .statics_table td{
            text-align: center;
            font-size: 14px;
            padding: 0 4px;
            height: 30px;
            width:  120px;
            border: 2px solid #D3D3D3;
        }
    </style>
</head>
<body>
    <div>
        <p class="title">MAC PS Capacity and Perfomance Report based on DSP RTM</p>
        <p class="ruler"><img src="glass.png" width=3 height=3 alt=""></p>
    </div>
    <center>
        <div>
            <p class="subtitle">Indicator Detail</p>
            <p class="subtitle"></p>
        </div> 
        <table class="statics_table">'''

    _footer ='''</table>
    </center>
</body>
</html>'''

    def read_bin_file(self,fileName):
        global num,names,reportdata,currentDir,EnodeB_version
        currentDir = os.path.abspath(__file__)
        currentDir = os.path.dirname(currentDir)
        print"currentDir is %s" %(currentDir)
        num = 0
        enbverison = [' ']
        names = ['ActiveUe', 'DlTdUe', 'DlExpectedFdUe','DlExpectedFdUeSp', 'DlScheUe', 'DlScheUeSp', 'DlCpuLoad','DlPreCycle','DlTdCycle','DlFdCycle','DlPostCycle', 'DlHarqViaPucch', 'DlSchResultMsg', 'DlDrxHarqMsg','UlTdUe', 'UlExpectedFdUe','UlScheUe', 'UlCpuLoad','UlPreCycle','UlTdCycle','UlFdCycle', 'PdcchCycle', 'PucchSRS','UlPostCycle','UlPostIdleCycle']
        reportdata =[[] for i in range(12)]  #12 cp case TC9502
        logsPath = currentDir + "/" + "logs"
        folderList = os.listdir(logsPath)
        for folder in folderList: 
            idx = folder.find("UE") #600UE_tcp
            if idx != -1:
               path = logsPath + "/" + folder    #path:HBtool\logs\600UE_tcp
               self.parse_bin_file(path, num)
               reportdatafile = path + "/" + "reportdata.txt"
               file_object = open(reportdatafile, 'w')
               reportdata_str = ''
               for line in reportdata[num]:
                   reportdata_str +='%s,'%line
               file_object.write(reportdata_str)
               file_object.close()
               num += 1
        reportdata.sort()
        self.construct(names, reportdata, currentDir + "/" + fileName)
        
    def parse_bin_file(self,path,num):    #Run Hbviewer.exe to generate *.txt and call process_file to handle txt data
        binlist = os.listdir(path)
        for binfile in binlist:
            dlexist = re.search("^mac_slow_1231.*\.bin$", binfile)
            if dlexist:
               dl_file = path + "/" + binfile.split("\\")[-1].split(".")[0]+".txt"
               os.system(currentDir + "/" + "Hbviewer.exe -b " + path + "/" + binfile + ">" + dl_file)
               is_ul = 0
               print 'tpj add31' + path
               print dl_file
               print num
               print is_ul
               self.process_file(path, dl_file, num, is_ul)
                   
            ulexist = re.search("^mac_slow_1234.*\.bin$", binfile)
            if ulexist:
               ul_file = path + "/" + binfile.split("\\")[-1].split(".")[0]+".txt"
               print 'tpj add1'+ ul_file
               print 'tpj add2'+ currentDir + "/" + "Hbviewer.exe -b " + path + "/" + binfile + ">" + ul_file
               os.system(currentDir + "/" + "Hbviewer.exe -b " + path + "/" + binfile + ">" + ul_file)
               is_ul = 1
               print 'tpj add34' + path
               print ul_file
               print num
               print is_ul
               self.process_file(path, ul_file, num, is_ul)

    def process_file(self, path, filename, num, is_ul):    #read data from txt and calculate the avrage value of each field
        'used to read a text file.'  
        global maxValue, tdUenum 
        if(is_ul):
            keylist = ["0xbeee90e4", "0xbeebcccc", "0xbeee90e0", "0xbeee90e1", "0xbeee90e2", "0xbeee90e7", "0xbeee90e8", "0xbeee90e3", "0xbeee90e9"]
            maxValue = [0]*12
        else:
            keylist = ["0xbeee90e4", "0xbeebcccc", "0xbeee90e0", "0xbeee90e1", "0xbeee90e2", "0xbeee90e3", "0xbeee90ea", "0xbeee90eb", "0xbeee90ec"] 
            maxValue = [0]*12                    
        
        tdUenum = 0
        data = [[] for i in range(12)] # ul:original 8 (cpu and schedule cycle) and add 4 UE monitor(4 ue data in 0xbeee90e4)
                                           # dl:original 5 (cpu and schedule cycle) and add 4 UE monitor(4 ue data in 0xbeee90e4)
        ave_win = 10
        try:
            fobj = open(filename,  'r')  
        except IOError as err:  
            print('file open error: {0}'.format(err))    
        else:
            for eachline in fobj:                          #read line and store the value to data list
                for idx, ele in  enumerate(keylist):
                    start =  eachline.find(ele)  
                    #print "start is:"+ str(start)
                    #tdUenum = 20
                    if start != -1:
                       linedata = eachline[start:len(eachline)-1].split(' ')
                       #print "linedata is:" + str(linedata)
                       if ele == keylist[0]:           # add ue number to data
                          tdUenum = int(linedata[3])     # judge td ue number,only get the td ue num > 0 data 
                          print "tduem is:" + str(tdUenum) + "key is:" + str(keylist[0])
                          if tdUenum >89 and tdUenum < 120:
                             for i in range(0,4):
                                 data[i].append(int(linedata[i+2]))     #[2]:active ue  [3]:td ue [4]:fd ue of normal esfn  [5]:fd ue of special esfn
                                 print "line is:" + str(eachline) 
                                 print "line data is:" + str(int(linedata[i+2])) + "key is:" + str(keylist[0])
                       elif ele == keylist[1]:         #cpu load                               
                            if tdUenum > 89 and tdUenum < 120:
                               data[idx+3].append(int(linedata[4]))    #[2]:CpuLoad  [3]:avg CpuLoad [4]:max CpuLoad
                       elif (is_ul==1 and ele == keylist[8]):
                              print "ulPostIdle line is:" + str(eachline)
                              print "tduem is:" + str(tdUenum) + "key is:" + str(ele)
                              cycle = int(linedata[6],16)   #SInterval  maxInterval
                              print "cycle is:" + str(cycle)
                              if cycle < 20000000:
                                print "add cycle" + str(ele) + "cycle is:" + str(cycle)
                                data[idx+3].append(cycle)
                       else:
                           print "line is:" + str(eachline)
                           print "tduem is:" + str(tdUenum) + "key is:" + str(ele)
                           cycle = int(linedata[6],16)   #SInterval  maxInterval
                           print "cycle is:" + str(cycle)
                           if cycle < 20000000 and tdUenum > 89 and tdUenum < 120:
                              print "add cycle" + str(ele) + "cycle is:" + str(cycle)
                              data[idx+3].append(cycle)
            print "#####################"
            print "data txt:"+str(data)
            print "#####################"
            for i in range(0,len(data)):    #get average max cpu and cycle 
                print "lenofdata is:" + str(len(data[i]))
                for j in range(0,len(data[i])-ave_win):
                    temp = 0
                    for k in range(j,j+ave_win):
                        temp += int(data[i][k])
                    temp /= ave_win
                    if maxValue[i] < temp:
                       maxValue[i] = temp 
            
            maxValue[4] = str(float(maxValue[4])/10) + "%"              #cpu data
               
            self.get_param_from_case(path, is_ul)                      # get FD ue num from case parameter 
            if is_ul == 0:     
               for i in range(0,len(maxValue)):    #write dl data               
                   reportdata[num].insert(i,maxValue[i])
            else :
               ulstart = names.index('UlTdUe')-1
               for i in range(1, len(maxValue)):
                   if i < 4:  #remove special subframe FD user num as not applicable for UL
                       reportdata[num].insert(i+ulstart, maxValue[i])
                   elif i > 4:
                       reportdata[num].insert(i+ulstart-1, maxValue[i])
                   
            fobj.close()
            
             
    def get_param_from_case(self, path, is_ul): 
        #filename = '../../../MacSctPegasus/Tests/MAC/' + path.split('/')[4].split('-')[0] + '/excel2txt/CellSetup.txt'
        #paramfile = open(filename,  'r')
        if is_ul == 0:   
               #for eachline in paramfile:
                   #start = eachline.find("db_cell_key_CELLID_MAC_CellSetupReq_maxNumUeDl ")
                   #if start != -1:
                      #linedata = eachline[start:len(eachline)-1].split(' ')
                      #maxValue.insert(2,4)
                      infoTxtPath = currentDir + "/" + "info.txt"
                      expectedUEfile=file(infoTxtPath)                      
                      for line in expectedUEfile:
                        version =  line.find('LNT')
                        direction = line.find('dl=')
                        directionsp = line.find('dlsp=')
                        if version == 0:
                            print "line=%s" %(line)
                        elif direction == 0:
                            linedata = line.split('=')
                            maxValue.insert(2,linedata[1])
                        elif directionsp == 0:
                            linedata = line.split('=')
                            maxValue.insert(3,linedata[1])
                            break
                                                   
                            
                      
                      
        else:
           #for eachline in paramfile:
                   #start = eachline.find("db_cell_key_CELLID_MAC_CellSetupReq_maxNumUeUl ")
                   #if start != -1:
                      #linedata = eachline[start:len(eachline)-1].split(' ')
                      #maxValue.insert(2,4)
                      infoTxtPath = currentDir + "/" + "info.txt"
                      expectedUEfile=file(infoTxtPath)                      
                      for line in expectedUEfile:
                        version =  line.find('LNT')
                        EnodeB_version = line.find('LNT')
                        direction = line.find('ul=')
                        if version == 0:
                            print "line=%s" %(line)
                        elif direction == 0:
                            linedata = line.split('=')
                            maxValue.insert(2,linedata[1])
                            break
                                                  
        
    def construct(self, header, data, output_file=None):
        self.header = header
        self.data = data
        self.output_file = output_file
        self.generate()
    
    def generate(self):
        self.report_str = self._header
        self.report_str += self.generate_table_head()
        self.report_str += self.generate_table_data()
        self.report_str += self._footer
        self._write_to_file()
    
    def generate_table_head(self):
        head_str = '<tr>\n'
        for hd in self.header:
            head_str += '    <td>%s</td>\n' % hd
        head_str += '</tr>\n'
        return head_str
    
    def generate_table_data(self):
        data_str = ''
        for data in self.data:
            if len(data)>0:
               data_str += '<tr>\n'
            for cell in data:
                data_str += '    <td>%s</td>\n' % self.parse_cell(cell)
            data_str += '</tr>'
        return data_str
    
    def parse_cell(self, cell):
        if isinstance(cell, basestring):
            return cell
        elif isinstance(cell, dict):
            title = cell.get('title', None)
            url = cell.get('url', None)
            if url is not None:
                return '<a href="%s" target="_blank">%s</a>' % (url, title or url)
            return title or ''
        else:
            return cell
    
    def _write_to_file(self):
        if self.output_file is not None:
            with open(self.output_file, 'w') as f:
                f.write(self.report_str)
            logging.info('Report %s generated.' % self.output_file)

if __name__ == '__main__':
    rg = ReportGenerator()
    if len(sys.argv) == 1:
        rg.read_bin_file('report.html')
    else:
        rg.read_bin_file(sys.argv[1])



