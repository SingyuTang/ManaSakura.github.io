'''
此程序用于从A文件夹中获取指定日期的哨兵轨道文件并复制到B文件夹
1所需准备：       1.存储下载好的哨兵轨道文件夹A的绝对路径，如oldorbitfolderpath= r'E:\哨兵轨道\SA'
                2.提取轨道后需存放的轨道文件夹B的绝对路径，如neworbitfolderpath= r'E:\myfile\myorbit'
                3.存放哨兵影像文件夹的绝对路径，如SARfolderpath=r'E:\myfile\SAR'
                4.存放轨道日期的文件路径，如datetxtpath= r'E:\myfile\datelist.txt'
2运行生成的文件：  1.提取的轨道文件的日期，路径需自行指定，即“准备”中的第4点
                2.被提取的轨道文件并以文件夹的形式存放在文件夹B中（由于代码的问题），此外B文件夹中还含有名为orbit的子文件夹，orbit文件夹中含有被提取的所有轨道文件
介于作者对Python仍处于学习阶段，程序中有许多不足之处，对于错误和异常的处理尚不到位，需注意以下事项：
                1.所要复制的轨道文件必须为文件夹A中所含有的
                2.存放轨道文件的文件夹B建议新建或不创建，会自动生成，且B文件夹下不能含有orbit文件夹，否则会报错
                3.当同一日期A、B星的轨道文件同时位于A文件夹下时，默认拷贝A星的轨道文件，故建议将A星和B星的轨道文件分开存放，以便正确获取对应日期的文件，
                同时将SAR不同卫星影像文件也分开存放来获取对应卫星的轨道文件
                其他问题读者如有发现，可自行修改和补充
'''

