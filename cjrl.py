#coding:utf-8
import requests
import json
import time
from PIL import Image,ImageDraw,ImageFont
import math
import re
import os

#date=input('输入日期(如2018/0322):')
'''
判断时间必须大于9:00
选择影响前三的美国数据，如果美国数据不足，则选欧洲及英国数据
做一个关键词列表，只要存在此类关键词则优先进入制图项
对字典按照值来进行排序 https://rili.jin10.com/datas/2018/0409/economics.json

'''
date=input('输入日期(如2018/0409):')
date_list=list(date)
date_list.insert(7,'/')
date_output="".join(date_list)
date_today=time.strftime("%Y-%m-%d",time.localtime(time.time()))
url='https://rili.jin10.com/datas/{0}/economics.json'.format(date)
html=requests.get(url)
data_list=json.loads(html.text)
#将所有美国数据保存至USA字典中
USA={}
Not_USA={}

#字体文件设置
#"{}\msyh.ttf".format(os.getcwd)
image_background=Image.open(r"E:\economic_calendar\backgroundimage.jpg")
#字体
#file_path='{0}/{1}.{2}'.format(os.getcwd(),md5(content).hexdigest(),'jpg')
myfont_Broadway = ImageFont.truetype(r'{}\Broadway.ttf'.format(os.getcwd()),size=100)#日期字体
myfont_fzzdhjt = ImageFont.truetype(r'{}\fzzhjt.TTF'.format(os.getcwd()),size=60)#股票名称字体
myfont_wryh1 = ImageFont.truetype(r'{}\msyh.ttf'.format(os.getcwd()),size=40)#内容字体
draw = ImageDraw.Draw(image_background)

#获取当前系统的桌面路径
def GetDesktopPath():
    return os.path.join(os.path.expanduser("~"), 'Desktop')

def get_USA_data():
	for i in data_list:
		if i["country"]=="美国":
			USA['{}   {}'.format(i["time_show"],i["title"])]={}
			USA['{}   {}'.format(i["time_show"],i["title"])]['star']=i["star"]
		#如果美国数据不足三个，则补足其他国家的数据
	reserve_list=sorted(USA.items(),key=lambda item:item[1]['star'],reverse = True)
	USA_list=[]
	for i in reserve_list:
		if int(i[0][0:2]) > 9 and i[0].find('EIA')==-1:#排除包含EIA字样的数据
			USA_list.append(i) 
	if len(USA_list)<3:
		output_list=USA_list
		Not_USA_list=get_other_data()
		for i in range(3-len(USA_list)):
			output_list.append(Not_USA_list[i])
		#return output_list
	elif len(USA_list)==3:
		output_list=USA_list
		#return output_list
	elif len(USA_list)>3:
		output_list=[]
		for i in range(3):
			output_list.append(USA_list[i])
	output_list=sorted(output_list,key=lambda item:(int(item[0][:2])*60+int(item[0][3:5])),reverse = False)#按时间从小到大排序
	return output_list
	
def get_other_data():
	for i in data_list:
		if i["country"]!="美国":
			Not_USA['{}   {}'.format(i["time_show"],i["title"])]={}
			Not_USA['{}   {}'.format(i["time_show"],i["title"])]['star']=i["star"]
	reserve_list=sorted(Not_USA.items(),key=lambda item:item[1]['star'],reverse = True)
	return reserve_list

#解析数据影响,目前并未调用
def get_influence(title):
	for i in data_list:
		if i["title"]==title:
			url_number=i["url"][-6:]
			#print(url_number)
			url_influence="http://rili.jin10.com/datas/jiedu/{}.json".format(url_number)
			html_influence=requests.get(url_influence)
			data_list_influence=json.loads(html_influence.text)
			influence_str=data_list_influence["impact"]
			#以下代码块用作对数据影响的解析
			pattern=re.compile('^((?!利空).)*(利多美元|利好美元).*$')
			pattern1=re.compile('^((?!利多|利好).)*(利空美元).*$')
			pattern2=re.compile('^((?!利空).)*(利多欧元|利好欧元).*$')
			pattern3=re.compile('^((?!利多|利好).)*(利空欧元).*$')
			if pattern.match(influence_str)!=None:
				influence_str='若数据>预期 利空金银'
			elif pattern1.match(influence_str)!=None:
				influence_str='若数据>预期 利多金银'
			elif pattern2.match(influence_str)!=None:
				influence_str='若数据>预期 利多金银'
			elif pattern3.match(influence_str)!=None:
				influence_str='若数据>预期 利空金银'
			else:
				influence_str='          /         '#如果数据内容不包含利多利空之类的字样，则影响不显示
			return influence_str

