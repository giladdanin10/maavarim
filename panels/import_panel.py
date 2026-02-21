"""Import Panel for uploading different file types."""

import panel as pn
import pandas as pd
from pathlib import Path
import db

pn.extension('tabulator')

# File type options with their keys
FILE_TYPES = {
    "conference_participants": "משתתפים בכנס יזמות",
    "conference_registrations": "נרשמים לכנס יזמות",
    "meetings_business": "פגישות ליווי עם בעלי עסקים",
    "meetings_employees": "פגישות ליווי עם שכירים",
}

# Column mapping for conference participants file
CONFERENCE_PARTICIPANTS_COLUMNS = {
    'שם': 'first_name',
    'שם משפחה': 'last_name',
    'דואר אלקטרוני': 'email',
    'מספר SMS': 'phone',
    'מקום מגורים': 'residence',
    'תפקיד': 'role',
    'יישוב (מקום העבודה)': 'work_location'
}

def create_import_panel():
    """Create the file import panel with RTL layout."""

    # Store loaded data for saving
    loaded_data = {"df": None, "file_type_key": None, "event_name": None}

    # --- Widgets ---
    event_name_input = pn.widgets.TextInput(
        name="שם אירוע",
        placeholder="הכנס שם אירוע...",
        width=250,
        styles={"direction": "rtl"}
    )

    file_type_select = pn.widgets.Select(
        name="סוג קובץ",
        options=[""] + list(FILE_TYPES.values()),
        value="",
        width=250,
        disabled=True,
        styles={"direction": "rtl"}
    )

    # File input container - will hold a dynamically created FileInput
    file_input_container = pn.Column(visible=False)

    save_button = pn.widgets.Button(
        name="שמור לבסיס הנתונים",
        button_type="primary",
        width=200,
        disabled=True,
        visible=False,
        styles={"direction": "rtl"}
    )

    # Status and preview
    status_message = pn.pane.Alert("הכנס שם אירוע", alert_type="info", styles={"direction": "rtl"})
    preview_table = pn.widgets.Tabulator(
        pd.DataFrame(),
        visible=False,
        layout='fit_columns',
        pagination='local',
        page_size=10,
        sizing_mode='stretch_width',
        height=300
    )

    # --- Helper functions ---
    def check_enable_file_input():
        """Check if file input should be enabled based on file type and event name."""
        if file_type_select.value and file_type_select.value != "" and event_name_input.value.strip():
            file_input_container.visible = True
            loaded_data["event_name"] = event_name_input.value.strip()
            status_message.object = f"נבחר: {file_type_select.value}, אירוע: {event_name_input.value.strip()}. העלה קובץ."
            status_message.alert_type = "info"
        else:
            file_input_container.visible = False
            save_button.visible = False
            preview_table.visible = False

    def get_file_type_key(display_name):
        """Get the key for a file type given its display name."""
        for key, value in FILE_TYPES.items():
            if value == display_name:
                return key
        return None

    def process_conference_participants(df):
        """Process conference participants file and save to people table."""
        people_data = []
        for _, row in df.iterrows():
            person = {}
            for col_heb, col_eng in CONFERENCE_PARTICIPANTS_COLUMNS.items():
                if col_heb in df.columns:
                    value = row[col_heb]
                    # Convert to string and handle NaN
                    if pd.notna(value):
                        person[col_eng] = str(value).strip()
                    else:
                        person[col_eng] = None
            if person.get('first_name') or person.get('last_name'):
                people_data.append(person)
        return people_data

    # --- Callbacks ---
    def on_file_type_change(event):
        """Show file upload when file type is selected."""
        if file_type_select.value and file_type_select.value != "":
            save_button.visible = False
            save_button.disabled = True
            loaded_data["df"] = None
            loaded_data["file_type_key"] = get_file_type_key(file_type_select.value)
            check_enable_file_input()
        else:
            file_input_container.visible = False
            save_button.visible = False
            preview_table.visible = False
            status_message.object = f"אירוע: {event_name_input.value.strip()}. בחר סוג קובץ."
            status_message.alert_type = "info"

    def on_event_name_change(event):
        """Enable file type selection when event name is entered."""
        if event_name_input.value.strip():
            file_type_select.disabled = False
            loaded_data["event_name"] = event_name_input.value.strip()
            if not file_type_select.value:
                status_message.object = f"אירוע: {event_name_input.value.strip()}. בחר סוג קובץ."
                status_message.alert_type = "info"
            else:
                check_enable_file_input()
        else:
            file_type_select.disabled = True
            file_type_select.value = ""
            file_input_container.visible = False
            save_button.visible = False
            preview_table.visible = False
            status_message.object = "הכנס שם אירוע"
            status_message.alert_type = "info"

    def on_file_upload(event):
        """Handle file upload and preview."""
        file_input = file_input_container[0]
        if file_input.value is None or file_input.value == b'':
            return

        try:
            filename = file_input.filename
            file_bytes = file_input.value

            # Read file based on extension
            if filename.endswith('.csv'):
                df = pd.read_csv(pd.io.common.BytesIO(file_bytes))
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(pd.io.common.BytesIO(file_bytes))
            else:
                status_message.object = "סוג קובץ לא נתמך. נא להעלות CSV או Excel."
                status_message.alert_type = "danger"
                return

            # Store loaded data
            loaded_data["df"] = df

            # Show preview
            preview_table.value = df.head(20)
            preview_table.visible = True
            save_button.visible = True
            save_button.disabled = False
            status_message.object = f"הקובץ '{filename}' נטען בהצלחה! ({len(df)} שורות). לחץ 'שמור' להכניס לבסיס הנתונים."
            status_message.alert_type = "success"

        except Exception as e:
            status_message.object = f"שגיאה בטעינת הקובץ: {str(e)}"
            status_message.alert_type = "danger"
            preview_table.visible = False
            save_button.visible = False

    def create_file_input():
        """Create a fresh FileInput widget."""
        fi = pn.widgets.FileInput(
            accept=".csv,.xlsx,.xls",
            multiple=False,
            styles={"direction": "rtl"}
        )
        fi.param.watch(on_file_upload, 'value')
        return fi
    
    # Initial file input
    file_input_container.append(create_file_input())

    def on_save_click(event):
        """Save loaded data to database."""
        df = loaded_data.get("df")
        file_type_key = loaded_data.get("file_type_key")

        if df is None:
            status_message.object = "אין נתונים לשמירה"
            status_message.alert_type = "danger"
            return

        try:
            if file_type_key == "conference_participants":
                # Process and save conference participants as employees
                employees_data = process_conference_participants(df)
                event_name = loaded_data.get("event_name", "")
                if employees_data:
                    # Add/update employees with event name
                    count = db.add_employees_bulk(employees_data, event_name=event_name)
                    total = db.get_employees_count()
                    status_message.object = f"עובדו {count} עובדים לאירוע '{event_name}' בהצלחה! (סה\"כ בטבלה: {total})"
                    status_message.alert_type = "success"
                else:
                    status_message.object = "לא נמצאו נתונים תקינים בקובץ"
                    status_message.alert_type = "warning"
            else:
                status_message.object = f"סוג קובץ '{file_type_key}' עדיין לא נתמך"
                status_message.alert_type = "warning"

            # Reset for next upload
            save_button.disabled = True
            save_button.visible = False
            preview_table.visible = False
            loaded_data["df"] = None
            # Replace file input with a fresh one to reset browser state
            file_input_container.clear()
            file_input_container.append(create_file_input())
            file_input_container.visible = True
            status_message.object += " - ניתן להעלות קובץ נוסף."

        except Exception as e:
            status_message.object = f"שגיאה בשמירה: {str(e)}"
            status_message.alert_type = "danger"

    # Bind callbacks
    file_type_select.param.watch(on_file_type_change, 'value')
    event_name_input.param.watch(on_event_name_change, 'value')
    save_button.on_click(on_save_click)

    # --- Layout ---
    panel = pn.Column(
        pn.pane.Markdown("# הכנסת קבצים", styles={"direction": "rtl"}),
        pn.layout.Divider(),
        pn.pane.Markdown("### שם אירוע:", styles={"direction": "rtl"}),
        event_name_input,
        pn.layout.Spacer(height=10),
        pn.pane.Markdown("### סוג קובץ:", styles={"direction": "rtl"}),
        file_type_select,
        pn.layout.Spacer(height=10),
        file_input_container,
        pn.layout.Spacer(height=10),
        save_button,
        status_message,
        pn.layout.Divider(),
        pn.pane.Markdown("### תצוגה מקדימה:", styles={"direction": "rtl"}, visible=True),
        preview_table,
        sizing_mode='stretch_width',
        styles={"direction": "rtl", "background-color": "#f5f5f5"}
    )

    return panel

if __name__ == "__main__":
    pn.serve(create_import_panel, port=5007, show=True)
