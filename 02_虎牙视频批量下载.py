'''
爬取虎牙视频
爬取内容    视频标题，视频
    分析播放页内容，得到单个视频的下载地址，通过对视频名文件名的分析，得到该视频响应的json数据（包含该视频的重要信息）
    视频下载的url地址的规律，每个视频的id不同，下载的内容不同

2.获取数据，获取单个视频数据
3.解析数据，获取视频的标题和下载url
4.保存数据到本地

批量下载思路
    获取到每个视频的id，循环遍历id下载即可

待实现功能，通过关键词下载视频

！关键词下载实现
    问题：下载方式是否一致，解析视频id方式是否一致
    解决：分析界面，下载方式一致，获取视频的id方式不一致
    代码：下载复用，更改获取id方式即可
    1.通过输入的关键词进行搜索到对应界面
    2.修改搜索页面对应的解析方式，获取搜索出来视频的id
    3.通过复用下载分区视频的功能,实现视频下载
实现多页下载
'''
import json
import urllib.parse
import urllib.request
import os
import jsonpath
import requests
from bs4 import BeautifulSoup


# 伪装请求头
def get_response(html_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.46"
    }
    response = requests.get(url=html_url,headers=headers)
    return response


# 获取请求内容
def get_content(response):
    content = response.text
    return content

# 解析JSON数据，获取下载视频的url和标题
def get_info(content):
    # 通过jsonpath解析JSON数据
    # 将json数据保存到本地
    with open('02_video.json', 'w', encoding='utf8') as fp:
        fp.write(content)
    obj =json.load(open('02_video.json', 'r', encoding='utf8'))
    # 获取视频标题
    title =jsonpath.jsonpath(obj,'$..title')[0]
    # 处理不符合的文件名
    sets = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in title:
        if char in sets:
            title = title.replace(char, '')
    # 获取视频url
    video_url = jsonpath.jsonpath(obj,'$..1.url')[0]
    video_info = [title,video_url]
    return video_info

# 保存视频到本地
def save(title,video_url,path):
    # 获取到视频的二进制数据
    video_content = get_response(html_url=video_url).content
    # 保存到本地
    with open(path+'/'+title+".mp4",mode='wb') as fp:
        fp.write(video_content)
    print(title,'视频下载完毕')

# 封装下载函数
def get_video(video_id,path):
    html_url = f'https://liveapi.huya.com/moment/getMomentContent?callback&videoId={video_id}&_=1647948024600'
    # 1.发送请求
    response = get_response(html_url)
    # 2.获取数据
    content = get_content(response)
    # 3.解析数据
    video_info = get_info(content)
    # 4.保存数据到本地
    save(video_info[0],video_info[1],path)

# 多个下载获取id
def get_id(url):
    # 发送请求
    response = get_response(html_url=url)
    # 服务器响应数据生成对象
    soup = BeautifulSoup(response.text,'lxml')
    # 解析数据,到到整页的li下a标签内容
    obj = soup.select('.vhy-video-search-list>li>a')
    # print(obj)
    # 通过循环对li列表的到所有id
    video_id_list = []
    for i in range(len(obj)):
        # video_id_list.append(obj[i].attrs.get('data-vid'))    下载分区视频用
        id = obj[i].attrs.get('href').split('/')[4].split('.')[0]   # 搜索视频下载用
        video_id_list.append(id)
    return video_id_list

# 通过关键字下载视频
# https://v.huya.com/
# search?w=%E8%8B%B1%E9%9B%84%E8%81%94%E7%9B%9F&type=video
# https://v.huya.com/
# search?w=lol&type=video
# 分析发现是通过修改下载的视频界面的url可以实现查找，属于get请求
def send_ket(key):
    # 将汉字转换成uncode编码格式
    key = urllib.parse.quote(key)
    base_url = f'https://v.huya.com/search/?w={key}&type=video'
    return base_url

if __name__ == '__main__':
    # 通过输出关键词下载视频
    key = input('请输入要虎牙视频的关键字：')
    key_url = send_ket(key)
    # 创建下载目录
    path = f'video{key}'
    try:
        os.mkdir(path)
    except FileExistsError:
        print('目录已存在，将会继续在下载到该目录')
    # 批量获取视频id
    id_list = get_id(url=key_url)
    for i in range(len(id_list)):
        get_video(id_list[i],path)




