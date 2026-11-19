USE veterinary_clinic_db;
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'veterinariaApp'@'%';

GRANT SELECT, INSERT, UPDATE, DELETE
	ON veterinary_clinic_db.*
    TO 'veterinariaApp'@'%';
    
    
ALTER TABLE employee_users
	ADD constraint chk_doc_number check (doc_number regexp '^[0-9]{8,10}$');
    
ALTER TABLE owners
	ADD constraint chk_doc_number_owner check (doc_number regexp '^[0-9]{8,10}$'),
    ADD constraint chk_phone check (phone regexp '^[0-9]{10}$');