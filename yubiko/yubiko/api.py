# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import date_diff, add_months, today, getdate, add_days, flt, get_last_day

@frappe.whitelist(allow_guest=True)
def send_data(date, order_id, carrier, shipping_method, shipping_date, item_qty, item_sku, first_name, last_name, street_name, city, postcode, state, country, email, telephone):
	new_customer = frappe.new_doc("Customer")
	new_customer.customer_name = str(first_name)+str(last_name)
	new_customer.customer_group = "All Customer Groups"
	new_customer.territory = "All Territories"
	new_customer.customer_type = "Individual"
	new_customer.save(ignore_permissions=True)
	new_contact = frappe.new_doc("Contact")
	new_contact.first_name = first_name
	new_contact.last_name = last_name
	new_contact.append('email_ids', {
		"email_id": email,
		"is_primary": 1
	})
	new_contact.append('phone_nos', {
		"phone": telephone,
		"is_primary_phone": 1
	})
	new_contact.append('links', {
		"link_doctype": "Customer",
		"link_name": new_customer.name
	})
	new_contact.insert(ignore_permissions=True)
	address = frappe.new_doc("Address")
	address.address_type = "Shipping"
	address.address_line1 = street_name
	address.city = city
	address.country = country
	address.state = state
	address.pincode = postcode
	address.phone = email
	address.email_id = telephone
	address.append("links", {
		"link_doctype": "Customer",
		"link_name": new_customer.name
	})
	address.flags.ignore_mandatory = True
	address.save(ignore_permissions=True)
	new_customer.customer_primary_contact = new_contact.name
	new_customer.customer_primary_address = address.name
	new_customer.save(ignore_permissions=True)
	new_sales_order = frappe.new_doc("Sales Order")
	new_sales_order.customer = new_customer.name
	if frappe.db.exists("Item", item_sku):
		item = frappe.get_doc("Item", item_sku)
		new_sales_order.append("items", {
			"item_code": item.name,
			"delivery_date": today(),
			"item_name": item.item_name,
			"description": item.description,
			"uom": item.stock_uom,
			"qty": item_qty
		})
	else:
		return {"errormsg": "Invalid Item SKU", "errorcode": "404"}
	new_sales_order.flags.ignore_mandatory = True
	new_sales_order.insert(ignore_permissions=True)
	frappe.db.commit()
	return {"res_status": "success", "transcactionId": new_sales_order.name, "so_data": new_sales_order}

@frappe.whitelist(allow_guest=True)
def request_status(so_number):
	if frappe.db.exists("Sales Order", so_number):
		so = frappe.get_doc("Sales Order", so_number)
		return {"status": "success", "order_id": so.name, "order_status": so.status, "items": so.items, "tracking_no": "123dseef", "status": so.delivery_status}
	else:
		return {"errorcode": "404", "errormsg": "Not Found"}
