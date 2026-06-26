-- MySQL dump 10.13  Distrib 8.4.8, for Linux (x86_64)
--
-- Home Inventory Database - Sample Data
-- Generic examples for each table
-- Update with your own data as needed

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

USE casa;

--
-- Dumping data for table `inventory_divisao` (House Divisions)
--

LOCK TABLES `inventory_divisao` WRITE;
/*!40000 ALTER TABLE `inventory_divisao` DISABLE KEYS */;
INSERT INTO `inventory_divisao` (nome) VALUES 
('Living Room'),
('Kitchen'),
('Bedroom'),
('Bathroom'),
('Office'),
('Garage'),
('Pantry');
/*!40000 ALTER TABLE `inventory_divisao` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `inventory_item` (Inventory Items)
--

LOCK TABLES `inventory_item` WRITE;
/*!40000 ALTER TABLE `inventory_item` DISABLE KEYS */;
INSERT INTO `inventory_item` (nome, descricao, quantidade, imagem, valor, divisao_id, data_aquisicao) VALUES 
('Coffee Maker', 'Kitchen appliance for brewing coffee', 1, '', 45.99, 2, '2024-01-15'),
('Desk Chair', 'Office chair for workspace', 1, '', 120.00, 5, '2024-02-10'),
('Bed Sheets Set', 'Queen size cotton bed sheets', 2, '', 35.50, 3, '2024-01-20'),
('Desk Lamp', 'LED desk lamp with adjustable brightness', 1, '', 28.99, 5, '2024-03-05'),
('Kitchen Knife Set', 'Stainless steel knife set with holder', 1, '', 65.00, 2, '2024-02-28'),
('Storage Shelves', 'Metal storage unit for garage', 1, '', 89.95, 6, '2024-03-10'),
('Bathroom Towels', 'Set of 6 cotton towels', 1, '', 42.00, 4, '2024-03-01');
/*!40000 ALTER TABLE `inventory_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `inventory_desejo` (Wishlist Items)
--

LOCK TABLES `inventory_desejo` WRITE;
/*!40000 ALTER TABLE `inventory_desejo` DISABLE KEYS */;
INSERT INTO `inventory_desejo` (nome, descricao, valor, imagem, divisao_id) VALUES 
('Bookshelf', 'Wooden bookshelf for office library', 150.00, '', 5),
('Monitor Stand', 'Ergonomic monitor stand for desk', 35.00, '', 5),
('Wall Art', 'Decorative wall art for living room', 75.00, '', 1);
/*!40000 ALTER TABLE `inventory_desejo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `inventory_compra` (Shopping List)
--

LOCK TABLES `inventory_compra` WRITE;
/*!40000 ALTER TABLE `inventory_compra` DISABLE KEYS */;
INSERT INTO `inventory_compra` (nome, quantidade, comprado, divisao_id) VALUES 
('Milk', 1, 0, 2),
('Bread', 1, 0, 2),
('Rice', 2, 0, 2),
('Light Bulbs', 4, 0, 2),
('Cleaning Supplies', 1, 0, 1),
('Paper Towels', 2, 0, 1);
/*!40000 ALTER TABLE `inventory_compra` ENABLE KEYS */;
UNLOCK TABLES;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed
