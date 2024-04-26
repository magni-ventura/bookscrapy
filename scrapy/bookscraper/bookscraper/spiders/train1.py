"""
import scrapy


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        books = response.css('article.product_pod')

        for book in books:
            yield {
                'name': book.css('h3 a::text').get(),
                'title': book.css('h3 a::attr(title)').get(),
                'price': book.css('.product_price .price_color::text').get(),
                'url': book.css('h3 a').attrib['href'],
            }
        next_page = response.css('li.next a ::attr(href)').get()

        if next_page is not None:
            #if the catalogue/ is in the next page
            if 'catalogue/' in next_page:
                next_page_url = 'https://books.toscrape.com/' + next_page
            else:
                # if not in the next page it should be added and ran
                next_page_url = 'https://books.toscrape.com/catalogue/' + next_page
            yield response.follow(next_page_url, callback= self.parse)

"""




"""

import scrapy
from bookscraper.items import BookItem

class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    #To control the spider
    allowed_domains = ["books.toscrape.com"]
    #Multiple urls can be added to this section
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        #the Item in search of
        books = response.css('article.product_pod')

        #loop through the books
        for book in books:
            relative_url = response.css('h3 a ::attr(href)').get()

            #if the catalogue/ is in the next page
            if 'catalogue/' in relative_url:
                book_url = 'https://books.toscrape.com/' + relative_url
            else:
                # if not in the next page it should be added and ran
                book_url = 'https://books.toscrape.com/catalogue/' + relative_url
            yield response.follow( book_url, callback= self.parse_book_page)

            next_page = response.css('li.next a ::attr(href)').get()

            if next_page is not None:
                if 'catalogue' in next_page:
                    next_page_url = 'https://books.toscrape.com/' + next_page
                else:
                    next_page_url = 'https://books.toscrape.com/catalogue/' + next_page
                yield response.follow(next_page_url, callback= self.parse)

    def parse_book_page(self, response):

        table_rows = response.css("table tr")
        book_item = BookItem()


        BookItem['url'] = response.url,

        BookItem['title'] = response.css('.product_main h1::text').get(),

        BookItem['product_type'] = table_rows[1].css('td ::text').get(),

        BookItem['price_excl_tax'] = table_rows[2].css('td ::text').get(),

        BookItem['price_incl_tax'] = table_rows[3].css('td ::text').get(),

        BookItem['tax'] = table_rows[4].css('td ::text').get(),

        BookItem['availability'] = table_rows[5].css('td ::text').get(),

        BookItem['num_reviews'] = table_rows[6].css('td ::text').get(),

        BookItem['stars'] = response.css("p.star-rating").attrib['class'],

        BookItem['category'] = response.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get(),

        BookItem['description']= response.xpath("//div[@id='product_description']/following-sibling::p/text()").get(),

        BookItem['price'] = response.css('p.price_color ::text()').get(),


        yield BookItem


"""