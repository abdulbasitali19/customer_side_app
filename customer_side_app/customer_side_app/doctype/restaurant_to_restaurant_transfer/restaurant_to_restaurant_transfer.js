// Copyright (c) 2024, basit and contributors
// For license information, please see license.txt

frappe.ui.form.on('Restaurant To Restaurant Transfer', {
	from_warehouse: function(frm) {
		let transaction_controller = new erpnext.TransactionController({frm:frm});
		transaction_controller.autofill_warehouse(frm.doc.items, "s_warehouse", frm.doc.from_warehouse);
	},

	to_warehouse: function(frm) {
		let transaction_controller = new erpnext.TransactionController({frm:frm});
		transaction_controller.autofill_warehouse(frm.doc.items, "t_warehouse", frm.doc.to_warehouse);
	},

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
});

frappe.ui.form.on('Restaurant Transfer Detail',{
	
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




});
