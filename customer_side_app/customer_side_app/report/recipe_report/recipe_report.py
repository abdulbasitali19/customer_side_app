# Copyright (c) 2024, basit and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data()
	return columns, data


def get_bom_data():
	bom_master_data = frappe.db.sql("""
		SELECT
			bom.item,
			bom_item.item_code as item_code,
			bom_item.qty as qty,
			bom_item.uom as uom,
			bom_item.rate as rate,
			bom_item.amount as amount
		FROM
			`tabBOM` as bom INNER JOIN `tabBOM Item` as bom_item on bom_item.parent = bom.name

			""",as_dict=1
			)
	return bom_master_data

def get_data():
    bom_data = get_bom_data()
    if bom_data:
        data = []
        added_items = set()

        for d in bom_data:
            if d.get("item") not in added_items:
                added_items.add(d.get("item"))

                data.append({"item": d.get("item")})

            data_dict = {}
            data_dict["item_code"] = d.get("item_code")
            data_dict["qty"] = d.get("qty")
            data_dict["uom"] = d.get("uom")
            data_dict["rate"] = d.get("rate")
            data_dict["amount"] = d.get("amount")
            data.append(data_dict)

        return data




def get_columns():
	columns = [
		{
            "label": _("Item"),
            "fieldname": "item",
            "fieldtype": "Link",
            "options": "Item",
            "width": 250,
        },
		{
            "label": _("Item"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 250,
        },
		{
            "label": _("QTY"),
            "fieldname": "qty",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("UOM"),
            "fieldname": "uom",
            "fieldtype": "Data",
            "width": 100,
        },
		{
            "label": _("Rate"),
            "fieldname": "rate",
            "fieldtype": "Data",
            "width": 100,
        },
		{
            "label": _("Amount"),
            "fieldname": "amount",
            "fieldtype": "Data",
            "width": 100,
        },

	]

	return columns