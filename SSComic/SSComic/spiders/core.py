# -*- coding: utf-8 -*-
import os
import scrapy

from scrapy_splash import SplashRequest


class FzdmSpider(scrapy.Spider):
    name = 'fzdm_demo'
    allowed_domains = ['fzdm.com', 'manhuapan.com']
    start_urls = ['https://manhua.fzdm.com/07/']

    base_url = 'https://manhua.fzdm.com/07/{}/'

    # start_url = [base_url.format(i) for i in range(131, 686)]

    def parse(self, response):

        # dir_list = response.xpath("//div[@id='content']//li")  # 目录界面

        # for i in dir_list:
        #     s_item = SscomicItem()
        #     s_item["title"] = i.xpath("./a/text()").extract_first()  # extract_first() 提取
        #     s_item["href"] = "https://manhua.fzdm.com/07/" + i.xpath("./a/@href").extract_first()  # 每个章节的url
        #     yield s_item
        #
        #     yield scrapy.Request(url=s_item['href'], callback=self.parse_chapter,
        #                          cb_kwargs={"item": s_item})  # 访问各个章节详情

        back = yield scrapy.Request(url="https://manhua.fzdm.com/07/684/", callback=self.parse_chapter)
        print("_____________________back___________________________", back)

    def parse_chapter(self, response):
        yield "hahahh"
        hrefs = []
        # tmp = True
        # while tmp:

        href_list = response.xpath("//div[@class='navigation']/a/@href").extract()  # 章节中的图片
        href_list = list(set(href_list))
        href_list.sort()
        print("_____________________________href______________________", href_list)
        hrefs.extend(href_list)
        for i in href_list:
            if ".html" not in i:
                break

            url = "https://manhua.fzdm.com/07/684/" + i
            print("__________________url______________________", url)
            yield SplashRequest(url=url, callback=self.parse_detail)

    def parse_detail(self, response):
        """
        # 进去详情
        # todo 使用scrapy-splash，获取js生成后的html画面
        see ： https://blog.csdn.net/zhengxiangwen/article/details/55227368
        :param response:
        :return:
        """
        src = response.xpath("//img[@id='mhpic']/@src").extract_first()  # 图片地址
        print("_________________________src___________________", src)
        yield scrapy.Request(url=src, callback=self.parse_image)

    def parse_image(self, response):
        """ 处理图片保存 """

        # todo 怎么进不来？？？

        print("____________________save___________________")


        image_file = response.url[-15:]

        with open(image_file, "wb") as f:
            f.write(response.body)
