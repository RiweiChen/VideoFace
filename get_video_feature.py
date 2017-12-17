import numpy as np
import os
import sys
import cv2
from collections import Counter
import dlib
import copy
from setting import *
sys.path.append("./thrift/gen-py")
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.transport import TSSLSocket
from thrift.transport import THttpClient
from thrift.protocol import TBinaryProtocol

from FaceAPI import FaceAPI
from FaceAPI.ttypes import *
transport = TSocket.TSocket(FaceApiHost, FaceApiPort)
transport = TTransport.TFramedTransport(transport)
protocol = TBinaryProtocol.TBinaryProtocol(transport)
client = FaceAPI.Client(protocol)

# face idx to expression
exps = {0:"Angry",
        1:"Disgust",
        2:"Fear",
        3:"Happy",
        4:"Sad",
        5:"Surprise",
        6:"Neutral",
        }
def get_feature(video_path, save_path, save_list):
    video_files = sorted(os.listdir(video_path))
    features = []
    idxs = []
    faces = []
    videos = []
    face_attrs = []
    fout = open(save_list,'w')
    for video_file in video_files:
        full_video_path = os.path.join(video_path, video_file)
        video = cv2.VideoCapture(full_video_path)
        fps = int(video.get(cv2.CAP_PROP_FPS))
        num_frame = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        print("processing video_file: {}, num_frame: {}, fps: {}".format(video_file, num_frame, fps))
        idx = 0
        for i in range(0,num_frame, fps):
            video.set(1,i)
            ret, frame = video.read()
            if not ret:
                print("done")
                break;
            transport.open()
            req = ImageReq()
            req.name =video_file+"#"+str(i)
            req.image_data = cv2.imencode(".jpg",frame)[1]
            rsp = client.predict_image(req)
            if rsp.status == "OK":
                for _, face_feature in enumerate(rsp.face_features):
                    r = face_feature.region
                    meta =[video_file, i]
                    meta.append([int(r.x1),int(r.x2), int(r.y1), int(r.y2)])
                    meta.append(int(face_feature.age))
                    meta.append(face_feature.gender)
                    meta.append(int(face_feature.attractive))
                    exp_idx = np.argmax(face_feature.exps)
                    exp = exps[exp_idx]
                    meta.append(exp)
                    if (r.x2-r.x1)*(r.y2-r.y1) < MinFaceSize*MinFaceSize:
                        continue
                    features.append(dlib.dlib.vector(face_feature.feature))
                    idxs.append(i)
                    faces.append(copy.deepcopy(frame[r.y1:r.y2,r.x1:r.x2,:]))
                    videos.append(video_file)
                    face_attrs.append(meta)
            else:
                print("error status: {}".format(rsp.status))
            transport.close();
            idx+=1
    # TODO(crw): for large features size, this would be very slow
    # for my case, it cost near 6 hours to complete.
    labels = dlib.chinese_whispers_clustering(features, FaceClustingThreshold)
    counter = Counter(labels)
    ids = []
    for id_, cnt in counter.most_common():
        if cnt > MinFaceCount:
            ids.append(id_)
    for i in range(len(labels)):
        if labels[i] in ids:
            id_path = os.path.join(save_path, str(labels[i]))
            if not os.path.exists(id_path):
                os.makedirs(id_path)
            cv2.imwrite(os.path.join(id_path, videos[i]+"_"+str(idxs[i])+".jpg"), faces[i])
            fout.write(str(labels[i])+"\t"+str(face_attrs[i])+"\n")
    fout.close()

if __name__ =="__main__":
    save_list = "result.list"
    get_feature(video_path, video_face_path, save_list)
