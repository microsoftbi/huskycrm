-- =============================================================
-- Husky CRM 测试数据
-- 用法: sqlite3 backend/huskycrm.db < TEST.sql
-- 注意: 需要先启动后端（自动建表和创建阶段）
-- =============================================================

-- ── 清空所有相关表（SQLite 不支持 TRUNCATE，使用 DELETE） ──
DELETE FROM territory_accounts;
DELETE FROM territory_products;
DELETE FROM territory_members;
DELETE FROM territories;
DELETE FROM contacts;
DELETE FROM accounts;
DELETE FROM products;
DELETE FROM users WHERE username != 'admin';

-- ── 系统用户 ─────────────────────────────────────────────────
-- 密码统一为 "123456" (bcrypt hash)
INSERT OR IGNORE INTO users (username, email, password_hash, display_name, is_active, is_superuser, created_at, updated_at) VALUES
('administrator', 'admin@huskycrm.local', '$2b$12$/kwxhYkjzgyGGSgQbEjknu.flcDCWIW5cJUsnvTTlnPHacPNtsiTK', 'Administrator', 1, 1, datetime('now'), datetime('now')),
('Global_CEO', 'ceo@huskycrm.local', '$2b$12$/kwxhYkjzgyGGSgQbEjknu.flcDCWIW5cJUsnvTTlnPHacPNtsiTK', 'Global CEO', 1, 0, datetime('now'), datetime('now')),
('Asia_manager', 'asia.mgr@huskycrm.local', '$2b$12$/kwxhYkjzgyGGSgQbEjknu.flcDCWIW5cJUsnvTTlnPHacPNtsiTK', 'Asia Manager', 1, 0, datetime('now'), datetime('now')),
('Asia_RedRussia_sales', 'red.russia@huskycrm.local', '$2b$12$/kwxhYkjzgyGGSgQbEjknu.flcDCWIW5cJUsnvTTlnPHacPNtsiTK', 'Red Russia Sales', 1, 0, datetime('now'), datetime('now')),
('Asia_Libert_sales', 'libert.sales@huskycrm.local', '$2b$12$/kwxhYkjzgyGGSgQbEjknu.flcDCWIW5cJUsnvTTlnPHacPNtsiTK', 'Libert Sales', 1, 0, datetime('now'), datetime('now')),
('Asia_Baji_sales', 'baji.sales@huskycrm.local', '$2b$12$/kwxhYkjzgyGGSgQbEjknu.flcDCWIW5cJUsnvTTlnPHacPNtsiTK', 'Baji Sales', 1, 0, datetime('now'), datetime('now')),
('Asia_Taji_sales', 'taji.sales@huskycrm.local', '$2b$12$/kwxhYkjzgyGGSgQbEjknu.flcDCWIW5cJUsnvTTlnPHacPNtsiTK', 'Taji Sales', 1, 0, datetime('now'), datetime('now')),
('Asia_HHK_sales', 'hhk.sales@huskycrm.local', '$2b$12$/kwxhYkjzgyGGSgQbEjknu.flcDCWIW5cJUsnvTTlnPHacPNtsiTK', 'HHK Sales', 1, 0, datetime('now'), datetime('now')),
('Europe_manager', 'europe.mgr@huskycrm.local', '$2b$12$/kwxhYkjzgyGGSgQbEjknu.flcDCWIW5cJUsnvTTlnPHacPNtsiTK', 'Europe Manager', 1, 0, datetime('now'), datetime('now')),
('Europe_EastTooth_sales', 'east.tooth@huskycrm.local', '$2b$12$/kwxhYkjzgyGGSgQbEjknu.flcDCWIW5cJUsnvTTlnPHacPNtsiTK', 'East Tooth Sales', 1, 0, datetime('now'), datetime('now')),
('Europe_PutiTooth_sales', 'puti.tooth@huskycrm.local', '$2b$12$/kwxhYkjzgyGGSgQbEjknu.flcDCWIW5cJUsnvTTlnPHacPNtsiTK', 'Puti Tooth Sales', 1, 0, datetime('now'), datetime('now')),
('Europe_TinyBritsh_sales', 'tiny.british@huskycrm.local', '$2b$12$/kwxhYkjzgyGGSgQbEjknu.flcDCWIW5cJUsnvTTlnPHacPNtsiTK', 'Tiny British Sales', 1, 0, datetime('now'), datetime('now')),
('Other_manager', 'other.mgr@huskycrm.local', '$2b$12$/kwxhYkjzgyGGSgQbEjknu.flcDCWIW5cJUsnvTTlnPHacPNtsiTK', 'Other Manager', 1, 0, datetime('now'), datetime('now')),
('Other_Jafanxa_sales', 'jafanxa@huskycrm.local', '$2b$12$/kwxhYkjzgyGGSgQbEjknu.flcDCWIW5cJUsnvTTlnPHacPNtsiTK', 'Jafanxa Sales', 1, 0, datetime('now'), datetime('now')),
('Other_Moyude_sales', 'moyude@huskycrm.local', '$2b$12$/kwxhYkjzgyGGSgQbEjknu.flcDCWIW5cJUsnvTTlnPHacPNtsiTK', 'Moyude Sales', 1, 0, datetime('now'), datetime('now'));

