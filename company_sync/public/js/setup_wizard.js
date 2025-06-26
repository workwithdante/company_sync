frappe.provide("company_sync.setup");

frappe.pages["setup-wizard"].on_page_load = function (wrapper) {
	if (frappe.sys_defaults.company) {
		frappe.set_route("desk");
		return;
	}
};

frappe.setup.on("before_load", function () {
	if (
		frappe.boot.setup_wizard_completed_apps?.length &&
		frappe.boot.setup_wizard_completed_apps.includes("company_sync")
	) {
		// Ya se completó, no mostrar más
		return;
	}

	company_sync.setup.slides_settings.map(frappe.setup.add_slide);
});

frappe.setup.on("complete", function () {
	// Marcar como completado para company_sync
	frappe.call({
		method: "frappe.desk.page.setup_wizard.setup_wizard.set_setup_completed",
		args: {
			// tu nombre de app aquí
			app: "company_sync",
		},
		callback: function () {
			// marcar localmente en boot para evitar reentrada
			if (!frappe.boot.setup_wizard_completed_apps) {
				frappe.boot.setup_wizard_completed_apps = [];
			}
			frappe.boot.setup_wizard_completed_apps.push("company_sync");

			frappe.set_route("desk");
		},
	});
});


company_sync.setup.slides_settings = [
	{
		name: "Database",
		title: __("Setup your config"),
		icon: "fa fa-building",
		fields: [
			{
				fieldname: "host",
				label: __("Host"),
				fieldtype: "Data",
				reqd: 1,
			},
            {
				fieldname: "port",
				label: __("Port"),
				fieldtype: "Int",
				reqd: 1,
			},
            {
				fieldname: "name_db",
				label: __("Name"),
				fieldtype: "Data",
				reqd: 1,
			},
            {
				fieldname: "user",
				label: __("User DB"),
				fieldtype: "Data",
				reqd: 1,
			},
            {
				fieldname: "password",
				label: __("Password"),
				fieldtype: "Password",
				reqd: 1,
			},
            {
				fieldname: "type",
				label: __("Type"),
				fieldtype: "Select",
				reqd: 1,
			},
            {
				fieldname: "connector",
				label: __("Connector"),
				fieldtype: "Select",
				reqd: 1,
			}
		],

		onload: function (slide) {
            let type_field = slide.get_field("type");
            if(type_field) {
                type_field.df.options = ['', 'MariaDB', 'MySQL', 'Postgresql'].join('\n');
				type_field.refresh();
            }
            
            let conn_field = slide.get_field("connector");
            if(conn_field) {
                conn_field.df.options = ['', 'pymysql', 'psycopg2'].join('\n');
				conn_field.refresh();
            }
            
		},
	},
	{
		name: "API",
		title: __("Setup your config"),
		icon: "fa fa-building",
		fields: [
			{
				fieldname: "endpoint",
				label: __("Endpoint"),
				fieldtype: "Data",
				reqd: 1,
			},
            {
				fieldname: "user_db",
				label: __("User DB"),
				fieldtype: "Data",
				reqd: 1,
			},
            {
				fieldname: "token",
				label: __("Token"),
				fieldtype: "Data",
				reqd: 1,
			},
		],

		onload: function (slide) {
            /* let type_field = slide.get_field("type");
            if(type_field) {
                type_field.df.options = ['', 'MariaDB', 'MySQL'].join('\n');
				type_field.refresh();
            }
            
            let conn_field = slide.get_field("connector");
            if(conn_field) {
                conn_field.df.options = ['', 'pymysql'].join('\n');
				conn_field.refresh();
            } */
		},
	}
]