// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.views.calendar["Issue"] = {
	field_map: {
		"start": "opening_date",
		"end": "due_date",
		"id": "name",
		"title": "subject",
		"status": "status",
	},
	style_map: {
		"Open": "info",
		"Closed": "success",
		"Replied": "info",
		"Hold": "warning"
	},
	get_events_method: "erpnext.support.doctype.issue.issue.get_events"
}