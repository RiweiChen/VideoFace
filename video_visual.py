import os
import sys
import math
import numpy as np
import cv2
import matplotlib.pyplot as plt
plt.switch_backend('agg')
from setting import *
colors =['b','g','r','c','m','y','k']


def show_time_expression_path(result_list, vid = 0):
    '''
    @brief show visual path by id
    '''
    with open(result_list) as f:
        result = []
        plt.figure(figsize = (12,6))
        plt.xlabel("time")
        plt.ylabel("phase")
        plt.ylim(-1.2,1.2)
        for line in f:
            item = line.strip().split("\t")
            pid = int(item[0])
            if pid == vid:
                meta = eval(item[1])
                exp = exp2scole[meta[6]]
                result.append(exp)
        np_res = np.array(result)
        np_res = np.convolve(np_res,[0.2,0.2,0.2,0.2,0.2],'same')
        plt.plot(range(len(result)),np_res,'-r.')
        plt.savefig(str(vid)+"_exprssion.png",format="png")


def ranking_by_attractive(result_list):
    id2result = dict()
    with open(result_list) as f:
        result = []
        for line in f:
            item = line.strip().split("\t")
            meta = eval(item[1])
            pid = int(item[0])
            gender = float(meta[4])
            attractive = float(meta[5])
            if pid not in id2result:
                id2result[pid] = dict()
                id2result[pid]['gender'] = [gender]
                id2result[pid]['attractive'] = [attractive]
            else:
                id2result[pid]['gender'].append(gender)
                id2result[pid]['attractive'].append(attractive)
        for key, value in id2result.items():
            result.append((key,np.mean(value["gender"]), np.mean(value["attractive"])))
        # sort by attractive
        result = sorted(result, key=lambda s:s[2])
        for r in result:
            print("Id:{}, Gender:{}, Attractive:{}".format(r[0],r[1],r[2]))


def select_most_attractive_cover(result_list, facebook):
    id2result = dict()
    with open(result_list) as f:
        result = []
        for line in f:
            item = line.strip().split("\t")
            meta = eval(item[1])
            pid = int(item[0])
            filename = meta[0]+"_"+str(meta[1])
            gender = float(meta[4])
            attractive = float(meta[5])
            if pid not in id2result:
                id2result[pid] = dict()
                id2result[pid]['filename'] = [filename]
                id2result[pid]['gender'] = [gender]
                id2result[pid]['attractive'] = [attractive]
            else:
                id2result[pid]['filename'].append(filename)
                id2result[pid]['gender'].append(gender)
                id2result[pid]['attractive'].append(attractive)
        for key, value in id2result.items():
            maxid = np.argmax(value["attractive"])
            result.append((key,value['filename'][maxid]))
        result = sorted(result,key=lambda s:s[0])
        num_pid = len(result)
        w = int(math.ceil(math.sqrt(num_pid)))
        # show face book
        plt.figure(figsize=(12,12))
        for idx, r in enumerate(result):
            image_path = os.path.join(video_face_path, str(r[0]), r[1]+".jpg")
            im = cv2.imread(image_path)
            im = cv2.resize(im,(256,256))
            im = cv2.cvtColor(im,cv2.COLOR_BGR2RGB)
            plt.subplot(w,w,idx+1)
            plt.title(str(r[0]),fontsize = 8)
            plt.xlabel(str(r[0]),fontsize = 8)
            plt.axis('off')
            plt.imshow(im)
        plt.savefig(facebook,format="png")


def show_time(set_id = "01.mp4", save_name):
    '''
    @brief video show time by id
    '''
    with open("result.list") as f:
        result = []
        plt.figure(figsize=(12,6))
        plt.xlabel("present time in second")
        vids = []
        times = []
        for line in f:
            item = line.strip().split("\t")
            meta = eval(item[1])
            pid = int(item[0])
            set_id_ = meta[0]
            if set_id_!=set_id:
                continue
            gender = float(meta[4])
            attractive = float(meta[5])
            vids.append(pid)
            times.append(int(meta[1])/25)
        vid2idx=dict()
        idx = 1
        for v in vids:
            if v not in vid2idx:
                vid2idx[v] = idx
                idx+=1
        plt.ylim([0,idx+1])
        ylen = idx+1
        pid2time = {}
        pid2idxs = {}
        for vid, time in zip(vids, times):
            idx = vid2idx[vid]
            plt.plot(time, idx, marker='.', color=colors[idx%len(colors)])
        plt.yticks(range(ylen), [""]+[str(v) for v in set(vids)]+[""])
        plt.ylabel("people id")
        plt.savefig(save_name,format="png")


if __name__ == "__main__":
    result_list = "result.list"
    ranking_by_attractive(result_list)
    select_most_attractive_cover(result_list, "facebook.png")
    for set_id in sorted(os.listdir(video_path)):
        show_time(set_id,set_id+"_show_time.png")
    show_time_expression_path(result_list,0)
