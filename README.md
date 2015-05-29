douban320k
==========

豆瓣320k播放器 v0.5(Beta)

直接使用豆瓣的公共频道

豆瓣用户登录方式：

当前目录命令行

>douban320k.py 豆瓣用户名 密码 mode

或者直接下载win版的zip解压后双击运行

>douban320k.exe

如果win版需要登陆可以在退出情况下双击Login.bat

输入 *豆瓣用户名 密码* mode

![截图1](https://raw.githubusercontent.com/houfukude/douban320k/master/screenshot/douban320K_1.PNG)
![截图2](https://raw.githubusercontent.com/houfukude/douban320k/master/screenshot/douban320K_2.PNG)

[mode:0|1|2]
    
    0 智能模式(*默认)
    
    1 高清模式
    
    2 流畅模式

[更新]操作方法：

    ← or 键盘 c:    返回频道列表

    → or 键盘 n:    下一曲

    ↑ or 键盘 r:    为当前歌曲红心

    ↓ or 键盘 u:    为当前歌曲取消红心


###PS：

<del>1.目前使用了 msvcrt 应该只支持 windows</del>
    
2.目前播放使用的是本地的 mpg123 来进行播放，详情[#L195](https://github.com/houfukude/douban320k/blob/master/douban320k.py#L195)

###Bug

1.已知mpg在linux对wma支持不友好，建议linux的同学不使用流畅模式

2.部分歌曲标题带有奇怪的字符（就是你脸滚键盘的！！）导致win下容易编码错误

####update： 

不依赖msvcrt，支持Linux！Linux 下也能使用方向键了

###release

下载地址:[百度网盘](http://pan.baidu.com/s/1gdnLuSF)