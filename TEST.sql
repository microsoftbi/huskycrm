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

-- ── 用户 ─────────────────────────────────────────────────────
INSERT OR IGNORE INTO users (id, username, email, password_hash, display_name, is_active, is_superuser, created_at, updated_at) VALUES
('user_a1b2c3d4e5f6', 'admin', 'admin@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'Administrator', 1, 1, datetime('now'), datetime('now')),
('user_b2c3d4e5f6a7', 'Global_CEO', 'ceo@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'Global CEO', 1, 0, datetime('now'), datetime('now')),
('user_c3d4e5f6a7b8', 'Asia_manager', 'asia.mgr@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'Asia Manager', 1, 0, datetime('now'), datetime('now')),
('user_d4e5f6a7b8c9', 'Asia_RedRussia_sales', 'red.russia@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'Red Russia Sales', 1, 0, datetime('now'), datetime('now')),
('user_e5f6a7b8c9d0', 'Asia_Libert_sales', 'libert.sales@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'Libert Sales', 1, 0, datetime('now'), datetime('now')),
('user_f6a7b8c9d0e1', 'Asia_Baji_sales', 'baji.sales@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'Baji Sales', 1, 0, datetime('now'), datetime('now')),
('user_a7b8c9d0e1f2', 'Asia_Taji_sales', 'taji.sales@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'Taji Sales', 1, 0, datetime('now'), datetime('now')),
('user_b8c9d0e1f2a3', 'Asia_HHK_sales', 'hhk.sales@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'HHK Sales', 1, 0, datetime('now'), datetime('now')),
('user_c9d0e1f2a3b4', 'Europe_manager', 'europe.mgr@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'Europe Manager', 1, 0, datetime('now'), datetime('now')),
('user_d0e1f2a3b4c5', 'Europe_EastTooth_sales', 'east.tooth@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'East Tooth Sales', 1, 0, datetime('now'), datetime('now')),
('user_e1f2a3b4c5d6', 'Europe_PutiTooth_sales', 'puti.tooth@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'Puti Tooth Sales', 1, 0, datetime('now'), datetime('now')),
('user_f2a3b4c5d6e7', 'America_manager', 'america.mgr@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'America Manager', 1, 0, datetime('now'), datetime('now')),
('user_a3b4c5d6e7f8', 'Africa_manager', 'africa.mgr@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'Africa Manager', 1, 0, datetime('now'), datetime('now')),
('user_b4c5d6e7f8a9', 'Oceania_manager', 'oceania.mgr@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'Oceania Manager', 1, 0, datetime('now'), datetime('now')),
('user_c5d6e7f8a9b0', 'Antarctica_manager', 'antarctica.mgr@huskycrm.local', '$2b$12$gCx0Z2gvO4rdmNgLBImeOOb5dif6xyKaQ8AOiM3tSJZuX0VkTR/P6', 'Antarctica Manager', 1, 0, datetime('now'), datetime('now'));

-- ── 产品 ─────────────────────────────────────────────────────
INSERT INTO products (id, name, product_code, description, price, cost, category, is_active, created_at, updated_at) VALUES
('prod_a1b2c3d4e5f6', 'HydroFlux Capsule', 'HF-001', '高纯度水萃取物胶囊', 299.99, 120.00, '保健品', 1, datetime('now'), datetime('now')),
('prod_b2c3d4e5f6a7', 'BioSync Patch', 'BS-002', '生物同步贴片', 159.50, 65.00, '医疗器械', 1, datetime('now'), datetime('now')),
('prod_c3d4e5f6a7b8', 'NeuroPulse Headset', 'NP-003', '神经脉冲头戴设备', 899.00, 420.00, '电子设备', 1, datetime('now'), datetime('now')),
('prod_d4e5f6a7b8c9', 'ChronoWrist Watch', 'CW-004', '计时腕表 - 限量版', 2499.99, 1100.00, '配件', 1, datetime('now'), datetime('now')),
('prod_e5f6a7b8c9d0', 'AeroGel Insulator', 'AG-005', '气凝胶保温材料（工业级）', 499.00, 210.00, '工业材料', 1, datetime('now'), datetime('now')),
('prod_f6a7b8c9d0e1', 'LumiSheet Display', 'LS-006', '发光薄膜显示屏', 1299.00, 580.00, '电子设备', 1, datetime('now'), datetime('now')),
('prod_a7b8c9d0e1f2', 'QuantumKey Encryptor', 'QK-007', '量子密钥加密器', 3999.00, 1800.00, '安全设备', 1, datetime('now'), datetime('now')),
('prod_b8c9d0e1f2a3', 'EcoBrick Foundation', 'EB-008', '生态砖基础模块（建材级）', 79.99, 35.00, '建筑材料', 1, datetime('now'), datetime('now'));

-- ── 账户 ─────────────────────────────────────────────────────
INSERT INTO accounts (id, name, industry, phone, email, description, owner_id, created_at, updated_at) VALUES
('acc_a1b2c3d4e5f6', 'Red Russia Corp', '能源', '+7-495-111-2233', 'info@redrussia.ru', '俄罗斯红色能源公司 - 亚太区客户', 'user_c3d4e5f6a7b8', datetime('now'), datetime('now')),
('acc_b2c3d4e5f6a7', 'Libert Group', '科技', '+1-555-0102', 'info@libert.com', 'Libert 科技集团 - 亚太区客户', 'user_c3d4e5f6a7b8', datetime('now'), datetime('now')),
('acc_c3d4e5f6a7b8', 'Baji Industries', '制造', '+86-21-8888-0001', 'info@baji.cn', '巴吉工业 - 亚太区客户', 'user_c3d4e5f6a7b8', datetime('now'), datetime('now')),
('acc_d4e5f6a7b8c9', 'Taji & Co', '零售', '+86-571-6666-7777', 'info@taji.com', '塔吉贸易 - 亚太区客户', 'user_c3d4e5f6a7b8', datetime('now'), datetime('now')),
('acc_e5f6a7b8c9d0', 'HHK Corporation', '金融', '+852-2222-3333', 'info@hhk.hk', 'HHK 集团 - 亚太区客户', 'user_c3d4e5f6a7b8', datetime('now'), datetime('now')),
('acc_f6a7b8c9d0e1', 'East Tooth GmbH', '医药', '+49-30-1111-0001', 'info@east-tooth.de', 'East Tooth 医药 - 欧洲区客户', 'user_c9d0e1f2a3b4', datetime('now'), datetime('now')),
('acc_a7b8c9d0e1f2', 'Puti Tooth Ltd', '食品', '+44-20-7777-8888', 'info@puti-tooth.co.uk', 'Puti Tooth 食品 - 欧洲区客户', 'user_c9d0e1f2a3b4', datetime('now'), datetime('now')),
('acc_b8c9d0e1f2a3', 'NovaStar Energy', '能源', '+1-212-333-4444', 'info@novastar.com', 'NovaStar 新能源 - 美洲区客户', 'user_f2a3b4c5d6e7', datetime('now'), datetime('now')),
('acc_c9d0e1f2a3b4', 'CrystalLake Pharma', '医药', '+1-617-555-0101', 'info@crystallake.com', 'CrystalLake 制药 - 美洲区客户', 'user_f2a3b4c5d6e7', datetime('now'), datetime('now')),
('acc_d0e1f2a3b4c5', 'GoldenSands Mining', '矿业', '+27-21-444-5555', 'info@goldensands.za', 'GoldenSands 矿业 - 非洲区客户', 'user_a3b4c5d6e7f8', datetime('now'), datetime('now')),
('acc_e1f2a3b4c5d6', 'DeepBlue Fisheries', '农业', '+61-2-9999-0000', 'info@deepblue.au', 'DeepBlue 渔业 - 大洋洲客户', 'user_b4c5d6e7f8a9', datetime('now'), datetime('now'));

-- ── 联系人 ───────────────────────────────────────────────────
INSERT INTO contacts (id, first_name, last_name, email, phone, title, department, owner_id, created_at, updated_at) VALUES
('con_a1b2c3d4e5f6', 'Ivan', 'Petrov', 'ivan@redrussia.ru', '+7-495-111-2234', '采购总监', '采购部', 'user_d4e5f6a7b8c9', datetime('now'), datetime('now')),
('con_b2c3d4e5f6a7', 'Olga', 'Smirnova', 'olga@redrussia.ru', '+7-495-111-2235', '技术主管', '技术部', 'user_d4e5f6a7b8c9', datetime('now'), datetime('now')),
('con_c3d4e5f6a7b8', 'John', 'Smith', 'john@libert.com', '+1-555-0103', 'VP Engineering', '工程部', 'user_e5f6a7b8c9d0', datetime('now'), datetime('now')),
('con_d4e5f6a7b8c9', 'Alice', 'Wang', 'alice@libert.com', '+1-555-0104', '产品经理', '产品部', 'user_e5f6a7b8c9d0', datetime('now'), datetime('now')),
('con_e5f6a7b8c9d0', '张', '伟', 'zhangwei@baji.cn', '+86-21-8888-0002', '供应链总监', '供应链部', 'user_f6a7b8c9d0e1', datetime('now'), datetime('now')),
('con_f6a7b8c9d0e1', '李', '娜', 'lina@baji.cn', '+86-21-8888-0003', '采购经理', '采购部', 'user_f6a7b8c9d0e1', datetime('now'), datetime('now')),
('con_a7b8c9d0e1f2', '王', '磊', 'wanglei@taji.com', '+86-571-6666-7778', 'CEO', '管理层', 'user_a7b8c9d0e1f2', datetime('now'), datetime('now')),
('con_b8c9d0e1f2a3', '陈', '静', 'chenjing@taji.com', '+86-571-6666-7779', '财务总监', '财务部', 'user_a7b8c9d0e1f2', datetime('now'), datetime('now')),
('con_c9d0e1f2a3b4', 'Michael', 'Chan', 'michael@hhk.hk', '+852-2222-3334', '投资总监', '投资部', 'user_b8c9d0e1f2a3', datetime('now'), datetime('now')),
('con_d0e1f2a3b4c5', 'Sarah', 'Lau', 'sarah@hhk.hk', '+852-2222-3335', '合规官', '合规部', 'user_b8c9d0e1f2a3', datetime('now'), datetime('now')),
('con_e1f2a3b4c5d6', 'Hans', 'Mueller', 'hans@east-tooth.de', '+49-30-1111-0002', '研发总监', '研发部', 'user_d0e1f2a3b4c5', datetime('now'), datetime('now')),
('con_f2a3b4c5d6e7', 'Klaus', 'Schmidt', 'klaus@east-tooth.de', '+49-30-1111-0003', '采购主管', '采购部', 'user_d0e1f2a3b4c5', datetime('now'), datetime('now')),
('con_a3b4c5d6e7f8', 'James', 'Brown', 'james@puti-tooth.co.uk', '+44-20-7777-8889', '市场总监', '市场部', 'user_e1f2a3b4c5d6', datetime('now'), datetime('now')),
('con_b4c5d6e7f8a9', 'Emily', 'Taylor', 'emily@puti-tooth.co.uk', '+44-20-7777-8890', '销售VP', '销售部', 'user_e1f2a3b4c5d6', datetime('now'), datetime('now')),
('con_c5d6e7f8a9b0', 'Bob', 'Johnson', 'bob@novastar.com', '+1-212-333-4445', 'CTO', '技术部', 'user_f2a3b4c5d6e7', datetime('now'), datetime('now')),
('con_d6e7f8a9b0c1', 'Maria', 'Garcia', 'maria@novastar.com', '+1-212-333-4446', '运营总监', '运营部', 'user_f2a3b4c5d6e7', datetime('now'), datetime('now')),
('con_e7f8a9b0c1d2', 'David', 'Lee', 'david@crystallake.com', '+1-617-555-0102', '首席科学家', '研发部', 'user_f2a3b4c5d6e7', datetime('now'), datetime('now')),
('con_f8a9b0c1d2e3', 'Grace', 'Kim', 'grace@goldensands.za', '+27-21-444-5556', '采购总监', '采购部', 'user_a3b4c5d6e7f8', datetime('now'), datetime('now')),
('con_a9b0c1d2e3f4', 'Tom', 'Wilson', 'tom@deepblue.au', '+61-2-9999-0001', 'CEO', '管理层', 'user_b4c5d6e7f8a9', datetime('now'), datetime('now')),
('con_b0c1d2e3f4a5', 'Lucy', 'Brown', 'lucy@deepblue.au', '+61-2-9999-0002', '销售总监', '销售部', 'user_b4c5d6e7f8a9', datetime('now'), datetime('now'));

-- ── 联系人-账户关联 ──────────────────────────────────────────
INSERT INTO contact_accounts (id, contact_id, account_id, assigned_at) VALUES
('conacc_a1b2c3d4e5', 'con_a1b2c3d4e5f6', 'acc_a1b2c3d4e5f6', datetime('now')),
('conacc_b2c3d4e5f6', 'con_b2c3d4e5f6a7', 'acc_a1b2c3d4e5f6', datetime('now')),
('conacc_c3d4e5f6a7', 'con_c3d4e5f6a7b8', 'acc_b2c3d4e5f6a7', datetime('now')),
('conacc_d4e5f6a7b8', 'con_d4e5f6a7b8c9', 'acc_b2c3d4e5f6a7', datetime('now')),
('conacc_e5f6a7b8c9', 'con_e5f6a7b8c9d0', 'acc_c3d4e5f6a7b8', datetime('now')),
('conacc_f6a7b8c9d0', 'con_f6a7b8c9d0e1', 'acc_c3d4e5f6a7b8', datetime('now')),
('conacc_a7b8c9d0e1', 'con_a7b8c9d0e1f2', 'acc_d4e5f6a7b8c9', datetime('now')),
('conacc_b8c9d0e1f2', 'con_b8c9d0e1f2a3', 'acc_d4e5f6a7b8c9', datetime('now')),
('conacc_c9d0e1f2a3', 'con_c9d0e1f2a3b4', 'acc_e5f6a7b8c9d0', datetime('now')),
('conacc_d0e1f2a3b4', 'con_d0e1f2a3b4c5', 'acc_e5f6a7b8c9d0', datetime('now')),
('conacc_e1f2a3b4c5', 'con_e1f2a3b4c5d6', 'acc_f6a7b8c9d0e1', datetime('now')),
('conacc_f2a3b4c5d6', 'con_f2a3b4c5d6e7', 'acc_f6a7b8c9d0e1', datetime('now')),
('conacc_a3b4c5d6e7', 'con_a3b4c5d6e7f8', 'acc_a7b8c9d0e1f2', datetime('now')),
('conacc_b4c5d6e7f8', 'con_b4c5d6e7f8a9', 'acc_a7b8c9d0e1f2', datetime('now')),
('conacc_c5d6e7f8a9', 'con_c5d6e7f8a9b0', 'acc_b8c9d0e1f2a3', datetime('now')),
('conacc_d6e7f8a9b0', 'con_d6e7f8a9b0c1', 'acc_b8c9d0e1f2a3', datetime('now')),
('conacc_e7f8a9b0c1', 'con_e7f8a9b0c1d2', 'acc_c9d0e1f2a3b4', datetime('now')),
('conacc_f8a9b0c1d2', 'con_f8a9b0c1d2e3', 'acc_d0e1f2a3b4c5', datetime('now')),
('conacc_a9b0c1d2e3', 'con_a9b0c1d2e3f4', 'acc_e1f2a3b4c5d6', datetime('now')),
('conacc_b0c1d2e3f4', 'con_b0c1d2e3f4a5', 'acc_e1f2a3b4c5d6', datetime('now'));

-- ── 销售阶段 ─────────────────────────────────────────────────
INSERT INTO stages (id, name, probability, sort_order, is_closed_won, is_closed_lost) VALUES
('stg_a1b2c3d4e5f6', '初步接触', 10, 1, 0, 0),
('stg_b2c3d4e5f6a7', '需求分析', 30, 2, 0, 0),
('stg_c3d4e5f6a7b8', '方案制定', 50, 3, 0, 0),
('stg_d4e5f6a7b8c9', '商务谈判', 70, 4, 0, 0),
('stg_e5f6a7b8c9d0', '合同签订', 90, 5, 0, 0),
('stg_f6a7b8c9d0e1', '赢单', 100, 6, 1, 0),
('stg_a7b8c9d0e1f2', '输单', 0, 7, 0, 1);

-- ── 商机 ─────────────────────────────────────────────────────
INSERT INTO opportunities (id, name, account_id, stage_id, amount, probability, close_date, description, owner_id, created_at, updated_at) VALUES
('oppo_a1b2c3d4e5f6', 'Red Russia 能源设备升级', 'acc_a1b2c3d4e5f6', 'stg_c3d4e5f6a7b8', 150000.00, 50, '2026-08-15', '俄罗斯客户能源设备升级项目', 'user_d4e5f6a7b8c9', datetime('now'), datetime('now'));

-- ── 商机产品 ─────────────────────────────────────────────────
INSERT INTO opportunity_products (id, opportunity_id, product_id, quantity, unit_price, total_price, created_at) VALUES
('opprod_a1b2c3d4e5', 'oppo_a1b2c3d4e5f6', 'prod_e5f6a7b8c9d0', 50, 499.00, 24950.00, datetime('now')),
('opprod_b2c3d4e5f6', 'oppo_a1b2c3d4e5f6', 'prod_f6a7b8c9d0e1', 20, 1299.00, 25980.00, datetime('now'));

-- ── 区域 ─────────────────────────────────────────────────────
INSERT INTO territories (id, name, code, territory_type, parent_id, description, is_active, owner_id, created_at, updated_at) VALUES
('terr_a1b2c3d4e5f6', 'Global', 'GL', 'region', NULL, '全球总部', 1, 'user_b2c3d4e5f6a7', datetime('now'), datetime('now')),
('terr_b2c3d4e5f6a7', 'Asia', 'ASIA', 'region', 'terr_a1b2c3d4e5f6', '亚太区域', 1, 'user_c3d4e5f6a7b8', datetime('now'), datetime('now')),
('terr_c3d4e5f6a7b8', 'Europe', 'EU', 'region', 'terr_a1b2c3d4e5f6', '欧洲区域', 1, 'user_c9d0e1f2a3b4', datetime('now'), datetime('now')),
('terr_d4e5f6a7b8c9', 'America', 'AM', 'region', 'terr_a1b2c3d4e5f6', '美洲区域', 1, 'user_f2a3b4c5d6e7', datetime('now'), datetime('now')),
('terr_e5f6a7b8c9d0', 'Asia_RedRussia', 'ASIA_RR', 'district', 'terr_b2c3d4e5f6a7', '红俄罗斯（亚洲分部）', 1, 'user_d4e5f6a7b8c9', datetime('now'), datetime('now')),
('terr_f6a7b8c9d0e1', 'Asia_Libert', 'ASIA_LBT', 'district', 'terr_b2c3d4e5f6a7', 'Libert（亚洲分部）', 1, 'user_e5f6a7b8c9d0', datetime('now'), datetime('now')),
('terr_a7b8c9d0e1f2', 'Asia_Baji', 'ASIA_BJ', 'district', 'terr_b2c3d4e5f6a7', 'Baji（亚洲分部）', 1, 'user_f6a7b8c9d0e1', datetime('now'), datetime('now')),
('terr_b8c9d0e1f2a3', 'Asia_Taji', 'ASIA_TJ', 'district', 'terr_b2c3d4e5f6a7', 'Taji（亚洲分部）', 1, 'user_a7b8c9d0e1f2', datetime('now'), datetime('now')),
('terr_c9d0e1f2a3b4', 'Asia_HHK', 'ASIA_HHK', 'district', 'terr_b2c3d4e5f6a7', 'HHK（亚洲分部）', 1, 'user_b8c9d0e1f2a3', datetime('now'), datetime('now')),
('terr_d0e1f2a3b4c5', 'Europe_EastTooth', 'EU_ET', 'district', 'terr_c3d4e5f6a7b8', 'East Tooth（欧洲分部）', 1, 'user_d0e1f2a3b4c5', datetime('now'), datetime('now')),
('terr_e1f2a3b4c5d6', 'Europe_PutiTooth', 'EU_PT', 'district', 'terr_c3d4e5f6a7b8', 'Puti Tooth（欧洲分部）', 1, 'user_e1f2a3b4c5d6', datetime('now'), datetime('now')),
('terr_f2a3b4c5d6e7', 'America_NovaStar', 'AM_NS', 'district', 'terr_d4e5f6a7b8c9', 'NovaStar（美洲分部）', 1, 'user_f2a3b4c5d6e7', datetime('now'), datetime('now')),
('terr_a3b4c5d6e7f8', 'Africa_GoldenSands', 'AF_GS', 'district', 'terr_a1b2c3d4e5f6', 'GoldenSands（非洲）', 1, 'user_a3b4c5d6e7f8', datetime('now'), datetime('now')),
('terr_b4c5d6e7f8a9', 'Oceania_DeepBlue', 'OC_DB', 'district', 'terr_a1b2c3d4e5f6', 'DeepBlue（大洋洲）', 1, 'user_b4c5d6e7f8a9', datetime('now'), datetime('now'));

-- ── 区域成员 ─────────────────────────────────────────────────
INSERT INTO territory_members (id, territory_id, user_id, role, assigned_at) VALUES
('tmem_a1b2c3d4e5f6', 'terr_a1b2c3d4e5f6', 'user_b2c3d4e5f6a7', 'manager', datetime('now')),
('tmem_b2c3d4e5f6a7', 'terr_b2c3d4e5f6a7', 'user_c3d4e5f6a7b8', 'manager', datetime('now')),
('tmem_c3d4e5f6a7b8', 'terr_e5f6a7b8c9d0', 'user_d4e5f6a7b8c9', 'manager', datetime('now')),
('tmem_d4e5f6a7b8c9', 'terr_f6a7b8c9d0e1', 'user_e5f6a7b8c9d0', 'manager', datetime('now')),
('tmem_e5f6a7b8c9d0', 'terr_a7b8c9d0e1f2', 'user_f6a7b8c9d0e1', 'manager', datetime('now')),
('tmem_f6a7b8c9d0e1', 'terr_b8c9d0e1f2a3', 'user_a7b8c9d0e1f2', 'manager', datetime('now')),
('tmem_a7b8c9d0e1f2', 'terr_c9d0e1f2a3b4', 'user_b8c9d0e1f2a3', 'manager', datetime('now')),
('tmem_b8c9d0e1f2a3', 'terr_c3d4e5f6a7b8', 'user_c9d0e1f2a3b4', 'manager', datetime('now')),
('tmem_c9d0e1f2a3b4', 'terr_d0e1f2a3b4c5', 'user_d0e1f2a3b4c5', 'manager', datetime('now')),
('tmem_d0e1f2a3b4c5', 'terr_e1f2a3b4c5d6', 'user_e1f2a3b4c5d6', 'manager', datetime('now')),
('tmem_e1f2a3b4c5d6', 'terr_d4e5f6a7b8c9', 'user_f2a3b4c5d6e7', 'manager', datetime('now')),
('tmem_f2a3b4c5d6e7', 'terr_f2a3b4c5d6e7', 'user_f2a3b4c5d6e7', 'manager', datetime('now')),
('tmem_a3b4c5d6e7f8', 'terr_a3b4c5d6e7f8', 'user_a3b4c5d6e7f8', 'manager', datetime('now')),
('tmem_b4c5d6e7f8a9', 'terr_b4c5d6e7f8a9', 'user_b4c5d6e7f8a9', 'manager', datetime('now'));

-- ── 区域-账户关联 ────────────────────────────────────────────
INSERT INTO territory_accounts (id, territory_id, account_id, assigned_at) VALUES
('tacc_a1b2c3d4e5f6', 'terr_e5f6a7b8c9d0', 'acc_a1b2c3d4e5f6', datetime('now')),
('tacc_b2c3d4e5f6a7', 'terr_f6a7b8c9d0e1', 'acc_b2c3d4e5f6a7', datetime('now')),
('tacc_c3d4e5f6a7b8', 'terr_a7b8c9d0e1f2', 'acc_c3d4e5f6a7b8', datetime('now')),
('tacc_d4e5f6a7b8c9', 'terr_b8c9d0e1f2a3', 'acc_d4e5f6a7b8c9', datetime('now')),
('tacc_e5f6a7b8c9d0', 'terr_c9d0e1f2a3b4', 'acc_e5f6a7b8c9d0', datetime('now')),
('tacc_f6a7b8c9d0e1', 'terr_d0e1f2a3b4c5', 'acc_f6a7b8c9d0e1', datetime('now')),
('tacc_a7b8c9d0e1f2', 'terr_e1f2a3b4c5d6', 'acc_a7b8c9d0e1f2', datetime('now')),
('tacc_b8c9d0e1f2a3', 'terr_f2a3b4c5d6e7', 'acc_b8c9d0e1f2a3', datetime('now')),
('tacc_c9d0e1f2a3b4', 'terr_f2a3b4c5d6e7', 'acc_c9d0e1f2a3b4', datetime('now')),
('tacc_d0e1f2a3b4c5', 'terr_a3b4c5d6e7f8', 'acc_d0e1f2a3b4c5', datetime('now')),
('tacc_e1f2a3b4c5d6', 'terr_b4c5d6e7f8a9', 'acc_e1f2a3b4c5d6', datetime('now'));

-- ── 区域-产品关联 ────────────────────────────────────────────
INSERT INTO territory_products (id, territory_id, product_id, price, is_active, created_at) VALUES
('tprod_a1b2c3d4e5', 'terr_e5f6a7b8c9d0', 'prod_e5f6a7b8c9d0', 549.00, 1, datetime('now')),
('tprod_b2c3d4e5f6', 'terr_f2a3b4c5d6e7', 'prod_f6a7b8c9d0e1', NULL, 1, datetime('now'));

-- ── 更多商机 ──────────────────────────────────────────────────
INSERT INTO opportunities (id, name, account_id, stage_id, amount, probability, close_date, description, owner_id, created_at, updated_at) VALUES
('oppo_b2c3d4e5f6a7', 'Libert 生物同步贴片采购', 'acc_b2c3d4e5f6a7', 'stg_b2c3d4e5f6a7', 48000.00, 30, '2026-09-01', 'Libert 集团批量采购 BioSync Patch 用于员工健康管理', 'user_e5f6a7b8c9d0', datetime('now','-30 days'), datetime('now','-5 days')),
('oppo_c3d4e5f6a7b8', 'Baji 工业传感器升级', 'acc_c3d4e5f6a7b8', 'stg_d4e5f6a7b8c9', 320000.00, 70, '2026-07-30', 'Baji 工业产线传感器全面升级项目', 'user_f6a7b8c9d0e1', datetime('now','-45 days'), datetime('now','-2 days')),
('oppo_d4e5f6a7b8c9', 'Taji 零售门店数字化方案', 'acc_d4e5f6a7b8c9', 'stg_c3d4e5f6a7b8', 185000.00, 50, '2026-10-15', 'Taji 全国 50 家门店数字化改造方案', 'user_a7b8c9d0e1f2', datetime('now','-20 days'), datetime('now','-3 days')),
('oppo_e5f6a7b8c9d0', 'HHK 金融安全系统', 'acc_e5f6a7b8c9d0', 'stg_a1b2c3d4e5f6', 650000.00, 10, '2027-01-15', 'HHK 集团量子加密安全系统项目', 'user_b8c9d0e1f2a3', datetime('now','-7 days'), datetime('now')),
('oppo_f6a7b8c9d0e1', 'East Tooth 研发设备采购', 'acc_f6a7b8c9d0e1', 'stg_b2c3d4e5f6a7', 220000.00, 30, '2026-08-20', 'East Tooth 医药研发中心设备采购', 'user_d0e1f2a3b4c5', datetime('now','-15 days'), datetime('now','-1 days')),
('oppo_a7b8c9d0e1f2', 'Puti Tooth 冷链物流项目', 'acc_a7b8c9d0e1f2', 'stg_c3d4e5f6a7b8', 95000.00, 50, '2026-09-30', 'Puti Tooth 食品冷链物流系统建设', 'user_e1f2a3b4c5d6', datetime('now','-25 days'), datetime('now','-4 days')),
('oppo_b8c9d0e1f2a3', 'NovaStar 能源管理系统', 'acc_b8c9d0e1f2a3', 'stg_d4e5f6a7b8c9', 780000.00, 70, '2026-08-10', 'NovaStar 新能源电站智能管理系统', 'user_f2a3b4c5d6e7', datetime('now','-60 days'), datetime('now','-1 days')),
('oppo_c9d0e1f2a3b4', 'CrystalLake 实验室装备', 'acc_c9d0e1f2a3b4', 'stg_e5f6a7b8c9d0', 430000.00, 90, '2026-07-20', 'CrystalLake 制药新实验室全套装备，已进入合同阶段', 'user_f2a3b4c5d6e7', datetime('now','-90 days'), datetime('now')),
('oppo_d0e1f2a3b4c5', 'GoldenSands 矿区安全监控', 'acc_d0e1f2a3b4c5', 'stg_a1b2c3d4e5f6', 160000.00, 10, '2026-12-01', 'GoldenSands 矿区安全监控系统初步接触', 'user_a3b4c5d6e7f8', datetime('now','-3 days'), datetime('now')),
('oppo_e1f2a3b4c5d6', 'DeepBlue 渔业溯源系统', 'acc_e1f2a3b4c5d6', 'stg_b2c3d4e5f6a7', 88000.00, 30, '2026-11-01', 'DeepBlue 海产品全程溯源系统', 'user_b4c5d6e7f8a9', datetime('now','-10 days'), datetime('now')),
('oppo_f2a3b4c5d6e7', 'Red Russia 量子安全通信', 'acc_a1b2c3d4e5f6', 'stg_f6a7b8c9d0e1', 600000.00, 100, '2026-06-15', '已赢单 - Red Russia 量子密钥加密器采购合同', 'user_d4e5f6a7b8c9', datetime('now','-120 days'), datetime('now','-60 days')),
('oppo_a3b4c5d6e7f8', 'Baji 生态砖海外采购', 'acc_c3d4e5f6a7b8', 'stg_a7b8c9d0e1f2', 120000.00, 0, '2026-05-01', '已输单 - Baji 评估后决定暂缓海外建材采购', 'user_f6a7b8c9d0e1', datetime('now','-150 days'), datetime('now','-90 days'));

-- ── 商机产品 ─────────────────────────────────────────────────
INSERT INTO opportunity_products (id, opportunity_id, product_id, quantity, unit_price, total_price, created_at) VALUES
-- Libert 生物同步贴片采购
('opprod_c3d4e5f6a7', 'oppo_b2c3d4e5f6a7', 'prod_b2c3d4e5f6a7', 300, 159.50, 47850.00, datetime('now','-30 days')),
-- Baji 工业传感器升级
('opprod_d4e5f6a7b8', 'oppo_c3d4e5f6a7b8', 'prod_e5f6a7b8c9d0', 200, 499.00, 99800.00, datetime('now','-45 days')),
('opprod_e5f6a7b8c9', 'oppo_c3d4e5f6a7b8', 'prod_a7b8c9d0e1f2', 30, 3999.00, 119970.00, datetime('now','-45 days')),
-- Taji 零售门店数字化方案
('opprod_f6a7b8c9d0', 'oppo_d4e5f6a7b8c9', 'prod_f6a7b8c9d0e1', 50, 1299.00, 64950.00, datetime('now','-20 days')),
('opprod_a7b8c9d0e1', 'oppo_d4e5f6a7b8c9', 'prod_c3d4e5f6a7b8', 100, 899.00, 89900.00, datetime('now','-20 days')),
-- HHK 金融安全系统
('opprod_b8c9d0e1f2', 'oppo_e5f6a7b8c9d0', 'prod_a7b8c9d0e1f2', 100, 3999.00, 399900.00, datetime('now','-7 days')),
('opprod_c9d0e1f2a3', 'oppo_e5f6a7b8c9d0', 'prod_c3d4e5f6a7b8', 200, 899.00, 179800.00, datetime('now','-7 days')),
-- East Tooth 研发设备采购
('opprod_d0e1f2a3b4', 'oppo_f6a7b8c9d0e1', 'prod_c3d4e5f6a7b8', 50, 899.00, 44950.00, datetime('now','-15 days')),
('opprod_e1f2a3b4c5', 'oppo_f6a7b8c9d0e1', 'prod_f6a7b8c9d0e1', 30, 1299.00, 38970.00, datetime('now','-15 days')),
-- Puti Tooth 冷链物流项目
('opprod_f2a3b4c5d6', 'oppo_a7b8c9d0e1f2', 'prod_e5f6a7b8c9d0', 150, 499.00, 74850.00, datetime('now','-25 days')),
-- NovaStar 能源管理系统
('opprod_a3b4c5d6e7', 'oppo_b8c9d0e1f2a3', 'prod_f6a7b8c9d0e1', 200, 1299.00, 259800.00, datetime('now','-60 days')),
('opprod_b4c5d6e7f8', 'oppo_b8c9d0e1f2a3', 'prod_e5f6a7b8c9d0', 500, 499.00, 249500.00, datetime('now','-60 days')),
-- CrystalLake 实验室装备
('opprod_c5d6e7f8a9', 'oppo_c9d0e1f2a3b4', 'prod_c3d4e5f6a7b8', 100, 899.00, 89900.00, datetime('now','-90 days')),
('opprod_d6e7f8a9b0', 'oppo_c9d0e1f2a3b4', 'prod_a1b2c3d4e5f6', 500, 299.99, 149995.00, datetime('now','-90 days')),
('opprod_e7f8a9b0c1', 'oppo_c9d0e1f2a3b4', 'prod_b2c3d4e5f6a7', 200, 159.50, 31900.00, datetime('now','-90 days')),
-- DeepBlue 渔业溯源系统
('opprod_f8a9b0c1d2', 'oppo_e1f2a3b4c5d6', 'prod_a7b8c9d0e1f2', 10, 3999.00, 39990.00, datetime('now','-10 days')),
('opprod_a9b0c1d2e3', 'oppo_e1f2a3b4c5d6', 'prod_b8c9d0e1f2a3', 500, 79.99, 39995.00, datetime('now','-10 days')),
-- Red Russia 量子安全通信（赢单）
('opprod_b0c1d2e3f4', 'oppo_f2a3b4c5d6e7', 'prod_a7b8c9d0e1f2', 80, 3999.00, 319920.00, datetime('now','-120 days')),
('opprod_c1d2e3f4a5', 'oppo_f2a3b4c5d6e7', 'prod_a1b2c3d4e5f6', 200, 299.99, 59998.00, datetime('now','-120 days'));

-- ── 拜访事件 ──────────────────────────────────────────────────
INSERT INTO events (id, subject, type, status, start_datetime, end_datetime, actual_start_time, actual_end_time, duration_minutes, what_id, what_type, who_id, owner_id, purpose, preparation_notes, description, outcome, next_steps, location, created_at, updated_at) VALUES
-- Red Russia 拜访记录
('event_a1b2c3d4e5f6', 'Red Russia 能源设备升级方案演示', 'Visit', 'completed', '2026-06-10 09:00:00', '2026-06-10 11:00:00', '2026-06-10 09:05:00', '2026-06-10 10:50:00', 105, 'acc_a1b2c3d4e5f6', 'account', 'con_a1b2c3d4e5f6', 'user_d4e5f6a7b8c9', '演示 AeroGel Insulator 和 LumiSheet Display 产品方案', '准备产品样机和技术参数文档', '客户对 AeroGel 很感兴趣，详细了解了技术指标', 'success', '准备报价单并跟进', 'Red Russia 总部 - 莫斯科', datetime('now','-37 days'), datetime('now','-37 days')),
('event_b2c3d4e5f6a7', 'Red Russia 量子安全方案讨论', 'Visit', 'completed', '2026-05-15 14:00:00', '2026-05-15 16:00:00', '2026-05-15 14:10:00', '2026-05-15 15:45:00', 95, 'oppo_f2a3b4c5d6e7', 'opportunity', 'con_b2c3d4e5f6a7', 'user_d4e5f6a7b8c9', '讨论量子加密方案技术细节和实施计划', '准备技术白皮书和案例', '双方就部署方案达成一致', 'success', '准备合同', 'Red Russia 总部 - 莫斯科', datetime('now','-63 days'), datetime('now','-63 days')),
('event_c3d4e5f6a7b8', 'Red Russia 合同签署拜访', 'Visit', 'completed', '2026-05-28 10:00:00', '2026-05-28 12:00:00', '2026-05-28 10:00:00', '2026-05-28 11:30:00', 90, 'oppo_f2a3b4c5d6e7', 'opportunity', 'con_a1b2c3d4e5f6', 'user_d4e5f6a7b8c9', '正式签署采购合同', '带齐合同文件和印章', '合同签署顺利完成', 'success', '安排发货', 'Red Russia 总部 - 莫斯科', datetime('now','-50 days'), datetime('now','-50 days')),

-- Libert 拜访记录
('event_d4e5f6a7b8c9', 'Libert 健康管理方案初次接触', 'Visit', 'completed', '2026-06-20 10:00:00', '2026-06-20 11:30:00', '2026-06-20 10:05:00', '2026-06-20 11:20:00', 75, 'acc_b2c3d4e5f6a7', 'account', 'con_c3d4e5f6a7b8', 'user_e5f6a7b8c9d0', '介绍 BioSync Patch 产品及企业健康管理方案', '准备产品介绍和健康管理方案PPT', '客户VP对方案表示兴趣，希望进行技术评估', 'success', '安排技术演示和样品寄送', 'Libert 硅谷总部', datetime('now','-27 days'), datetime('now','-27 days')),
('event_e5f6a7b8c9d0', 'Libert 技术评估会议', 'Video Conference', 'completed', '2026-07-01 14:00:00', '2026-07-01 15:00:00', '2026-07-01 14:00:00', '2026-07-01 14:50:00', 50, 'oppo_b2c3d4e5f6a7', 'opportunity', 'con_d4e5f6a7b8c9', 'user_e5f6a7b8c9d0', '线上技术评估会议', '准备技术文档和QA', '技术团队提出了一些兼容性问题', 'neutral', '提供补充技术资料', '线上 - Zoom', datetime('now','-16 days'), datetime('now','-16 days')),

-- Baji 拜访记录
('event_f6a7b8c9d0e1', 'Baji 工业传感器项目启动会', 'Visit', 'completed', '2026-06-05 09:30:00', '2026-06-05 12:00:00', '2026-06-05 09:30:00', '2026-06-05 11:45:00', 135, 'acc_c3d4e5f6a7b8', 'account', 'con_e5f6a7b8c9d0', 'user_f6a7b8c9d0e1', '项目启动会议，确认需求和范围', '准备项目方案书和报价', '确认了项目范围和初步时间表', 'success', '准备详细实施方案', 'Baji 上海总部', datetime('now','-42 days'), datetime('now','-42 days')),
('event_a7b8c9d0e1f2', 'Baji 商务谈判', 'Visit', 'in_progress', '2026-07-16 10:00:00', '2026-07-16 16:00:00', '2026-07-16 10:15:00', NULL, NULL, 'oppo_c3d4e5f6a7b8', 'opportunity', 'con_f6a7b8c9d0e1', 'user_f6a7b8c9d0e1', '价格谈判和合同条款讨论', '准备谈判策略和底线价格', '谈判正在进行中', 'neutral', '跟进客户反馈', 'Baji 上海总部 - 会议室A', datetime('now','-1 days'), datetime('now','-1 days')),

-- HHK 拜访记录
('event_b8c9d0e1f2a3', 'HHK 量子安全方案初次介绍', 'Visit', 'completed', '2026-07-10 14:00:00', '2026-07-10 16:00:00', '2026-07-10 14:00:00', '2026-07-10 15:30:00', 90, 'acc_e5f6a7b8c9d0', 'account', 'con_c9d0e1f2a3b4', 'user_b8c9d0e1f2a3', '介绍量子密钥加密方案', '准备方案PPT和金融行业案例', '客户投资总监表示需要内部评估', 'neutral', '跟进内部评估进展', 'HHK 香港总部', datetime('now','-7 days'), datetime('now','-7 days')),

-- East Tooth 拜访记录
('event_c9d0e1f2a3b4', 'East Tooth 研发设备需求沟通', 'Phone Call', 'completed', '2026-07-05 11:00:00', '2026-07-05 11:30:00', '2026-07-05 11:00:00', '2026-07-05 11:25:00', 25, 'acc_f6a7b8c9d0e1', 'account', 'con_e1f2a3b4c5d6', 'user_d0e1f2a3b4c5', '电话沟通设备需求细节', '提前了解客户需求文档', '客户明确了设备清单和预算', 'success', '准备正式报价', '电话沟通', datetime('now','-12 days'), datetime('now','-12 days')),

-- NovaStar 拜访记录
('event_d0e1f2a3b4c5', 'NovaStar 智能管理系统方案评审', 'Visit', 'completed', '2026-06-25 09:00:00', '2026-06-25 12:00:00', '2026-06-25 09:00:00', '2026-06-25 11:30:00', 150, 'acc_b8c9d0e1f2a3', 'account', 'con_c5d6e7f8a9b0', 'user_f2a3b4c5d6e7', '方案评审会', '准备完整的技术方案文档', 'CTO对方案表示认可，需调整部署架构', 'success', '调整方案架构后再次提交', 'NovaStar 纽约总部', datetime('now','-22 days'), datetime('now','-22 days')),

-- CrystalLake 拜访记录
('event_e1f2a3b4c5d6', 'CrystalLake 合同细节确认', 'Visit', 'completed', '2026-07-12 10:00:00', '2026-07-12 12:00:00', '2026-07-12 10:00:00', '2026-07-12 11:40:00', 100, 'oppo_c9d0e1f2a3b4', 'opportunity', 'con_e7f8a9b0c1d2', 'user_f2a3b4c5d6e7', '确认合同最终条款和交付时间', '准备最终合同版本', '双方确认所有条款，即将签署', 'success', '安排合同签署', 'CrystalLake 波士顿总部', datetime('now','-5 days'), datetime('now','-5 days')),

-- Puti Tooth 拜访记录
('event_f2a3b4c5d6e7', 'Puti Tooth 冷链物流需求调研', 'Visit', 'planned', '2026-07-22 10:00:00', '2026-07-22 12:00:00', NULL, NULL, NULL, 'acc_a7b8c9d0e1f2', 'account', 'con_a3b4c5d6e7f8', 'user_e1f2a3b4c5d6', '现场调研冷链物流现有系统和需求', '准备调研问卷和方案框架', NULL, NULL, '完成调研后输出方案', 'Puti Tooth 伦敦总部', datetime('now','-5 days'), datetime('now','-5 days')),

-- DeepBlue 拜访记录
('event_a3b4c5d6e7f8', 'DeepBlue 溯源方案视频沟通', 'Video Conference', 'completed', '2026-07-08 08:00:00', '2026-07-08 09:00:00', '2026-07-08 08:00:00', '2026-07-08 08:50:00', 50, 'acc_e1f2a3b4c5d6', 'account', 'con_a9b0c1d2e3f4', 'user_b4c5d6e7f8a9', '远程演示溯源系统方案', '准备方案演示和Demo环境', '客户CEO对方案感兴趣，希望进一步了解', 'success', '安排下一次详细技术交流', '线上 - Teams', datetime('now','-9 days'), datetime('now','-9 days')),

-- Taji 拜访记录
('event_b4c5d6e7f8a9', 'Taji 门店数字化方案演示', 'Visit', 'completed', '2026-06-28 13:00:00', '2026-06-28 16:00:00', '2026-06-28 13:10:00', '2026-06-28 15:40:00', 150, 'acc_d4e5f6a7b8c9', 'account', 'con_a7b8c9d0e1f2', 'user_a7b8c9d0e1f2', '现场演示数字化门店解决方案', '准备Demo环境和案例视频', '客户CEO非常认可方案', 'success', '准备项目报价', 'Taji 杭州总部 - 展示厅', datetime('now','-19 days'), datetime('now','-19 days')),

-- GoldenSands 初次接触
('event_c5d6e7f8a9b0', 'GoldenSands 安全监控初步接触', 'Phone Call', 'completed', '2026-07-15 15:00:00', '2026-07-15 15:30:00', '2026-07-15 15:00:00', '2026-07-15 15:20:00', 20, 'acc_d0e1f2a3b4c5', 'account', 'con_f8a9b0c1d2e3', 'user_a3b4c5d6e7f8', '初次电话沟通，了解安全监控需求', '准备开场话术', '客户表示有安全监控升级需求', 'success', '发送方案资料并安排正式拜访', '电话沟通', datetime('now','-2 days'), datetime('now','-2 days'));

-- ── 任务 ──────────────────────────────────────────────────────
INSERT INTO tasks (id, event_id, subject, status, priority, activity_date, what_id, what_type, who_id, assignee_id, description, sort_order, created_at, updated_at) VALUES
-- Red Russia 能源设备升级方案演示 的会前任务
('task_a1b2c3d4e5f6', 'event_a1b2c3d4e5f6', '准备 AeroGel 产品样机', 'completed', 'high', '2026-06-09', 'acc_a1b2c3d4e5f6', 'account', 'con_a1b2c3d4e5f6', 'user_d4e5f6a7b8c9', '从仓库领取 AeroGel 样机并测试', 1, datetime('now','-38 days'), datetime('now','-37 days')),
('task_b2c3d4e5f6a7', 'event_a1b2c3d4e5f6', '打印技术参数文档', 'completed', 'normal', '2026-06-10', 'acc_a1b2c3d4e5f6', 'account', 'con_a1b2c3d4e5f6', 'user_d4e5f6a7b8c9', '打印 10 份技术参数文档', 2, datetime('now','-38 days'), datetime('now','-37 days')),
-- Red Russia 合同签署 的会后任务
('task_c3d4e5f6a7b8', 'event_c3d4e5f6a7b8', '归档已签署合同', 'completed', 'high', '2026-05-29', 'oppo_f2a3b4c5d6e7', 'opportunity', 'con_a1b2c3d4e5f6', 'user_d4e5f6a7b8c9', '扫描并归档签署后的合同文件', 1, datetime('now','-50 days'), datetime('now','-49 days')),
('task_d4e5f6a7b8c9', 'event_c3d4e5f6a7b8', '通知生产部门安排发货', 'completed', 'high', '2026-05-29', 'oppo_f2a3b4c5d6e7', 'opportunity', NULL, 'user_d4e5f6a7b8c9', '通知生产部门准备 QuantumKey 和 HydroFlux 的发货', 2, datetime('now','-50 days'), datetime('now','-49 days')),
-- Baji 商务谈判 的任务
('task_e5f6a7b8c9d0', 'event_a7b8c9d0e1f2', '准备谈判策略文档', 'completed', 'high', '2026-07-15', 'oppo_c3d4e5f6a7b8', 'opportunity', 'con_f6a7b8c9d0e1', 'user_f6a7b8c9d0e1', '分析客户底牌，制定谈判策略', 1, datetime('now','-2 days'), datetime('now','-1 days')),
('task_f6a7b8c9d0e1', 'event_a7b8c9d0e1f2', '跟进客户反馈', 'in_progress', 'high', '2026-07-18', 'oppo_c3d4e5f6a7b8', 'opportunity', 'con_f6a7b8c9d0e1', 'user_f6a7b8c9d0e1', '跟进客户对报价的反馈意见', 2, datetime('now','-1 days'), datetime('now','-1 days')),
-- CrystalLake 合同确认 的会后任务
('task_a7b8c9d0e1f2', 'event_e1f2a3b4c5d6', '准备正式合同文本', 'completed', 'high', '2026-07-12', 'oppo_c9d0e1f2a3b4', 'opportunity', 'con_e7f8a9b0c1d2', 'user_f2a3b4c5d6e7', '根据确认条款准备正式合同', 1, datetime('now','-5 days'), datetime('now','-4 days')),
('task_b8c9d0e1f2a3', 'event_e1f2a3b4c5d6', '安排合同签署会议', 'completed', 'normal', '2026-07-13', 'oppo_c9d0e1f2a3b4', 'opportunity', 'con_e7f8a9b0c1d2', 'user_f2a3b4c5d6e7', '与客户协调签署时间和地点', 2, datetime('now','-5 days'), datetime('now','-4 days')),
-- Puti Tooth 冷链调研 的准备任务
('task_c9d0e1f2a3b4', 'event_f2a3b4c5d6e7', '准备调研问卷', 'completed', 'normal', '2026-07-21', 'acc_a7b8c9d0e1f2', 'account', 'con_a3b4c5d6e7f8', 'user_e1f2a3b4c5d6', '编写冷链物流调研问卷', 1, datetime('now','-6 days'), datetime('now','-5 days')),
('task_d0e1f2a3b4c5', 'event_f2a3b4c5d6e7', '预订机票和酒店', 'completed', 'low', '2026-07-21', NULL, NULL, NULL, 'user_e1f2a3b4c5d6', '预订前往伦敦的机票和酒店', 2, datetime('now','-6 days'), datetime('now','-5 days')),
-- NovaStar 方案评审 的任务
('task_e1f2a3b4c5d6', 'event_d0e1f2a3b4c5', '调整部署架构方案', 'in_progress', 'high', '2026-07-20', 'oppo_b8c9d0e1f2a3', 'opportunity', 'con_c5d6e7f8a9b0', 'user_f2a3b4c5d6e7', '根据CTO反馈调整系统部署架构', 1, datetime('now','-22 days'), datetime('now','-1 days')),
-- Taji 数字化方案演示 的任务
('task_f2a3b4c5d6e7', 'event_b4c5d6e7f8a9', '准备项目报价', 'pending', 'high', '2026-07-25', 'oppo_d4e5f6a7b8c9', 'opportunity', 'con_a7b8c9d0e1f2', 'user_a7b8c9d0e1f2', '根据演示反馈准备正式项目报价', 1, datetime('now','-19 days'), datetime('now','-19 days')),
-- DeepBlue 溯源方案 的任务
('task_a3b4c5d6e7f8', 'event_a3b4c5d6e7f8', '发送方案资料包', 'completed', 'normal', '2026-07-09', 'acc_e1f2a3b4c5d6', 'account', 'con_a9b0c1d2e3f4', 'user_b4c5d6e7f8a9', '邮件发送完整方案资料包给客户CEO', 1, datetime('now','-9 days'), datetime('now','-8 days'));

-- ── 报表 ──────────────────────────────────────────────────────
INSERT INTO reports (id, name, object_type, report_type, filters, grouping, aggregations, columns, owner_id, created_at, updated_at) VALUES
('rpt_a1b2c3d4e5f6', '按区域商机汇总', 'opportunity', 'summary', '{"conditions":[{"field":"stage_id","op":"ne","value":"stg_a7b8c9d0e1f2"}]}', '{"fields":["owner_id"]}', '{"amount":"sum","probability":"avg"}', '["name","account_id","stage_id","amount","probability","close_date","owner_id"]', 'user_b2c3d4e5f6a7', datetime('now','-30 days'), datetime('now','-5 days')),
('rpt_b2c3d4e5f6a7', '本月拜访统计', 'event', 'summary', '{"conditions":[{"field":"status","op":"in","value":["completed","in_progress"]}]}', '{"fields":["owner_id","status"]}', '{"duration_minutes":"sum"}', '["subject","type","status","owner_id","start_datetime","duration_minutes","outcome"]', 'user_b2c3d4e5f6a7', datetime('now','-20 days'), datetime('now','-3 days')),
('rpt_c3d4e5f6a7b8', '产品销售额排行', 'opportunity_product', 'summary', NULL, '{"fields":["product_id"]}', '{"total_price":"sum","quantity":"sum"}', '["product_id","quantity","total_price"]', 'user_b2c3d4e5f6a7', datetime('now','-25 days'), datetime('now','-4 days')),
('rpt_d4e5f6a7b8c9', '高概率赢单机会', 'opportunity', 'tabular', '{"conditions":[{"field":"probability","op":"ge","value":50},{"field":"stage_id","op":"ne","value":"stg_f6a7b8c9d0e1"},{"field":"stage_id","op":"ne","value":"stg_a7b8c9d0e1f2"}]}', NULL, NULL, '["name","account_id","amount","probability","close_date","owner_id","stage_id"]', 'user_c3d4e5f6a7b8', datetime('now','-10 days'), datetime('now')),
('rpt_e5f6a7b8c9d0', '账户活跃度分析', 'event', 'summary', '{"conditions":[{"field":"status","op":"eq","value":"completed"}]}', '{"fields":["what_id"]}', '{"id":"count"}', '["what_id","what_type","id"]', 'user_b2c3d4e5f6a7', datetime('now','-15 days'), datetime('now','-2 days'));

-- ── 仪表盘 ────────────────────────────────────────────────────
INSERT INTO dashboards (id, name, owner_id, created_at, updated_at) VALUES
('dsb_a1b2c3d4e5f6', '销售管理总览', 'user_b2c3d4e5f6a7', datetime('now','-30 days'), datetime('now','-2 days')),
('dsb_b2c3d4e5f6a7', '拜访执行看板', 'user_c3d4e5f6a7b8', datetime('now','-15 days'), datetime('now','-1 days'));

INSERT INTO dashboard_components (id, dashboard_id, report_id, title, chart_type, position_x, position_y, width, height) VALUES
('dsc_a1b2c3d4e5f6', 'dsb_a1b2c3d4e5f6', 'rpt_a1b2c3d4e5f6', '各销售人员商机汇总', 'table', 0, 0, 6, 3),
('dsc_b2c3d4e5f6a7', 'dsb_a1b2c3d4e5f6', 'rpt_c3d4e5f6a7b8', '热销产品排行', 'metric', 6, 0, 6, 3),
('dsc_c3d4e5f6a7b8', 'dsb_a1b2c3d4e5f6', 'rpt_d4e5f6a7b8c9', '高概率赢单机会', 'table', 0, 3, 12, 3),
('dsc_d4e5f6a7b8c9', 'dsb_b2c3d4e5f6a7', 'rpt_b2c3d4e5f6a7', '本月拜访统计', 'table', 0, 0, 8, 4),
('dsc_e5f6a7b8c9d0', 'dsb_b2c3d4e5f6a7', 'rpt_e5f6a7b8c9d0', '账户拜访活跃度', 'metric', 8, 0, 4, 4);

-- ── 自定义对象：培训课程 ──────────────────────────────────────
INSERT INTO custom_object_defs (id, api_name, label, plural_label, description, table_name, is_active, created_at, updated_at) VALUES
('cod_a1b2c3d4e5f6', 'Training_Course__c', '培训课程', '培训课程', '销售培训课程管理', 'custom_training_course', 1, datetime('now','-60 days'), datetime('now','-30 days')),
('cod_b2c3d4e5f6a7', 'Project__c', '项目', '项目', '内部项目管理', 'custom_project', 1, datetime('now','-50 days'), datetime('now','-20 days'));

INSERT INTO custom_field_defs (id, object_id, api_name, label, field_type, is_required, is_unique, default_value, max_length, picklist_values, precision_total, precision_scale, lookup_object_id, display_order, created_at, updated_at) VALUES
-- 培训课程字段
('cfd_a1b2c3d4e5f6', 'cod_a1b2c3d4e5f6', 'Name', '课程名称', 'text', 1, 0, NULL, 200, NULL, NULL, NULL, NULL, 1, datetime('now','-60 days'), datetime('now','-30 days')),
('cfd_b2c3d4e5f6a7', 'cod_a1b2c3d4e5f6', 'Instructor__c', '讲师', 'text', 0, 0, NULL, 100, NULL, NULL, NULL, NULL, 2, datetime('now','-60 days'), datetime('now','-30 days')),
('cfd_c3d4e5f6a7b8', 'cod_a1b2c3d4e5f6', 'Duration_Hours__c', '时长(小时)', 'number', 0, 0, '8', NULL, NULL, 5, 1, NULL, 3, datetime('now','-60 days'), datetime('now','-30 days')),
('cfd_d4e5f6a7b8c9', 'cod_a1b2c3d4e5f6', 'Status__c', '状态', 'picklist', 1, 0, 'planned', NULL, 'planned,in_progress,completed,cancelled', NULL, NULL, NULL, 4, datetime('now','-60 days'), datetime('now','-30 days')),
('cfd_e5f6a7b8c9d0', 'cod_a1b2c3d4e5f6', 'Max_Students__c', '最大人数', 'number', 0, 0, '20', NULL, NULL, 4, 0, NULL, 5, datetime('now','-60 days'), datetime('now','-30 days')),
('cfd_f6a7b8c9d0e1', 'cod_a1b2c3d4e5f6', 'Start_Date__c', '开始日期', 'date', 1, 0, NULL, NULL, NULL, NULL, NULL, NULL, 6, datetime('now','-60 days'), datetime('now','-30 days')),
-- 项目字段
('cfd_a7b8c9d0e1f2', 'cod_b2c3d4e5f6a7', 'Name', '项目名称', 'text', 1, 0, NULL, 200, NULL, NULL, NULL, NULL, 1, datetime('now','-50 days'), datetime('now','-20 days')),
('cfd_b8c9d0e1f2a3', 'cod_b2c3d4e5f6a7', 'Budget__c', '预算', 'currency', 0, 0, NULL, NULL, NULL, 12, 2, NULL, 2, datetime('now','-50 days'), datetime('now','-20 days')),
('cfd_c9d0e1f2a3b4', 'cod_b2c3d4e5f6a7', 'Priority__c', '优先级', 'picklist', 1, 0, 'medium', NULL, 'high,medium,low', NULL, NULL, NULL, 3, datetime('now','-50 days'), datetime('now','-20 days')),
('cfd_d0e1f2a3b4c5', 'cod_b2c3d4e5f6a7', 'Status__c', '状态', 'picklist', 1, 0, 'planning', NULL, 'planning,in_progress,completed,on_hold', NULL, NULL, NULL, 4, datetime('now','-50 days'), datetime('now','-20 days'));

-- ── 工作流规则 ────────────────────────────────────────────────
INSERT INTO workflow_rules (id, name, object_type, trigger_event, condition_expression, is_active, created_at, updated_at) VALUES
('wf_a1b2c3d4e5f6', '高金额商机通知', 'opportunity', 'create_or_update', '{"conditions":[{"field":"amount","op":"ge","value":500000}]}', 1, datetime('now','-45 days'), datetime('now','-10 days')),
('wf_b2c3d4e5f6a7', '赢单后自动更新', 'opportunity', 'update', '{"conditions":[{"field":"stage_id","op":"eq","value":"stg_f6a7b8c9d0e1"}]}', 1, datetime('now','-40 days'), datetime('now','-5 days'));

INSERT INTO workflow_actions (id, workflow_id, action_type, action_config, display_order) VALUES
('wfa_a1b2c3d4e5f6', 'wf_a1b2c3d4e5f6', 'notification', '{"message":"高金额商机创建: {{name}}, 金额: ¥{{amount}}","channels":["system"],"recipients":["user_b2c3d4e5f6a7"]}', 1),
('wfa_b2c3d4e5f6a7', 'wf_b2c3d4e5f6a7', 'notification', '{"message":"商机已赢单: {{name}}, 金额: ¥{{amount}}","channels":["system"],"recipients":["user_b2c3d4e5f6a7"]}', 1);

INSERT INTO workflow_execution_logs (id, workflow_id, object_type, record_id, workflow_name, conditions_met, action_executed, result_message, executed_at) VALUES
('wfl_a1b2c3d4e5f6', 'wf_a1b2c3d4e5f6', 'opportunity', 'oppo_e5f6a7b8c9d0', '高金额商机通知', 1, 1, '通知已发送', datetime('now','-7 days')),
('wfl_b2c3d4e5f6a7', 'wf_a1b2c3d4e5f6', 'opportunity', 'oppo_b8c9d0e1f2a3', '高金额商机通知', 1, 1, '通知已发送', datetime('now','-60 days')),
('wfl_c3d4e5f6a7b8', 'wf_b2c3d4e5f6a7', 'opportunity', 'oppo_f2a3b4c5d6e7', '赢单后自动更新', 1, 1, '赢单处理完成', datetime('now','-60 days'));
