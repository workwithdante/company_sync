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

	setup(frm) {
		if (frm.is_new() || !frm._has_shown_log) {
			frm.toggle_display("section_log", false);
			frm._has_shown_log = false;
			frm.set_df_property("company_file", "read_only", 1);
		}
	},

	after_save(frm) {
		//frm.reload_doc();
		frm.toggle_display("section_log", true);
	},

	status_log(frm) {
		frm.toggle_display("section_log", false);
		frm.fields_dict.sync_log.grid.reset_grid();
		frm.save();
	},

	onload(frm) {
		// Mostrar la sección de Log si ya existe
		if (!frm.is_new() || !frm._has_shown_log) {
		frm.toggle_display("section_log", true);
		frm._has_shown_log = true;
		}

		// Filtros iniciales y acción primaria
		//frm.trigger("status_log");
		frm.trigger("update_primary_action");
		frm.set_df_property("sync_log", "cannot_add_rows", true);
		frm.set_df_property("sync_log", "cannot_delete_rows", true);
		frm.set_df_property("sync_log", "allow_bulk_edit", false);
	},

	refresh(frm) {
		// Cada vez que recargue el form
		//frm.trigger("status_log");
		if (frm.is_new() || !frm._has_shown_log) {
			frm.toggle_display("section_log", false);
			frm._has_shown_log = false;
			frm.set_df_property("company_file", "read_only", 1);
		}
		frm.trigger("update_primary_action");
		frm.fields_dict.sync_log.grid.toggle_checkboxes(false);
		frm.fields_dict.sync_log.grid.reset_grid();
	},

	/**
	 * Habilita / cambia el botón primario según el estado del form
	 */
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
		}
	},

	/**
	 * Inicia el proceso de sincronización
	 */
	start_sync(frm) {
		frm.set_df_property("csv_file", "read_only", 1);
		frm.call({
			method: "start_sync",
			args: { company_sync_register: frm.doc.name },
			btn: frm.page.btn_primary
		}).then(r => {
			if (r.message === true) {
				frm.save();
				//frm.reload_doc();
				frm.disable_save();
			}
		});
	}
});
