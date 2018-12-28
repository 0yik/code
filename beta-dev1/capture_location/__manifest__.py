# -*- coding: utf-8 -*-
{
    'name': "capture_location",


    'description': """
        Create a new function called "Sign In" in Sales , next to Invoicing. Sign In will have a dropdown of 2 functions:
Sign In, and History

Sign In:
- In Sign In, it will show all the meetings you have in a Kanban view, showing:
Meeting Subject, Location, Start Time, End Time, Sign in button
- When the sign in button is clicked, it will capture the GPS location, the date and time and the user's name.
- After clicking sign in, the button changes to "Sign Out", when clicked, it will capture the GPS location, date and time and the user's name. And there will be a popup to enter the Meeting Summary (they can leave empty as well).
- In the meeting form view, there is a new tab called "Sign In History", which is a list view the name, date time sign in and out, GPS location, and meeting summary written by the user.
- The default filter for this kanban view is to show today's meetings related to the user
- There is also a create button in this Kanban view, which allows them to create Ad Hoc Meeting and sign in.

History:
- Shows a list view of all the Sign in history, showing the name, date time sign in, date time sign out , and GPS location and the meeting summary
- For Sales User, they only see their history, for Sales Manager, they can see everyone's sign in history

    """,

    'author': "HashMicro/Sang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale',
        'sales_team',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sign_in_history.xml',
        'views/sign_in_view.xml',
        'views/menu.xml',
        'views/template.xml',
        'security/sign_in_history_access.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}