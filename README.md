# homeseek
http://homeseek.ru -- небольшой парсер соцсетей, ищем объявления аренды жилья в москве

## парсеры
* метро -- sources/subway_parser.py
* цены -- sources/price_parser.py
* пост про сдачу, а не съем/оффтоп -- sources/rent_parser.py

замер качества на data/markup.json -- см. test_parsers.py
все основаны на регулярках

## фильтрация
* логика удаления дублей -- sources/dup_finder.py
* логика фильтрации -- load_posts.py
