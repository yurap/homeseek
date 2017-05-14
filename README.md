# homeseek
http://homeseek.ru -- небольшой парсер соцсетей, ищем объявления аренды жилья в москве

## парсеры
* метро -- sources/subway_parser.py
* цены -- sources/price_parser.py
* пост про сдачу, а не съем/оффтоп -- sources/rent_parser.py
* замер качества на data/markup.json -- см. test_parsers.py (у всех примерно f1 = 0.90)

## фильтрация
* логика удаления дублей -- sources/dup_finder.py
* логика фильтрации -- load_posts.py

## схема московского метро
* sources/subway_lines.py

## useful commands
sudo systemctl restart homeseek
sudo systemctl restart homeseek_load
