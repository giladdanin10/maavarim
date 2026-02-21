"""Updated Services Panel with RTL layout and improved UI structure."""

import panel as pn
import pandas as pd
import db

pn.extension('tabulator')

def get_services_df():
    services = db.get_all_services()
    if services:
        return pd.DataFrame(services)
    return pd.DataFrame(columns=["id", "name", "domain"])

def create_services_panel():
    """Create the services management panel with RTL layout."""

    # --- Widgets ---
    # Input fields
    service_input = pn.widgets.TextInput(
        name="שירות",
        placeholder="הכנס שירות...",
        align="end",
        width=200,
        styles={"direction": "rtl"}
    )

    domain_input = pn.widgets.TextInput(
        name="תחום",
        placeholder="הכנס תחום...",
        align="end",
        width=200,
        styles={"direction": "rtl"}
    )

    # Buttons
    add_button = pn.widgets.Button(
        name="הכנסת שירות",
        button_type="success",
        width=150,
        styles={"direction": "rtl"}
    )

    delete_button = pn.widgets.Button(
        name="מחיקת שירות",
        button_type="danger",
        width=150,
        styles={"direction": "rtl"}
    )

    # Table
    services_table = pn.widgets.Tabulator(
        get_services_df(),
        layout='fit_columns',
        selectable='checkbox',
        pagination='local',
        page_size=15,
        sizing_mode='stretch_width',
        height=400,
        titles={
            'id': 'מזהה',
            'name': 'שירות',
            'domain': 'תחום'
        },
        widths={
            'index': 50,
            'name': 200,
            'domain': 200
        },
        text_align={
            'index': 'center',
            'name': 'right',
            'domain': 'right'
        },
        header_align={
            'index': 'center',
            'name': 'right',
            'domain': 'right'
        },
        hidden_columns=['id'],
        show_index=True
    )

    # Status message
    status_message = pn.pane.Alert("", alert_type="light", visible=False)

    # --- Callbacks ---
    def show_message(text, msg_type="success"):
        """Show a status message."""
        status_message.object = text
        status_message.alert_type = msg_type
        status_message.visible = True

    def refresh_table():
        """Refresh the services table with latest data."""
        new_df = get_services_df()
        services_table.value = new_df
        services_table.selection = []

    def add_service_click(event):
        service = service_input.value.strip()
        domain = domain_input.value.strip()

        if not service or not domain:
            show_message("יש למלא שירות ותחום", "danger")
            return

        if db.add_service(service, domain):
            show_message(f"השירות '{service}' נוסף בהצלחה", "success")
            service_input.value = ""
            domain_input.value = ""
            refresh_table()
        else:
            show_message(f"שירות בשם '{service}' כבר קיים", "warning")

    def delete_selected_click(event):
        selected = services_table.selection
        if not selected:
            show_message("יש לבחור שירותים למחיקה", "danger")
            return

        for idx in selected:
            service_id = services_table.value.iloc[idx]['id']
            db.delete_service(service_id)

        show_message(f"נמחקו {len(selected)} שירותים", "success")
        refresh_table()

    # Bind callbacks
    add_button.on_click(add_service_click)
    delete_button.on_click(delete_selected_click)

    # --- Layout ---
    input_row = pn.Row(
        pn.Column(
            pn.pane.Markdown("### תחום", styles={"direction": "rtl"}),
            domain_input,
            align="end",
            margin=(0, 10, 0, 10)
        ),
        pn.Column(
            pn.pane.Markdown("### שירות", styles={"direction": "rtl"}),
            service_input,
            align="end",
            margin=(0, 10, 0, 10)
        ),
        pn.Column(
            pn.pane.Markdown("### פעולות", styles={"direction": "rtl"}),
            pn.Column(add_button, delete_button, sizing_mode="stretch_width"),
            align="end",
            margin=(0, 10, 0, 10)
        ),
        align="center",
        styles={"direction": "rtl"}
    )

    panel = pn.Column(
        pn.pane.Markdown("# ניהול שירותים", styles={"direction": "rtl"}),
        pn.layout.Divider(),
        input_row,
        status_message,
        pn.layout.Divider(),
        services_table,
        sizing_mode='stretch_width',
        styles={"direction": "rtl", "background-color": "#f5f5f5"}
    )

    return panel

if __name__ == "__main__":
    pn.serve(create_services_panel, port=5007, show=True)
