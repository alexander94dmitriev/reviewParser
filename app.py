from flask import Flask, jsonify
import requests
import logging
from lxml import html
from werkzeug.exceptions import NotFound, InternalServerError


def init_app():
    application = Flask(__name__)
    logging.basicConfig(level=logging.INFO)

    # GET method to parse LendingTree review pages
    # Returns: a list of reviews (title, text, reviewer name and review date) in JSON format
    # Else: throws an error and exists gracefully
    @application.route('/reviews/<path:path>', methods=['GET'])
    def get_reviews_list(path):
        logging.info("***Started parsing reviews list***")
        uri = "https://www.lendingtree.com/reviews/" + path
        response = requests.get(uri)
        if response is None or response.content is None or response.status_code != 200:
            raise NotFound
        content = response.content
        reviews = build_reviews_data(content)
        json_resp = {"response": reviews}
        logging.info("***Finished parsing reviews list***")
        return json_resp

    # convert HTML content into tree structure and parse it with queries
    # to get specific list of items.
    # Parsing process heavily dependends from HTML structure.
    def build_reviews_data(content):
        tree = html.fromstring(content)
        review_titles = tree.xpath('//p[@class="reviewTitle"]/text()')
        review_texts = tree.xpath('//p[@class="reviewText"]/text()')
        consumer_names = tree.xpath('//p[@class="consumerName"]/text()')
        consumer_review_dates = tree.xpath('//p[@class="consumerReviewDate"]/text()')
        num_recs = tree.xpath('//div[@class="numRec"]/text()')
        reviews = []
        for t, x, c, d, n in zip(review_titles, review_texts, consumer_names, consumer_review_dates, num_recs):
            review = {
                'review_titles': t,
                'review_texts': x,
                'consumer_names': c.strip(),
                'consumer_review_dates': d,
                'num_recs': n
            }
            reviews.append(review)
        return reviews

    @application.errorhandler(Exception)
    def error_handler(e):
        code = e.code
        if isinstance(e, NotFound):
            logging.error("Unable to find the page: %s", e.description)
            code = 404
        elif isinstance(e, InternalServerError):
            logging.info("Unable to connect to server.")
            code = 500
        else:
            logging.info("An exception has occurred.")
        resp = jsonify(str(e))
        resp.status_code = code
        return resp

    return application


if __name__ == '__main__':
    app = init_app()
    app.run(port='9001')