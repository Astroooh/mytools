"""@author:Yuhang Wang
   @Time   :2022/3/7 20:44   """

import json
import os

json_path = "G:/datasets/2021hadatu/json/"
json_list = os.listdir(json_path)
print("json_list:", json_list)

for i in json_list:
    json_path1 = json_path + i
    with open(json_path1, "r") as f:
         ann = json.load(f)
    print(str(i)+'中的数据',ann)

