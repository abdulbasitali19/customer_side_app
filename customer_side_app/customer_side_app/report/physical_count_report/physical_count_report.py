# Copyright (c) 2024, basit and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    conditions = get_conditions(filters)
    return columns, data


def get_stock_reconcilation_data(filters):
    if filters:
        from_date = filters.get("from_date")
        to_date = filters.get("to_date")
    conditions = get_conditions(filters)
    data = frappe.db.sql("""
        SELECT
            sri.item_code as item_code,
            sri.item_name as item_name,
            sri.custom_stock_uom as uom,
            sri.qty as actual_qty,
            sri.current_qty as available_qty,
            sri.quantity_difference as difference,
            sri.warehouse as warehouse,
            sr.posting_date as posting_date,
            sr.owner as owner
        FROM
            `tabStock Reconciliation` as sr inner join `tabStock Reconciliation Item` as sri on sr.name = sri.parent
        Where
            sr.purpose = 'Stock Reconciliation' AND sr.docstatus = 1 AND sr.posting_date between '{0}' and '{1}' {2}
    """.format(from_date, to_date, conditions), as_dict=1)

    return data


def get_data(filters):
    entries_array = []
    data = get_stock_reconcilation_data(filters)
    if data:
        for i in data:
            entries_dict = {}
            secondary_uom = frappe.db.get_value("Item", i.get("item_code"), "secondary_unit")
            unit_of_measure = frappe.get_all("UOM Conversion Detail", filters={"parent": i.get("item_code"), "parenttype": "Item"}, fields=["uom", "conversion_factor"],)
            entries_dict['item_code'] = i.get("item_code")
            entries_dict['item_name'] = i.get("item_name")
            # entries_dict['posting_date'] = i.get("posting_date")
            # entries_dict['warehouse'] = i.get("warehouse")
            entries_dict['uom'] = secondary_uom
            entries_dict['system_stock_value'] = round(i.get("available_qty"),3)
            entries_dict['actual_stock_value'] = round(i.get("actual_qty"),3)
            entries_dict['difference_value'] = round(float(i.get("difference")),3)
            if unit_of_measure:
                for uom in unit_of_measure:
                    uom_name = uom.get("uom")
                    if uom_name == secondary_uom:
                        converison_factor = uom.get('conversion_factor') if uom.get('conversion_factor') > 0 else 1
                        entries_dict["actual_stock_qty"] =  round(i.get('actual_qty') / converison_factor,3)
                        entries_dict["system_stock_qty"] =  round(i.get('available_qty') / converison_factor,3)
                        entries_dict["difference_qty"] =  round(float(i.get('difference')) / converison_factor,3)
                        
            entries_array.append(entries_dict)
    return entries_array


def get_columns():
    """return columns"""
    columns = [
        {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 90,
        },
        
        {"label": _("Item Name"), "fieldname": "item_name", "width": 150},
        {
            "label": _("Stock UOM"),
            "fieldname": "uom",
            "fieldtype": "Link",
            "options": "UOM",
            "width": 90,
        },
        {
            "label": _("System Stock Qty"),
            "fieldname": "system_stock_qty",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Actual Stock Qty"),
            "fieldname": "actual_stock_qty",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Difference Qty"),
            "fieldname": "difference_qty",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("System Stock Value"),
            "fieldname": "system_stock_value",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Actual Stock Value"),
            "fieldname": "actual_stock_value",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Difference Value"),
            "fieldname": "difference_value",
            "fieldtype": "Data",
            "width": 120,
        },
        
    ]

    return columns


def get_conditions(filters):
    conditions = ""
    if filters.get("item_code"):
        conditions += "and sri.item_code = '{0}'".format(filters.get("item_code"))
    if filters.get("warehouse"):
        conditions += "and sri.warehouse = '{0}'".format(filters.get("warehouse"))
    if filters.get("item_group"):
        conditions += "and sri.item_group = '{0}'".format(filters.get("item_group"))
    return conditions
