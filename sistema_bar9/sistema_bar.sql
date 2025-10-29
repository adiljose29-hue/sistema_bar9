
CREATE DATABASE IF NOT EXISTS sistema_bar;
USE sistema_bar;

-- Estrutura da tabela `devolucao_itens`

DROP TABLE IF EXISTS `devolucao_itens`;
CREATE TABLE IF NOT EXISTS `devolucao_itens` (
  `id_item_devolucao` int NOT NULL AUTO_INCREMENT,
  `id_devolucao` int DEFAULT NULL,
  `id_item_original` int DEFAULT NULL,
  `quantidade_devolvida` int DEFAULT NULL,
  `valor_devolvido` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id_item_devolucao`),
  KEY `id_devolucao` (`id_devolucao`),
  KEY `id_item_original` (`id_item_original`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Estrutura da tabela `devolucoes`

DROP TABLE IF EXISTS `devolucoes`;
CREATE TABLE IF NOT EXISTS `devolucoes` (
  `id_devolucao` int NOT NULL AUTO_INCREMENT,
  `id_venda_original` int DEFAULT NULL,
  `id_supervisor` int DEFAULT NULL,
  `id_vendedor` int DEFAULT NULL,
  `data_devolucao` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `motivo` text,
  `tipo` enum('total','parcial') DEFAULT NULL,
  `valor_devolvido` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id_devolucao`),
  KEY `id_venda_original` (`id_venda_original`),
  KEY `id_supervisor` (`id_supervisor`),
  KEY `id_vendedor` (`id_vendedor`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Estrutura da tabela `logs_sistema`

DROP TABLE IF EXISTS `logs_sistema`;
CREATE TABLE IF NOT EXISTS `logs_sistema` (
  `id_log` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int DEFAULT NULL,
  `acao` varchar(255) NOT NULL,
  `data_hora` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `detalhes` text,
  PRIMARY KEY (`id_log`),
  KEY `id_usuario` (`id_usuario`)
) ENGINE=MyISAM AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Extraindo dados da tabela `logs_sistema`

INSERT INTO `logs_sistema` (`id_log`, `id_usuario`, `acao`, `data_hora`, `detalhes`) VALUES
(1, 4, 'Venda criada: V202510214066', '2025-10-21 11:09:48', 'Total: 1650.00'),
(2, 4, 'Venda criada: V202510211752', '2025-10-21 11:10:48', 'Total: 700.00'),
(3, 4, 'Venda criada: V202510215177', '2025-10-21 11:11:28', 'Total: 2350.00'),
(30, 1, 'Venda criada: V202510292308', '2025-10-29 21:34:56', 'Total: 700.00'),
(31, 1, 'Venda criada: V202510291571', '2025-10-29 21:44:21', 'Total: 1050.00'),
(32, 1, 'Venda criada: V202510298589', '2025-10-29 21:45:22', 'Total: 1600.00'),
(33, 1, 'Venda criada: V202510299456', '2025-10-29 21:46:41', 'Total: 805.00');

-- Estrutura da tabela `produtos`

DROP TABLE IF EXISTS `produtos`;
CREATE TABLE IF NOT EXISTS `produtos` (
  `id_produto` int NOT NULL AUTO_INCREMENT,
  `codigo_barras` varchar(50) DEFAULT NULL,
  `nome` varchar(100) NOT NULL,
  `descricao` text,
  `preco_venda` decimal(10,2) NOT NULL,
  `preco_custo` decimal(10,2) DEFAULT NULL,
  `stock_atual` int DEFAULT '0',
  `stock_minimo` int DEFAULT '0',
  `iva` decimal(5,2) DEFAULT '0.00',
  `ativo` tinyint(1) DEFAULT '1',
  `categoria` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_produto`),
  UNIQUE KEY `codigo_barras` (`codigo_barras`)
) ENGINE=MyISAM AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Extraindo dados da tabela `produtos`

INSERT INTO `produtos` (`id_produto`, `codigo_barras`, `nome`, `descricao`, `preco_venda`, `preco_custo`, `stock_atual`, `stock_minimo`, `iva`, `ativo`, `categoria`) VALUES
(1, '001', 'Cerveja', 'Cerveja Nacional 33cl', 500.00, 300.00, 79, 20, 0.00, 1, 'Bebidas'),
(2, '002', 'Água 0.5L', 'Água Mineral 500ml', 200.00, 80.00, 27, 10, 0.00, 1, 'Bebidas'),
(3, '003', 'Sumo Laranja', 'Sumo Natural de Laranja', 350.00, 150.00, 10, 5, 0.00, 1, 'Bebidas'),
(4, '004', 'Refrigerante', 'Refrigerante 33cl', 300.00, 120.00, 72, 15, 0.00, 1, 'Bebidas'),
(5, '005', 'Café', 'Café Expresso', 150.00, 50.00, 196, 30, 0.00, 1, 'Bebidas'),
(6, '006', 'Chá', 'Chá Quente', 150.00, 40.00, 81, 20, 0.00, 1, 'Bebidas'),
(7, '007', 'Hambúrguer', 'Hambúrguer com Queijo', 1200.00, 600.00, 19, 5, 0.00, 1, 'Comidas'),
(8, '008', 'Pizza', 'Pizza Media', 1500.00, 800.00, 12, 3, 0.00, 1, 'Comidas'),
(9, '009', 'Batatas Fritas', 'Porção de Batatas Fritas', 600.00, 200.00, 39, 8, 0.00, 1, 'Comidas'),
(10, '010', 'Sanduíche', 'Sanduíche Mista', 800.00, 350.00, 28, 6, 0.00, 1, 'Comidas'),
(11, '011', 'Bolo', 'Fatia de Bolo', 450.00, 180.00, 17, 4, 0.00, 1, 'Sobremesas'),
(12, '012', 'Gelado', 'Gelado Artesanal', 400.00, 160.00, 32, 7, 0.00, 1, 'Sobremesas'),
(13, '013', 'Pudim', 'Pudim de Leite', 350.00, 140.00, 24, 5, 0.00, 1, 'Sobremesas'),
(14, '4897057900065', 'Agua', 'agua orion', 298.00, 200.00, 30, 2, 7.00, 1, 'Bebidas');

--
-- Estrutura da tabela `promocoes`

DROP TABLE IF EXISTS `promocoes`;
CREATE TABLE IF NOT EXISTS `promocoes` (
  `id_promocao` int NOT NULL AUTO_INCREMENT,
  `id_produto` int DEFAULT NULL,
  `nome_promocao` varchar(100) DEFAULT NULL,
  `desconto_percentual` decimal(5,2) DEFAULT NULL,
  `preco_promocao` decimal(10,2) DEFAULT NULL,
  `data_inicio` datetime NOT NULL,
  `data_fim` datetime NOT NULL,
  `ativa` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id_promocao`),
  KEY `id_produto` (`id_produto`)
) ENGINE=MyISAM AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Extraindo dados da tabela `promocoes`

