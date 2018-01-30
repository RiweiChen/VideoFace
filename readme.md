VideoFace
------

## 前言
经过漫长的单休之后，本周终于可以双休了 ：）

本来打算趁双休没事干，把最近我胡热播的电视剧《猎场》给过了，看到十多集的时候，越发看不下去了，额，怎么说呢，猎头相关的不专业，更像是《情场》，可是下载了这么多视频全集，rm 掉有点可惜，正好最近对视频分析这块比较感兴趣，因此想试试手，此外，自己一直依赖都是做人脸相关的研究应用，就先从人脸开始。：）

以上都是废话 ：）

## 主要技术和步骤

### 视频抽帧
直接用cv2就可以，我才用的是秒抽一帧。

###人脸检测和特征提取

人脸的检测包括人脸框，人脸识别特征，还有各种人脸属性特征：如性别、年龄、表情、颜值等。

```
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

```
其中 `feature` 主要用来用来做聚类用；

###人脸特征聚类；
人脸聚类主要用来识别出一个视频全集中到底有多少人，聚类的方法比较多，就不细扯了，在github上搜了一下，`chinese_whispers_clustering` 聚类算法对此类问题还算靠谱，而且dlib有对此的实现，直接拿来用（何必要重复造轮子呢：））


## 结果

### 人物聚类
识别聚类结果如下：
![聚类结果](http://img.blog.csdn.net/20171217224750309?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvY2hlbnJpd2VpMg==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

上面的id，代表一个人物，后面会用到。

简单的看了一下，主要的人物还算都聚起来了，很多人不认识（比较只看了十多集），也存在几个问题，可能是聚类算法的阈值选择的不太合适，如0和6都是郑秋冬，被分开了，还有346和763，另外还有21号，这个类聚合的都是误检的人脸；

##应用

###人物颜值排序
都说男女一号一般都是剧里的颜值担当，但在这部剧中，我是不同意的（不单单我不同意，我训练的颜值模型也不同意 ：））

结果如下：
![部分颜值得分截图](http://img.blog.csdn.net/20171217230950042?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvY2hlbnJpd2VpMg==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

正如预期的那样，统计意义上，女性演员的颜值要高于男性演员的，此外，模型认为本剧的颜值担当竟然是363号周放演的钟淮兰，第二是346号贾衣玫，而1号女主角排第五 : )

男演员方面： 最帅的是1454号，应该是后面的剧情才出现的，没见过。第二帅是345号林拜（我也觉得他最帅，符合我直男癌的审美：）），至于0号男主角也是排第五：）

### 人物情绪曲线
通过分析一个人物在剧中的情绪，大致就可以知道该人物是悲剧角色，还是喜剧角色。
我们将情绪归为3类：中性为0，正向表情为1，负向表情为-1；

```
exp2scole = {
    |   "Angry":-1,
    |   "Disgust":-1,
    |   "Fear":-1,
    |   "Happy":1,
    |   "Sad":-1,
    |   "Surprise":1,
    |   "Neutral":0
    |   }

```

拿363号钟淮兰为例：
![这里写图片描述](http://img.blog.csdn.net/20171217233444137?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvY2hlbnJpd2VpMg==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
可以看到钟淮兰的在前期负向情绪为主，猜测出现的剧情在广西监狱那段。符合预期。

### 人物出场时间可视化
一直以来，想做的一件事就是为那些追星族把明明星在电视剧中出现都整合在一起，就可以免去为了看一个明星而需要看整部剧的烦恼了。通过在每一集中，将每个人物的出场点都可视化出来，就可以基本实现这个功能，只需要用ffmpeg 来裁剪就可以。

以16集合为例：
结果如下：
![这里写图片描述](http://img.blog.csdn.net/20171217234740534?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvY2hlbnJpd2VpMg==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
大致可以看到这这一集中，有1号，3号两位郑秋冬女朋友同时出场，估计会比较好看 ：）

### 视频highlight裁剪
现在的很多小视频如西瓜视频上有很多电视剧的highlight，如果可以自动的highlight发现，那应该也是一个很有意思的事情，如在剧中，将1号和3号同时出现的裁剪出来，估计就会很有意思：）

贴不了视频 ：）



## 后记

额，大周末的，我这是在干啥呢。
