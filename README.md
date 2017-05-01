# homeseek
parse social networks for flat renting ads in moscow
we use tornado, mongo, sklearn

честных парсеров сейчас три, оценку качества см. test_parsers.py
все три основаны на регулярках, оптимизированы по небольшой выборке из data/markup.json
логика удаления дублей в sources/dup_finder.py
логика фильтрации в load_posts.py
