// Copyright (c) 2024, basit and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Food Cost Report Summary"] = {
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
			"fieldname":"Current_date_time",
			"label": __("Date Time"),
			"fieldtype": "Datetime",
			"width": "80",
		},

	]
};
