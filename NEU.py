#本程序利用GAMIT解算的q文件中的第二次NEU坐标生成的坐标，根据NEU坐标解算三个方向上的形变并绘制图形
#准备数据：qfilefolerpath，station_filepath，xtick_step，baseline_result_folderpath，plot_save_folderpath
#使用时建议不更改路径
import os
import numpy as np
from pathlib import Path
from datetime import datetime
from matplotlib import pyplot as plt

plt.rcParams['font.sans-serif']=['SimHei']#显示中文标签
plt.rcParams['axes.unicode_minus']=False

qfilefolerpath='.\data'#q文件存放文件夹
station_filepath=r'.\station.txt'#站点名文件，格式为：每一行（起点站名,终点站名）
xtick_step=11#绘图时数据量较大时可设置该值，该值越大，x轴标签越稀疏
baseline_result_folderpath='baseline_result'#读取初始q文件的NEU数据并存放到另一文件所存放的文件夹路径，此项不要更改
plot_save_folderpath=r'.\base_plot'#出图所存放的文件夹路径

class read_baseline:
    '''
    根据init_site和dest_site读取文件中的NEU并保存为单个文件
    '''
    marker_phrase_st= 'Adjustments larger than twice the a priori constraint'
    marker_phrase_ed= 'End of tight solution with LC   observable and ambiguities fixd'
    marker_baseline='Baseline vector (m )'
    NEUs=[]#所有文件的NEU，以列表形式输出，列表中为每个文件的元胞，每个元胞里面是三个列表（N、E、U）
    def __init__(self, filefolderpath:str,init_site:str,dest_site:str):
        #第一个为基准站，第二个为测站站点名
        self.filefolderpath=filefolderpath
        self.init_site=init_site
        self.dest_site=dest_site
    def get_filepathlist(self):
        '''
        读取文件夹下的所有文件名并返回所有文件的文件路径
        :return:
        '''
        filepathlist=[]
        filelist=os.listdir(self.filefolderpath)
        for file in filelist:
            path=os.path.join(self.filefolderpath,file)
            filepathlist.append(path)
        return filepathlist
    def readfile1(self, filepath, init_site:str, dest_site:str):
        '''
        读取单个文件中的指定两个站的基线数据,并返回 Baseline vector 行数据和NEU行数据,不考虑station是否存在
        :return:
        '''
        NEUs_index = []  # NEU所在行的所有索引
        content=[]
        with open(filepath) as f:
            line=f.readline()
            while line!='':
                content.append(line)
                line=f.readline()
        # print(content)
        index=1
        index_list_st=[]#self.marker_phrase_st所在行，列表索引要减1
        index_list_ed=[]#self.marker_phrase_ed所在行，列表索引要减1
        for tline in content:
            if self.marker_phrase_st in tline:
                index_list_st.append(index)
            if self.marker_phrase_ed in tline:
                index_list_ed.append(index)
            index=index+1
        content_mid=content[index_list_st[1]:index_list_ed[0]] #marker_phrase_st到marker_phrase_ed之间的内容
        index1=index_list_st[1]+1
        # print(content_mid)

        for tmp in content_mid:
            if (self.marker_baseline in tmp) and (tmp[len(tmp)-21:len(tmp)-17] == dest_site) and (tmp[len(tmp) - 45:len(tmp) - 41] == init_site):
                baseline_index=index1# Baseline vector所在行行号
                baseline_vector = tmp
                break
            index1 = index1 + 1
        NEU=content[baseline_index+3]
        # print(baseline_index)
        baseline_NEU=baseline_vector.strip('\n')+','+NEU.strip('\n')+'\n'
        return baseline_NEU
    def readStation(self,filepath):
        '''
        读取文件内的station名并返回
        :return:
        '''
        marker1='Station                   Cutoff angle '
        marker2='A priori coordinate errors in meters'
        content = []
        index=1
        with open(filepath) as f:
            line = f.readline()
            while line != '':
                if marker1 in line:
                    indexst=index+1
                if marker2 in line:
                    indexed=index-2
                index=index+1
                content.append(line)
                line = f.readline()
        station=[]
        content_mid=content[indexst:indexed]
        for x in content_mid:
            station.append(x[5:9])
        return station
    def readReferTime(self,filepath:str):
        '''
        读取文件refer time并返回行内容
        :param filepath:
        :return:
        '''
        marker='Solution refers to'
        content = []
        index = 1

        with open(filepath) as f:
            line = f.readline()
            while line != '':
                content.append(line)
                if marker in line:
                    index_refer=index
                index=index+1
                line=f.readline()
        referTime=content[index_refer-1]
        # print(referTime)
        return referTime
    def readfile2(self,folderpath,init_site:str,dest_site:str):
        '''
        读取指定两站点间的基线数据并返回NEU和baseline和refer time
        :param folderpath:
        :param init_site:
        :param dest_site:
        :return:
        '''
        filepathlist=self.get_filepathlist()
        NEUlist=[]
        for path in filepathlist:
            station=self.readStation(path)
            referTime=self.readReferTime(path)
            if (init_site in station) and (dest_site in station):
                NEU_tmp=self.readfile1(path,init_site,dest_site)
                # print(NEU_tmp)
            else:
                NEU_tmp='NAN\n'
                # print(NEU_tmp)
            # print(referTime, end='')
            # print(path)
            # print
            path1=path+'\n'
            NEUlist.append(referTime)
            NEUlist.append(path1)
            NEUlist.append(NEU_tmp)
        return NEUlist
    def mkdir(self,path):
        '''
        创建文件夹
        :param path:
        :return:
        '''
        path=path.strip()
        path=path.rstrip('\\')
        isExists=os.path.exists(path)
        if not isExists:
            os.makedirs(path)
            print(path,'创建成功')
            return True
        else:
            print(path,'目录已存在')
            return False
    def writeNEUlist(self,NEUlist:list,baseline_folder):
        filename=self.init_site+'-'+self.dest_site+'.txt'
        path1=os.path.join(baseline_folder,filename)
        self.mkdir('baseline_result')
        with open(path1,'w') as f:
            for tmp in NEUlist:
                f.write(tmp)
        print('文件已写入{}。'.format(path1))
