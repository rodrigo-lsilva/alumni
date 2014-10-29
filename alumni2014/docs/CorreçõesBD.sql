/**
 * Correções realizadas em 06-07/05/2014
 */

/*
 * Remove as linhas duplicadas. 
 */
delete from logica_convite where id=2;
/*
 * Torna a coluna id not nullable, chave primária e define auto incremento
 */
ALTER TABLE `egressosdb_v1`.`logica_convite` CHANGE COLUMN `id` `id` INT(11) NOT NULL AUTO_INCREMENT , ADD PRIMARY KEY (`id`) ;
/*
 * Readiciona a linha apenas uma das linhas duplicadas.
 */
INSERT INTO logica_convite(id, de_id, para_id, email, status, chave) VALUES('2', '1', '392', 'fubica@dsc.ufcg.edu.br', 'ok', 'e4KFmBtssUte7HnynynUpH060BmYlU81DZJispOUyfTd9WPepUNOdeD0uznUaVR4IrnjlUpSXfkTm8vb');
 