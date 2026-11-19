-- ============================================================================
-- VETERINARY CLINIC DATABASE SCHEMATICS (OPTIMIZED 3NF - CATALOG TABLES)
-- ============================================================================

DROP DATABASE IF EXISTS veterinary_clinic_db;
CREATE DATABASE veterinary_clinic_db
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE veterinary_clinic_db;

-- ============================================================================
-- PHASE 0: Master Catalog / Lookup Tables (Replaces ENUM types)
-- Description: Normalized reference tables using TINYINT UNSIGNED (1 byte)
--              for optimal InnoDB index performance and referential integrity.
-- ============================================================================

-- Catalog 1: Document Types (Shared by owners and employee_users)
CREATE TABLE document_types (
    doc_type_id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(15) NOT NULL UNIQUE,
    description VARCHAR(60) NOT NULL
) ENGINE=InnoDB;

-- Catalog 2: System User Roles
CREATE TABLE user_roles (
    role_id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(40) NOT NULL UNIQUE,
    description VARCHAR(120) NULL
) ENGINE=InnoDB;

-- Catalog 3: Clinical Service Types
CREATE TABLE service_types (
    service_type_id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(120) NULL
) ENGINE=InnoDB;

-- Catalog 4: Room Types
CREATE TABLE room_types (
    room_type_id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(30) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Catalog 5: Room Operational Statuses
CREATE TABLE room_statuses (
    room_status_id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(30) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Catalog 6: Pet Species
CREATE TABLE species (
    species_id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(40) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Catalog 7: Veterinary Specialties
CREATE TABLE specialties (
    specialty_id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(60) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Catalog 8: Appointment Types (Shared by schedules and appointments)
CREATE TABLE appointment_types (
    appointment_type_id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(40) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Catalog 9: Schedule Slot Statuses
CREATE TABLE schedule_statuses (
    schedule_status_id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(30) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Catalog 10: Appointment Workflow Statuses
CREATE TABLE appointment_statuses (
    appointment_status_id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(30) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Catalog 11: Vaccine Catalog
CREATE TABLE vaccine_catalog (
    vaccine_catalog_id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(60) NOT NULL UNIQUE,
    description VARCHAR(120) NULL
) ENGINE=InnoDB;

-- Catalog 12: Diagnostic Lab Exam Types
CREATE TABLE lab_exam_types (
    exam_type_id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Catalog 13: Hospitalization Statuses
CREATE TABLE hospitalization_statuses (
    hosp_status_id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(30) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Catalog 14: Payment Methods
CREATE TABLE payment_methods (
    payment_method_id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(40) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Catalog 15: Invoice Payment Statuses
CREATE TABLE invoice_statuses (
    invoice_status_id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(30) NOT NULL UNIQUE
) ENGINE=InnoDB;


-- ============================================================================
-- PHASE 1: Primary Entities
-- Description: Base operational tables referencing master catalogs.
-- ============================================================================

-- Table 1: Clinics (Stores headquarters and branch locations)
CREATE TABLE clinics (
    clinic_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(150) NOT NULL,
    city VARCHAR(60) NOT NULL,
    phone VARCHAR(10) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    opening_hours VARCHAR(100) NOT NULL,
    services_offered TEXT
) ENGINE=InnoDB;

-- Table 2: Owners (Stores pet owner personal details and contact info)
CREATE TABLE owners (
    owner_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    doc_type_id TINYINT UNSIGNED NOT NULL,
    doc_number VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    birth_date DATE NOT NULL,
    address VARCHAR(100) NOT NULL,
    phone VARCHAR(10) NOT NULL,
    email VARCHAR(70) NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doc_type_id) REFERENCES document_types(doc_type_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Table 3: Services (Catalog of available clinical procedures and rates)
CREATE TABLE services (
    service_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    service_type_id TINYINT UNSIGNED NOT NULL,
    description TEXT,
    duration_min INT UNSIGNED NOT NULL,
    base_price DECIMAL(10,2) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (service_type_id) REFERENCES service_types(service_type_id) ON DELETE RESTRICT
) ENGINE=InnoDB;


-- ============================================================================
-- PHASE 2: Infrastructure, Staff, and Patients
-- Description: Core operational entities referencing primary parent tables.
-- ============================================================================

-- Table 4: Rooms (Physical spaces within each clinic location)
CREATE TABLE rooms (
    room_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    clinic_id INT UNSIGNED NOT NULL,
    room_number VARCHAR(10) NOT NULL,
    room_type_id TINYINT UNSIGNED NOT NULL,
    room_status_id TINYINT UNSIGNED NOT NULL DEFAULT 1,
    capacity INT UNSIGNED DEFAULT 1,
    daily_cost DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id) ON DELETE RESTRICT,
    FOREIGN KEY (room_type_id) REFERENCES room_types(room_type_id) ON DELETE RESTRICT,
    FOREIGN KEY (room_status_id) REFERENCES room_statuses(room_status_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Table 5: Employee Users (System accounts for administrative and clinical staff)
CREATE TABLE employee_users (
    employee_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    clinic_id INT UNSIGNED NOT NULL,
    doc_type_id TINYINT UNSIGNED NOT NULL,
    doc_number VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    email VARCHAR(70) NOT NULL UNIQUE,
    role_id TINYINT UNSIGNED NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id) ON DELETE RESTRICT,
    FOREIGN KEY (doc_type_id) REFERENCES document_types(doc_type_id) ON DELETE RESTRICT,
    FOREIGN KEY (role_id) REFERENCES user_roles(role_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Table 6: Pets (Patient records linked to their respective owners)
CREATE TABLE pets (
    pet_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    owner_id INT UNSIGNED NOT NULL,
    name VARCHAR(60) NOT NULL,
    species_id TINYINT UNSIGNED NOT NULL,
    breed VARCHAR(60) NOT NULL,
    gender CHAR(1) NOT NULL CHECK (gender IN ('M', 'F')),
    estimated_birth_date DATE NOT NULL,
    weight_kg DECIMAL(5,2) NOT NULL,
    color VARCHAR(50),
    coat VARCHAR(50),
    has_chip BOOLEAN DEFAULT FALSE,
    chip_number VARCHAR(30) UNIQUE NULL,
    is_neutered BOOLEAN DEFAULT FALSE,
    is_alive BOOLEAN DEFAULT TRUE,
    photo_url VARCHAR(255) NULL,
    FOREIGN KEY (owner_id) REFERENCES owners(owner_id) ON DELETE RESTRICT,
    FOREIGN KEY (species_id) REFERENCES species(species_id) ON DELETE RESTRICT
) ENGINE=InnoDB;


-- ============================================================================
-- PHASE 3: Medical Personnel and Scheduling
-- Description: Specialized veterinary profile extension and work schedules.
-- ============================================================================

-- Table 7: Veterinarians (Professional licensing and specialties linked to employees)
CREATE TABLE veterinarians (
    veterinarian_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    employee_id INT UNSIGNED NOT NULL UNIQUE,
    professional_license VARCHAR(30) NOT NULL UNIQUE,
    specialty_id TINYINT UNSIGNED NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employee_users(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (specialty_id) REFERENCES specialties(specialty_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Table 8: Schedules (Time slots assigned to veterinarians for consultations)
CREATE TABLE schedules (
    schedule_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    veterinarian_id INT UNSIGNED NOT NULL,
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    schedule_status_id TINYINT UNSIGNED NOT NULL DEFAULT 1,
    allowed_appointment_type_id TINYINT UNSIGNED NOT NULL,
    FOREIGN KEY (veterinarian_id) REFERENCES veterinarians(veterinarian_id) ON DELETE CASCADE,
    FOREIGN KEY (schedule_status_id) REFERENCES schedule_statuses(schedule_status_id) ON DELETE RESTRICT,
    FOREIGN KEY (allowed_appointment_type_id) REFERENCES appointment_types(appointment_type_id) ON DELETE RESTRICT
) ENGINE=InnoDB;


-- ============================================================================
-- PHASE 4: Clinical Appointments and Service Details
-- Description: Appointment booking and itemized service allocation.
-- ============================================================================

-- Table 9: Appointments (Scheduled medical sessions connecting patients, vets, and slots)
CREATE TABLE appointments (
    appointment_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    pet_id INT UNSIGNED NOT NULL,
    clinic_id INT UNSIGNED NOT NULL,
    veterinarian_id INT UNSIGNED NOT NULL,
    schedule_id INT UNSIGNED NOT NULL UNIQUE,
    appointment_type_id TINYINT UNSIGNED NOT NULL,
    reason TEXT NOT NULL,
    appointment_status_id TINYINT UNSIGNED NOT NULL DEFAULT 1,
    arrival_time DATETIME NULL,
    consultation_start_time DATETIME NULL,
    completion_time DATETIME NULL,
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id),
    FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id),
    FOREIGN KEY (veterinarian_id) REFERENCES veterinarians(veterinarian_id),
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id),
    FOREIGN KEY (appointment_type_id) REFERENCES appointment_types(appointment_type_id) ON DELETE RESTRICT,
    FOREIGN KEY (appointment_status_id) REFERENCES appointment_statuses(appointment_status_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Table 10: Appointment Details (Breakdown of performed services and pricing)
CREATE TABLE appointment_details (
    detail_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT UNSIGNED NOT NULL,
    service_id INT UNSIGNED NOT NULL,
    quantity INT UNSIGNED DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    discount DECIMAL(10,2) DEFAULT 0.00,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES services(service_id)
) ENGINE=InnoDB;


-- ============================================================================
-- PHASE 5: Medical History, Treatments, and Diagnostics
-- Description: Detailed medical records, prescriptions, vaccines, and lab tests.
-- ============================================================================

-- Table 11: Medical Records (Clinical diagnosis and progress notes per appointment)
CREATE TABLE medical_records (
    record_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT UNSIGNED NOT NULL UNIQUE,
    pet_id INT UNSIGNED NOT NULL,
    veterinarian_id INT UNSIGNED NOT NULL,
    anamnesis TEXT NOT NULL,
    physical_exam TEXT NOT NULL,
    diagnosis TEXT NOT NULL,
    prognosis TEXT,
    care_instructions TEXT,
    next_appointment_date DATE NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id),
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id),
    FOREIGN KEY (veterinarian_id) REFERENCES veterinarians(veterinarian_id)
) ENGINE=InnoDB;

-- Table 12: Prescriptions (Medications and dosage instructions issued in consultations)
CREATE TABLE prescriptions (
    prescription_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    record_id INT UNSIGNED NOT NULL,
    medication VARCHAR(120) NOT NULL,
    dosage VARCHAR(80) NOT NULL,
    frequency VARCHAR(80) NOT NULL,
    duration_days INT UNSIGNED NOT NULL,
    instructions TEXT,
    FOREIGN KEY (record_id) REFERENCES medical_records(record_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table 13: Administered Vaccines (Vaccination logs and booster scheduling)
CREATE TABLE administered_vaccines (
    vaccine_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    pet_id INT UNSIGNED NOT NULL,
    record_id INT UNSIGNED NULL,
    veterinarian_id INT UNSIGNED NOT NULL,
    vaccine_catalog_id TINYINT UNSIGNED NOT NULL,
    dosage VARCHAR(50) NOT NULL,
    manufacturer VARCHAR(80) NOT NULL,
    batch_number VARCHAR(80) NOT NULL,
    application_date DATE NOT NULL,
    booster_date DATE NOT NULL,
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id),
    FOREIGN KEY (record_id) REFERENCES medical_records(record_id),
    FOREIGN KEY (veterinarian_id) REFERENCES veterinarians(veterinarian_id),
    FOREIGN KEY (vaccine_catalog_id) REFERENCES vaccine_catalog(vaccine_catalog_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Table 14: Lab Exams (Diagnostic tests and uploaded clinical reports)
CREATE TABLE lab_exams (
    exam_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    record_id INT UNSIGNED NOT NULL,
    requesting_vet_id INT UNSIGNED NOT NULL,
    exam_type_id TINYINT UNSIGNED NOT NULL,
    name VARCHAR(100) NOT NULL,
    result_date DATE NULL,
    result_value VARCHAR(100),
    reference_range VARCHAR(100),
    interpretation TEXT,
    file_url VARCHAR(255) NULL,
    FOREIGN KEY (record_id) REFERENCES medical_records(record_id),
    FOREIGN KEY (requesting_vet_id) REFERENCES veterinarians(veterinarian_id),
    FOREIGN KEY (exam_type_id) REFERENCES lab_exam_types(exam_type_id) ON DELETE RESTRICT
) ENGINE=InnoDB;


-- ============================================================================
-- PHASE 6: Inpatient Care and Billing
-- Description: Hospitalizations and payment invoice generation.
-- ============================================================================

-- Table 15: Hospitalizations (Inpatient admission tracking and room occupancy)
CREATE TABLE hospitalizations (
    hospitalization_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    pet_id INT UNSIGNED NOT NULL,
    attending_vet_id INT UNSIGNED NOT NULL,
    room_id INT UNSIGNED NOT NULL,
    admission_datetime DATETIME DEFAULT CURRENT_TIMESTAMP,
    estimated_discharge_date DATE NOT NULL,
    actual_discharge_datetime DATETIME NULL,
    reason TEXT NOT NULL,
    diagnosis TEXT NOT NULL,
    hosp_status_id TINYINT UNSIGNED NOT NULL DEFAULT 1,
    observations TEXT,
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id),
    FOREIGN KEY (attending_vet_id) REFERENCES veterinarians(veterinarian_id),
    FOREIGN KEY (room_id) REFERENCES rooms(room_id),
    FOREIGN KEY (hosp_status_id) REFERENCES hospitalization_statuses(hosp_status_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Table 16: Invoices (Billing records for appointments and hospital stays)
CREATE TABLE invoices (
    invoice_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT UNSIGNED NULL,
    hospitalization_id INT UNSIGNED NULL,
    cashier_id INT UNSIGNED NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    discounts DECIMAL(10,2) DEFAULT 0.00,
    tax DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    payment_method_id TINYINT UNSIGNED NOT NULL,
    invoice_status_id TINYINT UNSIGNED NOT NULL DEFAULT 2,
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id),
    FOREIGN KEY (hospitalization_id) REFERENCES hospitalizations(hospitalization_id),
    FOREIGN KEY (cashier_id) REFERENCES employee_users(employee_id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_methods(payment_method_id) ON DELETE RESTRICT,
    FOREIGN KEY (invoice_status_id) REFERENCES invoice_statuses(invoice_status_id) ON DELETE RESTRICT
) ENGINE=InnoDB;


-- ============================================================================
-- PHASE 7: Seed Data for Master Catalogs
-- Description: Populates all lookup values previously hardcoded in ENUMs.
-- ============================================================================

INSERT INTO document_types (code, description) VALUES
('CC', 'Cédula de Ciudadanía'),
('CE', 'Cédula de Extranjería'),
('TI', 'Tarjeta de Identidad'),
('PASSPORT', 'Pasaporte');

INSERT INTO user_roles (name, description) VALUES
('Administrator', 'Full system and clinic configuration access'),
('Veterinarian', 'Clinical records, consultations, and medical orders'),
('Receptionist', 'Owner, pet, and appointment scheduling management'),
('Cashier', 'Billing, invoicing, and payment processing');

INSERT INTO service_types (name) VALUES
('consultation'), ('emergency'), ('vaccination'), ('deworming'),
('surgery'), ('lab'), ('imaging'), ('hospitalization'), ('other');

INSERT INTO room_types (name) VALUES
('single'), ('general'), ('ICU');

INSERT INTO room_statuses (name) VALUES
('available'), ('occupied'), ('cleaning'), ('maintenance');

INSERT INTO species (name) VALUES
('dog'), ('cat'), ('bird'), ('reptile'), ('rodent'), ('other');

INSERT INTO specialties (name) VALUES
('general'), ('surgeon'), ('dermatologist'), ('ophthalmologist'), ('oncologist');

INSERT INTO appointment_types (name) VALUES
('general'), ('followup'), ('emergency'), ('vaccination');

INSERT INTO schedule_statuses (name) VALUES
('available'), ('occupied'), ('disabled');

INSERT INTO appointment_statuses (name) VALUES
('scheduled'), ('confirmed'), ('in_progress'), ('completed'), ('canceled'), ('no_show');

INSERT INTO vaccine_catalog (name) VALUES
('rabies'), ('hexavalente'), ('quintuple'), ('other');

INSERT INTO lab_exam_types (name) VALUES
('blood'), ('urine'), ('xray'), ('ultrasound'), ('other');

INSERT INTO hospitalization_statuses (name) VALUES
('active'), ('discharged');

INSERT INTO payment_methods (name) VALUES
('cash'), ('debit_card'), ('credit_card'), ('wire_transfer');

INSERT INTO invoice_statuses (name) VALUES
('pending'), ('paid'), ('canceled');