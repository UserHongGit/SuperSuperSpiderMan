import os

import scrapy
from Hongdemo1.items import Hongdemo1Item
import json
import urllib.request
from math import ceil


class BanciyuanSpider(scrapy.Spider):
    name = 'banciyuan'
    allowed_domains = ['bcy.net']
    start_urls = ['https://bcy.net/huodong/1179?order=hot&p=1#thumbs']



    def parse(self, response):
        script_list = response.xpath('//script/text()')
        use_script = ''
        for script in script_list:
            script = script.extract()
            if (script.find('window.__ssr_data = JSON') != -1):
                use_script = script.replace("\\\"", '"')
        if (use_script != ''):
            start = use_script.index('JSON.parse("') + 12
            end = use_script.index('");')
            json_str = use_script[start:end].replace("\\\"", '"')
            json_obj = json.loads(json_str, encoding='utf-8')

            total = json_obj.get('huodong').get('total')
            page_size = len(json_obj.get('huodong').get('items'))
            pages = ceil(total / page_size)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36'
        }
        print('-------------------需要解析的页面一共有:'+str(pages))
        for enter_time in range(pages):
            '''
            https://bcy.net/huodong/1179?order=hot&p=1#thumbs
            https://bcy.net/huodong/1179?order=hot&p=2#thumbs
            https://bcy.net/huodong/1179?order=hot&p=3#thumbs
            '''
            show_page_href = 'https://bcy.net/huodong/1179?order=hot&p='+ str(enter_time) + '#thumbs'

            yield scrapy.Request(headers=headers,url=show_page_href, callback=self.parse_show_page)


    #解析展示页面  文章首页列表
    def parse_show_page(self, response):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36'
        }

        a_list = response.xpath('//div/li/a');
        print('----------------, 找到'+str(len(a_list)) +'个图片链接')
        for a in a_list:
            href = a.xpath('./@href').extract_first();
            title = a.xpath('./@title').extract_first();

            href = 'https://bcy.net' + href

            yield scrapy.Request(headers=headers,url=href, callback=self.parse_detail_page, meta={'title': title})

    #解析详情页, 真正存储图片的页面
    def parse_detail_page(self,response):
        analy_response(response)

def analy_response(response):
    script_list = response.xpath('//script/text()')
    title = response.meta['title']
    use_script = ''
    for script in script_list:
        script = script.extract()
        if (script.find('window.__ssr_data = JSON') != -1):
            use_script = script.replace("\\\"", '"')

    if (use_script != ''):
        start = use_script.index('JSON.parse("') + 12
        end = use_script.index('");')
        json_str = use_script[start:end].replace("\\\"", '"')
        json_obj = json.loads(json_str, encoding='utf-8')

        pic_list = json_obj.get('detail').get('post_data').get('multi')

        folder = './pic/'

        i = 1;

        for pic in pic_list:
            origin_pic_url = pic['origin'].replace('\\u002F', '/')
            suffix = pic['format']
            if(suffix == None or suffix == '' or suffix.isspace()):
                suffix = 'jpg'
            folder_path = folder + title
            mkdir(folder_path)

            filename = folder_path + '/' + str(i) + '.' + suffix
            i += 1

#           TODO 多线程下载图片, 或者使用其他类库
            is_exists = os.path.exists(filename)
            if (not is_exists):
                urllib.request.urlretrieve(url=origin_pic_url, filename=filename)


def mkdir(path):
    '''
    创建指定的文件夹
    :param path: 文件夹路径，字符串格式
    :return: True(新建成功) or False(文件夹已存在，新建失败)
    '''
    # 引入模块
    import os

    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)

    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
         # 创建目录操作函数
        os.makedirs(path)
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        return False