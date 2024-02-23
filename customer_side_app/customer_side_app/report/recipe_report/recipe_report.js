// Copyright (c) 2024, basit and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Recipe Report"] = {
	"filters": [
		{
			label: "Item Group",
			fieldname: "item_group",
			fieldtype: "Link",
			options: "Item Group",
			// "get_query": function () {
			// 	return {
			// 		"filters": {
			// 			"item_group": frm.doc.item_group,
			// 		}
			// 	};
			// }

		},
		{
			"fieldname":"item_name",
			"label": __("Item"),
			"fieldtype": "Link",
			"options":"Item",
			"width": "80",
		},

	]
};
