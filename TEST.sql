-- =============================================================
-- Husky CRM 测试数据 (GUID IDs)
-- 用法: sqlite3 backend/huskycrm.db < TEST.sql
-- =============================================================

-- ── 清空所有相关表 ──
DELETE FROM tasks;
DELETE FROM events;
DELETE FROM territory_accounts;
DELETE FROM territory_products;
DELETE FROM territory_members;
DELETE FROM territories;
DELETE FROM opportunity_products;
DELETE FROM opportunities;
DELETE FROM stages;
DELETE FROM contact_accounts;
DELETE FROM contacts;
DELETE FROM accounts;
DELETE FROM products;
DELETE FROM users;
DELETE FROM profiles;
DELETE FROM dashboard_components;
DELETE FROM dashboards;
DELETE FROM reports;
DELETE FROM workflow_execution_logs;
DELETE FROM workflow_actions;
DELETE FROM workflow_rules;
DELETE FROM custom_field_defs;
DELETE FROM custom_object_defs;

-- ── Profiles ──────────────────────────────────────────────────
INSERT INTO profiles (id, name, profile_type, description, is_system) VALUES
('prof_admin_0001', 'System Administrator', 'admin', '全量系统权限 + 数据权限（View All / Modify All）', 1);
INSERT INTO profiles (id, name, profile_type, description, is_system) VALUES
('prof_standard_01', 'Standard User', 'standard', '基础销售 CRUD 权限（无删除）', 1);
INSERT INTO profiles (id, name, profile_type, description, is_system) VALUES
('prof_readonly_01', 'Read Only', 'readonly', '仅查询，无编辑/删除权限', 1);

