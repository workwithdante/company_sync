frappe.ui.form.on("Company Sync Log Item", {
	review(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        // Suponiendo que sync_on es algo como "2025-06-25 13:05:16.801642-1234"
        let sync_log_str = row.sync_log;
		let sync_on = row.sync_on;

        // Separar la cadena usando el último guion
        let parts = sync_log_str.split('-');
        let log_id = parseInt(parts.pop());  // Obtener el valor después del último guion (log_id)

        // Ahora tienes el log_id y la fecha (sync_on_date)
        console.log("Log ID:", log_id);
        console.log("Sync On Date:", sync_on);

        frm.call({
			method: "update_sync_log",
			args: { 
				sync_on: sync_on,  // Pasar la fecha convertida
                log_id: log_id,         // Pasar el log_id
                review: row.review
			},
		}).then((r) => {
			//frm.save()
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


// Copyright (c) 2024, Dante Devenir and contributors
// For license information, please see license.txt
/*
frappe.ui.form.on('Company Sync Log Item', {
  review: function(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    // 1) Batch = el name del padre
    const batch_name = frm.doc.name;
    // 2) Member = el campo que identifica la fila en tu tabla externa
    const memberid   = row.memberid;
    // 3) Nuevo review
    const review     = row.review;

    // 4) Llamada al servidor para actualizar la tabla externa
	console.log(item);
	
	let newReview = item.review;
	let p_log_id = item.id;
	let p_sync_on = cdt.sync_on;

	frappe.call({
		method: "company_sync.company_sync.doctype.company_sync_log.update_sync_log.update_sync_log",
		args: { sync_on: p_sync_on, log_id: p_log_id, review: newReview },
		callback: function (r) {
			//console.log("Update")
		}
	});
  }
});

frappe.ui.form.on('Company Sync Log Item', {
  refresh(frm) {
    co
  }
});


frappe.ui.form.on("Company Sync Log Item", "review2", function(frm, cdt, cdn) {
	console.log("Review2 triggered");
});

frappe.ui.form.on("Company Sync Scheduler", {
	setup(frm) {
		frappe.realtime.on("company_sync_refresh", ({ percentage, vtigercrm_sync }) => {		
			// Validar que el sync corresponda al documento actual
			if (vtigercrm_sync !== frm.doc.name) return;

			updateProgressBar(frm, percentage);
			//reloadDocument(frm);
			if (!frm._has_shown_sync_log_preview) {
				frm.toggle_display("section_sync_preview", true);
				frm.page.clear_primary_action();
				frm._has_shown_sync_log_preview = true;
			}
		})
		frappe.realtime.on("company_sync_error_log", ({ error_log, company_sync, memberID, company, broker }) => {
			if (!frm._has_shown_sync_error_log_preview) {
				console.log("Acá activo section_sync_log_preview");
				frm.toggle_display("section_sync_log_preview", true);
				frm._has_shown_sync_error_log_preview = true;
			}

			var d = frm.add_child("sync_log");
			d.memberid = memberID;
			d.status = error_log;

			frm.refresh_field('sync_log');
			
		})
		/*frappe.realtime.on("company_sync_success", ({ company_sync }) => {		
			if (!frm._has_shown_sync_log_preview) {
				frm.toggle_display("section_sync_preview", true);
				frm.page.clear_primary_action();
				frm._has_shown_sync_log_preview = true;
			}
			successProgressBar(frm);
			frm.refresh()
		})*/
	/*},
	onload(frm) {
		/* if (frm.is_new()) {
			frm.toggle_display("section_sync_preview", false);
		} */
	/*},
	refresh(frm) {
        frm.trigger("update_primary_action");
		frm.trigger("order_by_table");
		frm._has_shown_sync_log_preview = false;
		frm._has_shown_sync_error_log_preview = false;
	},
	/*hide_index(frm) {
		const $sync_log_wrapper = frm.get_field("sync_log").$wrapper;
		console.log($sync_log_wrapper)
		let $header_index = $sync_log_wrapper.find('.row-index');

		$header_index.each(function(index, element) {
			$(element).hide();
		});

		let $header_check = $sync_log_wrapper.find('.row-check');

		$header_check.each(function(index, element) {
			$(element).hide();
		});
	},*/
    /*onload_post_render(frm) {
		frm.trigger("update_primary_action");
		console.log("No debi entrar acá");
	},
    update_primary_action(frm) {
		if (frm.is_dirty()) {
			frm.enable_save();
			return;
		}
		//frm.disable_save();
		if (frm.doc.status !== "Success") {
			if (!frm.is_new()) {
				let label = frm.doc.status === "Pending" ? __("Start Sync") : __("Retry");
				frm.page.set_primary_action(label, () => frm.events.start_sync(frm));
			} else {
				frm.page.set_primary_action(__("Save"), () => frm.save());
			}
		} 
		//valide if child table sync_log is empty
		console.log(frm.doc.sync_log.length)
		if (frm.doc.sync_log.length > 0) {
			frm.toggle_display("section_sync_log_preview", true);
			frm._has_shown_sync_log_preview = false;
			console.log("Acá active en update_primary_action -> section_sync_log_preview");
			//frm.disable_save();
			frm.set_df_property("company_file", "read_only", 1);
		} else {
			frm.enable_save();
			let label = frm.doc.status === "Pending" ? __("Start Sync") : __("Retry");
			frm.page.set_primary_action(label, () => frm.events.start_sync(frm));
			frm._has_shown_sync_error_log_preview = false;
		}
	},
	start_sync(frm) {
		frm.set_df_property("company_file", "read_only", 1);
		frm.call({
			method: "form_start_sync",
			args: { company_sync_scheduler: frm.doc.name },
			btn: frm.page.btn_primary,
		}).then((r) => {
			if (r.message === true) {
				frm.disable_save();
			}
		});
	},
	order_by_table(frm) {
		if (frm.is_new()) return;
	  
		const $sync_log_wrapper = frm.get_field("sync_log").$wrapper;
	  
		function attachClickEvent() {
		  let $header = $sync_log_wrapper.find('.grid-heading-row div[data-fieldname="status"]').first();
		  if ($header.length) {
			// Aplicar estilo global (si no lo tienes ya en CSS)
			$header.css({
			  "cursor": "pointer",
			  "text-decoration": "underline"
			});
	  
			// Quitar cualquier listener previo y asignar el de toggle
			$header.off('click.sort_toggle').on('click.sort_toggle', function() {
			  // Almacenar el orden original la primera vez
			  if (!frm._sync_log_original) {
				frm._sync_log_original = frm.doc.sync_log.slice(); // Realiza una copia del arreglo
			  }
			  if (frm._is_sorted_desc) {
				// Si ya está ordenado de forma descendente, restaurar el orden original
				frm.doc.sync_log = frm._sync_log_original.slice();
				frm._is_sorted_desc = false;
			  } else {
				// Ordenar de forma descendente
				frm.doc.sync_log.sort((a, b) => {
				  if (a.status < b.status) return 1;
				  if (a.status > b.status) return -1;
				  return 0;
				});
				frm._is_sorted_desc = true;
			  }
			  // Refrescar el campo para actualizar la vista
			  frm.refresh_field('sync_log');
			});
		  }
		}
	  
		// Asignar el listener inicialmente
		attachClickEvent();
	  
		// MutationObserver para reactivar el listener cuando el grid se re-renderice
		const observer = new MutationObserver(() => {
		  attachClickEvent();
		});
		observer.observe($sync_log_wrapper.get(0), { childList: true, subtree: true });
	},		  
});

function updateProgressBar(frm, percentage) {
	console.log("Por acá ingresé al updateProgressBar");
	const $wrapper = frm.get_field("sync_preview").$wrapper;
	$wrapper.empty();
	
	const $progress = $('<div class="progress">').appendTo($wrapper);
	$('<div class="progress-bar progress-bar-striped progress-bar-animated bg-primary">')
		.attr({
			'role': 'progressbar',
			'style': `width: ${percentage}%`,
			'aria-valuenow': percentage,
			'aria-valuemin': '0', 
			'aria-valuemax': '100'
		})
		.text(`${percentage}%`)
		.appendTo($progress);
}*/

/*function successProgressBar(frm) {
	const $wrapper = frm.get_field("sync_preview").$wrapper;
	$wrapper.empty();
	
	const $progress = $('<div class="progress">').appendTo($wrapper);
	$('<div class="progress-bar progress-bar-striped progress-bar-animated bg-success">')
		.attr({
			'role': 'progressbar',
			'style': `width: 100%`,
			'aria-valuenow': '100',
			'aria-valuemin': '0', 
			'aria-valuemax': '100'
		})
		.text(`100%`)
		.appendTo($progress);
	
	frm.doc.status = "Success";
	frm.refresh_field("status");
}

function reloadDocument(frm) {
	frappe.model.with_doc("Company Sync Scheduler", frm.doc.name)
		.then(() => frm.reload_doc());
}*/
