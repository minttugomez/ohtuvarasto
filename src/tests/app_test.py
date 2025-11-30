""" Tests for Flask web application """

import unittest
from app import app, warehouses, warehouse_counter, safe_float


class TestApp(unittest.TestCase):
    """ Test cases for the Flask application """

    def setUp(self):
        """ Set up test client and clear data """
        app.config['TESTING'] = True
        self.client = app.test_client()
        warehouses.clear()
        warehouse_counter.reset()

    def test_index_empty(self):
        """ Test index page with no warehouses """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Warehouse Management', response.data)
        self.assertIn(b'No warehouses yet', response.data)

    def test_create_warehouse(self):
        """ Test creating a new warehouse """
        response = self.client.post('/warehouse/create', data={
            'tilavuus': '100',
            'alku_saldo': '25'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Warehouse #1', response.data)
        self.assertEqual(len(warehouses), 1)
        self.assertAlmostEqual(warehouses[1].tilavuus, 100.0)
        self.assertAlmostEqual(warehouses[1].saldo, 25.0)

    def test_add_to_warehouse(self):
        """ Test adding items to warehouse """
        # Create warehouse first
        self.client.post('/warehouse/create', data={
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        # Add items
        response = self.client.post('/warehouse/1/add', data={
            'maara': '50'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(warehouses[1].saldo, 50.0)

    def test_remove_from_warehouse(self):
        """ Test removing items from warehouse """
        # Create warehouse first
        self.client.post('/warehouse/create', data={
            'tilavuus': '100',
            'alku_saldo': '75'
        })
        # Remove items
        response = self.client.post('/warehouse/1/remove', data={
            'maara': '25'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(warehouses[1].saldo, 50.0)

    def test_edit_warehouse(self):
        """ Test editing warehouse capacity """
        # Create warehouse first
        self.client.post('/warehouse/create', data={
            'tilavuus': '100',
            'alku_saldo': '50'
        })
        # Edit capacity
        response = self.client.post('/warehouse/1/edit', data={
            'tilavuus': '200'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(warehouses[1].tilavuus, 200.0)
        self.assertAlmostEqual(warehouses[1].saldo, 50.0)

    def test_delete_warehouse(self):
        """ Test deleting a warehouse """
        # Create warehouse first
        self.client.post('/warehouse/create', data={
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        self.assertEqual(len(warehouses), 1)
        # Delete warehouse
        response = self.client.post(
            '/warehouse/1/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(warehouses), 0)

    def test_get_warehouse_api(self):
        """ Test API endpoint for getting warehouse details """
        # Create warehouse first
        self.client.post('/warehouse/create', data={
            'tilavuus': '100',
            'alku_saldo': '30'
        })
        # Get details via API
        response = self.client.get('/api/warehouse/1')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['id'], 1)
        self.assertAlmostEqual(data['tilavuus'], 100.0)
        self.assertAlmostEqual(data['saldo'], 30.0)
        self.assertAlmostEqual(data['tilaa'], 70.0)

    def test_get_warehouse_api_not_found(self):
        """ Test API endpoint for non-existent warehouse """
        response = self.client.get('/api/warehouse/999')
        self.assertEqual(response.status_code, 404)

    def test_operations_on_nonexistent_warehouse(self):
        """ Test operations on warehouses that don't exist """
        # Try to add to non-existent warehouse
        response = self.client.post('/warehouse/999/add', data={
            'maara': '50'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Try to remove from non-existent warehouse
        response = self.client.post('/warehouse/999/remove', data={
            'maara': '50'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Try to edit non-existent warehouse
        response = self.client.post('/warehouse/999/edit', data={
            'tilavuus': '200'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Try to delete non-existent warehouse
        response = self.client.post(
            '/warehouse/999/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_safe_float_valid_input(self):
        """ Test safe_float with valid input """
        self.assertAlmostEqual(safe_float('100'), 100.0)
        self.assertAlmostEqual(safe_float('3.14'), 3.14)
        self.assertAlmostEqual(safe_float(50), 50.0)

    def test_safe_float_invalid_input(self):
        """ Test safe_float with invalid input returns default """
        self.assertAlmostEqual(safe_float('invalid'), 0.0)
        self.assertAlmostEqual(safe_float('invalid', 10.0), 10.0)
        self.assertAlmostEqual(safe_float(None), 0.0)
        self.assertAlmostEqual(safe_float(''), 0.0)

    def test_create_warehouse_with_invalid_input(self):
        """ Test creating warehouse with invalid input uses defaults """
        response = self.client.post('/warehouse/create', data={
            'tilavuus': 'invalid',
            'alku_saldo': 'also_invalid'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(warehouses), 1)
        # Should use defaults
        self.assertAlmostEqual(warehouses[1].tilavuus, 10.0)
        self.assertAlmostEqual(warehouses[1].saldo, 0.0)
