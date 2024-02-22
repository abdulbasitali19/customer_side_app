// Copyright (c) 2024, basit and contributors
// For license information, please see license.txt

frappe.ui.form.on('Material Wastage Document', {
	// refresh: function(frm) {

	// }




});


frappe.ui.form.on('Wastage Item Table', {

	// on_submit:function(frm){
	// 	if(frm.doc.warehouse){
	// 		debugger;
	// 		frappe.model.set_value(cdt, cdn, "s_warehouse", frm.doc.warehouse);

	// 	}

	// },

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



});