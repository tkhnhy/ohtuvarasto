"""Tests for the Flask application."""
import unittest
import sys
import os

# Add src to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app, warehouses, _id_counter


class TestApp(unittest.TestCase):
    """Test cases for Flask app routes."""

    def setUp(self):
        """Set up test client and reset warehouses."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        warehouses.clear()
        _id_counter[0] = 1

    def test_index_empty(self):
        """Test index page with no warehouses."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Varastot', response.data)
        self.assertIn(b'Ei varastoja', response.data)

    def test_create_warehouse_get(self):
        """Test GET request to create warehouse page."""
        response = self.client.get('/warehouse/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Luo uusi varasto', response.data)

    def test_create_warehouse_post(self):
        """Test creating a new warehouse."""
        response = self.client.post('/warehouse/create', data={
            'name': 'Test Warehouse',
            'tilavuus': '100',
            'alku_saldo': '50'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Warehouse', response.data)
        self.assertEqual(len(warehouses), 1)

    def test_create_warehouse_empty_name(self):
        """Test creating warehouse with empty name shows error."""
        response = self.client.post('/warehouse/create', data={
            'name': '',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Name is required', response.data)

    def test_create_warehouse_invalid_capacity(self):
        """Test creating warehouse with invalid capacity shows error."""
        response = self.client.post('/warehouse/create', data={
            'name': 'Test',
            'tilavuus': 'invalid',
            'alku_saldo': '0'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid capacity or initial balance', response.data)

    def test_view_warehouse(self):
        """Test viewing a warehouse."""
        # First create a warehouse
        self.client.post('/warehouse/create', data={
            'name': 'View Test',
            'tilavuus': '100',
            'alku_saldo': '25'
        })
        response = self.client.get('/warehouse/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'View Test', response.data)
        self.assertIn(b'25.0', response.data)

    def test_view_nonexistent_warehouse(self):
        """Test viewing a non-existent warehouse redirects."""
        response = self.client.get('/warehouse/999', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Varastot', response.data)

    def test_edit_warehouse_get(self):
        """Test GET request to edit warehouse page."""
        self.client.post('/warehouse/create', data={
            'name': 'Edit Test',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        response = self.client.get('/warehouse/1/edit')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Muokkaa varastoa', response.data)
        self.assertIn(b'Edit Test', response.data)

    def test_edit_warehouse_post(self):
        """Test editing a warehouse."""
        self.client.post('/warehouse/create', data={
            'name': 'Original Name',
            'tilavuus': '100',
            'alku_saldo': '50'
        })
        response = self.client.post('/warehouse/1/edit', data={
            'name': 'New Name',
            'tilavuus': '200'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'New Name', response.data)
        # Saldo should be preserved
        self.assertEqual(warehouses[1]['varasto'].saldo, 50)
        self.assertEqual(warehouses[1]['varasto'].tilavuus, 200)

    def test_edit_warehouse_empty_name(self):
        """Test editing warehouse with empty name shows error."""
        self.client.post('/warehouse/create', data={
            'name': 'Test',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        response = self.client.post('/warehouse/1/edit', data={
            'name': '',
            'tilavuus': '100'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Name is required', response.data)

    def test_delete_warehouse(self):
        """Test deleting a warehouse."""
        self.client.post('/warehouse/create', data={
            'name': 'Delete Test',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        self.assertEqual(len(warehouses), 1)
        response = self.client.post('/warehouse/1/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(warehouses), 0)

    def test_add_content(self):
        """Test adding content to a warehouse."""
        self.client.post('/warehouse/create', data={
            'name': 'Add Test',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        response = self.client.post('/warehouse/1/add', data={
            'amount': '30'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(warehouses[1]['varasto'].saldo, 30)

    def test_add_content_invalid_amount(self):
        """Test adding invalid amount redirects without error."""
        self.client.post('/warehouse/create', data={
            'name': 'Add Test',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        response = self.client.post('/warehouse/1/add', data={
            'amount': 'invalid'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(warehouses[1]['varasto'].saldo, 0)

    def test_remove_content(self):
        """Test removing content from a warehouse."""
        self.client.post('/warehouse/create', data={
            'name': 'Remove Test',
            'tilavuus': '100',
            'alku_saldo': '50'
        })
        response = self.client.post('/warehouse/1/remove', data={
            'amount': '20'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(warehouses[1]['varasto'].saldo, 30)

    def test_remove_content_more_than_available(self):
        """Test removing more content than available takes all."""
        self.client.post('/warehouse/create', data={
            'name': 'Remove Test',
            'tilavuus': '100',
            'alku_saldo': '30'
        })
        self.client.post('/warehouse/1/remove', data={
            'amount': '50'
        })
        self.assertEqual(warehouses[1]['varasto'].saldo, 0)

    def test_add_content_nonexistent_warehouse(self):
        """Test adding content to non-existent warehouse redirects."""
        response = self.client.post('/warehouse/999/add', data={
            'amount': '10'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Varastot', response.data)

    def test_remove_content_nonexistent_warehouse(self):
        """Test removing content from non-existent warehouse redirects."""
        response = self.client.post('/warehouse/999/remove', data={
            'amount': '10'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Varastot', response.data)

    def test_multiple_warehouses(self):
        """Test creating and displaying multiple warehouses."""
        self.client.post('/warehouse/create', data={
            'name': 'Warehouse 1',
            'tilavuus': '100',
            'alku_saldo': '10'
        })
        self.client.post('/warehouse/create', data={
            'name': 'Warehouse 2',
            'tilavuus': '200',
            'alku_saldo': '50'
        })
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Warehouse 1', response.data)
        self.assertIn(b'Warehouse 2', response.data)
        self.assertEqual(len(warehouses), 2)


if __name__ == '__main__':
    unittest.main()