-- ── 产品 ─────────────────────────────────────────────────
INSERT OR IGNORE INTO products (name, product_code, price, cost, category, description, is_active, created_at, updated_at) VALUES
('东风导弹', 'DF-41', 50000000, 35000000, '导弹', '洲际弹道导弹', 1, datetime('now'), datetime('now')),
('小男孩原子弹', 'MK-1', 2000000000, 1500000000, '核武器', '原子弹，代号小男孩', 1, datetime('now'), datetime('now')),
('大伊万', 'AN602', 5000000000, 4000000000, '核武器', '沙皇炸弹', 1, datetime('now'), datetime('now')),
('卡秋莎火箭弹', 'BM-13', 50000, 30000, '火箭弹', '多管火箭炮系统', 1, datetime('now'), datetime('now')),
('T50坦克', 'T-50', 30000000, 20000000, '坦克', '第五代主战坦克', 1, datetime('now'), datetime('now')),
('Z50装甲车', 'Z-50', 15000000, 10000000, '装甲车', '步兵战车', 1, datetime('now'), datetime('now')),
('QBZ突击步枪', 'QBZ-95', 5000, 3000, '枪支', '5.8mm 无托突击步枪', 1, datetime('now'), datetime('now')),
('G0武装直升机', 'G-0', 80000000, 55000000, '直升机', '重型武装直升机', 1, datetime('now'), datetime('now'));

-- ── 账户 ─────────────────────────────────────────────────────
INSERT OR IGNORE INTO accounts (name, industry, billing_country, description, created_at, updated_at) VALUES
('俄罗斯', '军工', '俄罗斯', '横跨欧亚大陆的军事强国', datetime('now'), datetime('now')),
('利比亚', '石油', '利比亚', '北非石油输出国', datetime('now'), datetime('now')),
('巴基斯坦', '军工', '巴基斯坦', '南亚伊斯兰共和国', datetime('now'), datetime('now')),
('塔吉克斯坦', '矿业', '塔吉克斯坦', '中亚矿业国家', datetime('now'), datetime('now')),
('红俄罗斯', '科技', '未知', '虚拟国家，高科技产业', datetime('now'), datetime('now')),
('哈哈克斯坦', '能源', '哈哈克斯坦', '虚拟国家，能源输出', datetime('now'), datetime('now')),
('东班牙', '制造', '东班牙', '虚拟国家，制造业发达', datetime('now'), datetime('now')),
('菩提牙', '金融', '菩提牙', '虚拟国家，金融中心', datetime('now'), datetime('now')),
('小列颠', '航运', '小列颠', '虚拟国家，岛国航运', datetime('now'), datetime('now')),
('减放小', '农业', '减放小', '虚拟国家，农业国', datetime('now'), datetime('now')),
('墨鱼弟', '渔业', '墨鱼弟', '虚拟国家，海洋渔业', datetime('now'), datetime('now'));

