-- 初始化数据库脚本
CREATE TABLE IF NOT EXISTS example (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);
