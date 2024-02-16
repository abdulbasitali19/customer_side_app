// Copyright (c) 2024, basit and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Movement Report"] = {
	"filters": [
		{
			"fieldname":"item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"width": "80",
			"reqd": 1,
			"options": "Item"
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
	]
};
