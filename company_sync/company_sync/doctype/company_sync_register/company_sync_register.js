frappe.ui.form.on("Company Sync Log Item", {
	review(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        // Suponiendo que sync_on es algo como "2025-06-25 13:05:16.801642-1234"
        let sync_on_str = row.sync_on;

        // Separar la cadena usando el último guion
        let parts = sync_on_str.split('-');
        let log_id = parseInt(parts.pop());  // Obtener el valor después del último guion (log_id)

        // Ahora tienes el log_id y la fecha (sync_on_date)
        console.log("Log ID:", log_id);
        console.log("Sync On Date:", sync_on_str);

        frm.call({
			method: "update_sync_log",
			args: { 
				sync_on: sync_on_str,  // Pasar la fecha convertida
                log_id: log_id,         // Pasar el log_id
                review: row.review
			},
		}).then((r) => {
			/*if (r.message === true) {
				frm.disable_save();
			}*/
		});
    }
});

frappe.ui.form.on("Company Sync Register", {
	onload(frm) {
		if (!frm.is_new() || !frm._has_shown_log) {
			frm.toggle_display("section_log", true);
			frm._has_shown_log = true;
		}

		if (frm.doc.sync_log && !frm._sync_init_done) {
			const sync_log = frm.doc.sync_log || [];
			frm.clear_table('sync_log');
			sync_log.forEach(d => {
				let row = frm.add_child('sync_log');
				row.sync_log = d.name;
				row.id = d.id;
				row.review = d.review;
				row.status = d.status;
				row.sync_on = d.sync_on;
			});
			frm.refresh_field('sync_log');
			frm._sync_init_done = true;
		}

		frm.trigger("status_log");
	},

	status_log(frm) {
		// Obtener los valores seleccionados en el multiselect del padre
		const selected_statuses = (frm.doc.status_log || []).map(row => row.status_type);

		// Contar las filas visibles
		let visible_rows = 0;

		// Recorremos todas las filas y ocultamos las que no coincidan
		frm.fields_dict.sync_log.grid.grid_rows.forEach(row => {
			const visible = selected_statuses.length === 0 || selected_statuses.includes(row.doc.status);
			// Cambiamos el estado del estilo de display de las filas
			$(row.row).toggle(visible); // Oculta o muestra la fila
			if (visible) {
				visible_rows++;
			}
		});

		// Verificamos si hay filas visibles
		const gridBody = frm.fields_dict.sync_log.grid.wrapper.find(".grid-body");

		if (visible_rows === 0) {
			// Si no hay filas visibles, mostramos el mensaje "No Data"
			const gridEmpty = gridBody.find(".grid-empty");
			gridEmpty.removeClass("hidden");  // Elimina la clase "hidden"
			gridEmpty.show();  // Asegura que el mensaje "No Data" se muestra
		} else {
			// Si hay filas visibles, ocultamos el mensaje "No Data"
			gridBody.find(".grid-empty").hide();
		}
	},

	refresh(frm) {
		// Aplica el filtro al cargar también
		frm.trigger("status_log");
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
