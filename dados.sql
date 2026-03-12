-- MySQL dump 10.13  Distrib 8.4.8, for Linux (x86_64)
--
-- Host: localhost    Database: casa
-- ------------------------------------------------------
-- Server version	8.4.8

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `inventory_compra` WRITE;
/*!40000 ALTER TABLE `inventory_compra` DISABLE KEYS */;
INSERT INTO `inventory_compra` VALUES (8,'silicone para airfryer',1,0,3),(9,'Lampada',1,0,4),(10,'Saleiro',1,0,3),(11,'Jarro com filtro',1,0,3),(12,'Cesto da lenha',1,0,6),(13,'Taboa de engomar',1,0,7),(14,' Assadeira',1,0,3),(15,'Bacia para cozinhar',1,0,3);
/*!40000 ALTER TABLE `inventory_compra` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `inventory_desejo`
--

LOCK TABLES `inventory_desejo` WRITE;
/*!40000 ALTER TABLE `inventory_desejo` DISABLE KEYS */;
INSERT INTO `inventory_desejo` VALUES (1,'Secretaria','Secretaria para wifey',129.00,'desejos/Captura_de_ecrã_2026-03-05_114950.png',5);
/*!40000 ALTER TABLE `inventory_desejo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `inventory_divisao`
--

LOCK TABLES `inventory_divisao` WRITE;
/*!40000 ALTER TABLE `inventory_divisao` DISABLE KEYS */;
INSERT INTO `inventory_divisao` VALUES (2,'Quarto'),(3,'Cozinha'),(4,'WC'),(5,'Escritório'),(6,'Sala'),(7,'Marquise');
/*!40000 ALTER TABLE `inventory_divisao` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `inventory_item`
--

LOCK TABLES `inventory_item` WRITE;
/*!40000 ALTER TABLE `inventory_item` DISABLE KEYS */;
INSERT INTO `inventory_item` VALUES (2,'Fervedor','',1,'itens/Captura_de_ecrã_2026-03-05_115224.png','2026-03-05 11:55:18.577665',26.99,3,'2026-03-04'),(3,'Kallax','Movel TV',1,'itens/Captura_de_ecrã_2026-03-09_122732.png','2026-03-09 12:27:57.425419',55.00,6,'2026-03-07'),(4,'Espelho de pé','',1,'itens/Captura_de_ecrã_2026-03-09_122846.png','2026-03-09 12:28:57.736046',39.99,2,'2026-03-07'),(5,'Gavetas kallax','gavetas para o movel da tv',2,'itens/Captura_de_ecrã_2026-03-09_122956.png','2026-03-09 12:30:14.079647',30.00,6,'2026-03-07'),(6,'Portas Kallax','Portas para o movel da tv',2,'itens/Captura_de_ecrã_2026-03-09_123003.png','2026-03-09 12:31:24.193970',19.98,6,'2026-03-07'),(7,'Caixote do Lixo','',1,'itens/Captura_de_ecrã_2026-03-09_123251.png','2026-03-09 12:34:39.762713',25.00,3,'2026-03-04'),(8,'Protetor de colchao','',1,'itens/Captura_de_ecrã_2026-03-09_123257.png','2026-03-09 12:35:15.230199',15.99,2,'2026-03-04'),(9,'Tabua de cortar','',1,'itens/Captura_de_ecrã_2026-03-09_123302.png','2026-03-09 12:35:46.781260',9.99,3,'2026-03-04'),(10,'Conj copo sabao','',1,'itens/Captura_de_ecrã_2026-03-09_123308.png','2026-03-09 12:36:39.991093',9.99,4,'2026-03-04');
/*!40000 ALTER TABLE `inventory_item` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-11 17:39:28
