frappe.ui.form.on("Company Sync Log Item", "review", function(frm, cdt, cdn) {
	console.log("Review triggered");
});

frappe.ui.form.on("Company Sync Register", {
	onload(frm) {
		if (!frm.is_new() || !frm._has_shown_log) {
			frm.toggle_display("section_log", true);
			frm._has_shown_log = true;
		}
	},
	refresh(frm) {
        frm.trigger("update_primary_action");
	},
	update_primary_action(frm) {
		if (frm.is_dirty()) {
			frm.enable_save();
			return;
		}

		if (frm.doc.status !== "Success") {
			if (!frm.is_new()) {
				let label = frm.doc.status === "Pending" ? __("Start Sync") : __("Retry");
				frm.page.set_primary_action(label, () => frm.events.start_sync(frm));
			} else {
				frm.page.set_primary_action(__("Save"), () => frm.save());
			}
		}
	},
	start_sync(frm) {
		frm.set_df_property("csv_file", "read_only", 1);
		frm.call({
			method: "start_sync",
			args: { company_sync_register: frm.doc.name },
			btn: frm.page.btn_primary,
		}).then((r) => {
			if (r.message === true) {
				frm.disable_save();
			}
		});
	},
});