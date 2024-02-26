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
def get_items(warehouse, item_count_type, posting_date, posting_time, company, item_code=None, ignore_empty_stock=False):

	ignore_empty_stock = cint(ignore_empty_stock)
	items = [frappe._dict({"item_code": item_code, "warehouse": warehouse,"item_count_type":item_count_type})]

	if not item_code:
		items = get_items_for_stock_reco(warehouse, company, item_count_type)

	res = []
	itemwise_batch_data = get_itemwise_batch(warehouse, posting_date, company, item_code)

	for d in items:
		if d.item_code in itemwise_batch_data:
			valuation_rate = get_stock_balance(
				d.item_code, d.warehouse, posting_date, posting_time, with_valuation_rate=True
			)[1]

			for row in itemwise_batch_data.get(d.item_code):
				if ignore_empty_stock and not row.qty:
					continue

				args = get_item_data(row, row.qty, valuation_rate)
				res.append(args)
		else:
			stock_bal = get_stock_balance(
				d.item_code,
				d.warehouse,
				posting_date,
				posting_time,
				with_valuation_rate=True,
				with_serial_no=cint(d.has_serial_no),
			)
			qty, valuation_rate, serial_no = (
				stock_bal[0],
				stock_bal[1],
				stock_bal[2] if cint(d.has_serial_no) else "",
			)

			if ignore_empty_stock and not stock_bal[0]:
				continue

			args = get_item_data(d, qty, valuation_rate, serial_no)

			res.append(args)

	return res

def get_items_for_stock_reco(warehouse, company, item_count_type=None):
    lft, rgt = frappe.db.get_value("Warehouse", warehouse, ["lft", "rgt"])
    conditions = []

    if item_count_type == "Daily":
        conditions.append(f"AND i.item_count_type = 'Daily'")
    if item_count_type == "Weekly":
        conditions.append("AND i.item_count_type IN ('Daily', 'Weekly')")
    if item_count_type == "Monthly":
        conditions.append("AND i.item_count_type IN ('Daily', 'Weekly', 'Monthly')")

    conditions_str = " AND ".join(conditions) if conditions else ""


    items = frappe.db.sql(
        f"""
        SELECT
            i.name as item_code, i.item_name, bin.warehouse as warehouse, i.has_serial_no, i.has_batch_no
        FROM
            `tabBin` bin, `tabItem` i
        WHERE
            i.name = bin.item_code
            AND IFNULL(i.disabled, 0) = 0
            AND i.is_stock_item = 1
            AND i.has_variants = 0
            AND EXISTS (
                SELECT name FROM `tabWarehouse` WHERE lft >= '{lft}' AND rgt <= '{rgt}' AND name = bin.warehouse
            )
        """,
        as_dict=1,
        debug=True
    )

    items += frappe.db.sql(
        f"""
        SELECT
            i.name as item_code, i.item_name, id.default_warehouse as warehouse, i.has_serial_no, i.has_batch_no
        FROM
            `tabItem` i, `tabItem Default` id
        WHERE
            i.name = id.parent
            AND EXISTS (
                SELECT name FROM `tabWarehouse` WHERE lft >= '{lft}' AND rgt <= '{rgt}' AND name=id.default_warehouse
            )
            AND i.is_stock_item = 1
            AND i.has_variants = 0
            AND IFNULL(i.disabled, 0) = 0
            AND id.company = '{company}'
            {conditions_str}
        GROUP BY
            i.name
        """,
        as_dict=1,
        debug=True
    )

    # Remove duplicates
    iw_keys = set()
    items = [
        item
        for item in items
        if [
            (item.item_code, item.warehouse) not in iw_keys,
            iw_keys.add((item.item_code, item.warehouse)),
        ][0]
    ]

    return items




def get_itemwise_batch(warehouse, posting_date, company, item_code=None):
	from erpnext.stock.report.batch_wise_balance_history.batch_wise_balance_history import execute

	itemwise_batch_data = {}

	filters = frappe._dict(
		{"warehouse": warehouse, "from_date": posting_date, "to_date": posting_date, "company": company}
	)

	if item_code:
		filters.item_code = item_code

	columns, data = execute(filters)

	for row in data:
		itemwise_batch_data.setdefault(row[0], []).append(
			frappe._dict(
				{
					"item_code": row[0],
					"warehouse": warehouse,
					"qty": row[8],
					"item_name": row[1],
					"batch_no": row[4],
				}
			)
		)

	return itemwise_batch_data

def get_item_data(row, qty, valuation_rate, serial_no=None):
	return {
		"item_code": row.item_code,
		"warehouse": row.warehouse,
		"qty": qty,
		"item_name": row.item_name,
		"valuation_rate": valuation_rate,
		"current_qty": qty,
		"current_valuation_rate": valuation_rate,
		"current_serial_no": serial_no,
		"serial_no": serial_no,
		"batch_no": row.get("batch_no"),
	}


@frappe.whitelist()
def get_normal_items(warehouse, item_count_type, posting_date, posting_time, company, item_code=None, ignore_empty_stock=False):
	conditions = []
	item_list = []
	if item_count_type == "Daily":
		conditions.append(f"AND item_count_type = 'Daily'")
	if item_count_type == "Weekly":
		conditions.append("AND item_count_type IN ('Daily', 'Weekly')")
	if item_count_type == "Monthly":
		conditions.append("AND item_count_type IN ('Daily', 'Weekly', 'Monthly')")

	conditions_str = " AND ".join(conditions) if conditions else ""

	items = frappe.db.sql(f"""
	SElECT
		item_code,
	FROM
		`tabItem`
	Where
		1=1 {conditions_str}
	""",as_dict=1)

	for i in items:
		stock = frappe.db.get_list("Stock Ledger Entry",{item_code:i.get("item_code"), warehouse:i.get("warehouse")})
		if sum(stock) > 0:
			item_list.append({"item_code":i.get("item_code"), "warehouse":warehouse})

	return item_list