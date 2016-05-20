{% include 'support/support_common.js' %}
cur_frm.add_fetch("location_id","location_name", "location_name")

frappe.ui.form.on_change("Issue", "location_id",function(){
	frappe.call({
		method: "erpnext.utilities.doctype.address.address.get_address_display",
		args: {
			"address_dict": cur_frm.doc.location_id
		},
		callback: function(r) {
			if (r.message)
				cur_frm.set_value("address_display", r.message)
		}
	})
});

frappe.ui.form.on("Issue", {
	"refresh": function(frm) {
		if(frm.doc.status==="Open") {
			frm.add_custom_button("Close", function() {
				frm.set_value("status", "Closed");
				frm.save();
			});
		} else {
			frm.add_custom_button("Reopen", function() {
				frm.set_value("status", "Open");
				frm.save();
			});
		}
	}
});

cur_frm.add_fetch('customer','customer_name','customer_name');
// cur_frm.add_fetch('location_id','customer','customer');
// cur_frm.add_fetch('contact','customer','customer');
// cur_frm.add_fetch('contact','location_id','location_id');
cur_frm.add_fetch('contact','mobile_no','phone');
cur_frm.add_fetch('contact','email_id','raised_by');

cur_frm.cscript.refresh = function(doc, cdt, cdn){
	set_notification_mode(doc.contact)
}

cur_frm.cscript.onload = function(doc, cdt, cdn){
	set_notification_mode(doc.contact)
}

cur_frm.cscript.customer = function(doc, cdt, cdn){
	/*
		clear fields
		set the customer name
	*/

	doc.contact = "";
	doc.location_id = "";
	doc.raised_by = "";
	doc.phone = "";
	doc.contact_name = "";

	cur_frm.refresh_fields();
}

cur_frm.cscript.contact = function(doc, cdt, cdn){
	// get notification mode and set the checkbox
	set_notification_mode(doc.contact);
}

cur_frm.cscript.status = function(doc, cdt, cdn){
	if(doc.status == "Closed"){
		cur_frm.set_df_property("resolution_details","reqd",1)
	}
	else{
		cur_frm.set_df_property("resolution_details","reqd",0)
	}
}

cur_frm.fields_dict['location_id'].get_query = function(doc, cdt, cdn) {
	return {
		filters:{ 'customer': doc.customer }
	}
}

cur_frm.fields_dict['contact'].get_query = function(doc, cdt, cdn) {
	return {
		filters:{
			// 'location_id': doc.location_id,
			'customer': doc.customer
		}
	}
}
