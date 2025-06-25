// Copyright (c) 2025, Dante Devenir and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Company Sync Register", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Company Sync Log Item", "review", function(frm, cdt, cdn) {
	frm.save();
});