INSERT INTO `promocoes` (`id_promocao`, `id_produto`, `nome_promocao`, `desconto_percentual`, `preco_promocao`, `data_inicio`, `data_fim`, `ativa`) VALUES
(1, 1, 'Promoção Cerveja', 10.00, NULL, '2024-01-01 00:00:00', '2024-12-31 23:59:59', 1),
(2, 7, 'Promoção Hambúrguer', NULL, 1000.00, '2024-01-01 00:00:00', '2024-12-31 23:59:59', 0),
(3, 11, 'Promoção Bolo', 15.00, NULL, '2024-01-01 00:00:00', '2024-12-31 23:59:59', 1),
(4, 6, 'tet', 10.00, NULL, '2025-10-21 00:00:00', '2025-11-20 23:59:59', 1),
(5, 3, 'uyt', NULL, 20.00, '2025-10-21 00:00:00', '2025-11-20 23:59:59', 1),
(6, 14, 'der', NULL, 10.00, '2025-10-21 00:00:00', '2025-11-20 23:59:59', 0),
(7, 14, 'jt', 50.00, NULL, '2025-10-21 00:00:00', '2025-11-20 23:59:59', 0),
(8, 14, 'agua promo', 50.00, NULL, '2025-10-29 00:00:00', '2025-11-28 23:59:59', 1),
(9, 4, 'test', 50.00, NULL, '2025-10-29 00:00:00', '2025-11-28 23:59:59', 1),
(10, 12, 'gelado', NULL, 100.00, '2025-10-29 00:00:00', '2025-11-28 23:59:59', 1),
(11, 11, 'bolo', 10.00, NULL, '2025-10-29 00:00:00', '2025-11-28 23:59:59', 1);

-- Estrutura da tabela `usuarios`

