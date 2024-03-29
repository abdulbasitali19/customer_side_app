# Copyright (c) 2024, basit and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_bom_data(filters):
    conditions = get_conditions(filters)
    bom_master_data = frappe.db.sql("""
        SELECT
            bom.item_name as item,
            bom_item.item_name as item_name,
            bom_item.qty as qty,
            bom_item.uom as uom,
            bom_item.rate as rate,
            bom_item.amount as amount
        FROM
            `tabBOM` as bom INNER JOIN `tabBOM Item` as bom_item on bom_item.parent = bom.name
        WHERE 1 = 1 {0}

            """.format(conditions),as_dict=1
            )
    return bom_master_data

def get_data(filters):
    bom_data = get_bom_data(filters)
    if bom_data:
        data = []
        added_items = set()
        rate = 0
        for d in bom_data:
            if d.get("item") not in added_items:
                if rate != 0:  # Add total rate before new item row
                    data.append({"rate": "Total Rate {0}".format(rate)})
                added_items.add(d.get("item"))
                rate = 0
                data.append({"item": d.get("item")})

            rate += d.get("rate")
            data_dict = {}
            data_dict["item_code"] = d.get("item_name")
            data_dict["qty"] = d.get("qty")
            data_dict["uom"] = d.get("uom")
            data_dict["rate"] = d.get("rate")
            data_dict["amount"] = d.get("amount")
            data.append(data_dict)

        # Add total rate after the last item row
        data.append({"rate": "Total Rate {0}".format(rate)})

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
            "label": _("Item Name"),
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


def get_conditions(filters):
    conditions = ""
    if filters.get("item_name"):
        conditions += " AND bom.item = '{0}'".format(filters.get("item_name"))
    if filters.get("item_group"):
        conditions += " AND bom.item_group = '{0}'".format(filters.get("item_group"))
    return conditions