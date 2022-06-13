"""@author:Yuhang Wang
   @Time   :2022/3/7 20:44
   -------------------------------------
   2022.6.5 完成json的分割
   -------------------------------------
   2022.6.6 发现还有坐标没有根据切片参考系转换！
   -------------------------------------
   2022.6.7 解决坐标转换
            用deepcopy解决变量赋值改变问题
            成功
   2022.6.13 改了一个bug, 第87行,改成jsonpath
             坐标参考系转换那里不支持polygons
             改bug ，imagpath i j写反，已修改
"""

from PIL import Image
import json
import os
import math
import copy
#######################################
'''切割参数设置'''
x = 0
y = 0
w = 1024
h = 1024
overlap = 100
stride1 = w-overlap
stride2 = h-overlap
#####################################################
'''outputcrop的输出文件位置设置'''
outputcropdir = r"G:\datasets\hadatu\dataset\data1.0\addoutputcrop"
if not os.path.exists(outputcropdir):
    os.makedirs(outputcropdir)

'''jsoncrop的输出文件位置设置'''
outjsoncropdir = r"G:\datasets\hadatu\dataset\data1.0\addoutjsoncrop"
if not os.path.exists(outjsoncropdir):
    os.makedirs(outjsoncropdir)
#####################################################

img_path =r"G:\datasets\hadatu\dataset\data1.0\addimg"
fileList = os.listdir(img_path)
print("fileList:", fileList)
print('图片数量：', len(fileList))

json_path = r"G:\datasets\hadatu\dataset\data1.0\addjson"
json_list = os.listdir(json_path)
print("json_list:", json_list)  # json名称的列表

######################################################
for q in fileList:
    im = Image.open(os.path.join(img_path , q))
    # 获取图片无后缀名称
    img_name = q.strip(".JPG")
    print('无后缀名称',img_name)
    # 图片的宽度和高度
    img_size = im.size
    print("该图片宽度和高度分别是{}".format(img_size))

    imgcrop = []
    for j in range(math.ceil((img_size[1] - overlap) / stride2)):  # j是行数
        imgcrop.append([])
        for i in range(math.ceil((img_size[0] - overlap) / stride1)):
            imgcrop[j].append(0)  # 这一行有多少列，加几个0
    #print(imgcrop)
    jscrop = copy.deepcopy(imgcrop)  # json按照图剪裁的二维列表，复制一个空的imgcrop
    print('jscrop列表：',jscrop)
    print('行数',len(jscrop))
    print('列数',len(jscrop[0]))

    for j in range(0, math.ceil((img_size[1] - overlap) / stride2)):
        for i in range(0, math.ceil((img_size[0] - overlap) / stride1)):
            x1 = x + i * stride1
            y1 = y + j * stride2
            x2 = x + i * stride1 + w
            y2 = y + j * stride2 + h
            ##############
            #剪裁图像
            region = im.crop((x1, y1, x2, y2))  # 里面要封装成一个元组
            outputpath = os.path.join(outputcropdir,(str(img_name) + 'crop_' + str(j) + str(i) + ".jpg"))
            region.save(outputpath)
            ##############
            imgcrop[j][i] = [x1, y1, x2, y2]  # 边界储存到对应的位置上, 左上，右下
            print('crop_' + str(j) + str(i) + '的边界', imgcrop[j][i])
    print(imgcrop)   #储存边界的二维列表

