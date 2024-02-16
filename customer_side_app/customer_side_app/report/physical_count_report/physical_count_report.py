# Copyright (c) 2024, basit and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data



def get_stock_reconcilation_data(filters):
	if filters:
		from_date = filters.get("from_date")
		to_date = filters.get("to_date")
	data = frappe.db.sql("""
		SELECT
			sri.item_name as item_name,
			sri.uom as uom,
			sri.current_qty as available_qty,
			sri.qty as actual_qty,
			sri.quantity_difference as difference
		FROM 
			`tabStock Reconciliation` as sr inner join `tabStock Reconciliation Item` as sri on sr.name = sri.parent
		Where
			sr.posting_date between '{0}' and '{1}'
	""".format(from_date,to_date),as_dict = 1)

	return data 


def get_data(filters):
	entries_array = []
	data = get_stock_reconcilation_data(filters)
	if data:
		for i in data:
			entries_dict = {}
			entries_dict['item_name'] = i.get("item_name")
			entries_dict['uom'] = i.get("uom")
			entries_dict['available_qty'] = i.get("available_qty")
			entries_dict['actual_qty'] = i.get("actual_qty")
			entries_dict['difference'] = i.get("difference")
			entries_array.append(entries_dict)
		return entries_array



def get_columns():
	"""return columns"""
	columns = [
		{"label": _("Item Name"), "fieldname": "item_name", "width": 150},
		{
			"label": _("UOM"),
			"fieldname": "uom",
			"fieldtype": "Link",
			"options": "UOM",
			"width": 90,
		},
		{
			"label": _("Available Qty"),
			"fieldname": "available_qty",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Actual Qty"),
			"fieldname": "actual_qty",
			"fieldtype": "float",
			"width": 100,
		},
		{
			"label": _("Difference"),
			"fieldname": "difference",
			"fieldtype": "Float",
			"width": 100,
		},
	]
	return columns