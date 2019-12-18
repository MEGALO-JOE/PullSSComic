# -*- coding: utf-8 -*-
import os

import scrapy

from ..items import SscomicItem
from scrapy_splash import SplashRequest
import re


class FzdmSpider(scrapy.Spider):
    name = 'fzdm'
    allowed_domains = ['fzdm.com', 'manhuapan.com']
    start_urls = ['https://manhua.fzdm.com/07/']

    base_url = 'https://manhua.fzdm.com/07/{}/'

    start_url = [base_url.format(i) for i in range(131, 686)]

    def parse(self, response):

        dir_list = response.xpath("//div[@id='content']//li")  # 目录界面

        for i in dir_list:
            item = SscomicItem()
            item["title"] = i.xpath("./a/text()").extract_first()  # extract_first() 提取
            item["href"] = "https://manhua.fzdm.com/07/" + i.xpath("./a/@href").extract_first()  # 每个章节的url
            item["info"] = []
            item["err"] = []
            item["url"] = item["href"] + "index_0.html"
            yield item

            yield SplashRequest(url=item['href'], callback=self.parse_detail, meta={"item": item})  # 访问各个章节详情

        # item = SscomicItem()
        # item["title"] = "测试测试"
        # item["href"] = "https://manhua.fzdm.com/07/684/"
        # item["info"] = []
        # item["err"] = []
        # item["url"] = item["href"] + "index_0.html"
        # yield SplashRequest(url=item["href"], callback=self.parse_detail, meta={"item": item})

    def parse_detail(self, response):
        """
                # 进去详情
                # todo 使用scrapy-splash，获取js生成后的html画面
                see ： https://blog.csdn.net/zhengxiangwen/article/details/55227368
                :param response:
                :return:
        """
        item = response.meta['item']
        if response.status == 200:

            item["save_path"] = os.path.join("data", item["title"])
            if not os.path.exists(item["save_path"]):
                os.makedirs(item["save_path"])

            src = response.xpath("//img[@id='mhpic']/@src").extract_first()  # 图片地址
            if src is None:
                print("_______________________src is None_____________________")
            print("_________________________src___________________", src)
            yield scrapy.Request(url=src, callback=self.parse_image, meta={"item": item})

            url = item["url"]
            i = int(re.findall(r"index_(\d+)", url)[0])
            next_url = url.replace("index_" + str(i), "index_" + str(i + 1))
            item["url"] = next_url
            print("_______________next_url_______________", next_url)
            yield SplashRequest(url=next_url, callback=self.parse_detail, meta={"item": item})
        # else:
        #     yield item["err"].append(item["url"])

    def parse_image(self, response):
        """ 处理图片保存 """
        item = response.meta['item']
        print("____________________save___________________")

        save_path = os.path.join("data", item["title"])
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # name = re.findall("\w+_\d", item["url"])[-1]
        name = item["url"].split("/")[-1].split(".")[0]
        image_file = name + "." + response.url.split(".")[-1]

        with open(os.path.join(save_path, image_file), "wb") as f:
            f.write(response.body)
