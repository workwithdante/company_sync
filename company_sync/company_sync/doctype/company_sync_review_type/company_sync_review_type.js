frappe.ui.form.on("Company Sync Log Item", "review2", function(frm, cdt, cdn) {
	console.log("Review2 triggered");
});

frappe.ui.form.on('Company Sync Log Item', {
  refresh(frm) {
    // cada vez que se refresca la fila, volvemos a enganchar
    frm.fields_dict.sync_log.grid.wrapper
      .on('change', 'select[data-fieldname="review2"]', () => {
        frm.save();
      });
  }
});
