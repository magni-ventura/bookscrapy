from scrapy import Spider, Request
from bookscraper.items import BookItem

class BookspiderSpider(Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        books = response.css('article.product_pod')
        for book in books:
            relative_url = book.css('h3 a ::attr(href)').get()
            if 'catalogue/' not in relative_url:
                relative_url = 'catalogue/' + relative_url
            book_url = response.urljoin(relative_url)
            yield Request(book_url, callback=self.parse_book_page)

        next_page = response.css('li.next a ::attr(href)').get()
        if next_page:
            next_page = response.urljoin('catalogue/' + next_page)
            yield Request(next_page, callback=self.parse)

    def parse_book_page(self, response):
        book_item = BookItem()

        book_item['url'] = response.url
        book_item['title'] = response.css('.product_main h1::text').get()
        book_item['product_type'] = response.css("table tr:nth-child(1) td::text").get()
        book_item['price_excl_tax'] = response.css("table tr:nth-child(2) td::text").get()
        book_item['price_incl_tax'] = response.css("table tr:nth-child(3) td::text").get()
        book_item['tax'] = response.css("table tr:nth-child(4) td::text").get()
        book_item['availability'] = response.css("table tr:nth-child(5) td::text").get()
        book_item['num_reviews'] = response.css("table tr:nth-child(6) td::text").get()
        book_item['stars'] = response.css("p.star-rating::attr(class)").get().split()[-1]
        book_item['category'] = response.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get()
        book_item['description'] = response.xpath("//div[@id='product_description']/following-sibling::p/text()").get()
        book_item['price'] = response.css("p.price_color::text").get()

        yield book_item
