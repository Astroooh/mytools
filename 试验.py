"""@author:Yuhang Wang
   @Time   :2022/2/25 10:07   """
from PIL import Image
import os
import math
import json

x = 0
y = 0
w = 1280
h = 720
overlap = 100
stride1 = w-overlap
stride2 = h-overlap
outputcropdir = "./outputcrop/hadatuyanzheng/"
if not os.path.exists(outputcropdir):
    os.makedirs(outputcropdir)



'''
json_path = "G:/datasets/2021hadatu/json/"
json_list = os.listdir(json_path)
print("json_list:", json_list)
'''

img_path = "C:/Users/Astro_h/Desktop/yanzheng/hadatu/"
fileList = os.listdir(img_path)
print("fileList:", fileList)
print('图片数量：', len(fileList))

'''
# 获得图片无格式后缀名称
imgname=[]
for imageName in fileList:
    saveName = imageName.strip(".jpg")
    #print("图片名称:", saveName)
    imgname.append(saveName)
print('图片无格式后缀名称：',imgname)
'''

print('开始循环处理图片...')
# 循环依次打开每张图片
for q in range(len(fileList)):
    im = Image.open(img_path + str(fileList[q]))
    # 获取图片无后缀名称
    img_name = fileList[q].strip(".jpg")
    print('处理的图片名称为：', img_name)
    # 图片的宽度和高度
    img_size = im.size
    print("该图片宽度和高度分别是{}".format(img_size))

    # 获取图片分割对应的空二维列表
    imgcrop=[]
    for j in range(math.ceil((img_size[1]-overlap)/stride2)):
        imgcrop.append([])
        for i in range(math.ceil((img_size[0]-overlap)/stride1)):
            imgcrop[j].append(0)  #这一行有多少列，加几个0
    print(imgcrop) #打印一张图片个分割成的二位列表，每一个值代表对应的图片crop ，j代表行号，i代表列号

    for j in range(0,math.ceil((img_size[1]-overlap)/stride2)):
        for i in range(0,math.ceil((img_size[0]-overlap)/stride1)):
            x1=x+i*stride1
            y1=y+j*stride2
            x2=x+i*stride1 + w
            y2=y+j*stride2 + h
            region = im.crop((x1, y1, x2, y2)) #里面要封装成一个元组
            region.save(outputcropdir + str(img_name) + 'crop_' + str(j) + str(i) + ".jpg")

            imgcrop[j][i]=[x1,y1,x2,y2]
            print(str(img_name) + 'crop_' + str(j) + str(i) + '的边界', imgcrop[j][i])

