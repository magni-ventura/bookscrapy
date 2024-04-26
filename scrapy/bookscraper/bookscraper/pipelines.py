# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

class BookscraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Strip all white spaces from strings
        for field_name in adapter.field_names():
            if isinstance(adapter[field_name], str):
                adapter[field_name] = adapter[field_name].strip()

        # Category & Product Type --> switch to lowercase
        lowercase_keys = ['category', 'product_type']
        for lowercase_key in lowercase_keys:
            value = adapter.get(lowercase_key)
            adapter[lowercase_key] = value.lower()

        # Price --> convert to float
        for price_key in ['price', 'price_excl_tax', 'price_incl_tax', 'tax']:
            value = adapter.get(price_key)
            if value:  # Check if the value is not empty
                value = value.replace('£', '')
                try:
                    adapter[price_key] = float(value)
                except ValueError:
                    adapter[price_key] = None  # Or some other default value if the value is empty or cannot be converted
            else:
                adapter[price_key] = None

        # Availability --> extract number of books in stock
        availability_string = adapter.get('availability', '')
        split_string_array = availability_string.split('(')
        if len(split_string_array) < 2:
            adapter['availability'] = 0
        else:
            availability_count = split_string_array[1].split(' ')
            adapter['availability'] = int(availability_count[0])

        # Num Reviews --> extract number of reviews
        num_reviews_string = adapter.get('num_reviews', '0')
        adapter['num_reviews'] = self.clean_num_reviews(num_reviews_string)

        # Stars --> extract number of stars
        stars_string = adapter.get('stars', '')
        adapter['stars'] = self.clean_stars(stars_string)

        return item

    def clean_num_reviews(self, num_reviews_string):
        # Extract number of reviews
        try:
            return int(num_reviews_string)
        except ValueError:
            return 0

    def clean_stars(self, stars_string):
        # Extract number of stars
        split_string_array = stars_string.split(' ')
        stars_text_value = split_string_array[1].lower() if len(split_string_array) > 1 else ''
        if stars_text_value == 'zero':
            return 0
        elif stars_text_value == 'one':
            return 1
        elif stars_text_value == 'two':
            return 2
        elif stars_text_value == 'three':
            return 3
        elif stars_text_value == 'four':
            return 4
        elif stars_text_value == 'five':
            return 5
        else:
            return 0

        return item


import mysql.connector

class SaveToMySQLPipeline:

    def __init__(self):
        self.conn = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = '',# add password where needed
            database = 'bookscraper'
        )

        # Create cursor, used to execute commands
        self.cur = self.conn.cursor()

        # Create table in db bookscraper if none exists
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS bookscraper (
                id INT AUTO_INCREMENT PRIMARY KEY,
                url VARCHAR(255) NOT NULL,
                title VARCHAR(255) NOT NULL,
                price FLOAT,
                price_excl_tax FLOAT,
                price_incl_tax FLOAT,
                tax FLOAT,
                availability INT,
                num_reviews INT,
                stars INT,
                category VARCHAR(255) NOT NULL,
                product_type VARCHAR(255) NOT NULL,
                description VARCHAR(255) NOT NULL,
            )
            """
        )

    # Define insert statement
    def process_item(self, item, spider):
        # Insert item into db
        self.cur.execute(
            """
            INSERT INTO bookscraper (
                url,
                title,
                price,
                price_excl_tax,
                price_incl_tax,
                tax,
                availability,
                num_reviews,
                stars,
                category,
                product_type,
                description
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                item['url'],
                item['title'],
                item['price'],
                item['price_excl_tax'],
                item['price_incl_tax'],
                item['tax'],
                item['availability'],
                item['num_reviews'],
                item['stars'],
                item['category'],
                item['product_type'],
                str(item['description'][0])
            )
        )

        # Execute the insert of data into the database
        self.conn.commit()

        return item

    # Close the connection to database
    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()