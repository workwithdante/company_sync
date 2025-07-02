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

	status_log(frm) {
		// Se dispara cuando cambian los tags
	},

	onload(frm) {
		frm.trigger("update_primary_action");
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
			const abbreviation = words.map(word => word[0].toUpperCase()).join('');
			return abbreviation;
		};

		// Aplicar la función de abreviaturas a los labels
		const abbreviatedLabels = labels.map(label => generateAbbreviation(label));

		const originalLabels = labels

		const syncLogs = frm.doc.sync_log;

		const values = labels.map(label => {
			// Filtramos los registros de sync_log que tengan el mismo 'status' que el 'label'
			const count = syncLogs.filter(row => row.status === label).length;
			return count;  // Aquí calculamos cuántos registros tienen ese status
		});
		const totalValues = frm.doc.sync_log.length;

		const totalSyncLog = frappe.get_doc("Company Sync Register", frm.doc_name).get_count()

		frm.get_field('stats').$wrapper.empty()
			.append('<div id="total-stats" style="font-size: 18px; font-weight: bold; margin-bottom: 10px;">Reviewed: ' + totalSyncLog + '</div>')  // Total de registros en sync_log
			.append('<div id="total-values" style="font-size: 18px; font-weight: bold; margin-bottom: 10px;">Detected: ' + totalValues + '</div>')  // Total de los valores
			.append('<div id="stats-chart"></div>');  // Luego agregar el gráfico

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

		// Instancia un chart en el div#stats-chart
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
			tooltipOptions: {
				formatTooltipY: (value) => {
					// Mostrar solo la abreviatura, sin el label completo
					const abbreviation = generateAbbreviation(originalLabels[values.indexOf(value)]);
					return abbreviation + ": " + value;  // Solo muestra la abreviatura y el valor
				},
			},
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
