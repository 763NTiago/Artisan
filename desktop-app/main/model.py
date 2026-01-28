import sqlite3
import json
from . import utils
from datetime import datetime, timedelta

class DatabaseModel:
    """
    Camada de Acesso a Dados (DAO) do sistema Artisan.
    Gerencia todas as conexões e queries com o banco SQLite.
    """
    
    def __init__(self):
        # Inicializa o caminho do banco de dados na pasta do usuário
        db_path = utils.inicializar_db_persistente("orcamentos.db")
        # check_same_thread=False é necessário para bibliotecas que usam threads, como PDFKit
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON;") 
        self.conn.execute("PRAGMA busy_timeout = 5000") 
        self.conn.row_factory = sqlite3.Row 
        print(f"Conectado ao Banco de Dados Artisan em: {db_path}")

    def get_connection(self):
        return self.conn

    def init_db(self):
        """ Cria as tabelas do banco de dados se não existirem e aplica migrações. """
        cursor = self.conn.cursor()
        
        # --- TABELAS PRINCIPAIS ---
        
        # Tabela de Orçamentos (Histórico gerado em PDF)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orcamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, data_criacao TEXT,
            cliente_nome TEXT, cliente_endereco TEXT, cliente_cpf TEXT,
            cliente_email TEXT, cliente_telefone TEXT, itens_json TEXT, 
            valor_total_final TEXT, observacoes TEXT, condicoes_pagamento TEXT,
            agenda_id INTEGER,
            FOREIGN KEY (agenda_id) REFERENCES agenda (id) ON DELETE SET NULL
        )
        """)
        
        # Tabela de Materiais (Cadastro de insumos)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS materiais (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL UNIQUE, descricao TEXT
        )
        """)
        
        # Tabela de Clientes (Base centralizada)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes_app (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL UNIQUE
        )
        """)
        
        # Tabela Agenda (Controle de Obras e Prazos)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS agenda (
            id INTEGER PRIMARY KEY AUTOINCREMENT, cliente_id INTEGER, 
            data_previsao_termino DATE, descricao TEXT,
            data_inicio DATE,
            FOREIGN KEY (cliente_id) REFERENCES clientes_app (id) ON DELETE SET NULL
        )
        """)
        
        # Tabela Recebimentos (Cabeçalho financeiro)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS recebimentos_pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, cliente_id INTEGER, 
            agenda_id INTEGER,
            tipo_pagamento TEXT, valor_total REAL, valor_entrada REAL,
            num_parcelas INTEGER, valor_parcela REAL, data_1_venc DATE,
            FOREIGN KEY (cliente_id) REFERENCES clientes_app (id) ON DELETE SET NULL,
            FOREIGN KEY (agenda_id) REFERENCES agenda (id) ON DELETE SET NULL
        )
        """)
        
        # Tabela Comissões (Pagamentos a parceiros)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS comissoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            data DATE, 
            cliente_id INTEGER, 
            recebimento_id INTEGER,
            beneficiario TEXT,
            descricao TEXT, 
            valor REAL,
            porcentagem REAL, 
            valor_base REAL,
            FOREIGN KEY (cliente_id) REFERENCES clientes_app (id) ON DELETE SET NULL,
            FOREIGN KEY (recebimento_id) REFERENCES recebimentos_pagamentos (id) ON DELETE SET NULL
        )
        """)
        
        # Tabela Parcelas (Detalhamento financeiro)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS parcelas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recebimento_id INTEGER NOT NULL,
            num_parcela INTEGER,
            valor_parcela REAL,
            data_vencimento DATE,
            data_recebimento DATE,
            valor_recebido REAL,
            FOREIGN KEY (recebimento_id) REFERENCES recebimentos_pagamentos (id) ON DELETE CASCADE
        )
        """)
        
        # Tabela Arquitetos (Cadastro de Parceiros)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS arquitetos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            nome TEXT NOT NULL UNIQUE,
            data_pagamento DATE
        )
        """)
        
        # --- MIGRAÇÕES DE ESQUEMA (Para atualizar bancos antigos) ---
        self._adicionar_coluna('agenda', 'data_inicio', 'DATE')
        self._adicionar_coluna('parcelas', 'valor_recebido', 'REAL') 
        self._adicionar_coluna('comissoes', 'recebimento_id', 'INTEGER')
        self._adicionar_coluna('comissoes', 'beneficiario', 'TEXT')
        self._adicionar_coluna('recebimentos_pagamentos', 'agenda_id', 'INTEGER')
        self._adicionar_coluna('orcamentos', 'agenda_id', 'INTEGER')
        self._adicionar_coluna('comissoes', 'porcentagem', 'REAL')
        self._adicionar_coluna('comissoes', 'valor_base', 'REAL')
        self._adicionar_coluna('arquitetos', 'data_pagamento', 'DATE')
        self._remover_coluna_obsoleta('recebimentos_pagamentos', 'projeto')

        # --- OTIMIZAÇÃO: CRIAÇÃO DE ÍNDICES ---
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orcamentos_agenda ON orcamentos(agenda_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agenda_cliente ON agenda(cliente_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_recebimentos_cliente ON recebimentos_pagamentos(cliente_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_recebimentos_agenda ON recebimentos_pagamentos(agenda_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_parcelas_recebimento ON parcelas(recebimento_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_parcelas_vencimento ON parcelas(data_vencimento)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_comissoes_recebimento ON comissoes(recebimento_id)")
        
        self.conn.commit()
        cursor.close()
        print("Banco de dados Artisan inicializado.")

    def _adicionar_coluna(self, tabela, coluna, tipo):
        try:
            self.conn.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {tipo}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e): pass 
            else: raise e
    
    def _remover_coluna_obsoleta(self, tabela, coluna):
        try:
            self.conn.execute(f"ALTER TABLE {tabela} DROP COLUMN {coluna}")
        except sqlite3.OperationalError: pass

    def close(self): 
        if self.conn:
            self.conn.close()

    # =========================================================================
    # ORÇAMENTOS
    # =========================================================================

    def salvar_orcamento(self, dados, agenda_id=None):
        try:
            itens_para_json = json.dumps(dados["itens"])
            cursor = self.conn.cursor()
            cursor.execute("""
            INSERT INTO orcamentos (
                data_criacao, cliente_nome, cliente_endereco, cliente_cpf,
                cliente_email, cliente_telefone, itens_json, valor_total_final,
                observacoes, condicoes_pagamento, agenda_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dados["data_hoje"], dados["cliente_nome"], dados["cliente_endereco"], dados["cliente_cpf"],
                dados["cliente_email"], dados["cliente_telefone"], itens_para_json, dados["valor_total_final"],
                dados["observacoes_brutas"], dados["pagamento_brutas"], agenda_id
            ))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Erro ao salvar orçamento: {e}")
            return False
            
    def get_all_orcamentos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, data_criacao, cliente_nome, valor_total_final FROM orcamentos ORDER BY id DESC LIMIT 100")
        resultado = cursor.fetchall()
        cursor.close()
        return resultado
        
    def get_orcamento_by_id(self, orcamento_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM orcamentos WHERE id = ?", (orcamento_id,))
        res = cursor.fetchone()
        cursor.close()
        return res
        
    def delete_orcamento(self, orcamento_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM orcamentos WHERE id = ?", (orcamento_id,))
            self.conn.commit()
            cursor.close()
        except:
            self.conn.rollback()
        
    def update_orcamento(self, orcamento_id, dados):
        try:
            itens_para_json = json.dumps(dados["itens"])
            cursor = self.conn.cursor()
            cursor.execute("""
            UPDATE orcamentos 
            SET 
                cliente_nome = ?, cliente_endereco = ?, cliente_cpf = ?,
                cliente_email = ?, cliente_telefone = ?, itens_json = ?, 
                valor_total_final = ?, observacoes = ?, condicoes_pagamento = ?
            WHERE id = ?
            """, (
                dados["cliente_nome"], dados["cliente_endereco"], dados["cliente_cpf"],
                dados["cliente_email"], dados["cliente_telefone"], itens_para_json, 
                dados["valor_total_final"],
                dados["observacoes_brutas"], dados["pagamento_brutas"],
                orcamento_id 
            ))
            self.conn.commit()
            cursor.close()
            return True 
        except Exception as e:
            self.conn.rollback() 
            return False

    # =========================================================================
    # MATERIAIS
    # =========================================================================
    def add_material(self, nome, descricao):
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO materiais (nome, descricao) VALUES (?, ?)", (nome, descricao))
            self.conn.commit()
            cursor.close()
            return True
        except sqlite3.IntegrityError: return "IntegrityError"
        except Exception: return False

    def get_all_materiais(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nome, descricao FROM materiais ORDER BY nome ASC")
        res = cursor.fetchall()
        cursor.close()
        return res

    def delete_material(self, material_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM materiais WHERE id = ?", (material_id,))
        self.conn.commit()
        cursor.close()

    def get_material_by_id(self, material_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nome, descricao FROM materiais WHERE id = ?", (material_id,))
        res = cursor.fetchone()
        cursor.close()
        return res

    def update_material(self, material_id, nome, descricao):
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE materiais SET nome = ?, descricao = ? WHERE id = ?", (nome, descricao, material_id))
            self.conn.commit()
            cursor.close()
            return True
        except sqlite3.IntegrityError: return "IntegrityError"
        except Exception: return False

    # =========================================================================
    # CLIENTES
    # =========================================================================
    def get_or_create_cliente_app(self, nome):
        cursor = self.conn.cursor()
        nome = nome.strip()
        if not nome: raise ValueError("O nome do cliente não pode estar vazio.")
        cursor.execute("SELECT id FROM clientes_app WHERE nome = ?", (nome,))
        resultado = cursor.fetchone()
        if resultado: 
            cursor.close()
            return resultado[0]
        else:
            cursor.execute("INSERT INTO clientes_app (nome) VALUES (?)", (nome,))
            self.conn.commit()
            last_id = cursor.lastrowid
            cursor.close()
            return last_id

    def get_clientes_app_autocomplete(self, search_term):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nome FROM clientes_app WHERE nome LIKE ? ORDER BY nome ASC LIMIT 10", (f"{search_term}%",))
        res = [f"{id} - {nome}" for id, nome in cursor.fetchall()]
        cursor.close()
        return res

    def get_all_clientes_app_para_combobox(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nome FROM clientes_app ORDER BY nome ASC")
        res = [f"{id} - {nome}" for id, nome in cursor.fetchall()]
        cursor.close()
        return res

    # =========================================================================
    # COMISSÕES
    # =========================================================================
    def add_comissao(self, data, cliente_id, recebimento_id, beneficiario, descricao, valor, porcentagem, valor_base):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO comissoes (data, cliente_id, recebimento_id, beneficiario, descricao, valor, porcentagem, valor_base) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (data, cliente_id, recebimento_id, beneficiario, descricao, valor, porcentagem, valor_base))
            self.conn.commit()
            cursor.close()
        except Exception as e:
            self.conn.rollback()
            print(f"Erro add_comissao: {e}")

    def get_comissoes(self, filtro_texto=""):
        cursor = self.conn.cursor()
        query = """
            SELECT 
                com.id, 
                strftime('%d/%m/%Y', com.data) as data, 
                c.nome, 
                a.descricao AS projeto_nome,
                com.beneficiario,
                com.descricao, 
                com.valor,
                com.porcentagem,
                com.valor_base 
            FROM comissoes com 
            LEFT JOIN recebimentos_pagamentos r ON com.recebimento_id = r.id
            LEFT JOIN clientes_app c ON com.cliente_id = c.id
            LEFT JOIN agenda a ON r.agenda_id = a.id
        """
        params = []
        if filtro_texto:
            query += " WHERE (c.nome LIKE ? OR a.descricao LIKE ? OR com.beneficiario LIKE ? OR com.descricao LIKE ?)"
            term = f"%{filtro_texto}%"
            params.extend([term, term, term, term])
            
        query += " ORDER BY com.data DESC, com.id DESC LIMIT 200"
        cursor.execute(query, params)
        res = cursor.fetchall()
        cursor.close()
        return res
        
    def get_comissao_by_id(self, comissao_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                com.id, 
                com.data, 
                com.descricao, 
                com.valor, 
                com.cliente_id, 
                c.nome AS cliente_nome,
                com.recebimento_id,
                a.descricao AS projeto_nome,
                com.beneficiario,
                com.porcentagem,
                com.valor_base
            FROM comissoes com 
            LEFT JOIN recebimentos_pagamentos r ON com.recebimento_id = r.id
            LEFT JOIN clientes_app c ON com.cliente_id = c.id
            LEFT JOIN agenda a ON r.agenda_id = a.id
            WHERE com.id = ?
        """, (comissao_id,))
        res = cursor.fetchone()
        cursor.close()
        return res
        
    def update_comissao(self, comissao_id, data, cliente_id, recebimento_id, beneficiario, descricao, valor, porcentagem, valor_base):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE comissoes 
                SET data = ?, cliente_id = ?, recebimento_id = ?, beneficiario = ?, descricao = ?, valor = ?, porcentagem = ?, valor_base = ? 
                WHERE id = ?
            """, (data, cliente_id, recebimento_id, beneficiario, descricao, valor, porcentagem, valor_base, comissao_id))
            self.conn.commit()
            cursor.close()
        except: self.conn.rollback()
        
    def delete_comissao(self, comissao_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM comissoes WHERE id = ?", (comissao_id,))
            self.conn.commit()
            cursor.close()
        except: self.conn.rollback()

    # =========================================================================
    # AGENDA
    # =========================================================================
    def add_agenda(self, cliente_id, data_inicio, data_termino, descricao):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO agenda (cliente_id, data_inicio, data_previsao_termino, descricao) VALUES (?, ?, ?, ?)",
            (cliente_id, data_inicio, data_termino, descricao)
        )
        self.conn.commit()
        last_id = cursor.lastrowid
        cursor.close()
        return last_id

    def get_agenda(self, filtro_cliente="", filtro_data=None):
        cursor = self.conn.cursor()
        query = """
            SELECT r.id, c.nome, 
                   strftime('%d/%m/%Y', r.data_inicio), 
                   strftime('%d/%m/%Y', r.data_previsao_termino), 
                   r.descricao 
            FROM agenda r 
            LEFT JOIN clientes_app c ON r.cliente_id = c.id
        """
        params = []
        conditions = []

        if filtro_cliente:
            conditions.append("c.nome LIKE ?")
            params.append(f"%{filtro_cliente}%")
        
        if filtro_data:
            if filtro_data == "hoje":
                conditions.append("(date(r.data_inicio) = date('now', 'localtime') OR date(r.data_previsao_termino) = date('now', 'localtime'))")
            elif filtro_data == "semana":
                conditions.append("date(r.data_previsao_termino) BETWEEN date('now', 'localtime', 'weekday 0', '-6 days') AND date('now', 'localtime', 'weekday 0', '+6 days')")
            elif filtro_data == "mes":
                conditions.append("strftime('%Y-%m', r.data_previsao_termino) = strftime('%Y-%m', 'now', 'localtime')")
            else:
                try:
                    datetime.strptime(filtro_data, "%Y-%m-%d")
                    conditions.append("(r.data_inicio = ? OR r.data_previsao_termino = ?)")
                    params.append(filtro_data)
                    params.append(filtro_data)
                except ValueError: pass 

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY r.data_previsao_termino DESC, r.id DESC LIMIT 100"
        
        cursor.execute(query, params)
        res = cursor.fetchall()
        cursor.close()
        return res
        
    def get_agenda_by_id(self, agenda_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT r.id, r.data_inicio, r.data_previsao_termino, r.descricao, r.cliente_id, c.nome FROM agenda r LEFT JOIN clientes_app c ON r.cliente_id = c.id WHERE r.id = ?", (agenda_id,))
        res = cursor.fetchone()
        cursor.close()
        return res

    def update_agenda(self, agenda_id, cliente_id, data_inicio, data_termino, descricao):
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE agenda SET cliente_id = ?, data_inicio = ?, data_previsao_termino = ?, descricao = ? WHERE id = ?", (cliente_id, data_inicio, data_termino, descricao, agenda_id))
            self.conn.commit()
            cursor.close()
        except: self.conn.rollback()

    def delete_agenda(self, agenda_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM agenda WHERE id = ?", (agenda_id,))
            self.conn.commit()
            cursor.close()
        except: self.conn.rollback()
    
    # =========================================================================
    # RECEBIMENTOS E PAGAMENTOS
    # =========================================================================
    def add_recebimento_pagamento(self, dados):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO recebimentos_pagamentos (
                    cliente_id, agenda_id, tipo_pagamento, valor_total, valor_entrada,
                    num_parcelas, valor_parcela, data_1_venc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dados["cliente_id"], dados["agenda_id"], dados["tipo_pagamento"],
                dados["valor_total"], dados["valor_entrada"], dados["num_parcelas"],
                dados["valor_parcela"], dados["data_1_venc"]
            ))
            recebimento_id = cursor.lastrowid
            
            if dados["valor_entrada"] > 0.0:
                data_hoje_str = datetime.now().strftime("%Y-%m-%d")
                cursor.execute("""
                    INSERT INTO parcelas (
                        recebimento_id, num_parcela, valor_parcela, 
                        data_vencimento, data_recebimento, valor_recebido
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (recebimento_id, 0, dados["valor_entrada"], data_hoje_str, data_hoje_str, dados["valor_entrada"]))
            
            if dados["tipo_pagamento"] in ["Entrada + Parcelas", "Cartão (Crédito)", "Saldo Aberto (Abatimento)"]:
                if dados["data_1_venc"]:
                    try:
                        data_venc = datetime.strptime(dados["data_1_venc"], "%d/%m/%Y").date()
                    except ValueError:
                        data_venc = datetime.strptime(dados["data_1_venc"], "%Y-%m-%d").date()

                    for i in range(dados["num_parcelas"]):
                        cursor.execute("""
                            INSERT INTO parcelas (recebimento_id, num_parcela, valor_parcela, data_vencimento, valor_recebido)
                            VALUES (?, ?, ?, ?, ?)
                        """, (recebimento_id, i + 1, dados["valor_parcela"], data_venc, 0.0)) 
                        data_venc = data_venc + timedelta(days=30) 
                    
            self.conn.commit()
            cursor.close()
        except Exception as e:
            self.conn.rollback()
            print(f"Erro add_recebimento: {e}")
    
    def receber_parcela(self, parcela_id, data_recebimento, valor_pago_agora):
        cursor = self.conn.cursor()
        try:
            query_busca = "SELECT p.recebimento_id, p.num_parcela, p.valor_parcela, p.valor_recebido, p.data_vencimento FROM parcelas p WHERE p.id = ?"
            cursor.execute(query_busca, (parcela_id,))
            row = cursor.fetchone()
            
            if not row: raise Exception("Parcela não encontrada.")
            valor_original_parcela = row["valor_parcela"]
            valor_ja_pago = row["valor_recebido"] if row["valor_recebido"] is not None else 0.0
            data_venc_atual_str = row["data_vencimento"]
            
            novo_total_recebido = valor_ja_pago + valor_pago_agora
            
            try: data_fmt = datetime.strptime(data_recebimento, "%d/%m/%Y").strftime("%Y-%m-%d")
            except ValueError: data_fmt = data_recebimento

            restante = valor_original_parcela - novo_total_recebido
            sql_update = "UPDATE parcelas SET data_recebimento = ?, valor_recebido = ? WHERE id = ?"
            params = [data_fmt, novo_total_recebido, parcela_id]

            if restante > 0.01 and data_venc_atual_str:
                try:
                    date_obj = datetime.strptime(data_venc_atual_str, "%Y-%m-%d").date()
                    new_date = date_obj + timedelta(days=30)
                    new_date_str = new_date.strftime("%Y-%m-%d")
                    sql_update = "UPDATE parcelas SET data_recebimento = ?, valor_recebido = ?, data_vencimento = ? WHERE id = ?"
                    params = [data_fmt, novo_total_recebido, new_date_str, parcela_id]
                except Exception as e:
                    print(f"Erro ao calcular nova data: {e}")

            cursor.execute(sql_update, params)
            self.conn.commit()
            cursor.close()
        except Exception as e:
            self.conn.rollback() 
            if cursor: cursor.close()
            raise e

    # =========================================================================
    # CONSULTAS OTIMIZADAS (Dashboards e Relatórios)
    # =========================================================================

    def get_all_projetos_agenda(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT a.id, c.nome as cliente_nome, a.descricao, 
                   a.data_inicio, a.data_previsao_termino
            FROM agenda a
            LEFT JOIN clientes_app c ON a.cliente_id = c.id
            ORDER BY a.data_previsao_termino DESC LIMIT 50
        """)
        res = cursor.fetchall()
        cursor.close()
        return res

    def get_all_recebimentos(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.id, p.data_vencimento, p.valor_parcela, 
                   p.valor_recebido, c.nome as cliente_nome, a.descricao as projeto
            FROM parcelas p
            JOIN recebimentos_pagamentos r ON p.recebimento_id = r.id
            LEFT JOIN clientes_app c ON r.cliente_id = c.id
            LEFT JOIN agenda a ON r.agenda_id = a.id
            WHERE (p.valor_parcela - IFNULL(p.valor_recebido, 0)) > 0.01
            ORDER BY p.data_vencimento ASC LIMIT 200
        """)
        res = cursor.fetchall()
        cursor.close()
        return res

    def get_datas_agenda(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT data_inicio, data_previsao_termino FROM agenda 
            ORDER BY data_previsao_termino DESC LIMIT 300
        """)
        datas = set()
        for row in cursor.fetchall():
            if row["data_inicio"]: datas.add(datetime.strptime(row["data_inicio"], "%Y-%m-%d").date())
            if row["data_previsao_termino"]: datas.add(datetime.strptime(row["data_previsao_termino"], "%Y-%m-%d").date())
        cursor.close()
        return list(datas)

    def get_datas_vencimento_parcelas(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT data_vencimento FROM parcelas 
            WHERE (valor_parcela - IFNULL(valor_recebido, 0)) > 0.01
            LIMIT 300
        """)
        datas = set()
        for row in cursor.fetchall():
            if row["data_vencimento"]: datas.add(datetime.strptime(row["data_vencimento"], "%Y-%m-%d").date())
        cursor.close()
        return list(datas)
        
    def get_proximas_parcelas(self, limit=10):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.data_vencimento, (p.valor_parcela - IFNULL(p.valor_recebido, 0)) as valor_restante, 
                   c.nome, a.descricao AS projeto_nome
            FROM parcelas p
            JOIN recebimentos_pagamentos r ON p.recebimento_id = r.id
            JOIN clientes_app c ON r.cliente_id = c.id
            LEFT JOIN agenda a ON r.agenda_id = a.id
            WHERE p.num_parcela != 0 
            AND (p.valor_parcela - IFNULL(p.valor_recebido, 0)) > 0.01
            AND date(p.data_vencimento) >= date('now', 'localtime')
            ORDER BY p.data_vencimento ASC LIMIT ?
        """, (limit,))
        res = cursor.fetchall()
        cursor.close()
        return res
        
    def get_proximo_evento_unificado(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT data_inicio as data_evento, 'Início' as tipo, descricao, c.nome as cliente_nome,
                   CAST(julianday(data_inicio) - julianday('now', 'localtime') AS INTEGER) as dias
            FROM agenda a
            LEFT JOIN clientes_app c ON a.cliente_id = c.id
            WHERE date(data_inicio) >= date('now', 'localtime')
            
            UNION ALL
            
            SELECT data_previsao_termino as data_evento, 'Entrega' as tipo, descricao, c.nome as cliente_nome,
                   CAST(julianday(data_previsao_termino) - julianday('now', 'localtime') AS INTEGER) as dias
            FROM agenda a
            LEFT JOIN clientes_app c ON a.cliente_id = c.id
            WHERE date(data_previsao_termino) >= date('now', 'localtime')
            
            ORDER BY data_evento ASC
            LIMIT 1
        """)
        res = cursor.fetchone()
        cursor.close()
        return res

    def get_eventos_do_dia(self, data_iso):
        cursor = self.conn.cursor()
        eventos = {"entregas": [], "vencimentos": []}

        cursor.execute("""
            SELECT c.nome, a.descricao, a.data_inicio, a.data_previsao_termino
            FROM agenda a
            LEFT JOIN clientes_app c ON a.cliente_id = c.id
            WHERE a.data_inicio = ? OR a.data_previsao_termino = ?
        """, (data_iso, data_iso))
        
        for row in cursor.fetchall():
            if row["data_inicio"] == data_iso:
                cliente_nome = row["nome"] or "Cliente N/A"
                descricao = row["descricao"] or "Sem descrição"
                eventos["entregas"].append( (cliente_nome, f"Início: {descricao}") )
            
            if row["data_previsao_termino"] == data_iso:
                cliente_nome = row["nome"] or "Cliente N/A"
                descricao = row["descricao"] or "Sem descrição"
                eventos["entregas"].append( (cliente_nome, f"Entrega: {descricao}") )

        cursor.execute("""
            SELECT c.nome, a.descricao AS projeto_nome, 
                   (p.valor_parcela - IFNULL(p.valor_recebido, 0)) as valor_restante
            FROM parcelas p
            JOIN recebimentos_pagamentos r ON p.recebimento_id = r.id
            JOIN clientes_app c ON r.cliente_id = c.id
            LEFT JOIN agenda a ON r.agenda_id = a.id
            WHERE p.data_vencimento = ? 
            AND p.num_parcela != 0
            AND (p.valor_parcela - IFNULL(p.valor_recebido, 0)) > 0.01
        """, (data_iso,))
        
        eventos["vencimentos"] = cursor.fetchall()
        cursor.close()
        return eventos

    def get_total_projetos_ativos(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT COUNT(id) FROM agenda WHERE date(data_previsao_termino) >= date('now', 'localtime')")
            resultado = cursor.fetchone()
            cursor.close()
            return resultado[0] if resultado else 0
        except: 
            cursor.close()
            return 0

    def get_total_a_receber_30d(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT SUM(p.valor_parcela - IFNULL(p.valor_recebido, 0)) 
                FROM parcelas p
                WHERE p.num_parcela != 0
                AND (p.valor_parcela - IFNULL(p.valor_recebido, 0)) > 0.01
                AND date(p.data_vencimento) BETWEEN date('now', 'localtime') AND date('now', 'localtime', '+30 days')
            """)
            resultado = cursor.fetchone()
            cursor.close()
            return resultado[0] if resultado and resultado[0] else 0.0
        except: 
            cursor.close()
            return 0.0
            
    def get_total_a_receber_geral(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT SUM(p.valor_parcela - IFNULL(p.valor_recebido, 0)) 
                FROM parcelas p
                WHERE p.num_parcela != 0
                AND (p.valor_parcela - IFNULL(p.valor_recebido, 0)) > 0.01
            """)
            resultado = cursor.fetchone()
            cursor.close()
            return resultado[0] if resultado and resultado[0] else 0.0
        except: 
            cursor.close()
            return 0.0

    def get_todas_parcelas_pendentes_detalhadas(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.id, c.nome, a.descricao AS projeto_nome, 
                CASE p.num_parcela WHEN 0 THEN 'Entrada' ELSE 'Parcela ' || p.num_parcela END AS nome_parcela, 
                (p.valor_parcela - IFNULL(p.valor_recebido, 0)) AS valor_restante, 
                strftime('%d/%m/%Y', p.data_vencimento) AS data_vencimento
            FROM parcelas p
            JOIN recebimentos_pagamentos r ON p.recebimento_id = r.id
            LEFT JOIN clientes_app c ON r.cliente_id = c.id
            LEFT JOIN agenda a ON r.agenda_id = a.id
            WHERE p.num_parcela != 0 
            AND (p.valor_parcela - IFNULL(p.valor_recebido, 0)) > 0.01
            ORDER BY p.data_vencimento ASC LIMIT 500
        """)
        res = cursor.fetchall()
        cursor.close()
        return res
        
    def get_projetos_agenda_para_combobox(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT a.id, c.id AS id_cliente, c.nome, a.descricao FROM agenda a LEFT JOIN clientes_app c ON a.cliente_id = c.id ORDER BY a.id DESC LIMIT 100")
        res = cursor.fetchall()
        cursor.close()
        return res
    
    def get_orcamentos_antigos_para_combobox(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, cliente_nome, itens_json, observacoes FROM orcamentos ORDER BY id DESC LIMIT 50")
        res = cursor.fetchall()
        cursor.close()
        return res
    
    def get_todas_parcelas_pagas_detalhadas(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.id, c.nome, a.descricao AS projeto_nome, 
                CASE p.num_parcela WHEN 0 THEN 'Entrada' ELSE 'Parcela ' || p.num_parcela END AS nome_parcela, 
                p.valor_recebido AS valor_pago, strftime('%d/%m/%Y', p.data_recebimento) AS data_pagamento
            FROM parcelas p
            JOIN recebimentos_pagamentos r ON p.recebimento_id = r.id
            LEFT JOIN clientes_app c ON r.cliente_id = c.id
            LEFT JOIN agenda a ON r.agenda_id = a.id
            WHERE p.data_recebimento IS NOT NULL AND p.valor_recebido > 0 
            ORDER BY p.data_recebimento DESC LIMIT 500
        """)
        res = cursor.fetchall()
        cursor.close()
        return res
        
    def get_projetos_lancados_para_combobox(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT r.id, c.id AS cliente_id, c.nome, a.descricao AS projeto_nome
            FROM recebimentos_pagamentos r
            LEFT JOIN clientes_app c ON r.cliente_id = c.id
            LEFT JOIN agenda a ON r.agenda_id = a.id
            ORDER BY r.id DESC LIMIT 50
        """)
        res = cursor.fetchall()
        cursor.close()
        return res
        
    def get_detalhes_recebimento_para_comissao(self, recebimento_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT r.valor_total, r.tipo_pagamento, c.nome FROM recebimentos_pagamentos r LEFT JOIN clientes_app c ON r.cliente_id = c.id WHERE r.id = ?", (recebimento_id,))
        projeto_data = cursor.fetchone()
        if not projeto_data: 
            cursor.close()
            return None
        cursor.execute("SELECT SUM(valor) FROM comissoes WHERE recebimento_id = ?", (recebimento_id,))
        comissoes_data = cursor.fetchone()
        cursor.close()
        return {
            "cliente_nome": projeto_data["nome"],
            "valor_total": projeto_data["valor_total"],
            "tipo_pagamento": projeto_data["tipo_pagamento"],
            "total_comissoes": comissoes_data[0] if comissoes_data and comissoes_data[0] else 0.0
        }

    def add_arquiteto(self, nome, data_pagamento):
        try:
            nome = nome.strip()
            data_iso = datetime.strptime(data_pagamento, "%d/%m/%Y").strftime("%Y-%m-%d")
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO arquitetos (nome, data_pagamento) VALUES (?, ?)", (nome, data_iso))
            self.conn.commit()
            cursor.close()
            return True, "Arquiteto salvo."
        except: return False, "Erro ao salvar."

    def get_all_arquitetos_para_combobox(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nome FROM arquitetos ORDER BY nome ASC")
        res = [f"{id} - {nome}" for id, nome in cursor.fetchall()]
        cursor.close()
        return res

    def get_all_arquitetos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nome, strftime('%d/%m/%Y', data_pagamento) as data_pagamento_fmt FROM arquitetos ORDER BY nome ASC")
        res = cursor.fetchall()
        cursor.close()
        return res

    def delete_arquiteto(self, arquiteto_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM arquitetos WHERE id = ?", (arquiteto_id,))
            self.conn.commit()
            cursor.close()
        except: self.conn.rollback()
    
    def update_arquiteto(self, id_arq, nome, data_pagamento):
        try:
            data_iso = datetime.strptime(data_pagamento, "%d/%m/%Y").strftime("%Y-%m-%d")
            cursor = self.conn.cursor()
            cursor.execute("UPDATE arquitetos SET nome = ?, data_pagamento = ? WHERE id = ?", (nome, data_iso, id_arq))
            self.conn.commit()
            cursor.close()
            return True, "Atualizado."
        except: return False, "Erro."

    def get_parcela_by_id(self, parcela_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM parcelas WHERE id = ?", (parcela_id,))
            res = cursor.fetchone()
            cursor.close()
            return res
        except: return None

    def update_parcela_details(self, parcela_id, nova_data_venc, novo_valor, novo_valor_recebido=None):
        try:
            cursor = self.conn.cursor()
            try: data_iso = datetime.strptime(nova_data_venc, "%d/%m/%Y").strftime("%Y-%m-%d")
            except: data_iso = nova_data_venc 
            if novo_valor_recebido is not None:
                cursor.execute("UPDATE parcelas SET data_vencimento = ?, valor_parcela = ?, valor_recebido = ? WHERE id = ?", (data_iso, novo_valor, novo_valor_recebido, parcela_id))
            else:
                cursor.execute("UPDATE parcelas SET data_vencimento = ?, valor_parcela = ? WHERE id = ?", (data_iso, novo_valor, parcela_id))
            self.conn.commit()
            cursor.close()
            return True
        except: 
            self.conn.rollback()
            return False

    def get_total_recebido_geral(self):
        cursor = self.conn.cursor() 
        try:
            cursor.execute("SELECT SUM(valor_recebido) FROM parcelas WHERE data_recebimento IS NOT NULL AND valor_recebido > 0")
            resultado = cursor.fetchone()
            cursor.close()
            return resultado[0] if resultado and resultado[0] else 0.0
        except: 
            cursor.close()
            return 0.0

    def get_total_comissoes_ja_pagas(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT SUM(valor) FROM comissoes WHERE date(data) <= date('now', 'localtime')")
            resultado = cursor.fetchone()
            cursor.close()
            return resultado[0] if resultado and resultado[0] else 0.0
        except: 
            cursor.close()
            return 0.0

    def get_total_comissoes_pendentes(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT SUM(valor) FROM comissoes 
                WHERE date(data) > date('now', 'localtime')
            """)
            resultado = cursor.fetchone()
            cursor.close()
            return resultado[0] if resultado and resultado[0] else 0.0
        except: 
            cursor.close()
            return 0.0

    def get_valor_total_by_agenda_id(self, agenda_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT itens_json FROM orcamentos WHERE agenda_id = ? ORDER BY id DESC LIMIT 1", (agenda_id,))
            row = cursor.fetchone()
            cursor.close()
            if not row or not row["itens_json"]: return 0.0
            itens = json.loads(row["itens_json"])
            return sum(utils.string_para_float(item.get('valor_total', '0')) for item in itens)
        except: return 0.0

    def get_relatorio_completo(self, filtro_data_inicio=None, filtro_data_fim=None, 
                               filtro_cliente=None, filtro_arquiteto=None, 
                               filtro_projeto=None, filtro_material=None):
        cursor = self.conn.cursor()
        
        query = """
            SELECT a.id as agenda_id, a.descricao as nome_projeto, 
                   a.data_inicio, a.data_previsao_termino,
                   c.nome as nome_cliente, o.valor_total_final as valor_orcamento, o.itens_json,
                   r.id as recebimento_id, r.tipo_pagamento, r.num_parcelas, r.valor_total as valor_negociado
            FROM agenda a
            LEFT JOIN clientes_app c ON a.cliente_id = c.id
            LEFT JOIN orcamentos o ON o.agenda_id = a.id
            LEFT JOIN recebimentos_pagamentos r ON r.agenda_id = a.id
        """
        conditions = []
        params = []
        
        if filtro_data_inicio:
            conditions.append("date(a.data_previsao_termino) >= date(?)")
            params.append(filtro_data_inicio)
        if filtro_data_fim:
            conditions.append("date(a.data_previsao_termino) <= date(?)")
            params.append(filtro_data_fim)
        if filtro_cliente:
            conditions.append("c.nome LIKE ?")
            params.append(f"%{filtro_cliente}%")
        if filtro_projeto:
            conditions.append("a.descricao LIKE ?")
            params.append(f"%{filtro_projeto}%")
            
        if conditions: query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY a.data_previsao_termino DESC LIMIT 200"
        
        cursor.execute(query, params)
        projetos = cursor.fetchall()
        cursor.close() # Fecha o cursor principal para evitar locks durante o loop
        
        resultados = []
        
        # Cria um novo cursor para operações internas rápidas
        for p in projetos:
            # Reabre um cursor rápido apenas para esta iteração se necessário,
            # mas é melhor usar self.conn.execute direto para leituras rápidas
            recebimento_id = p["recebimento_id"]
            valor_projeto = utils.string_para_float(str(p["valor_negociado"])) if p["valor_negociado"] else (utils.string_para_float(str(p["valor_orcamento"])) if p["valor_orcamento"] else 0.0)
            
            total_recebido = 0.0
            if recebimento_id:
                # Usa context manager ou novo cursor rápido
                cur_temp = self.conn.cursor()
                cur_temp.execute("SELECT SUM(valor_recebido) FROM parcelas WHERE recebimento_id = ?", (recebimento_id,))
                res_parcelas = cur_temp.fetchone()
                total_recebido = res_parcelas[0] if res_parcelas and res_parcelas[0] else 0.0
                cur_temp.close()
            
            total_comissao = 0.0
            nome_beneficiario = ""
            if recebimento_id:
                cur_temp = self.conn.cursor()
                cur_temp.execute("SELECT SUM(valor), beneficiario FROM comissoes WHERE recebimento_id = ?", (recebimento_id,))
                res_comissao = cur_temp.fetchone()
                total_comissao = res_comissao[0] if res_comissao and res_comissao[0] else 0.0
                nome_beneficiario = res_comissao[1] or ""
                cur_temp.close()

            if filtro_arquiteto and (not nome_beneficiario or filtro_arquiteto.lower() not in nome_beneficiario.lower()): continue

            resultados.append({
                "data_inicio": p["data_inicio"],  
                "data": p["data_previsao_termino"],
                "cliente": p["nome_cliente"],
                "projeto": p["nome_projeto"],
                "tipo_pagamento": p["tipo_pagamento"] or "N/D",
                "num_parcelas": p["num_parcelas"] or 0,
                "arquiteto": nome_beneficiario,
                "total_projeto": valor_projeto,
                "total_comissao": total_comissao,
                "sobrou_liquido": valor_projeto - total_comissao,
                "valor_pago_cliente": total_recebido,
                "a_receber": valor_projeto - total_recebido
            })
        return resultados