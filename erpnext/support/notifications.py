import frappe
from datetime import datetime, timedelta

def new_support_queue_notification(doc, method):
    "email notification once a support ticket is assigned to the executor"
    user = doc.owner
    user_details = frappe.db.get_value("User", doc.owner, ["email", "first_name", "middle_name", "last_name"])
    if user_details:
        args = {
            "email": user_details[0],
            "full_name": " ".join([txt for txt in user_details[1:] if txt]),
            "subject": "Support Ticket is assigned to you",
            "title": "Support Ticket updates",
            "msg": "Please note a new Support Ticket '{0} - {1}' has been assigned to you.<br>Please review the ticket and update.".format(doc.reference_name, doc.description)
        }
        send_mail(args)

def notify_user_about_due_issues():
    "email notification sent to the executor 24 hrs prior to the due date"
    from datetime import datetime, timedelta

    today = frappe.utils.now_datetime().date()
    due_date = today + timedelta(days=1)
    due_date = due_date.strftime("%Y-%m-%d")
    issues = frappe.db.get_values("Issue", {"due_date":due_date, "status":"Open"}, "name", debug=True)
    if issues:
        users = {}
        names = ["'%s'"%issue[0] for issue in issues]
        query = """ SELECT owner, reference_name FROM `tabToDo`
                    WHERE reference_name in (%s) AND reference_type='Issue'
                    AND status='Open'"""%(",".join(names))
        results = frappe.db.sql(query, as_list=True)
        # [users.update({r[0]:users.get(r[0]).append(r[1]) if users.get(r[0]) else r[1:]}) for r in result]
        for result in results:
            issue = users.get(result[0]) if users.get(result[0]) else []
            issue.append(result[1])
            users.update({result[0]:issue})

        for user, issues in users.iteritems():
            user_details = frappe.db.get_value("User", user, ["email", "first_name", "middle_name", "last_name"])
            if user_details:
                args = {
                    "email": user_details[0],
                    "full_name": " ".join([txt for txt in user_details[1:] if txt]),
                    "subject": "Support Tickets are due",
                    "title": "Support Ticket updates",
                    "msg": "Support Ticket(s) %s %s due on %s.<br>Please address and close the ticket."%(",".join(issues),"is" if len(issues)==1 else "are", due_date)
                }
                send_mail(args)

def notify_user_about_past_due_issues():
    "email notification sent to the assignee everyday post the due date untill it is closed"
    from datetime import datetime, timedelta

    today = frappe.utils.now_datetime().date()
    query = """ SELECT DISTINCT name FROM `tabIssue` WHERE status='Open'
                AND due_date > '%s'"""%(today)
    issues = frappe.db.sql(query, as_list=True)

    if issues:
        users = {}
        names = ["'%s'"%issue[0] for issue in issues]
        query = """ SELECT owner, reference_name FROM `tabToDo`
                    WHERE reference_name in (%s) AND reference_type='Issue'
                    AND status='Open'"""%(",".join(names))
        results = frappe.db.sql(query, as_list=True)
        for result in results:
            issue = users.get(result[0]) if users.get(result[0]) else []
            issue.append(result[1])
            users.update({result[0]:issue})

        for user, issues in users.iteritems():
            user_details = frappe.db.get_value("User", user, ["email", "first_name", "middle_name", "last_name"])
            if user_details:
                args = {
                    "email": user_details[0],
                    "full_name": " ".join([txt for txt in user_details[1:] if txt]),
                    "subject": "Past due date Support Tickets",
                    "title": "Support Ticket updates",
                    "msg": "Following support ticket has extended its due date<br>%s<br>Please address the issue and close the ticket."%(get_issue_due_dates_table(issues))
                }
                send_mail(args)

def get_issue_due_dates_table(issues):
    table = "<table width='85%'>"
    table += "<thead><tr><td>Support Ticket</td><td>Due Date</td></tr></thead>"
    table += "<tbody align='center'>"
    for issue in issues:
        table += "<tr><td>%s</td><td>%s</td></tr>"%(issue,frappe.db.get_value("Issue",issue,"due_date"))
    table += "</tbody></table>"
    return table

def notify_customer_about_open_issues():
    "email notification to the customer everyday, untill the ticket is assigned to anyone."
    from datetime import datetime, timedelta

    today = frappe.utils.now_datetime().date()
    query = """ SELECT DISTINCT name, raised_by FROM `tabIssue` WHERE status='Open'
                AND opening_date < '%s'"""%(today)
    issues = frappe.db.sql(query, as_list=True)
    if issues:
        cust_details = {}
        for issue in issues:
            email = issue[1]
            dn = [] if not cust_details.get(email) else cust_details.get(email)
            dn.append(issue[0])
            cust_details.update({email:dn})

        for email, doc_names in cust_details.iteritems():
            args = {
                "email": email,
                "full_name": "Customer",
                "subject": "Telecom Advocate Support Ticket Updates",
                "title": "Telecom Advocate Support Ticket Updates",
                "msg": "Support Ticket%s %s %s created against the issue reported by you.<br>You will hear from us soon."%(
                            "s" if len(doc_names) > 1 else "",
                            ",".join(doc_names),
                            "are" if len(doc_names) > 1 else "is"
                        )
            }
            send_mail(args)

def notify_user_about_closed_ticket(doc, method):
    if not doc.is_billing_mail_sent and doc.status == "Closed" and doc.billing_status == "Not Completed":
        doc.billing_status = "Billing"
        args = {
            "email": doc.raised_by,
            "full_name": doc.customer_name or "Customer",
            "subject": "Support Ticket is resolved and closed",
            "title": "Support Ticket updates",
            "msg": "Your Support ticket '{0} - {1}' is resolved and closed.<br>Kindly process the billing.".format(doc.name, doc.subject)
        }
        send_mail(args)
    else:
        pass

def send_mail(args):
    """send mail to user"""
    from frappe.utils.user import get_user_fullname
    from frappe.utils import get_url
    try:
        sender = None
        template = "templates/emails/notification_template.html"
        frappe.sendmail(recipients=args.get("email"), sender=sender, subject=args.get("subject"),
            message=frappe.get_template(template).render(args))
        return True
    except Exception, e:
        import traceback
        print "notify", traceback.format_exc()
        return False
