-- Tabela para fatos observados
CREATE TABLE IF NOT EXISTS fatos_observados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    aluno_id INT NOT NULL,
    tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('Positivo', 'Negativo')),
    descricao TEXT NOT NULL,
    consequencia VARCHAR(50) NOT NULL,
    data TIMESTAMP NOT NULL,
    FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON DELETE CASCADE
);

-- Tabela para observações gerais
CREATE TABLE IF NOT EXISTS observacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    aluno_id INT NOT NULL,
    tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('Positivo', 'Negativo')),
    descricao TEXT NOT NULL,
    disciplina VARCHAR(50) NOT NULL,
    data TIMESTAMP NOT NULL,
    FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON DELETE CASCADE
);

-- Tabela para turmas
CREATE TABLE IF NOT EXISTS turmas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    escola_id INT NOT NULL,
    FOREIGN KEY (escola_id) REFERENCES escolas(id) ON DELETE CASCADE
);

-- Inserir turmas baseadas nos dados existentes
INSERT IGNORE INTO turmas (nome, escola_id)
SELECT DISTINCT turma, escola_id
FROM alunos
WHERE turma IS NOT NULL;

-- Atualizar turma_id na tabela alunos
UPDATE alunos a
JOIN turmas t ON a.turma = t.nome AND a.escola_id = t.escola_id
SET a.turma_id = t.id
WHERE a.turma_id IS NULL; 