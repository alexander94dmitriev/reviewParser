from unittest import TestCase
from app import init_app

class Test(TestCase):

    host = 'http://127.0.0.1:9001/'

    def create_app(self):
        app = init_app()
        app.config['TESTING'] = True
        return app

    def test_app_instance_exist(self):
        app = self.create_app()
        self.assertIsNotNone(app)

    def test_app_not_found_wrong_page(self):
        response = init_app().test_client().get(self.host + 'reviews/')
        assert response.status_code == 404

    def test_app_not_found_no_review_data(self):
        response = init_app().test_client().get(self.host + '/reviews/business/seek-capital/65175902ss')
        assert response.status_code == 404

    def test_app_get_review_data(self):
        response = init_app().test_client().get(self.host + '/reviews/business/seek-capital/65175902')
        assert response.status_code == 200
        assert response.data is not None
