'''
configurações do banco de dados
'''

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict( # carrega as variaveis de config
        env_file='.env', env_file_encoding='utf-8'
    )

    DATABASE_URL: str # essa var será preenchida com o valor encontrado com o mesmo nome no .env