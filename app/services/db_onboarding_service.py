from typing import List

class DBOnboardingService:
    @classmethod
    def generate_readonly_script(
        cls, 
        db_type: str, 
        db_name: str, 
        ro_username: str, 
        ro_password: str, 
        sync_all_tables: bool, 
        allowed_tables: List[str]
    ) -> str:
        """
        Generates a copy-paste SQL script for the client to create a read-only user.
        """
        db_type = db_type.lower()
        
        if db_type == "postgresql":
            script = (
                f"-- 1. Create the user\n"
                f"CREATE ROLE {ro_username} WITH LOGIN PASSWORD '{ro_password}';\n\n"
                f"-- 2. Grant connection and schema access\n"
                f"GRANT CONNECT ON DATABASE {db_name} TO {ro_username};\n"
                f"GRANT USAGE ON SCHEMA public TO {ro_username};\n\n"
            )
            
            if sync_all_tables:
                script += (
                    f"-- 3. Grant SELECT on ALL current and future tables\n"
                    f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {ro_username};\n"
                    f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO {ro_username};\n"
                )
            else:
                script += f"-- 3. Grant SELECT strictly on specific tables\n"
                for table in allowed_tables:
                    script += f"GRANT SELECT ON TABLE {table} TO {ro_username};\n"
                    
            return script

        elif db_type == "mysql":
            script = (
                f"-- 1. Create the user\n"
                f"CREATE USER '{ro_username}'@'%' IDENTIFIED BY '{ro_password}';\n\n"
            )
            
            if sync_all_tables:
                script += (
                    f"-- 2. Grant SELECT on ALL tables in the database\n"
                    f"GRANT SELECT ON {db_name}.* TO '{ro_username}'@'%';\n"
                )
            else:
                script += f"-- 2. Grant SELECT strictly on specific tables\n"
                for table in allowed_tables:
                    script += f"GRANT SELECT ON {db_name}.{table} TO '{ro_username}'@'%';\n"
                    
            script += "\nFLUSH PRIVILEGES;\n"
            return script
            
        else:
            return "-- Unsupported database type for automatic script generation."