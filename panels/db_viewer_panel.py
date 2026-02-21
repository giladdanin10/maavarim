"""Database Viewer Panel for viewing table contents."""

import panel as pn
import pandas as pd
import db

pn.extension('tabulator')

def create_db_viewer_panel():
    """Create the database viewer panel with RTL layout."""

    # --- Widgets ---
    table_select = pn.widgets.RadioButtonGroup(
        name="בחר טבלה",
        options=["עובדים", "שירותים", "אירועים"],
        button_type="primary",
        value="עובדים",
        styles={"direction": "rtl"}
    )

    refresh_button = pn.widgets.Button(
        name="רענן נתונים",
        button_type="success",
        width=150,
        styles={"direction": "rtl"}
    )

    clear_button = pn.widgets.Button(
        name="מחק טבלה",
        button_type="danger",
        width=150,
        styles={"direction": "rtl"}
    )

    auto_refresh_toggle = pn.widgets.Toggle(
        name="רענון אוטומטי",
        value=True,
        button_type="default",
        width=150,
        styles={"direction": "rtl"}
    )

    # Status and table
    status_message = pn.pane.Alert("", alert_type="info", visible=False, styles={"direction": "rtl"})
    
    data_table = pn.widgets.Tabulator(
        pd.DataFrame(),
        layout='fit_columns',
        pagination='local',
        page_size=20,
        sizing_mode='stretch_width',
        height=500,
        text_align='right',
        header_align='right'
    )

    # Column titles mapping
    EMPLOYEE_TITLES = {
        'id': 'מזהה',
        'first_name': 'שם פרטי',
        'last_name': 'שם משפחה',
        'email': 'דואר אלקטרוני',
        'phone': 'טלפון',
        'residence': 'מקום מגורים',
        'role': 'תפקיד',
        'work_location': 'מקום עבודה',
        'registered_events': 'אירועים רשומים'
    }

    SERVICE_TITLES = {
        'id': 'מזהה',
        'name': 'שירות',
        'domain': 'תחום'
    }

    EVENT_TITLES = {
        'id': 'מזהה',
        'name': 'שם אירוע',
        'date': 'תאריך'
    }

    # --- Callbacks ---
    def load_data(table_name=None):
        """Load data from the selected table."""
        if table_name is None:
            table_name = table_select.value

        try:
            if table_name == "עובדים":
                data = db.get_all_employees()
                if data:
                    df = pd.DataFrame(data)
                    data_table.titles = EMPLOYEE_TITLES
                else:
                    df = pd.DataFrame(columns=list(EMPLOYEE_TITLES.keys()))
                    data_table.titles = EMPLOYEE_TITLES
            elif table_name == "שירותים":
                data = db.get_all_services()
                if data:
                    df = pd.DataFrame(data)
                    data_table.titles = SERVICE_TITLES
                else:
                    df = pd.DataFrame(columns=list(SERVICE_TITLES.keys()))
                    data_table.titles = SERVICE_TITLES
            else:  # אירועים
                data = db.get_all_events()
                if data:
                    df = pd.DataFrame(data)
                    data_table.titles = EVENT_TITLES
                else:
                    df = pd.DataFrame(columns=list(EVENT_TITLES.keys()))
                    data_table.titles = EVENT_TITLES

            data_table.value = df
            count = len(df)
            status_message.object = f"נטענו {count} רשומות מטבלת {table_name}"
            status_message.alert_type = "success"
            status_message.visible = True

        except Exception as e:
            status_message.object = f"שגיאה בטעינת הנתונים: {str(e)}"
            status_message.alert_type = "danger"
            status_message.visible = True

    def on_table_change(event):
        """Handle table selection change."""
        load_data(event.new)

    def on_refresh_click(event):
        """Handle refresh button click."""
        load_data()

    def on_clear_click(event):
        """Handle clear table button click."""
        table_name = table_select.value
        try:
            if table_name == "עובדים":
                db.clear_employees_table()
                status_message.object = "טבלת העובדים נמחקה בהצלחה"
            elif table_name == "שירותים":
                db.clear_services_table()
                status_message.object = "טבלת השירותים נמחקה בהצלחה"
            else:  # אירועים
                db.clear_events_table()
                status_message.object = "טבלת האירועים נמחקה בהצלחה"
            status_message.alert_type = "warning"
            status_message.visible = True
            load_data()
        except Exception as e:
            status_message.object = f"שגיאה במחיקת הטבלה: {str(e)}"
            status_message.alert_type = "danger"
            status_message.visible = True

    def auto_refresh():
        """Auto refresh callback."""
        if auto_refresh_toggle.value:
            load_data()

    # Bind callbacks
    table_select.param.watch(on_table_change, 'value')
    refresh_button.on_click(on_refresh_click)
    clear_button.on_click(on_clear_click)

    # Add periodic auto-refresh (every 3 seconds)
    pn.state.add_periodic_callback(auto_refresh, period=3000)

    # Load initial data
    load_data()

    # --- Layout ---
    panel = pn.Column(
        pn.pane.Markdown("# צפייה בבסיס הנתונים", styles={"direction": "rtl"}),
        pn.layout.Divider(),
        pn.Row(
            pn.pane.Markdown("### בחר טבלה:", styles={"direction": "rtl"}),
            table_select,
            refresh_button,
            clear_button,
            auto_refresh_toggle,
            align="center",
            styles={"direction": "rtl"}
        ),
        pn.layout.Spacer(height=10),
        status_message,
        pn.layout.Divider(),
        data_table,
        sizing_mode='stretch_width',
        styles={"direction": "rtl", "background-color": "#f5f5f5"}
    )

    return panel

if __name__ == "__main__":
    pn.serve(create_db_viewer_panel, port=5007, show=True)
