Разработка
==========

Подготовка окружения
--------------------

Создать и активировать виртуальное окружение:

.. code-block:: bash

   python -m venv .venv
   source .venv/bin/activate

Установить проект с зависимостями для разработки:

.. code-block:: bash

   python -m pip install -e ".[dev]"

Тесты
-----

Запуск тестов:

.. code-block:: bash

   python -m pytest

Проверка покрытия:

.. code-block:: bash

   python -m doit coverage

Минимальное требуемое покрытие — 75%.

Проверка стиля
--------------

Проверка кода через Ruff:

.. code-block:: bash

   python -m doit lint

Автоматическое исправление части ошибок:

.. code-block:: bash

   python -m ruff check --fix src tests scripts

Сборка пакетов
--------------

Сборка wheel:

.. code-block:: bash

   python -m doit wheel

Сборка sdist:

.. code-block:: bash

   python -m doit sdist

Сборка обоих архивов:

.. code-block:: bash

   python -m doit build

Сборка документации
-------------------

Документация собирается командой:

.. code-block:: bash

   python -m doit docs

HTML-файлы появляются в каталоге ``docs/_build/html``.
