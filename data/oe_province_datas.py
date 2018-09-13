# coding=utf-8

init_sql = """
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (110000, '北京市', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (120000, '天津市', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (130000, '河北省', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (140000, '山西省', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (150000, '内蒙古自治区', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (210000, '辽宁省', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (220000, '吉林省', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (230000, '黑龙江省', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (310000, '上海市', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (320000, '江苏省', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (330000, '浙江省', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (340000, '安徽省', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (350000, '福建省', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (360000, '江西省', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (370000, '山东省', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (410000, '河南省', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (420000, '湖北省', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (430000, '湖南省', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (440000, '广东省', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (450000, '广西壮族自治区', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (460000, '海南省', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (500000, '重庆市', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (510000, '四川省', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (520000, '贵州省', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (530000, '云南省', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (540000, '西藏自治区', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (610000, '陕西省', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (620000, '甘肃省', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (630000, '青海省', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (640000, '宁夏回族自治区', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (650000, '新疆维吾尔自治区', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (710000, '台湾省', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (810000, '香港特别行政区', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
    INSERT INTO oe_province (id, name, create_uid, create_date, write_uid, write_date) VALUES (820000, '澳门特别行政区', 1, NOW() AT TIME ZONE 'UTC', 1, NOW() AT TIME ZONE 'UTC') ON CONFLICT DO NOTHING;
"""
