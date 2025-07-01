frappe.ui.form.on("Company Sync Register", {
	setup(frm) {
		if (frm.is_new() || !frm._has_shown_log) {
			frm.toggle_display("section_log", false);
			frm._has_shown_log = false;
		}
	},

	onload(frm) {
		const grid = frm.fields_dict.sync_log.grid;
		const $wrapper = $(grid.control.wrapper);
		const selector_review = 'input[data-fieldname="review"]';
		const selector_description = 'input[data-fieldname="description"]';

		// ————————————————
		// REVIEW (link)  
		// awesomplete-selectcomplete o input quedando vacío
		// ————————————————
		if (!$wrapper.data("review-listener")) {
			$wrapper.data("review-listener", true);
			
			$wrapper.on("focusout", selector_description, function(e) {
				const $inp    = $(this);
				const oldVal  = $inp.data("priorValue") || "";
				const newVal  = this.value;

				$inp.data("priorDescription", newVal);

				if (newVal === oldVal) return;

				const $row   = $inp.closest(".grid-row");
				const log_id = parseInt($row.attr("data-idx"), 10);
				const sync_on = frm.doc.creation;

				// Llamada al método del servidor
				frm.call({
					method: "update_sync_log",
					args: {
					sync_on: sync_on,
					log_id:  log_id,
					description:  newVal
					}
				}).then(() => {
					//frappe.show_alert({message: __("Review saved"), indicator: "green"});
					//frm.trigger("status_log");
				});
			});
		}

		// Solo una vez instalamos el listener
		if (!$wrapper.data("listener-added")) {
			$wrapper.data("listener-added", true);

			$wrapper.on("awesomplete-selectcomplete input", selector_review, function(e) {
				const $inp   = $(this);
				const oldVal = $inp.data("priorValue") || "";
				const newVal = this.value;

				// Guardamos el valor para la próxima comparación
				$inp.data("priorValue", newVal);

				// Si antes y ahora estaban vacíos, no hacemos nada
				if (oldVal === "" && newVal === "") {
					return;
				}

				// Solo cuando realmente cambie, y en los eventos que interesa:
				if (newVal !== oldVal &&
					(e.type === "awesomplete-selectcomplete" ||
					(e.type === "input" && newVal === ""))) {

					// Obtenemos el log_id (está en data-idx)
					const $row   = $inp.closest(".grid-row");
					const log_id = parseInt($row.attr("data-idx"), 10);
					const sync_on = frm.doc.creation; // la creación del padre

					// Llamada al método del servidor
					frm.call({
						method: "update_sync_log",
						args: {
						sync_on: sync_on,
						log_id:  log_id,
						review:  newVal
						}
					}).then(() => {
						//frappe.show_alert({message: __("Review saved"), indicator: "green"});
						//frm.trigger("status_log");
					});

					// También refrescamos el filtro visual inmediatamente
					//frm.trigger("status_log");
				}
			});
		}

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
		frm.set_df_property("sync_log", "cannot_select_rows", true);
		frm.set_df_property("sync_log", "allow_bulk_edit", false);
	},

	onload_post_render(frm) {
		// Asegúrate de hacerlo *después* de que el grid esté en el DOM
		const grid = frm.fields_dict.sync_log.grid;
		grid.toggle_checkboxes(false);
		// 3) remueve del DOM la columna de headers y las celdas de checkbox
		const $w = grid.wrapper;
		// elimina el header (la casilla "select all")
		$w.find(".grid-heading-row .grid-row-check").closest(".grid-row").remove();
		// elimina cada checkbox dentro de las filas
		$w.find(".grid-row .grid-row-check").closest(".grid-row-check").remove();
	},

	refresh(frm) {
		// Cada vez que recargue el form
		//frm.trigger("status_log");
		frm.trigger("update_primary_action");
		frm.fields_dict.sync_log.grid.reset_grid();
		frm.fields_dict.sync_log.grid.toggle_checkboxes(false);
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
		} else {
			frm.page.set_primary_action(__("Save"), () => frm.save());
		}
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
			frm.disable_save();
		}
		});
	}
});
