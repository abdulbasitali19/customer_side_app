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
   
    item_list = frappe.db.sql("""
            	SELECT 
                    sri.item_code as item_code
                FROM 
                	`tabStock Reconciliation` as sr INNER JOIN  `tabStock Reconciliation Item` AS sri   
                	on sr.name = sri.parent
                WHERE sr.docstatus = 1 AND sr.purpose = 'Stock Reconciliation' AND 
                   sr.posting_date BETWEEN '{0}' AND '{1}' and sri.warehouse = '{2}'
                   Group BY item_code
                """.format(from_date, to_date, warehouse), as_dict=1)
    data = []
    if item_list:
        for item in item_list:
            item_code = item.get("item_code")
            data_dict = {}
            stock_reconcile = frappe.db.sql("""
                SELECT 
                	sr.name, 
                 	sri.current_qty as current_qty, 
                  	sri.qty as qty, 
                   	sum(sri.amount) as amount,
                    sum(sri.current_Amount) as current_amount
                   FROM `tabStock Reconciliation` as sr INNER JOIN  `tabStock Reconciliation Item` AS sri
                   on sr.name = sri.parent
                   WHERE sr.docstatus = 1 AND sr.purpose = 'Stock Reconciliation' AND sri.item_code = '{0}' and sri.warehouse = '{1}' AND 
                   sr.posting_date BETWEEN '{2}' AND '{3}'""".format(item_code, warehouse, from_date, to_date),
                as_dict=1
            )

            if stock_reconcile:
                actual_amount = stock_reconcile[0].get("amount", 0) or 0
                current_amount = stock_reconcile[0].get("current_amount", 0) or 0
                
                net_sales = frappe.db.sql("""
                    SELECT
                        sum(sii.amount) as total
                    FROM
                        `tabSales Invoice` as si INNER JOIN `tabSales Invoice Item` as sii ON
                        si.name = sii.parent
                    WHERE  
                        sii.item_code = '{0}' and sii.warehouse = '{1}' and
                        si.docstatus = 1 and si.posting_date BETWEEN '{2}' AND '{3}'
                        """.format(
                        item_code, warehouse,from_date, to_date
                    ),
                    as_dict=1, debug=True)
                
                net_sales = net_sales[0].get("total") or 0.0
                
                data_dict["net_sales"] = net_sales
                if net_sales == 0:
                    net_sales = 1
                data_dict["item_code"] = item_code
                data_dict["actual_food_cost"] = actual_amount
                data_dict["actual_food_cost_percent"] = "{0}%".format(round((actual_amount * 100) / net_sales,2))
                data_dict["theoratical_food_cost"] = current_amount
                data_dict["theoratical_food_cost_percent"] = "{0}%".format(round((current_amount * 100) / net_sales,2))
                data_dict["variance"] = round(float(actual_amount) - float(current_amount),2)
                variance_percent = round((abs(actual_amount - current_amount) * 100) / net_sales,2)
                data_dict["variance_percent"] = "{:.2f}%".format(variance_percent)
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
            "label": _("Net Sales"),
            "fieldname": "net_sales",
            "fieldtype": "Data",
            "width": 100,
        },
      {
            "label": _("Actual Food Cost"),
            "fieldname": "actual_food_cost",
            "fieldtype": "Currency",
            "width": 120,
        },
      
		{
            "label": _("% to Sales"),
            "fieldname": "actual_food_cost_percent",
            "fieldtype": "data",
            "width": 120,
        },
      
      {
            "label": _("Theoratical Food Cost"),
            "fieldname": "theoratical_food_cost",
            "fieldtype": "Currency",
            "width": 120,
        },
      {
            "label": _("% to Sales"),
            "fieldname": "theoratical_food_cost_percent",
            "fieldtype": "data",
            "width": 120,
        },
      {
            "label": _("Variance"),
            "fieldname": "variance",
            "fieldtype": "Currency",
            "width": 120,
        },
      {
            "label": _("% to Sales"),
            "fieldname": "variance_percent",
            "fieldtype": "data",
            "width": 120,
        },
      	{
            "label": _("Remarks"),
            "fieldname": "remarks",
            "fieldtype": "data",
            "width": 120,
        },
      
	]
    
    
    return columns