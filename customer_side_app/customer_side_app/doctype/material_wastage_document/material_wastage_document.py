# Copyright (c) 2024, basit and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class MaterialWastageDocument(Document):
	def on_submit(self):
		self.create_material_request()

	def create_material_request(self):
		doc = frappe.new_doc('Stock Entry')
		doc.posting_date = self.posting_date
		doc.posting_time = self.posting_time
		doc.stock_entry_type = "Material Issue"
		for i in self.items:
			doc.append("items",{
				"item_code":i.get("item_code"),
				"s_warehouse":i.get("warehouse"),
				"qty":i.get("qty"),
				"uom":i.get("uom"),

			})
		doc.submit()
		# frappe.db.set_value('Material Wastage Document', self.name, 'material_issue_receipt', doc.name)

