# Copyright (c) 2024, basit and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data =  get_data(filters)
	conditions = get_conditions(filters)
	return columns, data

def get_data(filters):
	data = []
	material_issue_data = get_material_issue_data(filters)
	if material_issue_data:
		for d in material_issue_data:
			item_description  = frappe.db.get_value("Item", d.get("item_code"), "description")
			data_dict = {}
			data_dict["item_code"] = d.get("item_code")
			data_dict["item_name"] = item_description
			data_dict["uom"] = d.get("uom")
			data_dict["warehouse"] = d.get("warehouse")
			data_dict["qty"] = d.get("qty")
			data_dict["cost"] = d.get("cost")
			data_dict["date"] = d.get("date")
			data_dict["time"] = d.get("time")
			data_dict["owner"] = d.get("owner")
			data_dict["reason"] = d.get("reason")

			data.append(data_dict)
		return data
	else:
		frappe.throw("Data Not Found")


def get_material_issue_data(filters):
	if filters:
		from_date = filters.get("from_date")
		to_date = filters.get("to_date")
	conditions = get_conditions(filters)
	wastage_data = frappe.db.sql("""
		SELECT
			wit.item_code as item_code,
			wit.item_name as item_name,
			wit.stock_uom as uom,
			wit.s_warehouse as warehouse,
			wit.transfer_qty as qty,
			wit.amount as cost,
			mwd.posting_date as date,
			mwd.posting_time  as time,
			wit.reason,
			mwd.owner as owner
		FROM
			`tabMaterial Wastage Document` as mwd INNER JOIN `tabWastage Item Table` as wit on mwd.name = wit.parent
		WHERE
			mwd.docstatus = 1 and mwd.posting_date BETWEEN '{0}' AND '{1}' {2}
	""".format(from_date, to_date, conditions),as_dict = 1)
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
            "label": _("Location"),
            "fieldname": "warehouse",
            "fieldtype": "Link",
			"options" : "Warehouse",
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
            "label": _("Creted By"),
            "fieldname": "owner",
            "fieldtype": "Link",
			"options": "User",
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



def get_conditions(filters):
	conditions = ""
	if filters.get("item_name"):
		conditions += "and wit.item_name = '{0}'".format(filters.get("item"))
	if filters.get("warehouse"):
		conditions += "and wit.s_warehouse = '{0}'".format(filters.get("warehouse"))
	if filters.get("item_group"):
		conditions += "and wit.item_group = '{0}'".format(filters.get("item_group"))
	if filters.get("owner"):
		conditions += "and mwd.owner = '{0}'".format(filters.get("owner"))

	return conditions