###################################################################################
    jsonpath = os.path.join(json_path , (img_name+'.json'))
    print(jsonpath)
    with open(jsonpath, "r") as f:
         ann = json.load(f)
    #print(str(i)+'中的数据',ann['shapes'])

    print('jscrop列表：', jscrop)
    for i in range(len(ann['shapes'])):
        # print("该图片中有几个目标:", len(ann["shapes"]))
        print(i)
        # print(ann['shapes'][i])
        # print(ann['shapes'][i]['points'])
        # asp_x1 = min(ann['shapes'][i]['points'][0][0],ann['shapes'][i]['points'][1][0])
        asp_x1 = min(x[0] for x in ann['shapes'][i]['points'])   # 支持了polygons
        # asp_y1 = min(ann['shapes'][i]['points'][0][1],ann['shapes'][i]['points'][1][1])
        asp_y1 = min(x[1] for x in ann['shapes'][i]['points'])
        # asp_x2 = max(ann['shapes'][i]['points'][1][0],ann['shapes'][i]['points'][1][0])
        asp_x2 = max(x[0] for x in ann['shapes'][i]['points'])
        # asp_y2 = max(ann['shapes'][i]['points'][1][1],ann['shapes'][i]['points'][0][1])
        asp_y2 = max(x[1] for x in ann['shapes'][i]['points'])
        centerx=(asp_x1+asp_x2)/2
        centery=(asp_y1+asp_y2)/2
        print('中心点(',centerx,centery,')')
        ##############################################################
        cropl=int(centerx//stride1)  # w,横轴，列数
        croph=int(centery//stride2)  # h,纵轴，行数
        print('位于行列',croph,cropl)
        if asp_x1>imgcrop[croph][cropl][0] and asp_y1>imgcrop[croph][cropl][1]:
            print("true0")
            if jscrop[croph][cropl] == 0:
                jscrop[croph][cropl]=copy.deepcopy([ann['shapes'][i]])  # 不能直接赋值，要deepcopy一份
            else:
                jscrop[croph][cropl].append(copy.deepcopy(ann['shapes'][i]))
        # 判断左上角
        if centerx<imgcrop[croph-1][cropl-1][2] and centery<imgcrop[croph-1][cropl-1][3]:   # 6.13发现，当croph=0时，croph-1=-1,列表加入错误，加到了jscrop[-1]
            if asp_x2<imgcrop[croph-1][cropl-1][2] and asp_y2<imgcrop[croph-1][cropl-1][3]:

                if croph - 1 >= 0 and cropl - 1 >= 0:  # 6.13 加入判断，不能小于0
                    print("true1")
                    if jscrop[croph-1][cropl-1] == 0:
                        jscrop[croph-1][cropl-1] = copy.deepcopy([ann['shapes'][i]])
                    else:
                        jscrop[croph-1][cropl-1].append(copy.deepcopy(ann['shapes'][i]))
        # 判断正上方
        if centery<imgcrop[croph-1][cropl][3]:
            if asp_x1>imgcrop[croph-1][cropl][0] and asp_y1>imgcrop[croph-1][cropl][1] and asp_x2<imgcrop[croph-1][cropl][2] and asp_y2<imgcrop[croph-1][cropl][3]:
                if croph - 1 >= 0 :  # 6.13 加入判断，不能小于0
                    print("true2")
                    if jscrop[croph-1][cropl] == 0:
                        jscrop[croph-1][cropl] = copy.deepcopy([ann['shapes'][i]])
                    else:
                        jscrop[croph-1][cropl].append(copy.deepcopy(ann['shapes'][i]))
        # 判断左方
        if centerx<imgcrop[croph][cropl-1][2]:
            if asp_x1 > imgcrop[croph][cropl-1][0] and asp_y1 > imgcrop[croph][cropl-1][1] and asp_x2 < imgcrop[croph][cropl-1][2] and asp_y2 < imgcrop[croph][cropl-1][3]:
                if cropl - 1 >= 0:  # 6.13 加入判断，不能小于0
                    print("true3")
                    if jscrop[croph][cropl-1] == 0:
                        jscrop[croph][cropl-1] = copy.deepcopy([ann['shapes'][i]])
                    else:
                        jscrop[croph][cropl-1].append(copy.deepcopy(ann['shapes'][i]))
        #################################################################
    num=0  # 有目标的json切片数量
    for i in range(len(jscrop)):  # i   循环  jscrop的行数
        for j in range(len(jscrop[0])): # j 循环 jscrop的列数
            #print(i,j)
            if jscrop[i][j] != 0:   # 有目标存在的
                num+=1
                print('jscrop',i,'行',j,'列',jscrop[i][j])
                #########################################################
                #坐标转换
                for s in range(len(jscrop[i][j])):
                    # 矩形框的标注
                    jscrop[i][j][s]["points"][0][0]-=j*stride1  # 左上x # 6.13发现 这里不支持polygons
                    jscrop[i][j][s]["points"][0][1]-=i*stride2  # 左上y
                    jscrop[i][j][s]["points"][1][0]-=j*stride1
                    jscrop[i][j][s]["points"][1][1]-=i*stride2
                    ##############
                    # 支持polygons的标注（进行中）
                    # x_min = min(x[0] for x in jscrop[i][j][s]['points'])
                    # x_min -= j * stride1   #左上 # 用另一个变量指向这个要改变的值，然后改这个变量  # 支持了polygons
                    # y_min = min(x[1] for x in jscrop[i][j][s]['points'])
                    # y_min -= i * stride2
                    # x_max = max(x[0] for x in jscrop[i][j][s]['points'])
                    # x_max -= j * stride1
                    # y_max = max(x[1] for x in jscrop[i][j][s]['points'])
                    # y_max -= i * stride
                    ##############
                print('转换后的jsoncrop',i,'行',j,'列',jscrop[i][j])
                #########################################################
                jsonname = str(img_name)+ 'crop_' + str(i) + str(j) + '.json'
                jsoncrop_path = os.path.join(outjsoncropdir, jsonname)

                c=dict()
                c["version"]="4.6.0"
                c["flags"]={}
                c["shapes"]=jscrop[i][j]
                c["imagePath"]=str(img_name) + 'crop_' + str(i) + str(j) + ".jpg"  # 2022.6.13 发现i和j反了，已改正
                c["imageHeight"]=h
                c["imageWidth"]=w

                with open(jsoncrop_path, 'w') as f:
                    json.dump(c, f, indent=2)
    print('json切片数量',num)
