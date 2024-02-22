# Copyright (c) 2024, basit and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data =  get_data(filters)
	return columns, data

def get_data(filters):
	data = []
	material_issue_data = get_material_issue_data(filters)
	if material_issue_data:
		for d in material_issue_data:
			data_dict = {}
			data_dict["item_code"] = d.get("item_code")
			data_dict["item_name"] = d.get("item_name")
			data_dict["uom"] = d.get("uom")
			data_dict["qty"] = d.get("qty")
			data_dict["cost"] = d.get("cost")
			data_dict["date"] = d.get("date")
			data_dict["time"] = d.get("time")
			data_dict["reason"] = d.get("reason")

			data.append(data_dict)
		return data
	else:
		frappe.throw("Data Not Found")


def get_material_issue_data(filters):
	if filters:
		from_date = filters.get("from_date")
		to_date = filters.get("to_date")
	wastage_data = frappe.db.sql("""
		SELECT
			wit.item_code as item_code,
			wit.item_name as item_name,
			wit.uom as uom,
			wit.qty as qty,
			wit.basic_rate as cost,
			mwd.posting_date as date,
			mwd.posting_time  as time,
			wit.reason
		FROM
			`tabMaterial Wastage Document` as mwd INNER JOIN `tabWastage Item Table` as wit on mwd.name = wit.parent
		WHERE
			mwd.docstatus = 1 and mwd.posting_date BETWEEN '{0}' AND '{1}'
	""".format(from_date, to_date),as_dict = 1)
	return wastage_data


def get_columns():
	columns = [

		{
            "label": _("Item"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 100,
        },
		{
			"label": _("Item"),
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 100,


		},
        {
            "label": _("UOM"),
            "fieldname": "uom",
            "fieldtype": "Link",
			"options" : "UOM",
            "width": 100,
        },
		{
            "label": _("QTY"),
            "fieldname": "qty",
            "fieldtype": "Data",
            "width": 100,
        },
		{
            "label": _("Cost"),
            "fieldname": "cost",
            "fieldtype": "Data",
            "width": 100,
        },
		{
            "label": _("Date"),
            "fieldname": "date",
            "fieldtype": "Date",
            "width": 100,
        },
		{
            "label": _("Time"),
            "fieldname": "time",
            "fieldtype": "Data",
            "width": 100,
        },
		{
            "label": _("Reason"),
            "fieldname": "reason",
            "fieldtype": "Data",
            "width": 100,
        },


	]
	return columns