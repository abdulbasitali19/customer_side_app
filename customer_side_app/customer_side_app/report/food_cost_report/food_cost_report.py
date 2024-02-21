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
        theoratical_cost = 0
        actual_cost = 0
        data = []
        for item in item_list:
            data_dict = {}
            stock_reconcile = frappe.db.sql(
                """SELECT sr.name, sri.current_qty as current_qty, sri.qty as qty
                   FROM `tabStock Reconciliation` as sr INNER JOIN  `tabStock Reconciliation Item` AS sri
                   on sr.name = sri.parent
                   WHERE sr.docstatus = 1 AND sri.item_code = '{0}'""".format(
                    item
                ),
                as_dict=1,
            )

            if stock_reconcile:
                valuation_rate = frappe.get_value("Item", item, "valuation_rate")
                data_dict["item_code"] = item
                data_dict["theoratical"] = (
                    stock_reconcile[0].get("current_qty")
                    if stock_reconcile[0].get("current_qty")
                    else 0
                )
                data_dict["theoratical_valuation"] = (
                    stock_reconcile[0].get("current_qty") * valuation_rate
                    if stock_reconcile[0].get("current_qty")
                    else 0
                )
                theoratical_cost +=  stock_reconcile[0].get("current_qty") * valuation_rate

                data_dict["actual"] = (
                    stock_reconcile[0].get("qty")
                    if stock_reconcile[0].get("qty")
                    else 0
                )
                data_dict["actual_valuation"] = (
                    stock_reconcile[0].get("qty") * valuation_rate
                    if stock_reconcile[0].get("qty")
                    else 0
                )

                actual_cost += stock_reconcile[0].get("qty") * valuation_rate

                uom = frappe.db.sql(
                    """SELECT  uom.uom as uom
                       FROM `tabItem` as item inner join `tabUOM Conversion Detail` as uom on item.name = uom.parent
                       WHERE item.item_code = '{0}'""".format(
                        item
                    ),
                    as_dict=1,
                )
                data_dict["uom"] = uom[0].get("uom") if uom else None

                purchase_qty = frappe.db.sql(
                    """SELECT SUM(sit.qty) as purchase_qty
                       FROM `tabPurchase Invoice` AS pi
                       INNER JOIN `tabPurchase Invoice Item` AS sit ON pi.name = sit.parent
                       WHERE sit.item_code = '{0}' AND pi.docstatus = 1
                       AND pi.posting_date BETWEEN '{1}' AND '{2}'""".format(
                        item, from_date, to_date
                    ),
                    as_dict=1,
                )
                data_dict["purchase"] = (
                    purchase_qty[0].get("purchase_qty")
                    if purchase_qty[0].get("purchase_qty")
                    else 0
                )

                sales_qty = frappe.db.sql(
                    """SELECT SUM(sit.qty) as sales_qty
                       FROM `tabSales Invoice` AS si
                       INNER JOIN `tabSales Invoice Item` AS sit ON si.name = sit.parent
                       WHERE sit.item_code = '{0}' AND si.docstatus = 1
                       AND si.posting_date BETWEEN '{1}' AND '{2}'""".format(
                        item, from_date, to_date
                    ),
                    as_dict=1,
                )
                data_dict["sales"] = (
                    sales_qty[0].get("sales_qty")
                    if sales_qty[0].get("sales_qty")
                    else 0
                )

                transfer_qty = frappe.db.sql(
                    """SELECT SUM(sed.qty) as transfer_qty
                       FROM `tabStock Entry` AS se
                       INNER JOIN `tabStock Entry Detail` AS sed ON se.name = sed.parent
                       WHERE sed.item_code = '{0}' AND se.docstatus = 1
                       AND se.stock_entry_type = 'Material Transfer'
                       AND se.posting_date BETWEEN '{1}' AND '{2}'""".format(
                        item, from_date, to_date
                    ),
                    as_dict=1,
                )
                data_dict["transfer"] = (
                    transfer_qty[0].get("transfer_qty")
                    if transfer_qty[0].get("transfer_qty")
                    else 0
                )

                manufacturing_qty = frappe.db.sql(
                    """SELECT SUM(sed.qty) as manu_qty
                       FROM `tabStock Entry` AS se
                       INNER JOIN `tabStock Entry Detail` AS sed ON se.name = sed.parent
                       WHERE sed.item_code = '{0}'
                       AND se.stock_entry_type = 'Manufacture' AND se.docstatus = 1
                       AND se.posting_date BETWEEN '{1}' AND '{2}'""".format(
                        item, from_date, to_date
                    ),
                    as_dict=1,
                )
                data_dict["manufacture"] = (
                    manufacturing_qty[0].get("manu_qty")
                    if manufacturing_qty[0].get("manu_qty")
                    else 0
                )

                waste_qty = frappe.db.sql(
                    """SELECT SUM(sed.qty) as waste_qty
                       FROM `tabStock Entry` AS se
                       INNER JOIN `tabStock Entry Detail` AS sed ON se.name = sed.parent
                       WHERE sed.item_code = '{0}'
                       AND se.stock_entry_type = 'Material Issue' AND se.docstatus = 1
                       AND se.posting_date BETWEEN '{1}' AND '{2}'""".format(
                        item, from_date, to_date
                    ),
                    as_dict=1,
                )
                data_dict["waste"] = (
                    waste_qty[0].get("waste_qty")
                    if waste_qty[0].get("waste_qty")
                    else 0
                )

                opening = frappe.db.get_value("Stock Ledger Entry", item, "actual_qty")
                data_dict["opening"] = opening if opening else 0

                data.append(data_dict)

        net_sales = frappe.db.sql("""
            SELECT
                sum(total) as total
            FROM
                `tabSales Invoice`
            WHERE
            docstatus = 1 and posting_date BETWEEN '{0}' AND '{1}'""".format(
                        from_date, to_date
                    ),
                    as_dict=1,debug = True)

        total_sales = net_sales[0].get("total")
        data.append({})
        data.append({"item_code": "The Total Net Sales is {0}".format(total_sales)})
        if total_sales is not None:
            data.append({"item_code": "Theoratical Cost is  {0}".format(theoratical_cost)})
            data.append({"item_code": "Theoratical Percentage is {0}".format((theoratical_cost/total_sales)*100)})
            data.append({"item_code": "Actual Cost is {0}%".format(actual_cost)})
            data.append({"item_code": "Actual Percentage is {0}%".format((actual_cost/total_sales)*100)})


        return data


def get_columns():
    columns = [
        {
            "label": _("Item"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 250,
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
            "label": _("Theoretical Valuation"),
            "fieldname": "theoratical_valuation",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Actual"),
            "fieldname": "actual",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Actual Valuation"),
            "fieldname": "actual_valuation",
            "fieldtype": "Data",
            "width": 120,
        },
    ]
    return columns
