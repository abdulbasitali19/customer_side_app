import frappe
from frappe.utils import add_to_date, cint, cstr, flt
from erpnext.stock.utils import get_stock_balance

from erpnext.stock.doctype.stock_reconciliation.stock_reconciliation import StockController

class Customstockreconciliation(StockController):
	def get_items_for(self, warehouse):
			self.items = []
			for item in get_items(warehouse, item_count_type, self.posting_date, self.posting_time, self.company):
				self.append("items", item)


@frappe.whitelist()
def get_normal_items(warehouse, item_count_type, posting_date, posting_time, company, item_code=None, ignore_empty_stock=False):
    item_list = []
    conditions_str = get_conditions(item_count_type)

    # Optimize database query to fetch required fields directly
    items = frappe.db.sql("""
        SELECT
            item_code,
			valuation_rate,
            item_name,
            item_group
        FROM
            `tabItem`
        WHERE
            {conditions}
    """.format(conditions=conditions_str), as_dict=True)

    for item in items:
            item_list.append({"item_code": item['item_code'],"item_name": item['item_name'], "item_group": item['item_group'],"valuation_rate":item['valuation_rate'],"warehouse": warehouse})

    return item_list

def get_conditions(item_count_type):
    conditions = ''
    if item_count_type == "Daily":
        conditions += "item_count_type = 'Daily'"
    if item_count_type == "Weekly":
        conditions += "item_count_type IN ('Daily', 'Weekly')"
    if item_count_type == "Monthly":
        conditions += "item_count_type IN ('Daily', 'Weekly', 'Monthly')"
    return conditions

