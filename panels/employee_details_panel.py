"""Employee Details Panel for viewing specific employee data."""

import panel as pn
import pandas as pd
import db

pn.extension('tabulator')


def create_employee_details_panel():
    """Create the employee details panel with RTL layout."""

    # --- Widgets ---
    search_input = pn.widgets.TextInput(
        name="חיפוש עובד",
        placeholder="הקלד שם או אימייל...",
        width=300,
        styles={"direction": "rtl"}
    )

    employee_select = pn.widgets.Select(
        name="בחר עובד",
        options={},
        width=400,
        styles={"direction": "rtl"}
    )

    # Employee details display
    details_container = pn.Column(visible=False)
    
    # Events table
    events_table = pn.widgets.Tabulator(
        pd.DataFrame(columns=["אירוע"]),
        visible=False,
        layout='fit_columns',
        sizing_mode='stretch_width',
        height=200,
        text_align='right',
        header_align='right'
    )

    status_message = pn.pane.Alert("חפש עובד או בחר מהרשימה", alert_type="info", styles={"direction": "rtl"})

    # --- Helper functions ---
    def get_employees_for_select():
        """Get all employees formatted for select widget."""
        employees = db.get_all_employees()
        options = {}
        for emp in employees:
            display_name = f"{emp['first_name']} {emp['last_name']}"
            if emp.get('email'):
                display_name += f" ({emp['email']})"
            options[display_name] = emp['id']
        return options

    def filter_employees(search_text):
        """Filter employees by search text."""
        employees = db.get_all_employees()
        search_lower = search_text.lower().strip()
        options = {}
        for emp in employees:
            full_name = f"{emp['first_name']} {emp['last_name']}".lower()
            email = (emp.get('email') or '').lower()
            if search_lower in full_name or search_lower in email:
                display_name = f"{emp['first_name']} {emp['last_name']}"
                if emp.get('email'):
                    display_name += f" ({emp['email']})"
                options[display_name] = emp['id']
        return options

    def display_employee_details(employee_id):
        """Display details for a specific employee."""
        employees = db.get_all_employees()
        employee = None
        for emp in employees:
            if emp['id'] == employee_id:
                employee = emp
                break
        
        if not employee:
            status_message.object = "עובד לא נמצא"
            status_message.alert_type = "danger"
            details_container.visible = False
            events_table.visible = False
            return

        # Build details display
        details_container.clear()
        
        # Employee info cards
        info_items = [
            ("שם פרטי", employee.get('first_name', '')),
            ("שם משפחה", employee.get('last_name', '')),
            ("דואר אלקטרוני", employee.get('email', '') or '-'),
            ("טלפון", employee.get('phone', '') or '-'),
            ("מקום מגורים", employee.get('residence', '') or '-'),
            ("תפקיד", employee.get('role', '') or '-'),
            ("מקום עבודה", employee.get('work_location', '') or '-'),
        ]

        info_html = "<div style='direction: rtl; text-align: right;'>"
        info_html += "<table style='width: 100%; border-collapse: collapse;'>"
        for label, value in info_items:
            info_html += f"""
            <tr style='border-bottom: 1px solid #ddd;'>
                <td style='padding: 8px; font-weight: bold; width: 150px;'>{label}:</td>
                <td style='padding: 8px;'>{value}</td>
            </tr>
            """
        info_html += "</table></div>"
        
        details_container.append(pn.pane.HTML(info_html, sizing_mode='stretch_width'))
        details_container.visible = True

        # Events as separate rows
        events_str = employee.get('registered_events', '')
        if events_str:
            events_list = [e.strip() for e in events_str.split(',') if e.strip()]
            events_df = pd.DataFrame({"אירוע": events_list})
        else:
            events_df = pd.DataFrame({"אירוע": ["אין אירועים רשומים"]})
        
        events_table.value = events_df
        events_table.visible = True

        status_message.object = f"מציג פרטי עובד: {employee['first_name']} {employee['last_name']}"
        status_message.alert_type = "success"

    # --- Callbacks ---
    def on_search_change(event):
        """Filter employees based on search text."""
        search_text = search_input.value
        if search_text and len(search_text) >= 2:
            options = filter_employees(search_text)
            employee_select.options = options
            if options:
                status_message.object = f"נמצאו {len(options)} עובדים"
                status_message.alert_type = "info"
            else:
                status_message.object = "לא נמצאו עובדים מתאימים"
                status_message.alert_type = "warning"
        else:
            employee_select.options = get_employees_for_select()
            status_message.object = "חפש עובד או בחר מהרשימה"
            status_message.alert_type = "info"

    def on_employee_select(event):
        """Display selected employee details."""
        if employee_select.value:
            display_employee_details(employee_select.value)

    # Bind callbacks
    search_input.param.watch(on_search_change, 'value')
    employee_select.param.watch(on_employee_select, 'value')

    # Initialize employee list
    employee_select.options = get_employees_for_select()

    # --- Layout ---
    panel = pn.Column(
        pn.pane.Markdown("# פרטי עובד", styles={"direction": "rtl"}),
        pn.layout.Divider(),
        pn.Row(
            pn.Column(
                pn.pane.Markdown("### חיפוש:", styles={"direction": "rtl"}),
                search_input,
            ),
            pn.Column(
                pn.pane.Markdown("### בחירה:", styles={"direction": "rtl"}),
                employee_select,
            ),
            styles={"direction": "rtl"}
        ),
        pn.layout.Spacer(height=10),
        status_message,
        pn.layout.Divider(),
        pn.pane.Markdown("### פרטי העובד:", styles={"direction": "rtl"}),
        details_container,
        pn.layout.Spacer(height=20),
        pn.pane.Markdown("### אירועים רשומים:", styles={"direction": "rtl"}),
        events_table,
        sizing_mode='stretch_width',
        styles={"direction": "rtl", "background-color": "#f5f5f5"}
    )

    return panel


if __name__ == "__main__":
    pn.serve(create_employee_details_panel, port=5008, show=True)
