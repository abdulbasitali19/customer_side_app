frappe.ui.form.on("Stock Reconciliation", {
    refresh: function (frm) {
        if (frm.doc.docstatus < 1) {
            frm.add_custom_button(__("Fetch Items from Warehouse"), function () {
                frm.events.get_items(frm);
            });
        }

        if (frm.doc.company) {
            frm.trigger("toggle_display_account_head");
        }
    },
    get_items: function (frm) {
        let fields = [
            {
                label: 'Warehouse',
                fieldname: 'warehouse',
                fieldtype: 'Link',
                options: 'Warehouse',
                reqd: 1,
                "get_query": function () {
                    return {
                        "filters": {
                            "company": frm.doc.company,
                        }
                    };
                }
            },
            {
                label: 'Item Count Type',
                fieldname: 'item_count_type',
                fieldtype: 'Select',
                options: ["","Daily", "Weekly", "Monthly"],
                reqd: 1,


            },
            // {
            //     label: "Item Group",
            //     fieldname: "item_group",
            //     fieldtype: "Link",
            //     options: "Item Group",
            //     "get_query": function () {
            //         return {
            //             "filters": {
            //                 "item_group": frm.doc.item_group,
            //             }
            //         };
            //     }

            // },
            // {
            //     label: "Item Code",
            //     fieldname: "item_code",
            //     fieldtype: "Link",
            //     options: "Item",
            //     "get_query": function () {
            //         return {
            //             "filters": {
            //                 "disabled": 0,
            //             }
            //         };
            //     }
            // },
            {
                label: __("Ignore Empty Stock"),
                fieldname: "ignore_empty_stock",
                fieldtype: "Check",
                default : 1
            }
        ];

        frappe.prompt(fields, function (data) {
            frappe.call({
                method: "customer_side_app.overrides.stock_reconciliation.get_items",
                args: {
                    warehouse: data.warehouse,
                    posting_date: frm.doc.posting_date,
                    posting_time: frm.doc.posting_time,
                    company: frm.doc.company,
                    item_group :data.item_group,
                    item_code: data.item_code,
                    item_count_type:data.item_count_type,
                    ignore_empty_stock: data.ignore_empty_stock
                },
                callback: function (r) {
                    if (r.exc || !r.message || !r.message.length) return;

                    frm.clear_table("items");

                    r.message.forEach((row) => {
                        let item = frm.add_child("items");
                        $.extend(item, row);

                        item.qty = item.qty || 0;
                        item.valuation_rate = item.valuation_rate || 0;
                    });
                    frm.refresh_field("items");
                }
            });
        }, __("Get Items"), __("Update"));
    },
})


frappe.ui.form.on("Stock Reconciliation Item", {

    uom: function (doc, cdt, cdn) {
        var d = locals[cdt][cdn];
        if (d.uom && d.item_code) {
            return frappe.call({
                method: "erpnext.stock.doctype.stock_entry.stock_entry.get_uom_details",
                args: {
                    item_code: d.item_code,
                    uom: d.uom,
                    qty: d.qty
                },
                callback: function (r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, r.message);
                    }
                }
            });
        }
    },


})