import os
import datetime
from shutil import copyfile
from pathlib import Path
oldorbitfolderpath= r'C:\Users\tang xingyou\PycharmProjects\InSAR\orbit'     #存放轨道文件的文件夹路径
neworbitfolderpath= r'C:\Users\tang xingyou\PycharmProjects\InSAR\myorbit'           #提取目标轨道后所存放的文件夹路径
datetxtpath= r'C:\Users\tang xingyou\PycharmProjects\InSAR\datelist.txt'     #指定轨道日期文件
SARfolderpath=r'C:\Users\tang xingyou\PycharmProjects\InSAR\SAR'        #存放影像文件夹的路径
class orbit:
    def get_filelist(self, Folderpath):
        '''
        获取哨兵影像/轨道文件夹下的所有文件名
        :param Folderpath:文件夹路径
        :return: 返回文件名列表
        '''
        filelist = os.listdir(Folderpath)
        return filelist

    def readSAR_folderpath_4_datelist(self,SAR_folderpath,datetxtpath):
        '''
        读取存放影像数据的文件夹下的所有文件名并保存为列表，读取文件名列表并提取影像日期
        :param SAR_folderpath: 影像存放的文件夹路径
        :param datetxtpath: 保存SAR影像日期的文件路径
        :return:
        '''
        orbit1=orbit()
        filelist=orbit1.get_filelist(SAR_folderpath)
        datelist=[]
        for name in filelist:
            datelist.append(name[17:25]+'\n')
        with open(datetxtpath,mode='w') as f:
            f.writelines(datelist)
        print('影像日期写入完成。写入路径：{}'.format(datetxtpath))

    def get_orbitdate0(self,filelist):
        '''
        获取文件名列表中的所有轨道文件的日期的前一天
        :param filelist:
        :return:
        '''
        datelist=[]
        for name in filelist:
            datelist.append(name[42:50])
        return datelist

    def get_orbit_year_md(self, datelist):
        '''
        提取datestr中的年、月、日并返回相应的列表
        :param datelist:
        :return:
        '''
        listyyyy=[]
        listmm=[]
        listdd=[]
        for strtmp in datelist:
            listyyyy.append(int(strtmp[0:4]))
            listmm.append(int(strtmp[4:6]))
            listdd.append(int(strtmp[6:8]))
        return listyyyy,listmm,listdd

    def readtxtdate(self,txtpath:str):
        '''
        读取txt文件中的日期并保存为字符串列表
        :param txtpath:
        :return:date，轨道日期列表
        '''
        datelist=[]
        with open(txtpath) as f:
            tline=f.readline()
            while tline:
                s=tline.replace('\n','')
                datelist.append(s)
                tline=f.readline()
        return datelist

    def get_datesub1(self,datestr:str):
        '''
        计算指定日期的前一天日期
        :param datestr:
        :return:date_1_str
        '''
        int_year=int(datestr[0:4])
        int_month=int(datestr[4:6])
        int_day=int(datestr[6:8])
        date1=datetime.date(int_year,int_month,int_day)
        yesterday = date1 - datetime.timedelta(days=1)
        date_1_str=yesterday.__format__('%Y%m%d')
        return date_1_str

    def awk_orbit_filename(self,orbit_date:str,orbit_folder:str):
        '''
        获取轨道文件夹下指定日期的轨道文件名
        :param orbit_date: 指定日期
        :param orbit_folder: 轨道文件夹
        :return: 文件路径
        '''
        orbit1=orbit()
        filelist=orbit1.get_filelist(orbit_folder)
        date_1=orbit1.get_datesub1(orbit_date)
        orbitname=''
        for name in filelist:
            date_1_in_orbitname=name[42:50]
            if date_1_in_orbitname==date_1:
                orbitname=name
                break
        if orbitname=='':
            print("文件夹中没有日期为{}的文件。".format(orbit_date))
        return orbitname

    def get_file_abspath(self, filename:str, folderpath:str):
        '''
        获取文件夹下指定文件的绝对路径
        :param filename:
        :param folder:
        :return:
        '''
        orbit1=orbit()
        filelist=orbit1.get_filelist(folderpath)
        if filename in filelist:
            abspath=os.path.join(folderpath,filename)
            return abspath
        else:
            print('轨道文件不存在。')

    def get_file_abspath_bulk(self, txt_filepath:str, orbitfolderpath:str):
        '''
        批量获取文件路径
        :return:
        '''
        orbit1=orbit()
        abspathlist=[]
        datelist_txt=orbit1.readtxtdate(txt_filepath)
        for date_line in datelist_txt:
            filename=orbit1.awk_orbit_filename(date_line, orbitfolderpath)
            abspath=orbit1.get_file_abspath(filename, orbitfolderpath)
            abspathlist.append(abspath)
        return abspathlist

    def copyfile1(self, oldpath_name, newpath):
        '''
        复制文件
        :param oldpath_name: 文件的旧路径，包括文件名
        :param newpath: 目的文件夹地址，不含文件名
        :return:
        '''
        if not os.path.isfile(oldpath_name):
            print("文件{}不存在".format(oldpath_name))
        else:
            fpath,fname=os.path.split(oldpath_name)
            if not os.path.exists(newpath):
                os.makedirs(newpath)
                src=os.path.join(fpath,fname)
                dst=os.path.join(newpath,fname)
                print("文件{}正在复制,    {}-->{}".format(fname, fpath, newpath))
                copyfile(src, dst)

    def copyfile_bulk(self, oldfolerpath, newfolderpath, txtpath):
        '''
        复制文件批量
        :param oldfolerpath: 老文件夹地址
        :param newfolderpath: 新文件夹地址
        :return:
        '''
        orbit1 = orbit()
        abspathlist = orbit1.get_file_abspath_bulk(txtpath, oldfolerpath)
        for abspath in abspathlist:
            if os.path.isfile(abspath):
                fpath,fname=os.path.split(abspath)
                src=abspath
                dst=os.path.join(newfolderpath,fname)
                orbit1.copyfile1(src, dst)
            else:
                print('路径{}不存在'.format(abspath))
        print("所有轨道文件复制完成，文件写入路径：{}".format(newfolderpath))

    def copyfile2_bulk(self,neworbitfolderpath):
        '''
            从neworbitfolderpath文件夹中获取所有轨道文件并复制到neworbitfolderpath的子文件夹orbit中
            :param neworbitfolderpath: neworbit的文件夹路径
            :return:
            '''
        orbit1 = orbit()
        filelist = orbit1.get_filelist(neworbitfolderpath)
        oldfullpathlist = []
        newfullpathlist = []
        for name in filelist:
            fullpath = os.path.join(neworbitfolderpath, name, name)
            oldfullpathlist.append(fullpath)
        for name in filelist:
            fullpath = os.path.join(neworbitfolderpath, 'orbit', name)
            newfullpathlist.append(fullpath)
        file_num = len(oldfullpathlist)
        orbitfolderpath = os.path.join(neworbitfolderpath, 'orbit')
        if os.path.exists(orbitfolderpath):
            print('orbit文件夹已存在')
        else:
            os.chdir(neworbitfolderpath)
            os.makedirs('orbit')
        print('orbit文件夹正在生成...')
        for i in range(file_num):
            src = oldfullpathlist[i]
            dst = newfullpathlist[i]
            src_path = Path(src)
            dst_path = Path(dst)
            copyfile(src_path, dst_path)
        print('orbit文件夹已生成，路径为：{}'.format(orbitfolderpath))

def copy_main(oldorbitfolerpath, neworbitfolderpath, SAR_foldername, datetxtpath):
    '''
    复制文件的主函数
    :param oldorbitfolerpath: 存放轨道文件的文件夹路径
    :param neworbitfolderpath: 提取目标轨道后所存放的文件夹路径
    :param SAR_foldername: SAR影像存放的文件夹路径
    :param datetxtpath: 指定轨道日期文件路径
    :return:
    '''
    orbit1=orbit()
    orbit1.readSAR_folderpath_4_datelist(SAR_foldername, datetxtpath)
    orbit1.copyfile_bulk(oldorbitfolerpath, neworbitfolderpath, datetxtpath)
    orbit1.copyfile2_bulk(neworbitfolderpath)

copy_main(oldorbitfolderpath, neworbitfolderpath, SARfolderpath, datetxtpath)