-- ── Territory ────────────────────────────────────────────────
-- 层级: Global > Asia/Europe/Other > 子区域
INSERT OR IGNORE INTO territories (id, name, code, territory_type, parent_id, description, created_at, updated_at) VALUES
(1, 'Global', 'GLOBAL', 'region', NULL, '全球总部', datetime('now'), datetime('now')),
(2, 'Asia', 'ASIA', 'region', 1, '亚太区域', datetime('now'), datetime('now')),
(3, 'Europe', 'EUROPE', 'region', 1, '欧洲区域', datetime('now'), datetime('now')),
(4, 'Other', 'OTHER', 'region', 1, '其他区域', datetime('now'), datetime('now')),
(5, 'Asia_RedRussia', 'ASIA_RR', 'district', 2, '红俄罗斯（亚洲分部）', datetime('now'), datetime('now')),
(6, 'Asia_Libert', 'ASIA_LIB', 'district', 2, '利比亚（亚洲分部）', datetime('now'), datetime('now')),
(7, 'Asia_Baji', 'ASIA_BAJI', 'district', 2, '巴基斯坦', datetime('now'), datetime('now')),
(8, 'Asia_Taji', 'ASIA_TAJI', 'district', 2, '塔吉克斯坦', datetime('now'), datetime('now')),
(9, 'Asia_HHK', 'ASIA_HHK', 'district', 2, '哈哈克斯坦', datetime('now'), datetime('now')),
(10, 'Europe_EastTooth', 'EU_ET', 'district', 3, '东班牙', datetime('now'), datetime('now')),
(11, 'Europe_PutiTooth', 'EU_PT', 'district', 3, '菩提牙', datetime('now'), datetime('now')),
(12, 'Europe_TinyBritsh', 'EU_TB', 'district', 3, '小列颠', datetime('now'), datetime('now')),
(13, 'Other_Jafanxa', 'OTH_JFX', 'district', 4, '减放小', datetime('now'), datetime('now')),
(14, 'Other_Moyude', 'OTH_MYD', 'district', 4, '墨鱼弟', datetime('now'), datetime('now'));

-- ── Territory Members ───────────────────────────────────────
INSERT OR IGNORE INTO territory_members (territory_id, user_id, role) VALUES
(1, (SELECT id FROM users WHERE username = 'Global_CEO'), 'manager'),
(2, (SELECT id FROM users WHERE username = 'Asia_manager'), 'manager'),
(5, (SELECT id FROM users WHERE username = 'Asia_RedRussia_sales'), 'member'),
(6, (SELECT id FROM users WHERE username = 'Asia_Libert_sales'), 'member'),
(7, (SELECT id FROM users WHERE username = 'Asia_Baji_sales'), 'member'),
(8, (SELECT id FROM users WHERE username = 'Asia_Taji_sales'), 'member'),
(9, (SELECT id FROM users WHERE username = 'Asia_HHK_sales'), 'member'),
(3, (SELECT id FROM users WHERE username = 'Europe_manager'), 'manager'),
(10, (SELECT id FROM users WHERE username = 'Europe_EastTooth_sales'), 'member'),
(11, (SELECT id FROM users WHERE username = 'Europe_PutiTooth_sales'), 'member'),
(12, (SELECT id FROM users WHERE username = 'Europe_TinyBritsh_sales'), 'member'),
(4, (SELECT id FROM users WHERE username = 'Other_manager'), 'manager'),
(13, (SELECT id FROM users WHERE username = 'Other_Jafanxa_sales'), 'member'),
(14, (SELECT id FROM users WHERE username = 'Other_Moyude_sales'), 'member');

-- ── Territory-Account Assignments ────────────────────────────
INSERT OR IGNORE INTO territory_accounts (territory_id, account_id) VALUES
(5,  (SELECT id FROM accounts WHERE name = '红俄罗斯')),
(6,  (SELECT id FROM accounts WHERE name = '利比亚')),
(7,  (SELECT id FROM accounts WHERE name = '巴基斯坦')),
(8,  (SELECT id FROM accounts WHERE name = '塔吉克斯坦')),
(9,  (SELECT id FROM accounts WHERE name = '哈哈克斯坦')),
(10, (SELECT id FROM accounts WHERE name = '东班牙')),
(11, (SELECT id FROM accounts WHERE name = '菩提牙')),
(12, (SELECT id FROM accounts WHERE name = '小列颠')),
(13, (SELECT id FROM accounts WHERE name = '减放小')),
(14, (SELECT id FROM accounts WHERE name = '墨鱼弟'));
-- 俄罗斯同时属于 Asia 和 Europe 两个大区
INSERT OR IGNORE INTO territory_accounts (territory_id, account_id) VALUES
(2, (SELECT id FROM accounts WHERE name = '俄罗斯')),
(3, (SELECT id FROM accounts WHERE name = '俄罗斯'));

