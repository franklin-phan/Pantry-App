from unittest import TestCase, main as unittest_main, mock
from app import app
from bson.objectid import ObjectId


sample_item_id = ObjectId('5d55cffc4a3d4031f42827a3')
sample_item = {
    'name': 'Spaghetti',
    'image': 'https://thecozyapron.com/wp-content/uploads/2019/05/spaghetti-bolognese_thecozyapron_1.jpg',
    'price': '10',
    "description and quantity":'Good spaghetti and 2 bowls'
}
sample_form_data = {
    'name': sample_item['name'],
    'image': sample_item['image'],
    'price': sample_item['price'],
    'description and quantity': sample_item['description']
}


class listingsTests(TestCase):
    """Flask tests."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

    def test_index(self):
        """Test the pantry homepage."""
        result = self.client.get('/')
        self.assertEqual(result.status, '200 OK')
        self.assertIn(b'listing', result.data)

    def test_new(self):
        """Test the new listing creation page."""
        result = self.client.get('/pantry/new')
        self.assertEqual(result.status, '200 OK')
        self.assertIn(b'New item', result.data)

    @mock.patch('pymongo.collection.Collection.find_one')
    def test_show_item(self, mock_find):
        """Test showing a single listing."""
        mock_find.return_value = sample_item

        result = self.client.get(f'/pantry/{sample_item_id}')
        self.assertEqual(result.status, '200 OK')
        self.assertIn(b'Item', result.data)

    @mock.patch('pymongo.collection.Collection.find_one')
    def test_edit_item(self, mock_find):
        """Test editing a single item."""
        mock_find.return_value = sample_item

        result = self.client.get(f'/pantry/{sample_item_id}/edit')
        self.assertEqual(result.status, '200 OK')
        self.assertIn(b'Spaghetti', result.data)

    @mock.patch('pymongo.collection.Collection.insert_one')
    def test_submit_item(self, mock_insert):
        """Test submitting a new item."""
        result = self.client.post('/pantry/new', data=sample_form_data)

        # After submitting, should redirect to that item's page
        self.assertEqual(result.status, '302 FOUND')
        mock_insert.assert_called_with(sample_item)

    @mock.patch('pymongo.collection.Collection.update_one')
    def test_update_item(self, mock_update):
        result = self.client.post(f'/pantry/{sample_item_id}', data=sample_form_data)

        self.assertEqual(result.status, '302 FOUND')
        mock_update.assert_called_with({'_id': sample_item_id}, {'$set': sample_item})
    @mock.patch('pymongo.collection.Collection.delete_one')
    def test_delete_item(self, mock_delete):
        form_data = {'_method': 'DELETE'}
        result = self.client.post(f'/pantry/{sample_item_id}/delete', data=form_data)
        self.assertEqual(result.status, '302 FOUND')
        mock_delete.assert_called_with({'_id': sample_item_id})
if __name__ == '__main__':
    unittest_main()