-- ── 用户 ─────────────────────────────────────────────────────
INSERT INTO users (id, username, email, password_hash, display_name, is_active, is_superuser, profile_id) VALUES
('user_a1b2c3d4e5f6', 'admin', 'admin@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'Administrator', 1, 1, 'prof_admin_0001');
INSERT INTO users (id, username, email, password_hash, display_name, is_active, is_superuser, profile_id) VALUES
('user_b2c3d4e5f6a7', 'Global_CEO', 'ceo@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'Global CEO', 1, 0, 'prof_admin_0001');
INSERT INTO users (id, username, email, password_hash, display_name, is_active, is_superuser, profile_id) VALUES
('user_c3d4e5f6a7b8', 'Asia_manager', 'asia.mgr@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'Asia Manager', 1, 0, 'prof_standard_01');
INSERT INTO users (id, username, email, password_hash, display_name, is_active, is_superuser, profile_id) VALUES
('user_d4e5f6a7b8c9', 'Asia_RedRussia_sales', 'red.russia@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'Red Russia Sales', 1, 0, 'prof_standard_01');
INSERT INTO users (id, username, email, password_hash, display_name, is_active, is_superuser, profile_id) VALUES
('user_e5f6a7b8c9d0', 'Asia_Libert_sales', 'libert.sales@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'Libert Sales', 1, 0, 'prof_standard_01');
INSERT INTO users (id, username, email, password_hash, display_name, is_active, is_superuser, profile_id) VALUES
('user_f6a7b8c9d0e1', 'Asia_Baji_sales', 'baji.sales@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'Baji Sales', 1, 0, 'prof_standard_01');
INSERT INTO users (id, username, email, password_hash, display_name, is_active, is_superuser, profile_id) VALUES
('user_a7b8c9d0e1f2', 'Asia_Taji_sales', 'taji.sales@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'Taji Sales', 1, 0, 'prof_standard_01');
INSERT INTO users (id, username, email, password_hash, display_name, is_active, is_superuser, profile_id) VALUES
('user_b8c9d0e1f2a3', 'Asia_HHK_sales', 'hhk.sales@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'HHK Sales', 1, 0, 'prof_standard_01');
INSERT INTO users (id, username, email, password_hash, display_name, is_active, is_superuser, profile_id) VALUES
('user_c9d0e1f2a3b4', 'Europe_manager', 'europe.mgr@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'Europe Manager', 1, 0, 'prof_standard_01');
INSERT INTO users (id, username, email, password_hash, display_name, is_active, is_superuser, profile_id) VALUES
('user_d0e1f2a3b4c5', 'Europe_EastTooth_sales', 'east.tooth@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'East Tooth Sales', 1, 0, 'prof_standard_01');
INSERT INTO users (id, username, email, password_hash, display_name, is_active, is_superuser, profile_id) VALUES
('user_e1f2a3b4c5d6', 'Europe_PutiTooth_sales', 'puti.tooth@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'Puti Tooth Sales', 1, 0, 'prof_standard_01');
INSERT INTO users (id, username, email, password_hash, display_name, is_active, is_superuser, profile_id) VALUES
('user_f2a3b4c5d6e7', 'America_manager', 'america.mgr@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'America Manager', 1, 0, 'prof_standard_01');
INSERT INTO users (id, username, email, password_hash, display_name, is_active, is_superuser, profile_id) VALUES
('user_a3b4c5d6e7f8', 'Africa_manager', 'africa.mgr@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'Africa Manager', 1, 0, 'prof_standard_01');
INSERT INTO users (id, username, email, password_hash, display_name, is_active, is_superuser, profile_id) VALUES
('user_b4c5d6e7f8a9', 'Oceania_manager', 'oceania.mgr@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'Oceania Manager', 1, 0, 'prof_standard_01');
INSERT INTO users (id, username, email, password_hash, display_name, is_active, is_superuser, profile_id) VALUES
('user_c5d6e7f8a9b0', 'Antarctica_manager', 'antarctica.mgr@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'Antarctica Manager', 1, 0, 'prof_readonly_01');

-- ── Stages ────────────────────────────────────────────────────
INSERT INTO stages (id, name, probability, sort_order, is_closed_won, is_closed_lost) VALUES
('stg_a1b2c3d4e5f6', '初步接触', 10, 1, 0, 0);
INSERT INTO stages (id, name, probability, sort_order, is_closed_won, is_closed_lost) VALUES
('stg_b2c3d4e5f6a7', '需求分析', 30, 2, 0, 0);
INSERT INTO stages (id, name, probability, sort_order, is_closed_won, is_closed_lost) VALUES
('stg_c3d4e5f6a7b8', '方案制定', 50, 3, 0, 0);
INSERT INTO stages (id, name, probability, sort_order, is_closed_won, is_closed_lost) VALUES
('stg_d4e5f6a7b8c9', '商务谈判', 70, 4, 0, 0);
INSERT INTO stages (id, name, probability, sort_order, is_closed_won, is_closed_lost) VALUES
('stg_e5f6a7b8c9d0', '合同签订', 90, 5, 0, 0);
INSERT INTO stages (id, name, probability, sort_order, is_closed_won, is_closed_lost) VALUES
('stg_f6a7b8c9d0e1', '赢单', 100, 6, 1, 0);
INSERT INTO stages (id, name, probability, sort_order, is_closed_won, is_closed_lost) VALUES
('stg_a7b8c9d0e1f2', '输单', 0, 7, 0, 1);

-- ── Products ──────────────────────────────────────────────────
INSERT INTO products (id, name, product_code, description, price, cost, category, is_active) VALUES
('prod_a1b2c3d4e5f6', 'HydroFlux Capsule', 'HF-001', '高纯度水萃取物胶囊', 299.99, 120, '保健品', 1);
INSERT INTO products (id, name, product_code, description, price, cost, category, is_active) VALUES
('prod_b2c3d4e5f6a7', 'BioSync Patch', 'BS-002', '生物同步贴片', 159.5, 65, '医疗器械', 1);
INSERT INTO products (id, name, product_code, description, price, cost, category, is_active) VALUES
('prod_c3d4e5f6a7b8', 'NeuroPulse Headset', 'NP-003', '神经脉冲头戴设备', 899, 420, '电子设备', 1);
INSERT INTO products (id, name, product_code, description, price, cost, category, is_active) VALUES
('prod_d4e5f6a7b8c9', 'ChronoWrist Watch', 'CW-004', '计时腕表 - 限量版', 2499.99, 1100, '配件', 1);
INSERT INTO products (id, name, product_code, description, price, cost, category, is_active) VALUES
('prod_e5f6a7b8c9d0', 'AeroGel Insulator', 'AG-005', '气凝胶保温材料（工业级）', 499, 210, '工业材料', 1);
INSERT INTO products (id, name, product_code, description, price, cost, category, is_active) VALUES
('prod_f6a7b8c9d0e1', 'LumiSheet Display', 'LS-006', '发光薄膜显示屏', 1299, 580, '电子设备', 1);
INSERT INTO products (id, name, product_code, description, price, cost, category, is_active) VALUES
('prod_a7b8c9d0e1f2', 'QuantumKey Encryptor', 'QK-007', '量子密钥加密器', 3999, 1800, '安全设备', 1);
INSERT INTO products (id, name, product_code, description, price, cost, category, is_active) VALUES
('prod_b8c9d0e1f2a3', 'EcoBrick Foundation', 'EB-008', '生态砖基础模块（建材级）', 79.99, 35, '建筑材料', 1);

-- ── Territories ───────────────────────────────────────────────
INSERT INTO territories (id, name, code, territory_type, parent_id, description, is_active, owner_id) VALUES
('terr_a1b2c3d4e5f6', 'Global', 'GL', 'region', NULL, '全球总部', 1, 'user_b2c3d4e5f6a7');
INSERT INTO territories (id, name, code, territory_type, parent_id, description, is_active, owner_id) VALUES
('terr_b2c3d4e5f6a7', 'Asia', 'ASIA', 'region', 'terr_a1b2c3d4e5f6', '亚太区域', 1, 'user_c3d4e5f6a7b8');
INSERT INTO territories (id, name, code, territory_type, parent_id, description, is_active, owner_id) VALUES
('terr_c3d4e5f6a7b8', 'Europe', 'EU', 'region', 'terr_a1b2c3d4e5f6', '欧洲区域', 1, 'user_c9d0e1f2a3b4');
INSERT INTO territories (id, name, code, territory_type, parent_id, description, is_active, owner_id) VALUES
('terr_d4e5f6a7b8c9', 'America', 'AM', 'region', 'terr_a1b2c3d4e5f6', '美洲区域', 1, 'user_f2a3b4c5d6e7');
INSERT INTO territories (id, name, code, territory_type, parent_id, description, is_active, owner_id) VALUES
('terr_e5f6a7b8c9d0', 'Asia_RedRussia', 'ASIA_RR', 'district', 'terr_b2c3d4e5f6a7', '红俄罗斯（亚洲分部）', 1, 'user_d4e5f6a7b8c9');
INSERT INTO territories (id, name, code, territory_type, parent_id, description, is_active, owner_id) VALUES
('terr_f6a7b8c9d0e1', 'Asia_Libert', 'ASIA_LBT', 'district', 'terr_b2c3d4e5f6a7', 'Libert（亚洲分部）', 1, 'user_e5f6a7b8c9d0');
INSERT INTO territories (id, name, code, territory_type, parent_id, description, is_active, owner_id) VALUES
('terr_a7b8c9d0e1f2', 'Asia_Baji', 'ASIA_BJ', 'district', 'terr_b2c3d4e5f6a7', 'Baji（亚洲分部）', 1, 'user_f6a7b8c9d0e1');
INSERT INTO territories (id, name, code, territory_type, parent_id, description, is_active, owner_id) VALUES
('terr_b8c9d0e1f2a3', 'Asia_Taji', 'ASIA_TJ', 'district', 'terr_b2c3d4e5f6a7', 'Taji（亚洲分部）', 1, 'user_a7b8c9d0e1f2');
INSERT INTO territories (id, name, code, territory_type, parent_id, description, is_active, owner_id) VALUES
('terr_c9d0e1f2a3b4', 'Asia_HHK', 'ASIA_HHK', 'district', 'terr_b2c3d4e5f6a7', 'HHK（亚洲分部）', 1, 'user_b8c9d0e1f2a3');
INSERT INTO territories (id, name, code, territory_type, parent_id, description, is_active, owner_id) VALUES
('terr_d0e1f2a3b4c5', 'Europe_EastTooth', 'EU_ET', 'district', 'terr_c3d4e5f6a7b8', 'East Tooth（欧洲分部）', 1, 'user_d0e1f2a3b4c5');
INSERT INTO territories (id, name, code, territory_type, parent_id, description, is_active, owner_id) VALUES
('terr_e1f2a3b4c5d6', 'Europe_PutiTooth', 'EU_PT', 'district', 'terr_c3d4e5f6a7b8', 'Puti Tooth（欧洲分部）', 1, 'user_e1f2a3b4c5d6');
INSERT INTO territories (id, name, code, territory_type, parent_id, description, is_active, owner_id) VALUES
('terr_f2a3b4c5d6e7', 'America_NovaStar', 'AM_NS', 'district', 'terr_d4e5f6a7b8c9', 'NovaStar（美洲分部）', 1, 'user_f2a3b4c5d6e7');
INSERT INTO territories (id, name, code, territory_type, parent_id, description, is_active, owner_id) VALUES
('terr_a3b4c5d6e7f8', 'Africa_GoldenSands', 'AF_GS', 'district', 'terr_a1b2c3d4e5f6', 'GoldenSands（非洲）', 1, 'user_a3b4c5d6e7f8');
INSERT INTO territories (id, name, code, territory_type, parent_id, description, is_active, owner_id) VALUES
('terr_b4c5d6e7f8a9', 'Oceania_DeepBlue', 'OC_DB', 'district', 'terr_a1b2c3d4e5f6', 'DeepBlue（大洋洲）', 1, 'user_b4c5d6e7f8a9');

-- ── Territory Members ─────────────────────────────────────────
INSERT INTO territory_members (id, territory_id, user_id, role) VALUES
('tmem_a1b2c3d4e5f6', 'terr_a1b2c3d4e5f6', 'user_b2c3d4e5f6a7', 'manager');
INSERT INTO territory_members (id, territory_id, user_id, role) VALUES
('tmem_b2c3d4e5f6a7', 'terr_b2c3d4e5f6a7', 'user_c3d4e5f6a7b8', 'manager');
INSERT INTO territory_members (id, territory_id, user_id, role) VALUES
('tmem_c3d4e5f6a7b8', 'terr_e5f6a7b8c9d0', 'user_d4e5f6a7b8c9', 'manager');
INSERT INTO territory_members (id, territory_id, user_id, role) VALUES
('tmem_d4e5f6a7b8c9', 'terr_f6a7b8c9d0e1', 'user_e5f6a7b8c9d0', 'manager');
INSERT INTO territory_members (id, territory_id, user_id, role) VALUES
('tmem_e5f6a7b8c9d0', 'terr_a7b8c9d0e1f2', 'user_f6a7b8c9d0e1', 'manager');
INSERT INTO territory_members (id, territory_id, user_id, role) VALUES
('tmem_f6a7b8c9d0e1', 'terr_b8c9d0e1f2a3', 'user_a7b8c9d0e1f2', 'manager');
INSERT INTO territory_members (id, territory_id, user_id, role) VALUES
('tmem_a7b8c9d0e1f2', 'terr_c9d0e1f2a3b4', 'user_b8c9d0e1f2a3', 'manager');
INSERT INTO territory_members (id, territory_id, user_id, role) VALUES
('tmem_b8c9d0e1f2a3', 'terr_c3d4e5f6a7b8', 'user_c9d0e1f2a3b4', 'manager');
INSERT INTO territory_members (id, territory_id, user_id, role) VALUES
('tmem_c9d0e1f2a3b4', 'terr_d0e1f2a3b4c5', 'user_d0e1f2a3b4c5', 'manager');
INSERT INTO territory_members (id, territory_id, user_id, role) VALUES
('tmem_d0e1f2a3b4c5', 'terr_e1f2a3b4c5d6', 'user_e1f2a3b4c5d6', 'manager');
INSERT INTO territory_members (id, territory_id, user_id, role) VALUES
('tmem_e1f2a3b4c5d6', 'terr_d4e5f6a7b8c9', 'user_f2a3b4c5d6e7', 'manager');
INSERT INTO territory_members (id, territory_id, user_id, role) VALUES
('tmem_f2a3b4c5d6e7', 'terr_f2a3b4c5d6e7', 'user_f2a3b4c5d6e7', 'manager');
INSERT INTO territory_members (id, territory_id, user_id, role) VALUES
('tmem_a3b4c5d6e7f8', 'terr_a3b4c5d6e7f8', 'user_a3b4c5d6e7f8', 'manager');
INSERT INTO territory_members (id, territory_id, user_id, role) VALUES
('tmem_b4c5d6e7f8a9', 'terr_b4c5d6e7f8a9', 'user_b4c5d6e7f8a9', 'manager');

-- ── Accounts ──────────────────────────────────────────────────
INSERT INTO accounts (id, name, industry, phone, email, description, owner_id) VALUES
('acc_a1b2c3d4e5f6', 'Red Russia Corp', '能源', '+7-495-111-2233', 'info@redrussia.ru', '俄罗斯红色能源公司 - 亚太区客户', 'user_c3d4e5f6a7b8');
INSERT INTO accounts (id, name, industry, phone, email, description, owner_id) VALUES
('acc_b2c3d4e5f6a7', 'Libert Group', '科技', '+1-555-0102', 'info@libert.com', 'Libert 科技集团 - 亚太区客户', 'user_c3d4e5f6a7b8');
INSERT INTO accounts (id, name, industry, phone, email, description, owner_id) VALUES
('acc_c3d4e5f6a7b8', 'Baji Industries', '制造', '+86-21-8888-0001', 'info@baji.cn', '巴吉工业 - 亚太区客户', 'user_c3d4e5f6a7b8');
INSERT INTO accounts (id, name, industry, phone, email, description, owner_id) VALUES
('acc_d4e5f6a7b8c9', 'Taji & Co', '零售', '+86-571-6666-7777', 'info@taji.com', '塔吉贸易 - 亚太区客户', 'user_c3d4e5f6a7b8');
INSERT INTO accounts (id, name, industry, phone, email, description, owner_id) VALUES
('acc_e5f6a7b8c9d0', 'HHK Corporation', '金融', '+852-2222-3333', 'info@hhk.hk', 'HHK 集团 - 亚太区客户', 'user_c3d4e5f6a7b8');
INSERT INTO accounts (id, name, industry, phone, email, description, owner_id) VALUES
('acc_f6a7b8c9d0e1', 'East Tooth GmbH', '医药', '+49-30-1111-0001', 'info@east-tooth.de', 'East Tooth 医药 - 欧洲区客户', 'user_c9d0e1f2a3b4');
INSERT INTO accounts (id, name, industry, phone, email, description, owner_id) VALUES
('acc_a7b8c9d0e1f2', 'Puti Tooth Ltd', '食品', '+44-20-7777-8888', 'info@puti-tooth.co.uk', 'Puti Tooth 食品 - 欧洲区客户', 'user_c9d0e1f2a3b4');
INSERT INTO accounts (id, name, industry, phone, email, description, owner_id) VALUES
('acc_b8c9d0e1f2a3', 'NovaStar Energy', '能源', '+1-212-333-4444', 'info@novastar.com', 'NovaStar 新能源 - 美洲区客户', 'user_f2a3b4c5d6e7');
INSERT INTO accounts (id, name, industry, phone, email, description, owner_id) VALUES
('acc_c9d0e1f2a3b4', 'CrystalLake Pharma', '医药', '+1-617-555-0101', 'info@crystallake.com', 'CrystalLake 制药 - 美洲区客户', 'user_f2a3b4c5d6e7');
INSERT INTO accounts (id, name, industry, phone, email, description, owner_id) VALUES
('acc_d0e1f2a3b4c5', 'GoldenSands Mining', '矿业', '+27-21-444-5555', 'info@goldensands.za', 'GoldenSands 矿业 - 非洲区客户', 'user_a3b4c5d6e7f8');
INSERT INTO accounts (id, name, industry, phone, email, description, owner_id) VALUES
('acc_e1f2a3b4c5d6', 'DeepBlue Fisheries', '农业', '+61-2-9999-0000', 'info@deepblue.au', 'DeepBlue 渔业 - 大洋洲客户', 'user_b4c5d6e7f8a9');

-- ── Contacts ──────────────────────────────────────────────────
INSERT INTO contacts (id, first_name, last_name, email, phone, title, department, owner_id) VALUES
('con_a1b2c3d4e5f6', 'Ivan', 'Petrov', 'ivan@redrussia.ru', '+7-495-111-2234', '采购总监', '采购部', 'user_d4e5f6a7b8c9');
INSERT INTO contacts (id, first_name, last_name, email, phone, title, department, owner_id) VALUES
('con_b2c3d4e5f6a7', 'Olga', 'Smirnova', 'olga@redrussia.ru', '+7-495-111-2235', '技术主管', '技术部', 'user_d4e5f6a7b8c9');
INSERT INTO contacts (id, first_name, last_name, email, phone, title, department, owner_id) VALUES
('con_c3d4e5f6a7b8', 'John', 'Smith', 'john@libert.com', '+1-555-0103', 'VP Engineering', '工程部', 'user_e5f6a7b8c9d0');
INSERT INTO contacts (id, first_name, last_name, email, phone, title, department, owner_id) VALUES
('con_d4e5f6a7b8c9', 'Alice', 'Wang', 'alice@libert.com', '+1-555-0104', '产品经理', '产品部', 'user_e5f6a7b8c9d0');
INSERT INTO contacts (id, first_name, last_name, email, phone, title, department, owner_id) VALUES
('con_e5f6a7b8c9d0', '张', '伟', 'zhangwei@baji.cn', '+86-21-8888-0002', '供应链总监', '供应链部', 'user_f6a7b8c9d0e1');
INSERT INTO contacts (id, first_name, last_name, email, phone, title, department, owner_id) VALUES
('con_f6a7b8c9d0e1', '李', '娜', 'lina@baji.cn', '+86-21-8888-0003', '采购经理', '采购部', 'user_f6a7b8c9d0e1');
INSERT INTO contacts (id, first_name, last_name, email, phone, title, department, owner_id) VALUES
('con_a7b8c9d0e1f2', '王', '磊', 'wanglei@taji.com', '+86-571-6666-7778', 'CEO', '管理层', 'user_a7b8c9d0e1f2');
INSERT INTO contacts (id, first_name, last_name, email, phone, title, department, owner_id) VALUES
('con_b8c9d0e1f2a3', '陈', '静', 'chenjing@taji.com', '+86-571-6666-7779', '财务总监', '财务部', 'user_a7b8c9d0e1f2');
INSERT INTO contacts (id, first_name, last_name, email, phone, title, department, owner_id) VALUES
('con_c9d0e1f2a3b4', 'Michael', 'Chan', 'michael@hhk.hk', '+852-2222-3334', '投资总监', '投资部', 'user_b8c9d0e1f2a3');
INSERT INTO contacts (id, first_name, last_name, email, phone, title, department, owner_id) VALUES
('con_d0e1f2a3b4c5', 'Sarah', 'Lau', 'sarah@hhk.hk', '+852-2222-3335', '合规官', '合规部', 'user_b8c9d0e1f2a3');
INSERT INTO contacts (id, first_name, last_name, email, phone, title, department, owner_id) VALUES
('con_e1f2a3b4c5d6', 'Hans', 'Mueller', 'hans@east-tooth.de', '+49-30-1111-0002', '研发总监', '研发部', 'user_d0e1f2a3b4c5');
INSERT INTO contacts (id, first_name, last_name, email, phone, title, department, owner_id) VALUES
('con_f2a3b4c5d6e7', 'Klaus', 'Schmidt', 'klaus@east-tooth.de', '+49-30-1111-0003', '采购主管', '采购部', 'user_d0e1f2a3b4c5');
INSERT INTO contacts (id, first_name, last_name, email, phone, title, department, owner_id) VALUES
('con_a3b4c5d6e7f8', 'James', 'Brown', 'james@puti-tooth.co.uk', '+44-20-7777-8889', '市场总监', '市场部', 'user_e1f2a3b4c5d6');
INSERT INTO contacts (id, first_name, last_name, email, phone, title, department, owner_id) VALUES
('con_b4c5d6e7f8a9', 'Emily', 'Taylor', 'emily@puti-tooth.co.uk', '+44-20-7777-8890', '销售VP', '销售部', 'user_e1f2a3b4c5d6');
INSERT INTO contacts (id, first_name, last_name, email, phone, title, department, owner_id) VALUES
('con_c5d6e7f8a9b0', 'Bob', 'Johnson', 'bob@novastar.com', '+1-212-333-4445', 'CTO', '技术部', 'user_f2a3b4c5d6e7');
INSERT INTO contacts (id, first_name, last_name, email, phone, title, department, owner_id) VALUES
('con_d6e7f8a9b0c1', 'Maria', 'Garcia', 'maria@novastar.com', '+1-212-333-4446', '运营总监', '运营部', 'user_f2a3b4c5d6e7');
INSERT INTO contacts (id, first_name, last_name, email, phone, title, department, owner_id) VALUES
('con_e7f8a9b0c1d2', 'David', 'Lee', 'david@crystallake.com', '+1-617-555-0102', '首席科学家', '研发部', 'user_f2a3b4c5d6e7');
INSERT INTO contacts (id, first_name, last_name, email, phone, title, department, owner_id) VALUES
('con_f8a9b0c1d2e3', 'Grace', 'Kim', 'grace@goldensands.za', '+27-21-444-5556', '采购总监', '采购部', 'user_a3b4c5d6e7f8');
INSERT INTO contacts (id, first_name, last_name, email, phone, title, department, owner_id) VALUES
('con_a9b0c1d2e3f4', 'Tom', 'Wilson', 'tom@deepblue.au', '+61-2-9999-0001', 'CEO', '管理层', 'user_b4c5d6e7f8a9');
INSERT INTO contacts (id, first_name, last_name, email, phone, title, department, owner_id) VALUES
('con_b0c1d2e3f4a5', 'Lucy', 'Brown', 'lucy@deepblue.au', '+61-2-9999-0002', '销售总监', '销售部', 'user_b4c5d6e7f8a9');

-- ── Contact-Account Relations ────────────────────────────────
INSERT INTO contact_accounts (id, contact_id, account_id) VALUES
('conacc_a1b2c3d4e5', 'con_a1b2c3d4e5f6', 'acc_a1b2c3d4e5f6');
INSERT INTO contact_accounts (id, contact_id, account_id) VALUES
('conacc_b2c3d4e5f6', 'con_b2c3d4e5f6a7', 'acc_a1b2c3d4e5f6');
INSERT INTO contact_accounts (id, contact_id, account_id) VALUES
('conacc_c3d4e5f6a7', 'con_c3d4e5f6a7b8', 'acc_b2c3d4e5f6a7');
INSERT INTO contact_accounts (id, contact_id, account_id) VALUES
('conacc_d4e5f6a7b8', 'con_d4e5f6a7b8c9', 'acc_b2c3d4e5f6a7');
INSERT INTO contact_accounts (id, contact_id, account_id) VALUES
('conacc_e5f6a7b8c9', 'con_e5f6a7b8c9d0', 'acc_c3d4e5f6a7b8');
INSERT INTO contact_accounts (id, contact_id, account_id) VALUES
('conacc_f6a7b8c9d0', 'con_f6a7b8c9d0e1', 'acc_c3d4e5f6a7b8');
INSERT INTO contact_accounts (id, contact_id, account_id) VALUES
('conacc_a7b8c9d0e1', 'con_a7b8c9d0e1f2', 'acc_d4e5f6a7b8c9');
INSERT INTO contact_accounts (id, contact_id, account_id) VALUES
('conacc_b8c9d0e1f2', 'con_b8c9d0e1f2a3', 'acc_d4e5f6a7b8c9');
INSERT INTO contact_accounts (id, contact_id, account_id) VALUES
('conacc_c9d0e1f2a3', 'con_c9d0e1f2a3b4', 'acc_e5f6a7b8c9d0');
INSERT INTO contact_accounts (id, contact_id, account_id) VALUES
('conacc_d0e1f2a3b4', 'con_d0e1f2a3b4c5', 'acc_e5f6a7b8c9d0');
INSERT INTO contact_accounts (id, contact_id, account_id) VALUES
('conacc_e1f2a3b4c5', 'con_e1f2a3b4c5d6', 'acc_f6a7b8c9d0e1');
INSERT INTO contact_accounts (id, contact_id, account_id) VALUES
('conacc_f2a3b4c5d6', 'con_f2a3b4c5d6e7', 'acc_f6a7b8c9d0e1');
INSERT INTO contact_accounts (id, contact_id, account_id) VALUES
('conacc_a3b4c5d6e7', 'con_a3b4c5d6e7f8', 'acc_a7b8c9d0e1f2');
INSERT INTO contact_accounts (id, contact_id, account_id) VALUES
('conacc_b4c5d6e7f8', 'con_b4c5d6e7f8a9', 'acc_a7b8c9d0e1f2');
INSERT INTO contact_accounts (id, contact_id, account_id) VALUES
('conacc_c5d6e7f8a9', 'con_c5d6e7f8a9b0', 'acc_b8c9d0e1f2a3');
INSERT INTO contact_accounts (id, contact_id, account_id) VALUES
('conacc_d6e7f8a9b0', 'con_d6e7f8a9b0c1', 'acc_b8c9d0e1f2a3');
INSERT INTO contact_accounts (id, contact_id, account_id) VALUES
('conacc_e7f8a9b0c1', 'con_e7f8a9b0c1d2', 'acc_c9d0e1f2a3b4');
INSERT INTO contact_accounts (id, contact_id, account_id) VALUES
('conacc_f8a9b0c1d2', 'con_f8a9b0c1d2e3', 'acc_d0e1f2a3b4c5');
INSERT INTO contact_accounts (id, contact_id, account_id) VALUES
('conacc_a9b0c1d2e3', 'con_a9b0c1d2e3f4', 'acc_e1f2a3b4c5d6');
INSERT INTO contact_accounts (id, contact_id, account_id) VALUES
('conacc_b0c1d2e3f4', 'con_b0c1d2e3f4a5', 'acc_e1f2a3b4c5d6');

-- ── Opportunities ─────────────────────────────────────────────
INSERT INTO opportunities (id, name, account_id, stage_id, amount, probability, close_date, description, owner_id) VALUES
('oppo_a1b2c3d4e5f6', 'Red Russia 能源设备升级', 'acc_a1b2c3d4e5f6', 'stg_c3d4e5f6a7b8', 150000, 50, '2026-08-15', '俄罗斯客户能源设备升级项目', 'user_d4e5f6a7b8c9');
INSERT INTO opportunities (id, name, account_id, stage_id, amount, probability, close_date, description, owner_id) VALUES
('oppo_b2c3d4e5f6a7', 'Libert 生物同步贴片采购', 'acc_b2c3d4e5f6a7', 'stg_b2c3d4e5f6a7', 48000, 30, '2026-09-01', 'Libert 集团批量采购 BioSync Patch 用于员工健康管理', 'user_e5f6a7b8c9d0');
INSERT INTO opportunities (id, name, account_id, stage_id, amount, probability, close_date, description, owner_id) VALUES
('oppo_c3d4e5f6a7b8', 'Baji 工业传感器升级', 'acc_c3d4e5f6a7b8', 'stg_d4e5f6a7b8c9', 320000, 70, '2026-07-30', 'Baji 工业产线传感器全面升级项目', 'user_f6a7b8c9d0e1');
INSERT INTO opportunities (id, name, account_id, stage_id, amount, probability, close_date, description, owner_id) VALUES
('oppo_d4e5f6a7b8c9', 'Taji 零售门店数字化方案', 'acc_d4e5f6a7b8c9', 'stg_c3d4e5f6a7b8', 185000, 50, '2026-10-15', 'Taji 全国 50 家门店数字化改造方案', 'user_a7b8c9d0e1f2');
INSERT INTO opportunities (id, name, account_id, stage_id, amount, probability, close_date, description, owner_id) VALUES
('oppo_e5f6a7b8c9d0', 'HHK 金融安全系统', 'acc_e5f6a7b8c9d0', 'stg_a1b2c3d4e5f6', 650000, 10, '2027-01-15', 'HHK 集团量子加密安全系统项目', 'user_b8c9d0e1f2a3');
INSERT INTO opportunities (id, name, account_id, stage_id, amount, probability, close_date, description, owner_id) VALUES
('oppo_f6a7b8c9d0e1', 'East Tooth 研发设备采购', 'acc_f6a7b8c9d0e1', 'stg_b2c3d4e5f6a7', 220000, 30, '2026-08-20', 'East Tooth 医药研发中心设备采购', 'user_d0e1f2a3b4c5');
INSERT INTO opportunities (id, name, account_id, stage_id, amount, probability, close_date, description, owner_id) VALUES
('oppo_a7b8c9d0e1f2', 'Puti Tooth 冷链物流项目', 'acc_a7b8c9d0e1f2', 'stg_c3d4e5f6a7b8', 95000, 50, '2026-09-30', 'Puti Tooth 食品冷链物流系统建设', 'user_e1f2a3b4c5d6');
INSERT INTO opportunities (id, name, account_id, stage_id, amount, probability, close_date, description, owner_id) VALUES
('oppo_b8c9d0e1f2a3', 'NovaStar 能源管理系统', 'acc_b8c9d0e1f2a3', 'stg_d4e5f6a7b8c9', 780000, 70, '2026-08-10', 'NovaStar 新能源电站智能管理系统', 'user_f2a3b4c5d6e7');
INSERT INTO opportunities (id, name, account_id, stage_id, amount, probability, close_date, description, owner_id) VALUES
('oppo_c9d0e1f2a3b4', 'CrystalLake 实验室装备', 'acc_c9d0e1f2a3b4', 'stg_e5f6a7b8c9d0', 430000, 90, '2026-07-20', 'CrystalLake 制药新实验室全套装备，已进入合同阶段', 'user_f2a3b4c5d6e7');
INSERT INTO opportunities (id, name, account_id, stage_id, amount, probability, close_date, description, owner_id) VALUES
('oppo_d0e1f2a3b4c5', 'GoldenSands 矿区安全监控', 'acc_d0e1f2a3b4c5', 'stg_a1b2c3d4e5f6', 160000, 10, '2026-12-01', 'GoldenSands 矿区安全监控系统初步接触', 'user_a3b4c5d6e7f8');
INSERT INTO opportunities (id, name, account_id, stage_id, amount, probability, close_date, description, owner_id) VALUES
('oppo_e1f2a3b4c5d6', 'DeepBlue 渔业溯源系统', 'acc_e1f2a3b4c5d6', 'stg_b2c3d4e5f6a7', 88000, 30, '2026-11-01', 'DeepBlue 海产品全程溯源系统', 'user_b4c5d6e7f8a9');
INSERT INTO opportunities (id, name, account_id, stage_id, amount, probability, close_date, description, owner_id) VALUES
('oppo_f2a3b4c5d6e7', 'Red Russia 量子安全通信', 'acc_a1b2c3d4e5f6', 'stg_f6a7b8c9d0e1', 600000, 100, '2026-06-15', '已赢单 - Red Russia 量子密钥加密器采购合同', 'user_d4e5f6a7b8c9');
INSERT INTO opportunities (id, name, account_id, stage_id, amount, probability, close_date, description, owner_id) VALUES
('oppo_a3b4c5d6e7f8', 'Baji 生态砖海外采购', 'acc_c3d4e5f6a7b8', 'stg_a7b8c9d0e1f2', 120000, 0, '2026-05-01', '已输单 - Baji 评估后决定暂缓海外建材采购', 'user_f6a7b8c9d0e1');

-- ── Opportunity Products ───────────────────────────────────────
INSERT INTO opportunity_products (id, opportunity_id, product_id, quantity, unit_price, total_price) VALUES
('opprod_a1b2c3d4e5', 'oppo_a1b2c3d4e5f6', 'prod_e5f6a7b8c9d0', 50, 499, 24950);
INSERT INTO opportunity_products (id, opportunity_id, product_id, quantity, unit_price, total_price) VALUES
('opprod_b2c3d4e5f6', 'oppo_a1b2c3d4e5f6', 'prod_f6a7b8c9d0e1', 20, 1299, 25980);
INSERT INTO opportunity_products (id, opportunity_id, product_id, quantity, unit_price, total_price) VALUES
('opprod_c3d4e5f6a7', 'oppo_b2c3d4e5f6a7', 'prod_b2c3d4e5f6a7', 300, 159.5, 47850);
INSERT INTO opportunity_products (id, opportunity_id, product_id, quantity, unit_price, total_price) VALUES
('opprod_d4e5f6a7b8', 'oppo_c3d4e5f6a7b8', 'prod_e5f6a7b8c9d0', 200, 499, 99800);
INSERT INTO opportunity_products (id, opportunity_id, product_id, quantity, unit_price, total_price) VALUES
('opprod_e5f6a7b8c9', 'oppo_c3d4e5f6a7b8', 'prod_a7b8c9d0e1f2', 30, 3999, 119970);
INSERT INTO opportunity_products (id, opportunity_id, product_id, quantity, unit_price, total_price) VALUES
('opprod_f6a7b8c9d0', 'oppo_d4e5f6a7b8c9', 'prod_f6a7b8c9d0e1', 50, 1299, 64950);
INSERT INTO opportunity_products (id, opportunity_id, product_id, quantity, unit_price, total_price) VALUES
('opprod_a7b8c9d0e1', 'oppo_d4e5f6a7b8c9', 'prod_c3d4e5f6a7b8', 100, 899, 89900);
INSERT INTO opportunity_products (id, opportunity_id, product_id, quantity, unit_price, total_price) VALUES
('opprod_b8c9d0e1f2', 'oppo_e5f6a7b8c9d0', 'prod_a7b8c9d0e1f2', 100, 3999, 399900);
INSERT INTO opportunity_products (id, opportunity_id, product_id, quantity, unit_price, total_price) VALUES
('opprod_c9d0e1f2a3', 'oppo_e5f6a7b8c9d0', 'prod_c3d4e5f6a7b8', 200, 899, 179800);
INSERT INTO opportunity_products (id, opportunity_id, product_id, quantity, unit_price, total_price) VALUES
('opprod_d0e1f2a3b4', 'oppo_f6a7b8c9d0e1', 'prod_c3d4e5f6a7b8', 50, 899, 44950);
INSERT INTO opportunity_products (id, opportunity_id, product_id, quantity, unit_price, total_price) VALUES
('opprod_e1f2a3b4c5', 'oppo_f6a7b8c9d0e1', 'prod_f6a7b8c9d0e1', 30, 1299, 38970);
INSERT INTO opportunity_products (id, opportunity_id, product_id, quantity, unit_price, total_price) VALUES
('opprod_f2a3b4c5d6', 'oppo_a7b8c9d0e1f2', 'prod_e5f6a7b8c9d0', 150, 499, 74850);
INSERT INTO opportunity_products (id, opportunity_id, product_id, quantity, unit_price, total_price) VALUES
('opprod_a3b4c5d6e7', 'oppo_b8c9d0e1f2a3', 'prod_f6a7b8c9d0e1', 200, 1299, 259800);
INSERT INTO opportunity_products (id, opportunity_id, product_id, quantity, unit_price, total_price) VALUES
('opprod_b4c5d6e7f8', 'oppo_b8c9d0e1f2a3', 'prod_e5f6a7b8c9d0', 500, 499, 249500);
INSERT INTO opportunity_products (id, opportunity_id, product_id, quantity, unit_price, total_price) VALUES
('opprod_c5d6e7f8a9', 'oppo_c9d0e1f2a3b4', 'prod_c3d4e5f6a7b8', 100, 899, 89900);
INSERT INTO opportunity_products (id, opportunity_id, product_id, quantity, unit_price, total_price) VALUES
('opprod_d6e7f8a9b0', 'oppo_c9d0e1f2a3b4', 'prod_a1b2c3d4e5f6', 500, 299.99, 149995);
INSERT INTO opportunity_products (id, opportunity_id, product_id, quantity, unit_price, total_price) VALUES
('opprod_e7f8a9b0c1', 'oppo_c9d0e1f2a3b4', 'prod_b2c3d4e5f6a7', 200, 159.5, 31900);
INSERT INTO opportunity_products (id, opportunity_id, product_id, quantity, unit_price, total_price) VALUES
('opprod_f8a9b0c1d2', 'oppo_e1f2a3b4c5d6', 'prod_a7b8c9d0e1f2', 10, 3999, 39990);
INSERT INTO opportunity_products (id, opportunity_id, product_id, quantity, unit_price, total_price) VALUES
('opprod_a9b0c1d2e3', 'oppo_e1f2a3b4c5d6', 'prod_b8c9d0e1f2a3', 500, 79.99, 39995);
INSERT INTO opportunity_products (id, opportunity_id, product_id, quantity, unit_price, total_price) VALUES
('opprod_b0c1d2e3f4', 'oppo_f2a3b4c5d6e7', 'prod_a7b8c9d0e1f2', 80, 3999, 319920);
INSERT INTO opportunity_products (id, opportunity_id, product_id, quantity, unit_price, total_price) VALUES
('opprod_c1d2e3f4a5', 'oppo_f2a3b4c5d6e7', 'prod_a1b2c3d4e5f6', 200, 299.99, 59998);

-- ── Territory Accounts ─────────────────────────────────────────
INSERT INTO territory_accounts (id, territory_id, account_id) VALUES
('tacc_a1b2c3d4e5f6', 'terr_e5f6a7b8c9d0', 'acc_a1b2c3d4e5f6');
INSERT INTO territory_accounts (id, territory_id, account_id) VALUES
('tacc_b2c3d4e5f6a7', 'terr_f6a7b8c9d0e1', 'acc_b2c3d4e5f6a7');
INSERT INTO territory_accounts (id, territory_id, account_id) VALUES
('tacc_c3d4e5f6a7b8', 'terr_a7b8c9d0e1f2', 'acc_c3d4e5f6a7b8');
INSERT INTO territory_accounts (id, territory_id, account_id) VALUES
('tacc_d4e5f6a7b8c9', 'terr_b8c9d0e1f2a3', 'acc_d4e5f6a7b8c9');
INSERT INTO territory_accounts (id, territory_id, account_id) VALUES
('tacc_e5f6a7b8c9d0', 'terr_c9d0e1f2a3b4', 'acc_e5f6a7b8c9d0');
INSERT INTO territory_accounts (id, territory_id, account_id) VALUES
('tacc_f6a7b8c9d0e1', 'terr_d0e1f2a3b4c5', 'acc_f6a7b8c9d0e1');
INSERT INTO territory_accounts (id, territory_id, account_id) VALUES
('tacc_a7b8c9d0e1f2', 'terr_e1f2a3b4c5d6', 'acc_a7b8c9d0e1f2');
INSERT INTO territory_accounts (id, territory_id, account_id) VALUES
('tacc_b8c9d0e1f2a3', 'terr_f2a3b4c5d6e7', 'acc_b8c9d0e1f2a3');
INSERT INTO territory_accounts (id, territory_id, account_id) VALUES
('tacc_c9d0e1f2a3b4', 'terr_f2a3b4c5d6e7', 'acc_c9d0e1f2a3b4');
INSERT INTO territory_accounts (id, territory_id, account_id) VALUES
('tacc_d0e1f2a3b4c5', 'terr_a3b4c5d6e7f8', 'acc_d0e1f2a3b4c5');
INSERT INTO territory_accounts (id, territory_id, account_id) VALUES
('tacc_e1f2a3b4c5d6', 'terr_b4c5d6e7f8a9', 'acc_e1f2a3b4c5d6');

-- ── Territory Products ─────────────────────────────────────────
INSERT INTO territory_products (id, territory_id, product_id, price, is_active) VALUES
('tprod_a1b2c3d4e5', 'terr_e5f6a7b8c9d0', 'prod_e5f6a7b8c9d0', 549, 1);
INSERT INTO territory_products (id, territory_id, product_id, is_active) VALUES
('tprod_b2c3d4e5f6', 'terr_f2a3b4c5d6e7', 'prod_f6a7b8c9d0e1', 1);

-- ── Events (15 rows) ───────────────────────────────────────────
INSERT INTO events (id, subject, type, status, start_datetime, end_datetime, duration_minutes, what_id, what_type, who_id, owner_id, purpose, preparation_notes, description, outcome, next_steps, location) VALUES
('event_a1b2c3d4e5f6', 'Red Russia 能源设备升级方案演示', 'Visit', 'completed', '2026-06-10', '2026-06-10', 105, 'acc_a1b2c3d4e5f6', 'account', 'con_a1b2c3d4e5f6', 'user_d4e5f6a7b8c9', '演示 AeroGel Insulator 和 LumiSheet Display 产品方案', '准备产品样机和技术参数文档', '客户对 AeroGel 很感兴趣，详细了解了技术指标', 'success', '准备报价单并跟进', 'Red Russia 总部 - 莫斯科');
INSERT INTO events (id, subject, type, status, start_datetime, end_datetime, duration_minutes, what_id, what_type, who_id, owner_id, purpose, preparation_notes, description, outcome, next_steps, location) VALUES
('event_b2c3d4e5f6a7', 'Red Russia 量子安全方案讨论', 'Visit', 'completed', '2026-05-15', '2026-05-15', 95, 'oppo_f2a3b4c5d6e7', 'opportunity', 'con_b2c3d4e5f6a7', 'user_d4e5f6a7b8c9', '讨论量子加密方案技术细节和实施计划', '准备技术白皮书和案例', '双方就部署方案达成一致', 'success', '准备合同', 'Red Russia 总部 - 莫斯科');
INSERT INTO events (id, subject, type, status, start_datetime, end_datetime, duration_minutes, what_id, what_type, who_id, owner_id, purpose, preparation_notes, description, outcome, next_steps, location) VALUES
('event_c3d4e5f6a7b8', 'Red Russia 合同签署拜访', 'Visit', 'completed', '2026-05-28', '2026-05-28', 90, 'oppo_f2a3b4c5d6e7', 'opportunity', 'con_a1b2c3d4e5f6', 'user_d4e5f6a7b8c9', '正式签署采购合同', '带齐合同文件和印章', '合同签署顺利完成', 'success', '安排发货', 'Red Russia 总部 - 莫斯科');
INSERT INTO events (id, subject, type, status, start_datetime, end_datetime, duration_minutes, what_id, what_type, who_id, owner_id, purpose, preparation_notes, description, outcome, next_steps, location) VALUES
('event_d4e5f6a7b8c9', 'Libert 健康管理方案初次接触', 'Visit', 'completed', '2026-06-20', '2026-06-20', 75, 'acc_b2c3d4e5f6a7', 'account', 'con_c3d4e5f6a7b8', 'user_e5f6a7b8c9d0', '介绍 BioSync Patch 产品及企业健康管理方案', '准备产品介绍和健康管理方案PPT', '客户VP对方案表示兴趣，希望进行技术评估', 'success', '安排技术演示和样品寄送', 'Libert 硅谷总部');
INSERT INTO events (id, subject, type, status, start_datetime, end_datetime, duration_minutes, what_id, what_type, who_id, owner_id, purpose, preparation_notes, description, outcome, next_steps, location) VALUES
('event_e5f6a7b8c9d0', 'Libert 技术评估会议', 'Video Conference', 'completed', '2026-07-01', '2026-07-01', 50, 'oppo_b2c3d4e5f6a7', 'opportunity', 'con_d4e5f6a7b8c9', 'user_e5f6a7b8c9d0', '线上技术评估会议', '准备技术文档和QA', '技术团队提出了一些兼容性问题', 'neutral', '提供补充技术资料', '线上 - Zoom');
INSERT INTO events (id, subject, type, status, start_datetime, end_datetime, duration_minutes, what_id, what_type, who_id, owner_id, purpose, preparation_notes, description, outcome, next_steps, location) VALUES
('event_f6a7b8c9d0e1', 'Baji 工业传感器项目启动会', 'Visit', 'completed', '2026-06-05', '2026-06-05', 135, 'acc_c3d4e5f6a7b8', 'account', 'con_e5f6a7b8c9d0', 'user_f6a7b8c9d0e1', '项目启动会议，确认需求和范围', '准备项目方案书和报价', '确认了项目范围和初步时间表', 'success', '准备详细实施方案', 'Baji 上海总部');
INSERT INTO events (id, subject, type, status, start_datetime, end_datetime, duration_minutes, what_id, what_type, who_id, owner_id, purpose, preparation_notes, description, outcome, next_steps, location) VALUES
('event_a7b8c9d0e1f2', 'Baji 商务谈判', 'Visit', 'in_progress', '2026-07-16', '2026-07-16', NULL, 'acc_c3d4e5f6a7b8', 'account', 'con_f6a7b8c9d0e1', 'user_f6a7b8c9d0e1', '价格谈判和合同条款讨论', '准备谈判策略和底线价格', '谈判正在进行中', 'neutral', '跟进客户反馈', 'Baji 上海总部 - 会议室A');
INSERT INTO events (id, subject, type, status, start_datetime, end_datetime, duration_minutes, what_id, what_type, who_id, owner_id, purpose, preparation_notes, description, outcome, next_steps, location) VALUES
('event_b8c9d0e1f2a3', 'HHK 量子安全方案初次介绍', 'Visit', 'completed', '2026-07-10', '2026-07-10', 90, 'acc_e5f6a7b8c9d0', 'account', 'con_c9d0e1f2a3b4', 'user_b8c9d0e1f2a3', '介绍量子密钥加密方案', '准备方案PPT和金融行业案例', '客户投资总监表示需要内部评估', 'neutral', '跟进内部评估进展', 'HHK 香港总部');
INSERT INTO events (id, subject, type, status, start_datetime, end_datetime, duration_minutes, what_id, what_type, who_id, owner_id, purpose, preparation_notes, description, outcome, next_steps, location) VALUES
('event_c9d0e1f2a3b4', 'East Tooth 研发设备需求沟通', 'Phone Call', 'completed', '2026-07-05', '2026-07-05', 25, 'acc_f6a7b8c9d0e1', 'account', 'con_e1f2a3b4c5d6', 'user_d0e1f2a3b4c5', '电话沟通设备需求细节', '提前了解客户需求文档', '客户明确了设备清单和预算', 'success', '准备正式报价', '电话沟通');
INSERT INTO events (id, subject, type, status, start_datetime, end_datetime, duration_minutes, what_id, what_type, who_id, owner_id, purpose, preparation_notes, description, outcome, next_steps, location) VALUES
('event_d0e1f2a3b4c5', 'NovaStar 智能管理系统方案评审', 'Visit', 'completed', '2026-06-25', '2026-06-25', 150, 'acc_b8c9d0e1f2a3', 'account', 'con_c5d6e7f8a9b0', 'user_f2a3b4c5d6e7', '方案评审会', '准备完整的技术方案文档', 'CTO对方案表示认可，需调整部署架构', 'success', '调整方案架构后再次提交', 'NovaStar 纽约总部');
INSERT INTO events (id, subject, type, status, start_datetime, end_datetime, duration_minutes, what_id, what_type, who_id, owner_id, purpose, preparation_notes, description, outcome, next_steps, location) VALUES
('event_e1f2a3b4c5d6', 'CrystalLake 合同细节确认', 'Visit', 'completed', '2026-07-12', '2026-07-12', 100, 'oppo_c9d0e1f2a3b4', 'opportunity', 'con_e7f8a9b0c1d2', 'user_f2a3b4c5d6e7', '确认合同最终条款和交付时间', '准备最终合同版本', '双方确认所有条款，即将签署', 'success', '安排合同签署', 'CrystalLake 波士顿总部');
INSERT INTO events (id, subject, type, status, start_datetime, end_datetime, what_id, what_type, who_id, owner_id, purpose, preparation_notes, next_steps, location) VALUES
('event_f2a3b4c5d6e7', 'Puti Tooth 冷链物流需求调研', 'Visit', 'planned', '2026-07-22', '2026-07-22', 'acc_a7b8c9d0e1f2', 'account', 'con_a3b4c5d6e7f8', 'user_e1f2a3b4c5d6', '现场调研冷链物流现有系统和需求', '准备调研问卷和方案框架', '完成调研后输出方案', 'Puti Tooth 伦敦总部');
INSERT INTO events (id, subject, type, status, start_datetime, end_datetime, duration_minutes, what_id, what_type, who_id, owner_id, purpose, preparation_notes, description, outcome, next_steps, location) VALUES
('event_a3b4c5d6e7f8', 'DeepBlue 溯源方案视频沟通', 'Video Conference', 'completed', '2026-07-08', '2026-07-08', 50, 'acc_e1f2a3b4c5d6', 'account', 'con_a9b0c1d2e3f4', 'user_b4c5d6e7f8a9', '远程演示溯源系统方案', '准备方案演示和Demo环境', '客户CEO对方案感兴趣，希望进一步了解', 'success', '安排下一次详细技术交流', '线上 - Teams');
INSERT INTO events (id, subject, type, status, start_datetime, end_datetime, duration_minutes, what_id, what_type, who_id, owner_id, purpose, preparation_notes, description, outcome, next_steps, location) VALUES
('event_b4c5d6e7f8a9', 'Taji 门店数字化方案演示', 'Visit', 'completed', '2026-06-28', '2026-06-28', 150, 'acc_d4e5f6a7b8c9', 'account', 'con_a7b8c9d0e1f2', 'user_a7b8c9d0e1f2', '现场演示数字化门店解决方案', '准备Demo环境和案例视频', '客户CEO非常认可方案', 'success', '准备项目报价', 'Taji 杭州总部 - 展示厅');

-- ── Tasks (13 rows) ────────────────────────────────────────────
INSERT INTO tasks (id, event_id, subject, status, priority, assignee_id, activity_date) VALUES
('task_a1b2c3d4e5f6', 'event_a1b2c3d4e5f6', '准备 Red Russia 报价单', 'completed', 'high', 'user_d4e5f6a7b8c9', '2026-06-12');
INSERT INTO tasks (id, event_id, subject, status, priority, assignee_id, activity_date) VALUES
('task_b2c3d4e5f6a7', 'event_a1b2c3d4e5f6', '跟进 Red Russia 技术参数确认', 'in_progress', 'medium', 'user_d4e5f6a7b8c9', '2026-06-20');
INSERT INTO tasks (id, event_id, subject, status, priority, assignee_id, activity_date) VALUES
('task_c3d4e5f6a7b8', 'event_d4e5f6a7b8c9', '寄送 BioSync Patch 样品', 'completed', 'high', 'user_e5f6a7b8c9d0', '2026-06-25');
INSERT INTO tasks (id, event_id, subject, status, priority, assignee_id, activity_date) VALUES
('task_d4e5f6a7b8c9', 'event_e5f6a7b8c9d0', '准备 Libert 技术补充资料', 'pending', 'high', 'user_e5f6a7b8c9d0', '2026-07-08');
INSERT INTO tasks (id, event_id, subject, status, priority, assignee_id, activity_date) VALUES
('task_e5f6a7b8c9d0', 'event_f6a7b8c9d0e1', '编写 Baji 详细实施方案', 'completed', 'high', 'user_f6a7b8c9d0e1', '2026-06-15');
INSERT INTO tasks (id, event_id, subject, status, priority, assignee_id, activity_date) VALUES
('task_f6a7b8c9d0e1', 'event_a7b8c9d0e1f2', 'Baji 谈判后续 - 整理客户反馈', 'pending', 'medium', 'user_f6a7b8c9d0e1', '2026-07-20');
INSERT INTO tasks (id, event_id, subject, status, priority, assignee_id, activity_date) VALUES
('task_a7b8c9d0e1f2', 'event_c9d0e1f2a3b4', '准备 East Tooth 正式报价', 'in_progress', 'high', 'user_d0e1f2a3b4c5', '2026-07-10');
INSERT INTO tasks (id, event_id, subject, status, priority, assignee_id, activity_date) VALUES
('task_b8c9d0e1f2a3', 'event_d0e1f2a3b4c5', '调整 NovaStar 方案架构', 'in_progress', 'high', 'user_f2a3b4c5d6e7', '2026-07-03');
INSERT INTO tasks (id, event_id, subject, status, priority, assignee_id, activity_date) VALUES
('task_c9d0e1f2a3b4', 'event_e1f2a3b4c5d6', '准备 CrystalLake 合同终版', 'completed', 'high', 'user_f2a3b4c5d6e7', '2026-07-15');
INSERT INTO tasks (id, event_id, subject, status, priority, assignee_id, activity_date) VALUES
('task_d0e1f2a3b4c5', 'event_e1f2a3b4c5d6', '安排 CrystalLake 合同签署', 'pending', 'high', 'user_f2a3b4c5d6e7', '2026-07-18');
INSERT INTO tasks (id, event_id, subject, status, priority, assignee_id, activity_date) VALUES
('task_e1f2a3b4c5d6', 'event_b8c9d0e1f2a3', '跟进 HHK 内部评估进展', 'in_progress', 'medium', 'user_b8c9d0e1f2a3', '2026-07-25');
INSERT INTO tasks (id, event_id, subject, status, priority, assignee_id, activity_date) VALUES
('task_f2a3b4c5d6e7', 'event_f2a3b4c5d6e7', '准备 Puti Tooth 调研报告', 'pending', 'medium', 'user_e1f2a3b4c5d6', '2026-07-25');
INSERT INTO tasks (id, event_id, subject, status, priority, assignee_id, activity_date) VALUES
('task_a3b4c5d6e7f8', 'event_b4c5d6e7f8a9', '准备 Taji 项目报价', 'pending', 'high', 'user_a7b8c9d0e1f2', '2026-07-05');

-- ── Reports ────────────────────────────────────────────────────
INSERT INTO reports (id, name, object_type, report_type, owner_id) VALUES
('rpt_a1b2c3d4e5f6', '本月赢单分析', 'opportunity', 'summary', 'user_b2c3d4e5f6a7');
INSERT INTO reports (id, name, object_type, report_type, owner_id) VALUES
('rpt_b2c3d4e5f6a7', '亚洲区商机清单', 'opportunity', 'tabular', 'user_c3d4e5f6a7b8');
INSERT INTO reports (id, name, object_type, report_type, owner_id) VALUES
('rpt_c3d4e5f6a7b8', '欧洲区拜访统计', 'event', 'summary', 'user_c9d0e1f2a3b4');
INSERT INTO reports (id, name, object_type, report_type, owner_id) VALUES
('rpt_d4e5f6a7b8c9', '产品销售额排行', 'product', 'tabular', 'user_b2c3d4e5f6a7');
INSERT INTO reports (id, name, object_type, report_type, owner_id) VALUES
('rpt_e5f6a7b8c9d0', '本周待办任务', 'task', 'tabular', 'user_b2c3d4e5f6a7');

-- ── Dashboards ─────────────────────────────────────────────────
INSERT INTO dashboards (id, name, owner_id) VALUES
('dsb_a1b2c3d4e5f6', '销售管理仪表盘', 'user_b2c3d4e5f6a7');
INSERT INTO dashboards (id, name, owner_id) VALUES
('dsb_b2c3d4e5f6a7', '区域业绩看板', 'user_b2c3d4e5f6a7');

-- ── Dashboard Components ───────────────────────────────────────
INSERT INTO dashboard_components (id, dashboard_id, report_id, title, chart_type, position_x, position_y, width, height) VALUES
('dsc_a1b2c3d4e5f6', 'dsb_a1b2c3d4e5f6', 'rpt_a1b2c3d4e5f6', '本月赢单', 'pie', 0, 0, 4, 3);
INSERT INTO dashboard_components (id, dashboard_id, report_id, title, chart_type, position_x, position_y, width, height) VALUES
('dsc_b2c3d4e5f6a7', 'dsb_a1b2c3d4e5f6', 'rpt_d4e5f6a7b8c9', '产品排行', 'bar', 4, 0, 4, 3);
INSERT INTO dashboard_components (id, dashboard_id, report_id, title, chart_type, position_x, position_y, width, height) VALUES
('dsc_c3d4e5f6a7b8', 'dsb_a1b2c3d4e5f6', 'rpt_e5f6a7b8c9d0', '待办任务', 'table', 8, 0, 4, 3);
INSERT INTO dashboard_components (id, dashboard_id, report_id, title, chart_type, position_x, position_y, width, height) VALUES
('dsc_d4e5f6a7b8c9', 'dsb_b2c3d4e5f6a7', 'rpt_b2c3d4e5f6a7', '亚洲商机', 'table', 0, 0, 6, 3);
INSERT INTO dashboard_components (id, dashboard_id, report_id, title, chart_type, position_x, position_y, width, height) VALUES
('dsc_e5f6a7b8c9d0', 'dsb_b2c3d4e5f6a7', 'rpt_c3d4e5f6a7b8', '欧洲拜访', 'bar', 6, 0, 6, 3);

-- ── Custom Objects ─────────────────────────────────────────────
INSERT INTO custom_object_defs (id, api_name, label, plural_label, table_name, description) VALUES
('cod_a1b2c3d4e5f6', 'custom_invoice', '发票', '发票列表', 'obj_cod_a1b2c3d4e5f6', '自定义发票管理');
INSERT INTO custom_field_defs (id, object_id, api_name, label, field_type, is_required, display_order) VALUES
('cfd_a1b2c3d4e5f6', 'cod_a1b2c3d4e5f6', 'invoice_number', '发票编号', 'text', 1, 0);
INSERT INTO custom_field_defs (id, object_id, api_name, label, field_type, display_order) VALUES
('cfd_b2c3d4e5f6a7', 'cod_a1b2c3d4e5f6', 'amount', '金额', 'number', 1);
INSERT INTO custom_field_defs (id, object_id, api_name, label, field_type, picklist_values, display_order) VALUES
('cfd_c3d4e5f6a7b8', 'cod_a1b2c3d4e5f6', 'status', '状态', 'picklist', '["待付款","已付款"]', 2);
INSERT INTO custom_object_defs (id, api_name, label, plural_label, table_name, description) VALUES
('cod_b2c3d4e5f6a7', 'custom_contract', '合同', '合同列表', 'obj_cod_b2c3d4e5f6a7', '自定义合同管理');
INSERT INTO custom_field_defs (id, object_id, api_name, label, field_type, is_required, display_order) VALUES
('cfd_d4e5f6a7b8c9', 'cod_b2c3d4e5f6a7', 'contract_number', '合同编号', 'text', 1, 0);
INSERT INTO custom_field_defs (id, object_id, api_name, label, field_type, display_order) VALUES
('cfd_e5f6a7b8c9d0', 'cod_b2c3d4e5f6a7', 'contract_value', '合同金额', 'number', 1);
INSERT INTO custom_field_defs (id, object_id, api_name, label, field_type, display_order) VALUES
('cfd_f6a7b8c9d0e1', 'cod_b2c3d4e5f6a7', 'sign_date', '签署日期', 'date', 2);
INSERT INTO custom_field_defs (id, object_id, api_name, label, field_type, display_order) VALUES
('cfd_a7b8c9d0e1f2', 'cod_b2c3d4e5f6a7', 'contract_type', '合同类型', 'picklist', 3);
INSERT INTO custom_field_defs (id, object_id, api_name, label, field_type, display_order) VALUES
('cfd_b8c9d0e1f2a3', 'cod_b2c3d4e5f6a7', 'description', '备注', 'textarea', 4);

-- ── Workflow Rules ─────────────────────────────────────────────
INSERT INTO workflow_rules (id, name, object_type, trigger_event, condition_expression, is_active) VALUES
('wf_a1b2c3d4e5f6', '高价值商机通知', 'opportunity', 'create', '[{"field":"amount","operator":"gt","value":500000}]', 1);
INSERT INTO workflow_actions (id, workflow_id, action_type, action_config, display_order) VALUES
('wfa_a1b2c3d4e5f6', 'wf_a1b2c3d4e5f6', 'notification', '{"channels":["email"],"template":"high_value_opportunity"}', 0);
INSERT INTO workflow_rules (id, name, object_type, trigger_event, is_active) VALUES
('wf_b2c3d4e5f6a7', '赢单后自动通知', 'opportunity', 'update', 1);
INSERT INTO workflow_actions (id, workflow_id, action_type, action_config, display_order) VALUES
('wfa_b2c3d4e5f6a7', 'wf_b2c3d4e5f6a7', 'notification', '{"channels":["email","in_app"],"template":"won_deal"}', 0);
INSERT INTO workflow_execution_logs (id, workflow_id, object_type, record_id, conditions_met, action_executed, result_message) VALUES
('wfl_a1b2c3d4e5f6', 'wf_a1b2c3d4e5f6', 'opportunity', 'oppo_e5f6a7b8c9d0', 1, 1, '通知已发送');
INSERT INTO workflow_execution_logs (id, workflow_id, object_type, record_id, conditions_met, action_executed) VALUES
('wfl_b2c3d4e5f6a7', 'wf_a1b2c3d4e5f6', 'opportunity', 'oppo_d0e1f2a3b4c5', 1, 1);
INSERT INTO workflow_execution_logs (id, workflow_id, object_type, record_id, conditions_met, action_executed, result_message) VALUES
('wfl_c3d4e5f6a7b8', 'wf_b2c3d4e5f6a7', 'opportunity', 'oppo_f2a3b4c5d6e7', 1, 1, '赢单通知已发送');