-- ── 联系人（每个账户2个） ─────────────────────────────────────
INSERT OR IGNORE INTO contacts (first_name, last_name, email, title, account_id, created_at, updated_at) VALUES
('亚历山大', '伊万诺夫', 'alex.ivanov@russia.com', '采购总监', (SELECT id FROM accounts WHERE name = '俄罗斯'), datetime('now'), datetime('now')),
('尼古拉', '彼得罗夫', 'nikolai.petrov@russia.com', '总经理', (SELECT id FROM accounts WHERE name = '俄罗斯'), datetime('now'), datetime('now')),
('奥马尔', '阿卜杜拉', 'omar.abdulla@libya.com', '军事顾问', (SELECT id FROM accounts WHERE name = '利比亚'), datetime('now'), datetime('now')),
('阿里', '卡里姆', 'ali.karim@libya.com', '技术总监', (SELECT id FROM accounts WHERE name = '利比亚'), datetime('now'), datetime('now')),
('穆罕默德', '汗', 'mohammed.khan@pakistan.com', '项目经理', (SELECT id FROM accounts WHERE name = '巴基斯坦'), datetime('now'), datetime('now')),
('艾哈迈德', '拉希德', 'ahmed.rasheed@pakistan.com', '采购经理', (SELECT id FROM accounts WHERE name = '巴基斯坦'), datetime('now'), datetime('now')),
('拉赫蒙', '卡里莫夫', 'rahmon.karimov@tajik.com', '财务总监', (SELECT id FROM accounts WHERE name = '塔吉克斯坦'), datetime('now'), datetime('now')),
('达乌德', '拉赫莫诺夫', 'daud.rahmonov@tajik.com', '运营主管', (SELECT id FROM accounts WHERE name = '塔吉克斯坦'), datetime('now'), datetime('now')),
('谢尔盖', '库兹涅佐夫', 'sergei.kuz@redrussia.com', 'CEO', (SELECT id FROM accounts WHERE name = '红俄罗斯'), datetime('now'), datetime('now')),
('安德烈', '索科洛夫', 'andrei.sokolov@redrussia.com', '技术总监', (SELECT id FROM accounts WHERE name = '红俄罗斯'), datetime('now'), datetime('now')),
('马克西姆', '费奥多罗夫', 'maxim.fyodorov@hhk.com', '销售经理', (SELECT id FROM accounts WHERE name = '哈哈克斯坦'), datetime('now'), datetime('now')),
('弗拉基米尔', '米哈伊洛夫', 'vladimir.mikhailov@hhk.com', '市场总监', (SELECT id FROM accounts WHERE name = '哈哈克斯坦'), datetime('now'), datetime('now')),
('卡洛斯', '桑切斯', 'carlos.sanchez@eastooth.com', '采购总监', (SELECT id FROM accounts WHERE name = '东班牙'), datetime('now'), datetime('now')),
('何塞', '加西亚', 'jose.garcia@eastooth.com', '总经理', (SELECT id FROM accounts WHERE name = '东班牙'), datetime('now'), datetime('now')),
('佩德罗', '罗德里格斯', 'pedro.rodriguez@putitooth.com', '财务总监', (SELECT id FROM accounts WHERE name = '菩提牙'), datetime('now'), datetime('now')),
('胡安', '马丁内斯', 'juan.martinez@putitooth.com', '运营经理', (SELECT id FROM accounts WHERE name = '菩提牙'), datetime('now'), datetime('now')),
('詹姆斯', '史密斯', 'james.smith@tinybritish.com', 'CEO', (SELECT id FROM accounts WHERE name = '小列颠'), datetime('now'), datetime('now')),
('威廉', '布朗', 'william.brown@tinybritish.com', '采购经理', (SELECT id FROM accounts WHERE name = '小列颠'), datetime('now'), datetime('now')),
('李明', '小王', 'liming.wang@jianfangxiao.com', '项目经理', (SELECT id FROM accounts WHERE name = '减放小'), datetime('now'), datetime('now')),
('张伟', '大勇', 'zhangwei.dayong@jianfangxiao.com', '技术总监', (SELECT id FROM accounts WHERE name = '减放小'), datetime('now'), datetime('now')),
('田中', '一郎', 'tanaka.ichiro@moyude.com', '社长', (SELECT id FROM accounts WHERE name = '墨鱼弟'), datetime('now'), datetime('now')),
('山本', '太郎', 'yamamoto.taro@moyude.com', '采购部长', (SELECT id FROM accounts WHERE name = '墨鱼弟'), datetime('now'), datetime('now'));
