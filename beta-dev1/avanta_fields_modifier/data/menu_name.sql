UPDATE ir_ui_menu SET name = 'Leads' where id in (SELECT id FROM ir_ui_menu WHERE name = 'Lead');
UPDATE ir_ui_menu SET name = 'Leads' where id in (SELECT id FROM ir_ui_menu WHERE name = 'My Pipeline');
DELETE FROM crm_stage where name in ('Won', 'Proposition', 'Qualified');
DELETE FROM crm_stage where name not in ('Enquiry', 'Allocation', 'Follow up', 'Quotation', 'In Progress', 'Status');