"""Константы приложения recipes"""

# РЕЦЕПТЫ.
# Максимальная длинна названия рецепта.
RECIPE_NAME_MAX_LENGTH: int = 256

# Минимальная и максимальная соответственно длинна поля cooking_time.
COOKING_TIME_MIN_LENGTH: int = 1
COOKING_TIME_MAX_LENGTH: int = 32767


# ИНГРЕДИЕНТЫ.
# Максимальная длинна название ингредиента.
INGREDIENT_MAX_LENGTH: int = 128

# Максимальная длинна единицы измерения.
MEASUREMENT_UNIT_MAX_LENGTH: int = 64

# Минимальная и максимальная соответственно длинна поля amount.
AMOUNT_MIN_LENGTH: int = 1
AMOUNT_MAX_LENGTH: int = 32767


# ТЕГИ.
# Максимальная длинна тега.
TAG_MAX_LENGTH: int = 32


# ПРОЧИЕ.
# ID админа.
ADMIN_ID: int = 1

# Объектов на страницу.
PAGINATION_PAGE_SIZE: int = 6

# Длинна кода для короткой ссылки.
SHORT_CODE_LENGTH: int = 8

# Длинна текста описания в админке.
SHORT_TEXT_IN_ADMIN_LENGTH: int = 50

# Максимальное количество попыток сохранить короткий код при ошибке.
MAXIMUM_NUMBER_ATTEMPTS: int = 10