#写入数据到baseline_result文件
def read_station_file(station_filepath):
    '''
    读取站点文件，包括起始站和终点站
    :param station_filepath:
    :return:
    '''
    station_st=[]
    station_ed=[]
    with open(station_filepath) as f:
        line=f.readline()
        while line !='':
            tmp=line.split(',')
            station_st.append(tmp[0])
            station_ed.append(tmp[1].strip('\n'))
            line=f.readline()
    return station_st,station_ed
def write_basefile(filefolerpath:str,station_filepath:str):
    '''
    利用station.txt读取基线数据并生成多个文件并保存到baseline_result文件夹中
    :param filefolerpath:
    :param savepath:
    :return:
    '''
    station=read_station_file(station_filepath)
    station_st,station_ed=station[0],station[1]
    for init_site, dest_site in zip(station_st,station_ed):
        pl = read_baseline(filefolerpath, init_site,dest_site)
        NEUlist=pl.readfile2(filefolerpath,pl.init_site,pl.dest_site)
        # print(NEUlist)
        baseline_folder='baseline_result'
        folderpath=os.path.join(os.getcwd(),'baseline_result')
        pl.writeNEUlist(NEUlist,folderpath)

#读取baseline_result中的文本数据并绘图
class plot_baseline():
    def __init__(self,baseline_result_folderpath,plot_save_folerpath,xtick_step:int):
        self.baseline_result_folderpath=baseline_result_folderpath
        self.plot_save_folderpath=plot_save_folerpath
        self.xtick_step=xtick_step
    def __del__(self):
        print("__del__")
    def get_filepathlist(self):
        '''
        读取文件夹下的所有文件名并返回所有文件的文件路径
        :return:
        '''
        filepathlist = []
        filelist = os.listdir(self.baseline_result_folderpath)
        for file in filelist:
            path = os.path.join(self.baseline_result_folderpath, file)
            filepathlist.append(path)
        return filepathlist
    def getindex(self,list1:list,element):
        '''
        获取列表中指定元素的索引
        :param list1:
        :param element:
        :return:
        '''
        newlist=[]
        for index, elem in list(enumerate(list1)):
            if elem == element:
                newlist.append(index)
        return newlist
    def read_baseline_result_file(self,filepath:str):
        '''
        读取baseline_result中的单个文件，并返回N、E、U、L、date的列表组成的字典
        :param filepath: 文件路径，包含文件名
        :return: output_dict（dict）:以字典形式输出，包含Nlist,Elist,Ulist,Llist和datelist五个关键字，都由列表组成
        '''
        content=[]
        with open(filepath) as f:
            line = f.readline()
            while line != '':
                content.append(line)
                line = f.readline()
        datelist=[]
        NEUlist=[]
        index=0
        for tmp in content:
            tmp=tmp.strip('\n')#去掉末尾的换行符
            if index%3==0:
                datelist.append(tmp[26:42])
            elif index%3==2:
                if tmp!='NAN':
                    bask_data=tmp.split(',')
                    data_NEU=bask_data[1].split()
                else:
                    data_NEU=tmp
                NEUlist.append(data_NEU)
            index=index+1
        # print(NEUlist)
        Nlist,Elist,Ulist,Llist=[],[],[],[]
        for tmp in NEUlist:
            if type(tmp)!=str:#如果tmp为NAN则为str类型，有数据则为list类型
                Nlist.append(tmp[1])
                Elist.append(tmp[3])
                Ulist.append(tmp[5])
                Llist.append(tmp[7])
            elif type(tmp) == str:
                Nlist.append(tmp)
                Elist.append(tmp)
                Ulist.append(tmp)
                Llist.append(tmp)
        output_dict={'Nlist':Nlist,'Elist':Elist,'Ulist':Ulist,"Llist":Llist,'datelist':datelist}
        # print(output_dict)
        return output_dict
    def replace_char(self,string,char,index):
        '''
        替换指定位置字符串
        :param string:
        :param char:
        :param index:
        :return:
        '''
        string=list(string)
        string[index]=char
        return ''.join(string)
    def awk_elementlist_equidistance(self, anylist: list):
        '''
        等间距取列表元素
        :param anylist:
        :param step:
        :return:
        '''
        nn = len(anylist)
        index = 0
        equidistance_list = []
        while index < nn:
            equidistance_list.append(anylist[index])
            index = index + self.xtick_step
        return equidistance_list
    def mkdir(self,path):
        '''
        创建文件夹
        :param path:
        :return:
        '''
        path=path.strip()
        path=path.rstrip('\\')
        isExists=os.path.exists(path)
        if not isExists:
            os.makedirs(path)
            print(path,'创建成功')
            return True
        else:
            print(path,'目录已存在')
            return False
    def plot_baseline_file_skip(self, result_filepath:str, title:str):
        '''
        绘制单个文件的结果图
        :param result_filepath: baseline_result的文件路径
        :param title: 图标题，图文件命名也用这个
        :return:
        '''
        output_dict=self.read_baseline_result_file(result_filepath)
        Nlist=output_dict['Nlist']
        Elist=output_dict['Elist']
        Ulist=output_dict['Ulist']
        datelist=output_dict['datelist']
        datelist1=[]
        # #datelist格式转换为标准格式
        for tmp in datelist:
            ttmp=tmp.replace(' ','0')
            tttmp=self.replace_char(ttmp,' ',10)
            datelist1.append(tttmp)
        datelist=datelist1
        nan_index=self.getindex(Nlist,'NAN')
        # print(nan_index)
        # print('Nlistlen',len(Nlist))
        Nlist1,Elist1,Ulist1,datelist2=[],[],[],[]
        index=0
        for Nl,El,Ul,dal in zip(Nlist,Elist,Ulist,datelist1):
            if index in nan_index:
                index=index+1
                continue
            else:
                Nlist1.append(Nl)
                Elist1.append(El)
                Ulist1.append(Ul)
                datelist2.append(dal)
                index=index+1
        Nlist,Elist,Ulist,datelist=Nlist1,Elist1,Ulist1,datelist2
        # print(len(Nlist),Nlist)
        # print(len(Elist),Elist)
        # print(len(Ulist),Ulist)
        # print(len(datelist),datelist)
        Nar=np.asarray(Nlist,dtype='f8')
        Ear=np.asarray(Elist,dtype='f8')
        Uar=np.asarray(Ulist,dtype='f8')
        N0,E0,U0=Nar[0],Ear[0],Uar[0]
        dN,dE,dU=(Nar-N0)*1000,(Ear-E0)*1000,(Uar-U0)*1000  #换算为mm
        date_dt=[]#以date_dt作为x轴坐标,datetime类型
        for tmp in datelist:
            date1 = datetime.strptime(tmp, "%Y/%m/%d %H:%M")
            # print(date1,datetime.strftime(date1,"%Y/%m/%d"))
            date_dt.append(date1)
        date_dt_awk = self.awk_elementlist_equidistance(list(date_dt))#等间距提取的datetime类型日期，用于xtick
        date_str_awk=self.awk_elementlist_equidistance(datelist)#等间距提取的str类型日期，用于xtick
        date_str_awk1=[]
        for tmp in date_str_awk:
            ttmp=tmp[0:-6]
            date_str_awk1.append(ttmp)
        plt.plot(date_dt,dN)
        plt.plot(date_dt,dE)
        plt.plot(date_dt,dU)
        plt.legend(['dN','dE','dU'],loc='best')
        plt.title(title)
        plt.ylim(-100,100)#设置y轴范围
        plt.xlabel('日期', loc='center')
        plt.ylabel('偏移量(mm)', loc='center')
        plt.xticks(date_dt_awk,date_str_awk1)
        # plt.grid() #添加格网
        # plt.minorticks_on()#显示次刻度线
        # plt.tick_params(which='minor',direction='in')#设置次刻度线朝向，in，out，inout
        plt.tick_params(direction='in')  # 设置主坐标轴刻度线朝向
        plt.tick_params(top=True, bottom=True, left=True, right=True)  # 在哪些轴显示刻度线
        self.mkdir(self.plot_save_folderpath)
        picsavepath=os.path.join(self.plot_save_folderpath,title)
        plt.savefig(picsavepath)
        # plt.show()
        plt.close()
        print('{}已绘制完成，保存在{}文件夹中。'.format(title,self.plot_save_folderpath))

def plot_baseline_multi(baseline_result_folderpath,plot_save_folderpath,xtick_step):
    '''
    绘制所有文件图形
    :param baseline_result_folderpath:
    :param plot_save_folderpath:
    :param xtick_step:
    :return:
    '''
    tmp=plot_baseline(baseline_result_folderpath,plot_save_folderpath,xtick_step)
    filepathlist = tmp.get_filepathlist()
    for pathtmp in filepathlist:
        plb=plot_baseline(baseline_result_folderpath,plot_save_folderpath,xtick_step)
        name=os.path.basename(pathtmp).split('.')[0]
        plb.plot_baseline_file_skip(pathtmp,name)

write_basefile(qfilefolerpath,station_filepath)
plot_baseline_multi(baseline_result_folderpath,plot_save_folderpath,xtick_step)

