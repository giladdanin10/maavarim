"""Main entry point for the Maavarim app."""

import panel as pn
import socket
from panels.services_panel import create_services_panel
from panels.import_panel import create_import_panel
from panels.db_viewer_panel import create_db_viewer_panel
from panels.employee_details_panel import create_employee_details_panel

pn.extension('tabulator')

def find_free_port():
    """Find a free port by letting the OS assign one."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

# Create the main app with tabs
def create_app():
    """Create the main application with all panels."""
    
    tabs = pn.Tabs(
        ("ניהול שירותים", create_services_panel()),
        ("הכנסת קבצים", create_import_panel()),
        ("צפייה בנתונים", create_db_viewer_panel()),
        ("פרטי עובד", create_employee_details_panel()),
        # Future panels will be added here:
        # ("שאילתות", create_queries_panel()),
        # ("גרפים", create_graphs_panel()),
        tabs_location='above',
        sizing_mode='stretch_width',
        active=1  # Default to "הכנסת קבצים" tab
    )
    
    template = pn.template.FastListTemplate(
        title="מערכת מעברים",
        main=[tabs],
        header_background="#2c3e50",
        accent_base_color="#3498db",
    )
    
    return template


if __name__ == "__main__":
    port = find_free_port()
    print(f"Starting app on port {port}")
    pn.serve(create_app, port=port, show=True)
