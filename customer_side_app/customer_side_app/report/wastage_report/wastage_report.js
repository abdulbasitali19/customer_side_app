// Copyright (c) 2024, basit and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Wastage Report"] = {
	"filters": [

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
		{
			"fieldname":"warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options":"Warehouse",
			"width": "80",
		},
		{
			"fieldname":"item_name",
			"label": __("Item"),
			"fieldtype": "Link",
			"options":"Item",
			"width": "80",
		},
		{
			"fieldname":"item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options":"Item Group",
			"width": "80",

		},
		{
			"fieldname":"owner",
			"label": __("Created By"),
			"fieldtype": "Link",
			"options":"User",
			"width": "80",

		},


	]
};
