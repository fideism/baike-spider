#备份已存在数据
RENAME TABLE `pf_sphinx_docs` TO `pf_sphinx_docs_back`;
CREATE TABLE `pf_sphinx_docs` LIKE `pf_sphinx_docs_back`;
RENAME TABLE `pf_sphinx_lemma` TO `pf_sphinx_lemma_back`;
CREATE TABLE `pf_sphinx_lemma` LIKE `pf_sphinx_lemma_back`;
RENAME TABLE `pf_sphinx_synonym` TO `pf_sphinx_synonym_back`;
CREATE TABLE `pf_sphinx_synonym` LIKE `pf_sphinx_synonym_back`;
RENAME TABLE `pf_sphinx_synonym_relate` TO `pf_sphinx_synonym_relate_back`;
CREATE TABLE `pf_sphinx_synonym_relate` LIKE `pf_sphinx_synonym_relate_back`;

#修改字符编码，解决特殊字符插入数据库错误问题
ALTER TABLE `pf_sphinx_docs` CHARACTER set utf8mb4;
ALTER TABLE `pf_sphinx_docs` MODIFY COLUMN `content_wrapper` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;
ALTER TABLE `pf_sphinx_docs` MODIFY COLUMN `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;

ALTER TABLE `pf_sphinx_lemma` CHARACTER set utf8mb4;
ALTER TABLE `pf_sphinx_lemma` MODIFY COLUMN `word` varchar(250) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;

ALTER TABLE `pf_sphinx_synonym` CHARACTER set utf8mb4;
ALTER TABLE `pf_sphinx_synonym` MODIFY COLUMN `item` varchar(250) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;

ALTER TABLE `pf_sphinx_synonym_relate` CHARACTER set utf8mb4;
ALTER TABLE `pf_sphinx_synonym_relate` MODIFY COLUMN `item` varchar(240) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;
ALTER TABLE `pf_sphinx_synonym_relate` MODIFY COLUMN `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;

# SET character_set_client= utf8mb4;
# SET character_set_results=utf8mb4;
# SET character_set_connection =utf8mb4;