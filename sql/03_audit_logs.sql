-- ============================================================================
-- Script: 03_audit_logs.sql
-- Objetivo: Crear tabla unificada de auditoria para operaciones INSERT/UPDATE/DELETE
--           en las tablas gestionadas por la API (owners, pets).
-- Fecha: 2026-11-22
-- ============================================================================

USE veterinary_clinic_db;

CREATE TABLE IF NOT EXISTS audit_logs (
    audit_id     INT UNSIGNED NOT NULL AUTO_INCREMENT,
    table_name   VARCHAR(50)  NOT NULL,
    operation    CHAR(1)      NOT NULL CHECK (operation IN ('I', 'U', 'D')),
    record_id    INT UNSIGNED NOT NULL,
    old_data     JSON         NULL,
    new_data     JSON         NULL,
    performed_by VARCHAR(100) NOT NULL,
    created_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (audit_id),
    KEY idx_audit_table_record (table_name, record_id),
    KEY idx_audit_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;