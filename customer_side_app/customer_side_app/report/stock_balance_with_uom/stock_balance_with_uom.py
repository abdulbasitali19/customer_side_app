# Copyright (c) 2024, abdul basit ali and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	if not filters:
		filters = {}
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_stock_value(filters):
	if filters:
		from_date = filters.get("from_date")
		to_date = filters.get("to_date")
		warehouse = filters.get("warehouse")
		data = frappe.db.sql(
			"""
			SELECT
				item_code,
				warehouse,
				stock_uom,
				qty_after_transaction
			FROM
				`tabStock Ledger Entry`
			WHERE
				posting_date BETWEEN '{0}' AND '{1}' AND warehouse = '{2}'
			GROUP BY
				item_code, warehouse
			""".format(from_date , to_date, warehouse),
			as_dict=1,
		)
		return data


def get_data(filters):
    data = []
    stock_values = get_stock_value(filters)

    for i in stock_values:
        data_dict = {}
        item_details = get_item_and_item_group(i.get("item_code"))

        data_dict["item_code"] = i.get("item_code")
        data_dict["item_name"] = item_details.get("item_name")
        data_dict["item_group"] = item_details.get("item_group")
        data_dict["warehouse"] = i.get("warehouse")
        data_dict["stock_uom"] = i.get("stock_uom")
        data_dict["bal_qty"] = i.get("qty_after_transaction")

        stock_value_difference = i.get("qty_after_transaction")
        if item_details:
            if "Box" in item_details and stock_value_difference:
                conversion_factor = item_details.get("Box")
                data_dict["box"] = round(stock_value_difference / conversion_factor, 2)
            else:
                data_dict["box"] = 0.0

            if "Kg" in item_details and stock_value_difference:
                conversion_factor = item_details.get("Kg")
                data_dict["kg"] = conversion_factor * stock_value_difference
            else:
                data_dict["kg"] = 0.0

            if "Liter" in item_details and stock_value_difference:
                conversion_factor = item_details.get("Liter")
                data_dict["liter"] = conversion_factor * stock_value_difference
            else:
                data_dict["liter"] = 0.0
        else:
            data_dict["box"] = 0.0
            data_dict["kg"] = 0.0
            data_dict["liter"] = 0.0

        data.append(data_dict)

    return data


def get_item_and_item_group(item_code):
    item_group, item_name = frappe.db.get_value(
        "Item", item_code, ["item_group", "item_name"]
    )
    unit_of_measure = frappe.get_all(
        "UOM Conversion Detail",
        filters={"parent": item_code, "parenttype": "Item"},
        fields=["uom", "factor"],
    )

    uom_factor_dict = {"item_name": item_name, "item_group": item_group}
    for uom_factor in unit_of_measure:
        uom = uom_factor["uom"]
        factor = uom_factor["factor"]
        uom_factor_dict[uom] = factor

    return uom_factor_dict


def get_columns():
    columns = [
        {
            "label": _("Item"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 100,
        },
        {"label": _("Item Name"), "fieldname": "item_name", "width": 150},
        {
            "label": _("Item Group"),
            "fieldname": "item_group",
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 100,
        },
        {
            "label": _("Warehouse"),
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 100,
        },
        {
            "label": _("Stock UOM"),
            "fieldname": "stock_uom",
            "fieldtype": "Link",
            "options": "UOM",
            "width": 90,
        },
        {
            "label": _("Balance Qty"),
            "fieldname": "bal_qty",
            "fieldtype": "Float",
            "width": 100,
            "convertible": "qty",
        },
        {
            "label": _("Balance in KG"),
            "fieldname": "kg",
            "fieldtype": "data",
            "width": 120,
        },
        {
            "label": _("Balance in Box"),
            "fieldname": "box",
            "fieldtype": "data",
            "width": 120,
        },
        {
            "label": _("Balance in Liter"),
            "fieldname": "liter",
            "fieldtype": "data",
            "width": 120,
        },
    ]
    return columns
