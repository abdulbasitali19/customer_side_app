# Copyright (c) 2024, basit and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_data(filters):
    if filters:
        to_date = filters.get("to_date")
        from_date = filters.get("from_date")
    item_list = frappe.db.get_list("Item", pluck="item_code")
    if item_list:
        data = []

        for item in item_list:
            data_dict = {}
            stock_reconcile = frappe.db.sql(
                """SELECT sri.name, sri.current_qty as current_qty, sri.qty as qty
                   FROM `tabStock Reconciliation Item` AS sri
                   WHERE sri.item_code = '{0}'""".format(item),as_dict = 1
            )

            if stock_reconcile:
                data_dict["item_code"] = item
                data_dict["theoratical"] = stock_reconcile[0].get("current_qty") if stock_reconcile[0].get("current_qty") else 0
                data_dict["actual"] = stock_reconcile[0].get("qty") if stock_reconcile[0].get("qty")else 0

                data_dict["uom"] = "uom"  # Replace this with the appropriate SQL query

                purchase_qty = frappe.db.sql(
                    """SELECT SUM(sit.qty) as purchase_qty
                       FROM `tabPurchase Invoice` AS pi
                       INNER JOIN `tabPurchase Invoice Item` AS sit ON pi.name = sit.parent
                       WHERE sit.item_code = '{0}' 
                       AND pi.posting_date BETWEEN '{1}' AND '{2}'""".format(item, from_date, to_date),
					   as_dict = 1
                )
                data_dict["purchase"] = purchase_qty[0].get("purchase_qty") if purchase_qty[0].get("purchase_qty") else 0

                sales_qty = frappe.db.sql(
                    """SELECT SUM(sit.qty) as sales_qty
                       FROM `tabSales Invoice` AS si
                       INNER JOIN `tabSales Invoice Item` AS sit ON si.name = sit.parent
                       WHERE sit.item_code = '{0}' 
                       AND si.posting_date BETWEEN '{1}' AND '{2}'""".format(item, from_date, to_date),
						as_dict = 1
                )
                data_dict["sales"] = sales_qty[0].get("sales_qty") if sales_qty[0].get("sales_qty") else 0

                transfer_qty = frappe.db.sql(
                    """SELECT SUM(sed.qty) as transfer_qty
                       FROM `tabStock Entry` AS se
                       INNER JOIN `tabStock Entry Detail` AS sed ON se.name = sed.parent
                       WHERE sed.item_code = '{0}'
                       AND se.stock_entry_type = 'Material Transfer'
                       AND se.posting_date BETWEEN '{1}' AND '{2}'""".format(item, from_date, to_date),
					   as_dict = 1
                )
                data_dict["transfer"] = transfer_qty[0].get("transfer_qty")if transfer_qty[0].get("transfer_qty") else 0

                manufacturing_qty = frappe.db.sql(
                    """SELECT SUM(sed.qty) as manu_qty
                       FROM `tabStock Entry` AS se
                       INNER JOIN `tabStock Entry Detail` AS sed ON se.name = sed.parent
                       WHERE sed.item_code = '{0}' 
                       AND se.stock_entry_type = 'Manufacturing'
                       AND se.posting_date BETWEEN '{1}' AND '{2}'""".format(item, from_date, to_date),
					   as_dict = 1
                )
                data_dict["manufacture"] = manufacturing_qty[0].get("manu_qty") if manufacturing_qty[0].get("manu_qty") else 0

                waste_qty = frappe.db.sql(
                    """SELECT SUM(sed.qty) as waste_qty
                       FROM `tabStock Entry` AS se
                       INNER JOIN `tabStock Entry Detail` AS sed ON se.name = sed.parent
                       WHERE sed.item_code = '{0}'
                       AND se.stock_entry_type = 'Material Issue'
                       AND se.posting_date BETWEEN '{1}' AND '{2}'""".format(item, from_date, to_date),
					   as_dict = 1
                )
                data_dict["waste"] = waste_qty[0].get("waste_qty") if waste_qty[0].get("waste_qty") else 0

                opening = frappe.db.get_value("Stock Ledger Entry", item, "actual_qty")
                data_dict["opening"] = opening if opening else 0

                data.append(data_dict)

        return data




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
            "label": _("UOM"),
            "fieldname": "uom",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Opening"),
            "fieldname": "opening",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Purchase"),
            "fieldname": "purchase",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Sales"),
            "fieldname": "sales",
            "fieldtype": "Data",
            "width": 90,
        },
        {
            "label": _("Transfer"),
            "fieldname": "transfer",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Manufacture"),
            "fieldname": "manufacture",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Waste"),
            "fieldname": "waste",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Theoretical"),
            "fieldname": "theoratical",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Actual"),
            "fieldname": "actual",
            "fieldtype": "Data",
            "width": 120,
        },
    ]
    return columns