#不对数据影响进行转义，直接抓取影响及数据解释
def get_influence1(title):
	for i in data_list:
		if i["title"]==title:
			url_number=i["url"][-6:]
			#print(url_number)
			url_influence="http://rili.jin10.com/datas/jiedu/{}.json".format(url_number)
			html_influence=requests.get(url_influence)
			data_list_influence=json.loads(html_influence.text)
			influence_str=data_list_influence["impact"]
			paraphrase_str='数据释义：{}'.format(data_list_influence["paraphrase"])
			return (influence_str,paraphrase_str)

#实现当字符串长度>=1565时自动换行，locals()的动态变量名方法
def print_text(text,text1,star,title,start_pos):
	j=1
	draw.text((206,start_pos),text1,font=myfont_wryh1,fill=(251,200,0),align="center")#打印影响
	star_str='影响星级:{0}星'.format(star)
	star_str_pos_hori=1771-myfont_wryh1.getsize(star_str)[0]
	draw.text((star_str_pos_hori,start_pos),star_str,font=myfont_wryh1,fill=(251,200,0),align="center")#打印影响星级
	while 1:
		locals()['text_return'+str(j)]=''
		#可以输出所有长度>=1500的行，但最后一行无法输出
		for i in text:
			locals()['text_return'+str(j)]=locals()['text_return'+str(j)].__add__(i)
			#保证text每传递一个字符就删除一个字符，实现字符串的从前向后pop的功能
			text=text[1:]
			if  myfont_wryh1.getsize(locals()['text_return'+str(j)])[0]>=1565:
				draw.text((206,start_pos+(j)*80),locals()['text_return'+str(j)],font=myfont_wryh1,fill=(255,255,255),align="center")
				break
		#输出不满足长度>=1500的最后一行，同时为下一个段落返回一个位置定位pos
		if text=='':
			draw.text((206,start_pos-100),title,font=myfont_fzzdhjt,fill=(255,200,0),align="center")
			draw.text((206,start_pos+(j)*80),locals()['text_return'+str(j)],font=myfont_wryh1,fill=(255,255,255),align="center")
			pos=start_pos+(j)*80+280
			break
		else:
			j+=1
	return pos

def main():
	output_list=get_USA_data()
	for i in output_list:
		i[1]['influence']=get_influence1(i[0][8:])[0]
		i[1]['paraphrase']=get_influence1(i[0][8:])[1]
	#print(output_list)
	draw.text((660,468),date_output,font=myfont_Broadway,fill=(251,200,0),align="center")
	pos_next1=print_text(output_list[0][1]['paraphrase'],output_list[0][1]['influence'],str(output_list[0][1]['star']),output_list[0][0],780)
	pos_next2=print_text(output_list[1][1]['paraphrase'],output_list[1][1]['influence'],str(output_list[1][1]['star']),output_list[1][0],pos_next1)
	pos_next3=print_text(output_list[2][1]['paraphrase'],output_list[2][1]['influence'],str(output_list[2][1]['star']),output_list[2][0],pos_next2)
	#pos_next4=print_text(output_list[1]['paraphrase'],j[0],pos_next3)
	image_background.save("{0}\\财经日历.jpg".format(GetDesktopPath(),"JPEG"))

if __name__=='__main__':
	main()

#下一步修改，背景图拉长些，将影响增加进去，加入判断是否超出范围的语句
#增加重要性，将筛选出的三个数据按照时间从上至下排序
#将部分功能进行完善，增加函数的可扩展性

