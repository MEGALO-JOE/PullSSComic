# -*- coding: utf-8 -*-
import os
import re

import scrapy
from scrapy_splash import SplashRequest

from ..items import SscomicItem


class FzdmSpider(scrapy.Spider):
    """火影爬取"""
    name = 'naruto'
    allowed_domains = ['fzdm.com', 'manhuapan.com']

    global base_url
    base_url = 'https://manhua.fzdm.com/1/{}/index_0.html'
    hua = [base_url.format(i) for i in range(227, 701)]
    juan = [base_url.format(f"Vol_0{i}") for i in [f"0{i}" if len(str(i)) == 1 else i for i in range(1, 26)]]
    start_urls = hua + juan

    # start_urls = ['https://manhua.fzdm.com/1/704/index_0.html']

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url,
                                callback=self.parse,
                                args={'wait': 5},  # 最大超时时间，单位：秒
                                endpoint='render.html')  # 使用splash服务的固定参数

    def parse(self, response):
        """
            # 进去详情
            # todo 使用scrapy-splash，获取js生成后的html画面
            see ：
            :param response:
            :return:
        """

        item = SscomicItem()
        item["href"] = response.url  # 每个章节的url
        item["title"] = item["href"].split("/")[-2]  # extract_first() 提取
        item["info"] = [item["href"]]

        item["save_path"] = os.path.join("naruto", item["title"])
        if not os.path.exists(item["save_path"]):
            os.makedirs(item["save_path"])

        src = response.xpath("//img[@id='mhpic']/@src").extract_first()  # 图片地址
        if src is None:
            print("____________________src is None_____________", self)
            # 由于是借助scrapy-splash，所以不能借助response.status==200 判断页面是否接收成功。
            # 因为是先经过splash服务，然后由sqlash返回结果，response并不是原始的response返回
            if "404" in response.text:
                return
        else:
            print("____________________src____________________", src)
            name = item["href"].split("/")[-1].split(".")[0]
            item["image_file"] = name + "." + src.split(".")[-1]
            download_file = os.listdir(item["save_path"])
            if item["image_file"] not in download_file:
                yield scrapy.Request(url=src, callback=self.parse_image, meta={"item": item})

        url = item["href"]
        i = int(re.findall(r"index_(\d+)", url)[0])
        next_url = url.replace("index_" + str(i), "index_" + str(i + 1))
        item["info"].append(next_url)
        print("_______________next_url_______________", next_url)
        yield SplashRequest(url=next_url, callback=self.parse, meta={"item": item})

    def parse_image(self, response):
        """ 处理图片保存 """
        item = response.meta['item']
        print("____________________save____________________", response.url)

        save_path = item["save_path"]
        image_file = item["image_file"]

        with open(os.path.join(save_path, image_file), "wb") as f:
            f.write(response.body)
