import numpy as np
import os
import sys
import cv2
import matplotlib.pyplot as plt
plt.switch_backend('agg')
import setting import *

fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')



def get_clip_cv2(video_name, vid, (start, end)):
    '''
    @brief for cv2, it will lose voice
    '''
    full_video_path = os.path.join(video_path, video_name)
    video = cv2.VideoCapture(full_video_path)
    video.set(1,start)
    ret, frame = video.read()
    h,w = frame.shape[:2]
    video_writer = cv2.VideoWriter("clips_happy/"+video_name+"_"+str(vid)+"_"+str(start)+".mp4", fourcc, 25, (w,h), 1)
    for i in range(start,end):
        ret, frame = video.read()
        video_writer.write(frame)
    video_writer.release()


def int2time(t):
    h = t/3600
    m = (t%3600)/60
    s = (t%3600)%60
    result = "{:02}:{:02}:{:02}".format(h,m,s)
    return result


def get_clip_ffmpeg(video_name, save_name, (start, end)):
    full_video_path = os.path.join(video_path, video_name)
    cmd = "ffmpeg -i {} -ss {} -t {} -async 1 -strict -2  {}".format(
            full_video_path,
            int2time(start/25),
            int2time((end-start)/25),
            save_name)
    os.system(cmd)


def get_video_range(ptss, gap=25*5, min_cnt_face=10):
    '''
    @note extract clips on one video only, in continue form.

    '''
    result = []
    cnt = 0
    for i in range(1,len(ptss)):
        if ptss[i] - ptss[i-1] < gap:
            cnt+=1
        else:
            if cnt >= min_cnt_face:
                result.append((ptss[i-cnt], ptss[i-1]))
            cnt = 1
    return result



def extract_special_expression_clip(vid, exp="Angry"):
    with open("result.list") as f:
        result = []
        video2pts = dict()
        for line in f:
            item = line.strip().split("\t")
            pid = int(item[0])
            if pid == vid:
                meta = eval(item[1])
                video_name = meta[0]
                pts = int(meta[1])
                #exp_ = exp2scole[meta[6]]
                exp_ = meta[6]
                if exp == exp_:
                    result.append(pts)
                    if video_name not in video2pts:
                        video2pts[video_name] = [pts]
                    else:
                        video2pts[video_name].append(pts)
        #get_video_range(result)
        #print(result)
        for key, value in video2pts.items():
            if len(value) < 10:
                continue
            #print(vid, key)
            result = get_video_range(value)
            for item in result:
                #get_clip(key,vid,item)
                get_clip_ffmpeg(key,vid,item)


def get_unit((start1,end1), (start2,end2)):
    return (min(start1,start2),max(end1,end2))


def get_intersection((start1,end1),(start2,end2)):
    if start2 > end1 or start1 > end2:
        return (0,0)
    else:
        start = max(start1, start2)
        end = min(end1, end2)
        return (start,end)


def get_iou((start1,end1), (start2,end2)):
    s1,e1 = get_intersection((start1,end1),(start2,end2))
    s2,e2 = get_unit((start1,end1),(start2,end2))
    return 1.0*(e1-s1)/(e2-s2)


def combile_close(to_clips):
    if len(to_clips) <=1:
        return to_clips
    to_clips = sorted(to_clips, key=lambda s:s[0])
    result = []
    last_clip = to_clips[0]
    i = 1
    num_clips = len(to_clips)
    while i < num_clips:
        if to_clips[i][0]-last_clip[1] < 20*25:
            last_clip = get_unit(last_clip, to_clips[i])
            i+=1
        else:
            result.append(last_clip)
            if i < (num_clips-2):
                last_clip = to_clips[i+1]
            i+=2
    if last_clip not in to_clips:
        result.append(last_clip)
    return result


def extract_common_clip(vids):
    """
    @get get clips of common show
    """
    with open("result.list") as f:
        result = []
        video2pid2pts = dict()
        for line in f:
            item = line.strip().split("\t")
            pid = int(item[0])
            if pid in vids:
                meta = eval(item[1])
                video_name = meta[0]
                pts = int(meta[1])
                result.append(pts)
                if video_name not in video2pid2pts:
                    video2pid2pts[video_name] = dict()
                    video2pid2pts[video_name][pid] = [pts]
                else:
                    if pid not in video2pid2pts[video_name]:
                        video2pid2pts[video_name][pid] = [pts]
                    else:
                        video2pid2pts[video_name][pid].append(pts)
        for video_name, pid2pts in video2pid2pts.items():
            pid2results = dict()
            for pid, pts in pid2pts.items():
                if len(pts) < 5:
                    continue
                result= get_video_range(pts, gap=25*10, min_cnt_face=5)
                if result !=[]:
                    if pid not in pid2results:
                        pid2results[pid] = result
                    else:
                        pid2results[pid].extend(result)
            for pid1, results1 in pid2results.items():
                for pid2, result2 in pid2results.items():
                    if pid1 >= pid2:
                        continue
                    to_clips = []
                    for u in results1:
                        for v in result2:
                            iou = get_iou(u,v)
                            #print("u v: ",u,v,iou)
                            if iou > 0.0:
                                print(video_name, pid1, pid2, u, v, iou)
                                (s,e) = get_unit(u,v)
                                to_clips.append((s,e))
                    #combine sets which close
                    if to_clips == []:
                        continue
                    to_clips = list(set(to_clips))
                    to_clips = combile_close(to_clips)
                    for (s,e) in to_clips:
                        save_name = "clips_common_show/"+video_name+"_"+str(pid1)+"_"+str(pid2)+"_"+str(s)+"_"+str(e)+".mp4"
                        get_clip_ffmpeg(video_name, save_name, (s,e))


if __name__ == "__main__":
    extract_special_expression_clip(3,"Happy")
    extract_common_clip([6,176])