DROP TABLE IF EXISTS `usuarios`;
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `numero_trabalhador` varchar(5) NOT NULL,
  `senha` varchar(4) NOT NULL,
  `nome` varchar(100) NOT NULL,
  `tipo` enum('admin','gerente','supervisor','vendedor') NOT NULL,
  `ativo` tinyint(1) DEFAULT '1',
  `data_criacao` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `numero_trabalhador` (`numero_trabalhador`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
--
-- Extraindo dados da tabela `usuarios`
INSERT INTO `usuarios` (`id_usuario`, `numero_trabalhador`, `senha`, `nome`, `tipo`, `ativo`, `data_criacao`) VALUES
(1, '00001', '1234', 'Administrador Sistema', 'admin', 1, '2025-10-21 10:18:32'),
(2, '10001', '1111', 'Maria Silva - Gerente', 'gerente', 1, '2025-10-21 10:18:32'),
(3, '20001', '2222', 'João Santos - Supervisor', 'supervisor', 1, '2025-10-21 10:18:32'),
(4, '30001', '3333', 'Ana Costa - Vendedora', 'vendedor', 1, '2025-10-21 10:18:32'),
(5, '30002', '4444', 'Carlos Lima - Vendedor', 'vendedor', 1, '2025-10-21 10:18:32');

-- Estrutura da tabela `vendas`

DROP TABLE IF EXISTS `vendas`;
CREATE TABLE IF NOT EXISTS `vendas` (
  `id_venda` int NOT NULL AUTO_INCREMENT,
  `numero_venda` varchar(20) DEFAULT NULL,
  `id_vendedor` int DEFAULT NULL,
  `data_venda` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `total` decimal(10,2) NOT NULL,
  `desconto` decimal(10,2) DEFAULT '0.00',
  `total_final` decimal(10,2) NOT NULL,
  `forma_pagamento` enum('dinheiro','multicaixa','transferencia','outro') DEFAULT NULL,
  `estado` enum('pendente','concluida','anulada') DEFAULT 'concluida',
  `id_supervisor` int DEFAULT NULL,
  PRIMARY KEY (`id_venda`),
  UNIQUE KEY `numero_venda` (`numero_venda`),
  KEY `id_vendedor` (`id_vendedor`),
  KEY `id_supervisor` (`id_supervisor`)
) ENGINE=MyISAM AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
-
-- Extraindo dados da tabela `vendas`
--INSERT INTO `vendas` (`id_venda`, `numero_venda`, `id_vendedor`, `data_venda`, `total`, `desconto`, `total_final`, `forma_pagamento`, `estado`, `id_supervisor`) VALUES
(1, 'V202510214066', 4, '2025-10-21 11:09:48', 1650.00, 0.00, 1650.00, 'multicaixa', 'concluida', NULL),
(2, 'V202510211752', 4, '2025-10-21 11:10:48', 700.00, 0.00, 700.00, 'transferencia', 'concluida', NULL),
(33, 'V202510299456', 1, '2025-10-29 21:46:41', 805.00, 0.00, 805.00, 'dinheiro', 'concluida', NULL);
--
-- Estrutura da tabela `venda_itens`
--

DROP TABLE IF EXISTS `venda_itens`;
CREATE TABLE IF NOT EXISTS `venda_itens` (
  `id_item` int NOT NULL AUTO_INCREMENT,
  `id_venda` int DEFAULT NULL,
  `id_produto` int DEFAULT NULL,
  `quantidade` int NOT NULL,
  `preco_unitario` decimal(10,2) NOT NULL,
  `desconto` decimal(10,2) DEFAULT '0.00',
  `total_item` decimal(10,2) NOT NULL,
  `anulado` tinyint(1) DEFAULT '0',
  `id_supervisor_anulacao` int DEFAULT NULL,
  PRIMARY KEY (`id_item`),
  KEY `id_venda` (`id_venda`),
  KEY `id_produto` (`id_produto`),
  KEY `id_supervisor_anulacao` (`id_supervisor_anulacao`)
) ENGINE=MyISAM AUTO_INCREMENT=113 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
--
-- Extraindo dados da tabela `venda_itens`
--
INSERT INTO `venda_itens` (`id_item`, `id_venda`, `id_produto`, `quantidade`, `preco_unitario`, `desconto`, `total_item`, `anulado`, `id_supervisor_anulacao`) VALUES
(1, 1, 2, 1, 200.00, 0.00, 200.00, 0, NULL),
(2, 1, 5, 1, 150.00, 0.00, 150.00, 0, NULL),
(3, 1, 6, 1, 150.00, 0.00, 150.00, 0, NULL),
(4, 1, 3, 1, 350.00, 0.00, 350.00, 0, NULL),
(5, 1, 4, 1, 300.00, 0.00, 300.00, 0, NULL),
(6, 1, 1, 1, 500.00, 0.00, 500.00, 0, NULL),
(109, 32, 7, 1, 1200.00, 0.00, 1200.00, 0, NULL),
(110, 32, 12, 1, 400.00, 0.00, 400.00, 0, NULL),
(111, 33, 12, 1, 400.00, 0.00, 400.00, 0, NULL),
(112, 33, 11, 1, 405.00, 0.00, 405.00, 0, NULL);
COMMIT;

