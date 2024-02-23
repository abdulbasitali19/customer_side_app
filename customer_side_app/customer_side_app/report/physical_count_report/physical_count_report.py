# Copyright (c) 2024, basit and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	conditions = get_conditions(filters)
	return columns, data



def get_stock_reconcilation_data(filters):
	if filters:
		from_date = filters.get("from_date")
		to_date = filters.get("to_date")
	conditions = get_conditions(filters)
	data = frappe.db.sql("""
		SELECT
			sri.item_name as item_name,
			sri.uom as uom,
			sri.current_qty as available_qty,
			sri.qty as actual_qty,
			sri.quantity_difference as difference,
			sri.warehouse as warehouse
		FROM
			`tabStock Reconciliation` as sr inner join `tabStock Reconciliation Item` as sri on sr.name = sri.parent
		Where
			sr.posting_date between '{0}' and '{1}' {2}
	""".format(from_date,to_date,conditions),as_dict = 1, debug = True)

	return data


def get_data(filters):
	entries_array = []
	data = get_stock_reconcilation_data(filters)
	if data:
		for i in data:
			valuation_rate = frappe.db.get_value("Item", i.get("item_name"),"valuation_rate")
			entries_dict = {}
			entries_dict['item_name'] = i.get("item_name")
			entries_dict['uom'] = i.get("uom")
			entries_dict['warehouse'] = i.get("warehouse")
			entries_dict['available_qty'] = i.get("available_qty")
			entries_dict['available_qty_cost'] = i.get("available_qty") * valuation_rate if valuation_rate else 0.0
			entries_dict['actual_qty'] = i.get("actual_qty")
			entries_dict['actual_qty_cost'] = i.get("actual_qty")*valuation_rate if valuation_rate else 0.0
			entries_dict['difference'] = i.get("difference")
			entries_dict['difference_cost'] = i.get("difference")*valuation_rate if valuation_rate else 0.0
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
			"label": _("Location"),
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 90,
		},
		{
			"label": _("Available Qty"),
			"fieldname": "available_qty",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Available Qty Cost"),
			"fieldname": "available_qty_cost",
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
			"label": _("Actual Qty Cost"),
			"fieldname": "actual_qty_cost",
			"fieldtype": "float",
			"width": 100,
		},
		{
			"label": _("Difference"),
			"fieldname": "difference",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Difference Cost"),
			"fieldname": "difference_cost",
			"fieldtype": "Float",
			"width": 100,
		},
	]
	return columns

def get_conditions(filters):
	conditions = ""
	if filters.get("item_name"):
		conditions += "and sri.item_name = '{0}'".format(filters.get("item"))
	if filters.get("warehouse"):
		conditions += "and sri.warehouse = '{0}'".format(filters.get("warehouse"))
	if filters.get("item_group"):
		conditions += "and sri.item_group = '{0}'".format(filters.get("item_group"))
	return conditions
