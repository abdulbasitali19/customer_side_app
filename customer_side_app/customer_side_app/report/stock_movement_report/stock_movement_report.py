# Copyright (c) 2024, basit and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils.data import nowtime,nowdate


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_data(filters):
    if filters:
        to_date = filters.get("to_date")
        from_date = filters.get("from_date")
        warehouse = filters.get("warehouse")
        item = filters.get("item_code")
        item_group = filters.get("item_group")
        conditions = get_conditions(filters)


    item_list =frappe.db.sql("""
            	SELECT 
                    sri.item_code as item_code
                FROM 
                	`tabStock Reconciliation` as sr INNER JOIN  `tabStock Reconciliation Item` AS sri   
                	on sr.name = sri.parent
                WHERE sr.docstatus = 1 AND sr.purpose = 'Stock Reconciliation' AND 
                   sr.posting_date BETWEEN '{0}' AND '{1}' and sri.warehouse = '{2}' {3}
                   Group BY item_code
                """.format(from_date,to_date,warehouse,conditions), as_dict=1, debug = True)

    if item_list:
        data = []

        for item in item_list:
            item_name = frappe.db.get_value("Item", item.get("item_code"), 'item_name')
            item = item.get("item_code")
            data_dict = {}
            stock_reconcile = frappe.db.sql(
                """SELECT sr.name, sri.current_qty as current_qty, sri.qty as qty
                   FROM `tabStock Reconciliation` as sr INNER JOIN  `tabStock Reconciliation Item` AS sri
                   on sr.name = sri.parent
                   WHERE sr.docstatus = 1 AND sr.purpose = 'Stock Reconciliation' AND sri.item_code = '{0}' and sri.warehouse = '{1}'
                   AND sr.posting_date BETWEEN '{2}' AND '{3}'""".format(
                    item,warehouse,from_date,to_date
                ),
                as_dict=1,
            )

            if stock_reconcile:
                data_dict["item_name"] = item_name
                data_dict["item_code"] = item
                
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
                       FROM `tabPurchase Receipt` AS pi
                       INNER JOIN `tabPurchase Receipt Item` AS sit ON pi.name = sit.parent
                       WHERE sit.item_code = '{0}' and pi.docstatus = 1
                       AND pi.posting_date BETWEEN '{1}' AND '{2}' AND sit.warehouse = '{3}' """.format(item, from_date, to_date, warehouse ),
					   as_dict = 1
                )
                purchase_qty = purchase_qty[0].get("purchase_qty") if purchase_qty[0].get("purchase_qty") else 0
                data_dict["purchase"] = purchase_qty

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
                    """SELECT SUM(sed.qty) as transfer_qty
                       FROM `tabStock Entry` AS se
                       INNER JOIN `tabStock Entry Detail` AS sed ON se.name = sed.parent
                       WHERE sed.item_code = '{0}'
                       AND se.stock_entry_type = 'Material Transfer' AND se.docstatus = 1
                       AND se.posting_date BETWEEN '{1}' AND '{2}' AND sed.s_warehouse = '{3}'""".format(item, from_date, to_date,warehouse),
					   as_dict = 1
                )
                data_dict["transfer"] = transfer_qty[0].get("transfer_qty")if transfer_qty[0].get("transfer_qty") else 0


                received_qty = frappe.db.sql(
                    """SELECT SUM(sed.qty) as transfer_qty
                       FROM `tabStock Entry` AS se
                       INNER JOIN `tabStock Entry Detail` AS sed ON se.name = sed.parent
                       WHERE sed.item_code = '{0}'
                       AND se.stock_entry_type = 'Material Transfer' AND se.docstatus = 1
                       AND se.posting_date BETWEEN '{1}' AND '{2}' AND sed.t_warehouse = '{3}'""".format(item, from_date, to_date,warehouse),
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
                manufacturing_qty = manufacturing_qty[0].get("manu_qty") if manufacturing_qty[0].get("manu_qty") else 0
                data_dict["manufacture"] = manufacturing_qty

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
                opening = get_stock_balance(item,warehouse,from_date,"23:59:59")
                end_count = get_stock_balance(item,warehouse,to_date,"23:59:59")
                actual_usage = opening + purchase_qty - end_count
                variance = manufacturing_qty - actual_usage
                data_dict["opening"] =  opening
                data_dict["end_count"]  = end_count
                data_dict["actual_usage"]  = actual_usage
                data_dict["variance"] = variance
                
                


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
            "label": _("Item Name"),
            "fieldname": "item_name",
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
            "label": _("End Count"),
            "fieldname": "end_count",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Purchase"),
            "fieldname": "purchase",
            "fieldtype": "Data",
            "width": 100,
        },
        # {
        #     "label": _("POS Sales"),
        #     "fieldname": "sales",
        #     "fieldtype": "Data",
        #     "width": 90,
        # },
        {
            "label": _("Transfer Out"),
            "fieldname": "transfer",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Transfer In"),
            "fieldname": "received",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Theoretical Qty"),
            "fieldname": "manufacture",
            "fieldtype": "Data",
            "width": 120,
        },
         {
            "label": _("Actual Qty"),
            "fieldname": "actual_usage",
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
            "label": _("Variance Qty"),
            "fieldname": "variance",
            "fieldtype": "Data",
            "width": 120,
        },
      
       
    ]
    return columns



def get_conditions(filters):
    conditions = ""
    if filters.get("item_code"):
        conditions += " AND item_code = '{0}'".format(filters.get("item_code"))
    if filters.get("item_group"):
        conditions += " AND item_group = '{0}'".format(filters.get("item_group"))
    return conditions


def get_stock_balance(
	item_code,
	warehouse,
	posting_date=None,
	posting_time=None,
	with_valuation_rate=False,
	with_serial_no=False,
	inventory_dimensions_dict=None,
	batch_no=None,
	voucher_no=None,
):
	"""Returns stock balance quantity at given warehouse on given posting date or current date.

	If `with_valuation_rate` is True, will return tuple (qty, rate)"""

	# from erpnext.stock.stock_ledger import get_previous_sle

	if posting_date is None:
		posting_date = nowdate()
	if posting_time is None:
		posting_time = nowtime()


	args = {
		"item_code": item_code,
		"warehouse": warehouse,
		"posting_date": posting_date,
		"posting_time": posting_time,
	}

	if voucher_no:
		args["voucher_no"] = voucher_no

	extra_cond = ""
	if inventory_dimensions_dict:
		for field, value in inventory_dimensions_dict.items():
			args[field] = value
			extra_cond += f" and {field} = %({field})s"

	last_entry = get_previous_sle(args, extra_cond=extra_cond)

	if with_valuation_rate:
		if with_serial_no:
			if batch_no:
				args["batch_no"] = batch_no

			serial_nos = get_serial_nos_data_after_transactions(args)

			return (
				(last_entry.qty_after_transaction, last_entry.valuation_rate, serial_nos)
				if last_entry
				else (0.0, 0.0, None)
			)
		else:
			return (
				(last_entry.qty_after_transaction, last_entry.valuation_rate) if last_entry else (0.0, 0.0)
			)
	else:
		return last_entry.qty_after_transaction if last_entry else 0.0


def get_previous_sle(args, for_update=False, extra_cond=None):
	"""
	get the last sle on or before the current time-bucket,
	to get actual qty before transaction, this function
	is called from various transaction like stock entry, reco etc

	args = {
	        "item_code": "ABC",
	        "warehouse": "XYZ",
	        "posting_date": "2012-12-12",
	        "posting_time": "12:00",
	        "sle": "name of reference Stock Ledger Entry"
	}
	"""
	args["name"] = args.get("sle", None) or ""
	sle = get_stock_ledger_entries(
		args, "<=", "desc", "limit 1", for_update=for_update, extra_cond=extra_cond
	)
	return sle and sle[0] or {}


def get_stock_ledger_entries(
	previous_sle,
	operator=None,
	order="desc",
	limit=None,
	for_update=False,
	debug=False,
	check_serial_no=True,
	extra_cond=None,
):
	"""get stock ledger entries filtered by specific posting datetime conditions"""
	conditions = " and timestamp(posting_date, posting_time) {0} timestamp(%(posting_date)s, %(posting_time)s)".format(
		operator
	)
	if previous_sle.get("warehouse"):
		conditions += " and warehouse = %(warehouse)s"
	elif previous_sle.get("warehouse_condition"):
		conditions += " and " + previous_sle.get("warehouse_condition")

	if check_serial_no and previous_sle.get("serial_no"):
		# conditions += " and serial_no like {}".format(frappe.db.escape('%{0}%'.format(previous_sle.get("serial_no"))))
		serial_no = previous_sle.get("serial_no")
		conditions += (
			""" and
			(
				serial_no = {0}
				or serial_no like {1}
				or serial_no like {2}
				or serial_no like {3}
			)
		"""
		).format(
			frappe.db.escape(serial_no),
			frappe.db.escape("{}\n%".format(serial_no)),
			frappe.db.escape("%\n{}".format(serial_no)),
			frappe.db.escape("%\n{}\n%".format(serial_no)),
		)

	if not previous_sle.get("posting_date"):
		previous_sle["posting_date"] = "1900-01-01"
	if not previous_sle.get("posting_time"):
		previous_sle["posting_time"] = "00:00"

	if operator in (">", "<=") and previous_sle.get("name"):
		conditions += " and name!=%(name)s"

	if operator in (">", "<=") and previous_sle.get("voucher_no"):
		conditions += " and voucher_no!=%(voucher_no)s"

	if extra_cond:
		conditions += f"{extra_cond}"

	return frappe.db.sql(
		"""
		select *, timestamp(posting_date, posting_time) as "timestamp"
		from `tabStock Ledger Entry`
		where item_code = %%(item_code)s
		and is_cancelled = 0
		%(conditions)s
		order by timestamp(posting_date, posting_time) %(order)s, creation %(order)s
		%(limit)s %(for_update)s"""
		% {
			"conditions": conditions,
			"limit": limit or "",
			"for_update": for_update and "for update" or "",
			"order": order,
		},
		previous_sle,
		as_dict=1,
		debug=debug,
	)

def get_serial_nos_data_after_transactions(args):
	serial_nos = set()
	args = frappe._dict(args)

	sle = frappe.qb.DocType("Stock Ledger Entry")
	query = (
		frappe.qb.from_(sle)
		.select(sle.serial_no, sle.actual_qty)
		.where(
			(sle.is_cancelled == 0)
			& (sle.item_code == args.item_code)
			& (sle.warehouse == args.warehouse)
			& (
				CombineDatetime(sle.posting_date, sle.posting_time)
				< CombineDatetime(args.posting_date, args.posting_time)
			)
		)
		.orderby(sle.posting_date, sle.posting_time, sle.creation)
	)

	if args.batch_no:
		query = query.where(sle.batch_no == args.batch_no)

	stock_ledger_entries = query.run(as_dict=True)

	for stock_ledger_entry in stock_ledger_entries:
		changed_serial_no = get_serial_nos_data(stock_ledger_entry.serial_no)
		if stock_ledger_entry.actual_qty > 0:
			serial_nos.update(changed_serial_no)
		else:
			serial_nos.difference_update(changed_serial_no)

	return "\n".join(serial_nos)