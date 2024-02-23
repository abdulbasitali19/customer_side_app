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
        warehouse = filters.get("warehouse")
        item = filters.get("item_name")
        item_group = filters.get("item_group")
        conditions = get_conditions(filters)


        item_list = frappe.db.sql("""
            SELECT
                item_code
            FROM
                `tabItem`
            WHERE
             1 = 1
                {0}
        """.format(conditions),as_dict=1, debug = True)

    if item_list:
        data = []

        for item in item_list:
            item = item.get("item_code")
            data_dict = {}
            stock_reconcile = frappe.db.sql(
                """SELECT sr.name, sri.current_qty as current_qty, sri.qty as qty
                   FROM `tabStock Reconciliation` as sr INNER JOIN  `tabStock Reconciliation Item` AS sri
                   on sr.name = sri.parent
                   WHERE sr.docstatus = 1 AND sri.item_code = '{0}' and sri.warehouse = '{1}'""".format(
                    item,warehouse
                ),
                as_dict=1,
            )

            if stock_reconcile:
                data_dict["item_code"] = item
                data_dict["theoratical"] = stock_reconcile[0].get("current_qty") if stock_reconcile[0].get("current_qty") else 0
                data_dict["actual"] = stock_reconcile[0].get("qty") if stock_reconcile[0].get("qty")else 0

                uom = frappe.db.sql("""
                    SELECT
                        stock_uom as uom
                    FROM
                        `tabItem` as item
                    WHERE
                        item.item_code = '{0}'
                """.format(item),as_dict = 1)


                data_dict["uom"] = uom[0].get("uom")

                purchase_qty = frappe.db.sql(
                    """SELECT SUM(sit.stock_qty) as purchase_qty
                       FROM `tabPurchase Invoice` AS pi
                       INNER JOIN `tabPurchase Invoice Item` AS sit ON pi.name = sit.parent
                       WHERE sit.item_code = '{0}' and pi.docstatus = 1
                       AND pi.posting_date BETWEEN '{1}' AND '{2}' AND sit.warehouse = '{3}' """.format(item, from_date, to_date, warehouse ),
					   as_dict = 1
                )
                data_dict["purchase"] = purchase_qty[0].get("purchase_qty") if purchase_qty[0].get("purchase_qty") else 0

                sales_qty = frappe.db.sql(
                    """SELECT SUM(sit.stock_qty) as sales_qty
                       FROM `tabSales Invoice` AS si
                       INNER JOIN `tabSales Invoice Item` AS sit ON si.name = sit.parent
                       WHERE sit.item_code = '{0}' AND si.docstatus = 1
                       AND si.posting_date BETWEEN '{1}' AND '{2}' AND sit.warehouse = '{3}'""".format(item, from_date, to_date,warehouse),
						as_dict = 1
                )
                data_dict["sales"] = sales_qty[0].get("sales_qty") if sales_qty[0].get("sales_qty") else 0

                transfer_qty = frappe.db.sql(
                    """SELECT SUM(sed.transfer_qty) as transfer_qty
                       FROM `tabStock Entry` AS se
                       INNER JOIN `tabStock Entry Detail` AS sed ON se.name = sed.parent
                       WHERE sed.item_code = '{0}'
                       AND se.stock_entry_type = 'Material Transfer' AND se.docstatus = 1
                       AND se.posting_date BETWEEN '{1}' AND '{2}' AND sed.t_warehouse = '{3}'""".format(item, from_date, to_date,warehouse),
					   as_dict = 1
                )
                data_dict["transfer"] = transfer_qty[0].get("transfer_qty")if transfer_qty[0].get("transfer_qty") else 0


                received_qty = frappe.db.sql(
                    """SELECT SUM(sed.transfer_qty) as transfer_qty
                       FROM `tabStock Entry` AS se
                       INNER JOIN `tabStock Entry Detail` AS sed ON se.name = sed.parent
                       WHERE sed.item_code = '{0}'
                       AND se.stock_entry_type = 'Material Transfer' AND se.docstatus = 1
                       AND se.posting_date BETWEEN '{1}' AND '{2}' AND sed.s_warehouse = '{3}'""".format(item, from_date, to_date,warehouse),
					   as_dict = 1
                )
                data_dict["received"] = received_qty[0].get("transfer_qty")if received_qty[0].get("transfer_qty") else 0

                manufacturing_qty = frappe.db.sql(
                    """SELECT SUM(sed.transfer_qty) as manu_qty
                       FROM `tabStock Entry` AS se
                       INNER JOIN `tabStock Entry Detail` AS sed ON se.name = sed.parent
                       WHERE sed.item_code = '{0}'
                       AND se.stock_entry_type = 'Manufacture' AND se.docstatus = 1
                       AND se.posting_date BETWEEN '{1}' AND '{2}' AND sed.s_warehouse = '{3}'""".format(item, from_date, to_date,warehouse),
					   as_dict = 1
                )
                data_dict["manufacture"] = manufacturing_qty[0].get("manu_qty") if manufacturing_qty[0].get("manu_qty") else 0

                waste_qty = frappe.db.sql(
                    """SELECT SUM(sed.transfer_qty) as waste_qty
                       FROM `tabStock Entry` AS se
                       INNER JOIN `tabStock Entry Detail` AS sed ON se.name = sed.parent
                       WHERE sed.item_code = '{0}'
                       AND se.stock_entry_type = 'Material Issue' AND se.docstatus = 1
                       AND se.posting_date BETWEEN '{1}' AND '{2}' AND sed.s_warehouse= '{3}'""".format(item, from_date, to_date,warehouse),
					   as_dict = 1
                )
                data_dict["waste"] = waste_qty[0].get("waste_qty") if waste_qty[0].get("waste_qty") else 0

                opening = frappe.db.sql("""
                    SELECT
                        actual_qty
                    FROM
                        `tabStock Ledger Entry`
                    WHERE
                        item_code = '{0}' and posting_date BETWEEN '{1}' AND '{2}' AND warehouse = '{3}'
                    ORDER BY
                        creation DESC
                """.format(item,from_date,to_date,warehouse),as_dict=1)
                data_dict["opening"] = opening[0].get("actual_qty") if opening[0].get("actual_qty") else 0

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
            "label": _("POS Sales"),
            "fieldname": "sales",
            "fieldtype": "Data",
            "width": 90,
        },
        {
            "label": _("Transfer Qty"),
            "fieldname": "transfer",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Received Qty"),
            "fieldname": "received",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Recipe Used"),
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



def get_conditions(filters):
    conditions = ""
    if filters.get("item_name"):
        conditions += " AND item_code = '{0}'".format(filters.get("item_name"))
    if filters.get("item_group"):
        conditions += " AND item_group = '{0}'".format(filters.get("item_group"))
    return conditions
