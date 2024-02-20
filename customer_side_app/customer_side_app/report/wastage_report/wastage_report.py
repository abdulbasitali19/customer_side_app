# Copyright (c) 2024, basit and contributors
# For license information, please see license.txt

# import frappe


def execute(filters=None):
	columns, data = [], []
	return columns, data


def get_data(filters):
	data = []
	material_issue_data = get_material_issue_data(filters)
	if material_issue_data:
		for d in data:
			data_dict = {}
			data_dict["item_code"] = d.get("item_code")
			data_dict["item_name"] = d.get("item_name")
			data_dict["uom"] = d.get("uom")
			data_dict["qty"] = d.get("qty")
			data_dict["cost"] = d.get("cost")
			data_dict["date"] = d.get("date")
			data_dict["time"] = d.get("time")
			
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
			wit.rate as cost,
			mwd.date as date,
			mwd.time  as time,
			wit.reason
		FROM
			`tabMaterial Wastage Document` as mwd INNER JOIN `tabWastage Item Table` as wit on mwd.name = wit.parent
		WHERE
			mwd.docstatus = 1 and mwd.posting_date BETWEEN '{1}' AND '{2}'
	""".format(from_date, to_date),as_dict = 1)


