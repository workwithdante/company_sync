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
	setup(frm) {
		frappe.realtime.on("company_sync_refresh", ({ percentage }) => {		

			updateProgressBar(frm, percentage);
			//reloadDocument(frm);
			if (!frm._has_shown_sync_log_preview) {
				frm.toggle_display("section_sync_preview", true);
				frm.page.clear_primary_action();
				frm._has_shown_sync_log_preview = true;
			}
		})
		frappe.realtime.on("company_sync_success", ({ success }) => {		
			frm.toggle_display("section_sync_preview", false);
			//successProgressBar(frm);
			frm.reload_doc();
		})
	},

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

	onload(frm) {
		frm.trigger("update_primary_action");
		frm.trigger("create_stats");
		//frm.set_df_property("sync_log", "cannot_add_rows", true);
		//frm.set_df_property("sync_log", "cannot_delete_rows", true);
		//frm.set_df_property("sync_log", "allow_bulk_edit", true);
	},

	refresh(frm) {
		if (!frm.is_new()) {
			frm.set_df_property("company_file", "read_only", 1);
		}
		frm.trigger("update_primary_action");
		const labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
		const values = [12, 18, 9, 24];
		frm.trigger("create_stats");
		//frm.fields_dict.sync_log.grid.toggle_checkboxes(false);
	},

	create_stats(frm) {
		const labels = frm.fields_dict.status_log._rows_list;
    	//const values = statusLogs.map(row => row.description || 0); // Aquí 'description' es el valor (o usa otro campo)

		// Crear una función para generar abreviaturas
		const generateAbbreviation = (label) => {
			// Divide el label en palabras y toma la primera letra de cada una
			const words = label.split(' ');
			if (words.length > 1) {
				const abbreviation = words.map(word => word[0].toUpperCase()).join('');
				return abbreviation;
			}
			
			return words[0];
		};

		// Aplicar la función de abreviaturas a los labels
		const abbreviatedLabels = labels.map(label => generateAbbreviation(label));

		const syncLogs = frm.doc.sync_log;

		const values = labels.map(label => {
			// Filtramos los registros de sync_log que tengan el mismo 'status' que el 'label'
			const count = syncLogs.filter(row => row.status === label).length;
			return count;  // Aquí calculamos cuántos registros tienen ese status
		});
		const totalDetected = syncLogs.length;

		const colors = [
			"#000000",  // Negro
			"#5E2A8C",  // Morado intenso
			"#9B4D96",  // Morado oscuro
			"#D5338D",  // Rosado intenso
			"#C81C7A",  // Rosado profundo
			"#800080",  // Morado puro
			"#9B1D40",  // Rosado fuerte
			"#6200EE",  // Morado eléctrico
			"#A8A8A8",  // Gris claro
			"#595959",  // Gris medio oscuro
			"#333333",  // Gris oscuro
			"#B10D3A",  // Rosado vibrante
			"#E40046",  // Rosado brillante
			"#6A0DAD",  // Morado profundo
			"#A44D9C",  // Rosado suave y vibrante
			"#9B30FF",  // Morado eléctrico
			"#990000",  // Rojo intenso (casi negro)
			"#404040",  // Gris muy oscuro
			"#E5A6D1",  // Rosado pálido
			"#6D4C41",  // Gris madera
		];

		frm.call({
			method: "get_count_logs",
			args: { batch_name: frm.docname },
		}).then(r => {
			//const totalUpdated = syncLogs.filter(row => row.status === 'Update').length;
			frm.get_field('stats').$wrapper.empty()
				.append('<div id="total-review" style="font-size: 18px; font-weight: bold; margin-bottom: 10px;">Reviewed: ' + r.message + '</div>')  // Total de registros en sync_log
				.append('<div id="total-detected" style="font-size: 18px; font-weight: bold; margin-bottom: 10px;">Detected: ' + totalDetected + '</div>')  // Total de los valores
				//.append('<div id="total-updated" style="font-size: 18px; font-weight: bold; margin-bottom: 10px;">Updated: ' + totalUpdated + '</div>')  // Total de los valores
				.append('<div id="stats-chart"></div>');  // Luego agregar el gráfico
			
			let index = 0;
			new frappe.Chart("#stats-chart", {
				title: "Total",
				data: {
					labels: labels,
					datasets: [{ values: values }],
				},
				type: 'percentage',
				colors: colors,
				height: 220,
				truncateLegends: 1,  // Truncar leyendas largas si es necesario
				percentageOptions: {
					stacked: 1,
				},
				tooltipOptions: {
					formatTooltipY: (value) => {
						// Mostrar solo la abreviatura, sin el label completo
						if (index == abbreviatedLabels.length) index = 0;
						const abbreviation = abbreviatedLabels[index];
						index += 1;
						return abbreviation + ": " + value;  // Solo muestra la abreviatura y el valor
					},
				},
			});	
		});
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
			frm.toggle_display("section_stats", true);
			frm.toggle_display("status_log", true);
		}
	},


	start_sync(frm) {
		frm.call({
			method: "start_sync",
			args: { company_sync_register: frm.doc.name },
			btn: frm.page.btn_primary
		}).then(r => {
			frm.refresh()
		});
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
}

function successProgressBar(frm) {
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
