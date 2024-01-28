from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from .models import Order


class OrderDetailViewTestCase(TestCase):
	@classmethod
	def setUpClass(cls):
		cls.user = User.objects.create_user(username="testuser", password="12345")
		permission = Permission.objects.get(codename="view_order")
		cls.user.user_permissions.add(permission)

	@classmethod
	def tearDownClass(cls):
		cls.user.delete()

	def setUp(self):
		self.client.force_login(self.user)
		self.order = Order.objects.create(
				user=self.user,
				delivery_address = "Test Address",
				promocode = "TESTCODE",
		)

	def tearDown(self) -> None:
		self.order.delete()

	def test_order_details(self):
		response = self.client.get(reverse("shopapp:order_details",
		                                   kwargs={"pk": self.order.pk}))
		self.assertContains(response, "TESTCODE")
		self.assertEqual(response.context["order"].pk, self.order.pk)


class OrdersExportTestCase(TestCase):
	fixtures = [
			"orders-fixtures.json",
	]

	@classmethod
	def setUpClass(cls):
		cls.user = User.objects.create_user(username="testuser2", password="12345")
		cls.user.is_staff = True
		cls.user.save()

	@classmethod
	def tearDownClass(cls):
		cls.user.delete()

	def setUp(self):
		self.client.force_login(self.user)

	def test_get_orders_view(self):
		response = self.client.get(
				reverse("shopapp:orders_export")
		)
		self.assertEqual(response.status_code, 200)
		orders = Order.objects.order_by("pk").all()
		expected_data = [
				{
						"pk":order.pk,
						"address":order.delivery_address,
						"promocode":order.promocode,
						"id_user":order.user,
						"id_products":order.products,
				}
				for order in orders
		]
		orders_data = response.json()
		self.assertEqual(orders_data["orders"], expected_data)
