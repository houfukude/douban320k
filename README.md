douban320k
==========

豆瓣320k播放器 v0.5(Beta)

直接使用豆瓣的公共频道

豆瓣用户登录方式：

    
    当前目录命令行>>douban320k.py 用户名 密码 mode
    
[mode:0|1|2]
    
    0 智能模式(*默认)
    
    1 高清模式
    
    2 流畅模式

[更新]操作方法：

    ← or 键盘 c:    返回频道列表

    → or 键盘 n:    下一曲

    ↑ or 键盘 r:    为当前歌曲红心

    ↓ or 键盘 u:    为当前歌曲取消红心


PS：

    ~~1.目前使用了 msvcrt 应该只支持 windows~~
    
    2.目前播放使用的是本地的 mpg123.exe 来进行播放，详间douban320k第157行

update： 不依赖msvcrt，支持Linux！Linux 下也能使用方向键了