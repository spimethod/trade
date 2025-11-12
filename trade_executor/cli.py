"""
CLI точка входа для Trade Executor.
"""

from .main import run_executor_loop


def main():
    """Запускает бесконечный цикл копирования сделок."""
    run_executor_loop()


if __name__ == "__main__":
    main()

