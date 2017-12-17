#!/usr/local/bin/thrift --gen cpp --gen py:new_style -o . -r
namespace cpp FaceAPI
#face rect
struct Region {
    1: double x1,
    2: double x2,
    3: double y1,
    4: double y2,
}

struct FaceFeature{
    1: Region region,
    2: double age,
    3: double gender,
    4: list<double> racial,
    5: list<double> feature,
    6: double smile,
    7: double attractive,
    8: list<double> exps,
}

struct ImageReq {
    1: string name,
    2: binary image_data,
}

struct ImageRsp {
    1: string status,
    2: list<FaceFeature> face_features,
}

service FaceAPI{
    ImageRsp predict_image(1: ImageReq req),
}
