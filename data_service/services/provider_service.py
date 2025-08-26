from datetime import datetime
from db.postgres_db import PostgresDB

class ProviderService:
    def __init__(self):
        self.db = PostgresDB()
        self._create_table()

    def _create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS provider (
            id SERIAL PRIMARY KEY,
            network_ip VARCHAR(45) NOT NULL,
            user_id VARCHAR(255) NOT NULL,
            last_connection_time TIMESTAMP NOT NULL,
            public_key TEXT NOT NULL,
            credits INTEGER NOT NULL DEFAULT 0
        );
        """
        self.db.execute(query)

    def _get_next_available_ip(self) -> str:
        query = """
        SELECT network_ip 
        FROM provider 
        ORDER BY network_ip DESC 
        LIMIT 1;
        """
        result = self.db.execute(query)
        if not result:
            return "10.10.0.2"
        
        last_ip = result[0][0]
        last_octet = int(last_ip.split('.')[-1])
        return f"10.10.0.{last_octet + 1}"

    def create_provider_with_ip(self, user_id: str, public_key: str) -> str:
        client_ip = self._get_next_available_ip()
        query = """
        INSERT INTO provider (network_ip, user_id, last_connection_time, public_key, credits)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
        """
        self.db.execute(query, (client_ip, user_id, datetime.now(), public_key, 0))
        return client_ip

    def update_last_connection(self, provider_id: int):
        query = """
        UPDATE provider
        SET last_connection_time = %s
        WHERE id = %s;
        """
        self.db.execute(query, (datetime.now(), provider_id))

    def get_provider(self, user_id: str):
        query = """
        SELECT id, network_ip, user_id, last_connection_time, public_key, credits
        FROM provider
        WHERE user_id = %s;
        """
        result = self.db.execute(query, (user_id,))
        if not result:
            return None
        columns = ["id", "network_ip", "user_id", "last_connection_time", "public_key", "credits"]
        provider_row = result[0]
        return dict(zip(columns, provider_row))

    def get_all_providers(self):
        query = """
        SELECT id, network_ip, user_id, last_connection_time, public_key, credits
        FROM provider;
        """
        result = self.db.execute(query)
        columns = ["id", "network_ip", "user_id", "last_connection_time", "public_key", "credits"]
        return [dict(zip(columns, row)) for row in result]

    def add_credits_by_ip(self, network_ips, amount: int):
        if not network_ips:
            return []
        if isinstance(network_ips, str):
            network_ips = [network_ips]

        placeholders = ",".join(["%s"] * len(network_ips))
        update_query = f"""
        UPDATE provider
        SET credits = credits + %s
        WHERE network_ip IN ({placeholders});
        """
        params = tuple([amount] + list(network_ips))
        self.db.execute(update_query, params)

        select_query = f"""
        SELECT network_ip, credits FROM provider WHERE network_ip IN ({placeholders});
        """
        result = self.db.execute(select_query, tuple(network_ips))
        return [{"network_ip": row[0], "credits": row[1]} for row in result]

    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()