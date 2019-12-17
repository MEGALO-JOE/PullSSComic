# -*- coding: utf-8 -*-
import os

import scrapy

from ..items import SscomicItem


class FzdmSpider(scrapy.Spider):
    name = 'fzdm'
    allowed_domains = ['fzdm.com']
    start_urls = ['https://manhua.fzdm.com/07/']

    base_url = 'https://manhua.fzdm.com/07/{}/'

    # start_url = [base_url.format(i) for i in range(131, 686)]

    def parse(self, response):

        dir_list = response.xpath("//div[@id='content']//li")  # 目录界面

        for i in dir_list:
            s_item = SscomicItem()
            s_item["title"] = i.xpath("./a/text()").extract_first()  # extract_first() 提取
            s_item["href"] = "https://manhua.fzdm.com/07/" + i.xpath("./a/@href").extract_first()  # 每个章节的url
            yield s_item

            yield scrapy.Request(url=s_item['href'], callback=self.parse_chapter,
                                 cb_kwargs={"item": s_item})  # 访问各个章节详情

    def parse_chapter(self, response, item):
        hrefs = []
        tmp = True
        while tmp:
            href_list = response.xpath("//div[@class='navigation']/a/@href").extract()  # 章节中的图片
            list(set(href_list)).sort()
            hrefs.extend(href_list)
            for i in href_list:
                if ".html" not in i:
                    tmp = False
                    break
                yield scrapy.Request(url=item["href"] + i, callback=self.parse_detail, meta={"item": item})
        item["info"] = hrefs

    def parse_detail(self, response):
        # 进去详情
        item = response.meta['item']
        save_path = "data" + item["title"]
        src = response.xpath("//img[@id='mhpic']/@src").extract_first()  # 图片地址
        yield scrapy.Request(url=src, callback=self.parse_image, cb_kwargs={"save_path": save_path})

    def parse_image(self, response, save_path):
        """ 处理图片保存 """

        image_file = response.url[-15:]
        if os.path.exists(save_path):
            os.makedirs(save_path)

        with open(os.path.join(save_path, image_file), "wb") as f:
            f.write(response.body)
