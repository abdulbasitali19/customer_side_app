frappe.ui.form.on("Stock Reconciliation", {

    setup: function (frm) {
        frm.set_query("uom", "items", function (doc, cdt, cdn) {
          let row = locals[cdt][cdn];
          return {
            query:
              "erpnext.accounts.doctype.pricing_rule.pricing_rule.get_item_uoms",
            filters: {
              value: row.item_code,
              apply_on: "Item Code",
            },
          };
        });
      },


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
            {
                label: __("Ignore Empty Stock"),
                fieldname: "ignore_empty_stock",
                fieldtype: "Check",
                default : 1
            }
        ];

        frappe.prompt(fields, function (data) {
            frappe.call({
                method: "customer_side_app.overrides.custom_stock_reconciliation.get_normal_items",
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
                    debugger;
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
                        console.log(r.message)
                        frappe.model.set_value(cdt, cdn, r.message);
                    }
                }
            });
        }
    },


    qty:function(frm,cdt, cdn){
        var d = locals[cdt][cdn];
        if (d.qty){
            frappe.model.set_value(cdt, cdn, "amount", flt(d.qty * d.valuation_rate));
        }
    }

    

})

