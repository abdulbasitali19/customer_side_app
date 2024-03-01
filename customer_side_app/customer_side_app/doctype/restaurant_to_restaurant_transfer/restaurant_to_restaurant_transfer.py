# Copyright (c) 2024, basit and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now


class RestaurantToRestaurantTransfer(Document):
	
	def on_submit(self):
		self.create_material_transfer_entry()


	def create_material_transfer_entry(self):
		doc = frappe.new_doc('Stock Entry')
		doc.stock_entry_type = "Material Transfer"
		doc.posting_date = now()
		for i in self.items:
			doc.append("items",{
				"item_code":i.get("item_code"),
				"s_warehouse":i.get("s_warehouse"),
				"t_warehouse":i.get("t_warehouse"),
				"qty":i.get("qty"),
				"uom":i.get("uom"),

			})
		doc.submit(ignore_permission = True)