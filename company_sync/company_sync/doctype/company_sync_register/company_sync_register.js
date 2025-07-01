frappe.ui.form.on("Company Sync Log Item", {
  review(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    // Llamada directa a tu función, pasándole toda la info que necesitas
    frm.events.update_log(frm, cdt, cdn, {
      review: row.review
    });
  },

  description(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    frm.events.update_log(frm, cdt, cdn, {
      description: row.description
    });
  }
});

function _update_status_tags(frm) {
  // 1) Construimos un mapa { status: count }
  const counts = {};
  (frm.doc.sync_log || []).forEach(r => {
    counts[r.status] = (counts[r.status] || 0) + 1;
  });

  // 2) Localizamos todos los tags de status_log
  const tags = frm.fields_dict.status_log.$wrapper.find(".tag");

  // 3) Para cada tag, sacamos el status_type original
  tags.each((i, tag) => {
    const status = frm.doc.status_log[i].status_type;
    const count  = counts[status] || 0;
    // 4) Reemplazamos el texto interno del tag
    $(tag).find(".tag-text").text(`${status} (${count})`);
  });
}

frappe.ui.form.on("Company Sync Register", {
	update_log(frm, cdt, cdn, data) {
		const row        = locals[cdt][cdn];
		const sync_on    = frm.doc.creation;
		const log_id     = row.idx;        // o row.id, según tu PK
		const args = {
		sync_on,
		log_id,
		description: data.description,
		review:      data.review
		};

		frm.call({
		method: "update_sync_log",
		args
		});
	},

	status_log(frm) {
		// Se dispara cuando cambian los tags
		_update_status_tags(frm);
	},

	onload(frm) {
		frm.trigger("update_primary_action");
		//frm.set_df_property("sync_log", "cannot_add_rows", true);
		//frm.set_df_property("sync_log", "cannot_delete_rows", true);
		//frm.set_df_property("sync_log", "allow_bulk_edit", true);
		_update_status_tags(frm);
	},

	refresh(frm) {
		if (!frm.is_new()) {
			frm.set_df_property("company_file", "read_only", 1);
		}
		frm.trigger("update_primary_action");
		_update_status_tags(frm);
		//frm.fields_dict.sync_log.grid.toggle_checkboxes(false);
	},

	update_primary_action(frm) {
		if (frm.is_dirty()) {
			frm.enable_save();
			return;
		}
		if (frm.doc.status !== "Success") {
			if (!frm.is_new()) {
				const label = frm.doc.status === "Pending"
				? __("Start Sync")
				: __("Retry");
				frm.page.set_primary_action(label, () => frm.events.start_sync(frm));

				if (frm.doc.status === "Pending") {
					frm.toggle_display("status_log", false);
				}
			} else {
				frm.page.set_primary_action(__("Save"), () => frm.save());
			}
		} else {
			frm.set_df_property("csv_file", "read_only", 1);
			frm.toggle_display("section_log", true);
		}
	},


	start_sync(frm) {
		frm.call({
			method: "start_sync",
			args: { company_sync_register: frm.doc.name },
			btn: frm.page.btn_primary
		}).then(r => {
			if (r.message === true) {
				frm.disable_save();
			}
		});
	}
});
