import logging
import sys
from pathlib import Path

# Создаем директорию для логов, если она не существует
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Настройка базового логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def get_logger(name: str) -> logging.Logger:
    """
    Получить логгер с указанным именем
    """
    return logging.getLogger(name) 
