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
            stock_reconcile = frappe.get_all(
                "Stock Reconciliation Item",
                filters={"parent": item, "parenttype": "Stock Reconciliation"},
                fields=["name"]
            )

            if stock_reconcile:
                data_dict["item_code"] = item

                uom = frappe.get_all(
                    "Uoms",
                    filters={"parent": item, "parenttype": "Item"},
                    fields=["uom"]
                )
                data_dict["uom"] = uom if uom else None

                purchase_qty = frappe.get_all(
                    "Purchase Invoice Items",
                    filters={"parent": item, "parenttype": "Purchase Invoice", "posting_date": ["between", (from_date, to_date)]},
                    fields=["qty", "uom"]
                )
                data_dict["purchase"] = sum(purchase_qty)

                sales_qty = frappe.get_all(
                    "Sales Invoice Items",
                    filters={"parent": item, "parenttype": "Sales Invoice", "posting_date": ["between", (from_date, to_date)]},
                    fields=["qty"]
                )
                data_dict["sales"] = sum(sales_qty)

                transfer_qty = frappe.get_all(
                    "Stock Entry Detail",
                    filters={
                        "parent": item,
                        "parenttype": "Stock Entry",
                        "stock_entry_type": "Material Transfer",
                        "posting_date": ["between", (from_date, to_date)]
                    },
                    fields=["qty"]
                )
                data_dict["transfer"] = sum(transfer_qty)

                manufacturing_qty = frappe.get_all(
                    "Stock Entry Detail",
                    filters={
                        "parent": item,
                        "parenttype": "Stock Entry",
                        "stock_entry_type": "Manufacturing",
                        "posting_date": ["between", (from_date, to_date)]
                    },
                    fields=["qty"]
                )
                data_dict["manufacturing"] = sum(manufacturing_qty)

                waste_qty = frappe.get_all(
                    "Stock Entry Detail",
                    filters={
                        "parent": item,
                        "parenttype": "Stock Entry",
                        "stock_entry_type": "Material Issue",
                        "posting_date": ["between", (from_date, to_date)]
                    },
                    fields=["qty"]
                )
                data_dict["waste"] = sum(waste_qty)

                opening = frappe.db.get_value("Stock Ledger Entry", item, "actual_qty")
                data_dict["opening"] = sum(opening)

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
            "fieldtype": "Link",
            "options": "UOM",
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
            "label": _("Theoritical"),
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