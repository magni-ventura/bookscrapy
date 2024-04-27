from scrapy import Spider, Request
from bookscraper.items import BookItem

class BookspiderSpider(Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    custom_settings = {
        'FEEDS': {
            'booksdata.json': {'format': 'json', 'overwrite' : True},
        }
    }

    def parse(self, response):
        # Extracting book URLs from the main page
        books = response.css('article.product_pod')
        for book in books:
            relative_url = book.css('h3 a ::attr(href)').get()
            if 'catalogue/' not in relative_url:
                relative_url = 'catalogue/' + relative_url
            book_url = response.urljoin(relative_url)
            yield Request(book_url, callback=self.parse_book_page)

        # Extracting the URL of the next page (if it exists)
        next_page = response.css('li.next a ::attr(href)').get()
        if next_page:
            next_page = response.urljoin('catalogue/' + next_page)
            yield Request(next_page, callback=self.parse)

    def parse_book_page(self, response):
        # Initializing a BookItem object to store scraped data
        book_item = BookItem()

        # Extracting data from the book page
        book_item['url'] = response.url
        book_item['title'] = response.css('.product_main h1::text').get()
        book_item['upc'] = response.xpath("//th[contains(text(),'UPC')]/following-sibling::td/text()").get()
        book_item['product_type'] = response.xpath("//th[contains(text(),'Product Type')]/following-sibling::td/text()").get()
        book_item['price_excl_tax'] = response.xpath("//th[contains(text(),'Price (excl. tax)')]/following-sibling::td/text()").get()
        book_item['price_incl_tax'] = response.xpath("//th[contains(text(),'Price (incl. tax)')]/following-sibling::td/text()").get()
        book_item['tax'] = response.xpath("//th[contains(text(),'Tax')]/following-sibling::td/text()").get()
        book_item['availability'] = response.xpath("//th[contains(text(),'Availability')]/following-sibling::td/text()").get()
        book_item['num_reviews'] = response.xpath("//th[contains(text(),'Number of reviews')]/following-sibling::td/text()").get()

        # Extracting star rating (e.g., five-star, four-star, etc.)
        book_item['stars'] = response.css("p.star-rating::attr(class)").get().split()[-1]

        # Extracting the category of the book
        book_item['category'] = response.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get()

        # Extracting the book description
        book_item['description'] = response.xpath("//div[@id='product_description']/following-sibling::p/text()").get()

        # Extracting the price (without tax)
        book_item['price'] = response.css("p.price_color::text").get()

        # Returning the BookItem object
        return book_item
