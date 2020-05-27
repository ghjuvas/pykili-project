from ufal.udpipe import Model, Pipeline # pylint: disable=no-name-in-module
import conllu
import json
import collections

see_list_of_pairs = '''Вы хотите увидеть список? Введите 'да' или 'нет'.\nОтвет: '''
save_list_of_pairs = '''Вы хотите отдельно сохранить список соответствий? Введите 'да' или 'нет'.\nОтвет: '''
write_corpora = '''Для записи корпуса вы хотите создать новый файл или работать с уже существующим? Введите '1' или '2' соответственно.\nОтвет: '''
users_corpora_or_made = '''Программа осуществит поиск словоформы. Вы хотите загрузить свой корпус или продолжить работу с только что созданным? Введите '1' или '2' соответственно.\nОтвет: '''
users_corpora_filename = '''Выберите файл, в котором хранится ваш корпус. Например, corpora.json (обязательно сохраняя указанное расширение).\nУбедитесь, что в нём есть необходимые данные:\n'full text' - тексты на двух языках с метаинформацией,\n'sentences' - тексты, токенизированные по предложениям,\n'tokens' - предложения токенизированные по словам,\n'results_same_words' - соответствия слов.\nИмя файла: '''
language_of_search = '''На каком языке вы собираетесь вводить словоформу? Введите 'английский' или 'французский'.\nЯзык: '''
make_corpora_or_search_or_exit = '''Введите '1', чтобы создать корпус\nВведите '2', чтобы искать по уже созданному корпусу\nВведите '3', чтобы программа закончила работу\nВаш ответ: '''
main_menu_or_exit = '''Вы хотите перейти в главное меню или выйти из программы? Введите '1' или '2' соответственно\nВаш ответ: '''
search_or_menu_or_exit = '''Вы хотите начать поиск по созданному корпусу, перейти в главное меню или выйти из программы?\nВведите '1', '2' или '3' соответственно\nВаш ответ: '''

def read_file(): 
    filename_or_path = input('Введите имя файла или путь к нему: ')
    with open(filename_or_path, "r", encoding='utf-8') as users_text:
        users_text = users_text.read()
        parts_of_users_text = users_text.split('\n\n\n')
        dict_texts_with_info = dict()
        info_about_texts = parts_of_users_text[0]
        eng_text = parts_of_users_text[1]
        fr_text = parts_of_users_text[2]
        dict_texts_with_info['full_text'] = [info_about_texts, eng_text, fr_text]       
        # print(dict_texts_with_info)
        return dict_texts_with_info 

def tokenize_and_tag_texts(dict_texts): 
    eng_model = Model.load('english-partut-ud-2.5-191206.udpipe')
    fr_model = Model.load('french-partut-ud-2.5-191206.udpipe')
    eng_pipeline = Pipeline(eng_model, 'generic_tokenizer', '', '', '')
    fr_pipeline = Pipeline(fr_model, 'generic_tokenizer', '', '', '')
    for language_key, primal_texts in dict_texts.items():
        tokenized_tagged_eng_text = eng_pipeline.process(primal_texts[1])
        tokenized_tagged_fr_text = fr_pipeline.process(primal_texts[2])
    dict_tokenized_tagged_texts = {'eng': tokenized_tagged_eng_text,
                'fr': tokenized_tagged_fr_text}
    # print(tokenized_tagged_eng_text)
    # print(tokenized_tagged_fr_text)
    # print(dict_tokenized_tagged_texts)
    return dict_tokenized_tagged_texts 

def extract_sentences_from_conllu_outputs(dict_ud): 
    dict_sents = collections.defaultdict(list) 
    pattern_text = '# text = '
    for dict_ud_language_key, dict_ud_texts in dict_ud.items():
        for ud_str in dict_ud_texts.splitlines(): 
            if ud_str.startswith(pattern_text):
                sent = ud_str.replace(pattern_text, '')
                dict_sents[dict_ud_language_key].append(sent)
    # print(dict_sents)
    return dict_sents 

def parse_conllu(tokenized_tagged_text): 
    not_conllu_ud = conllu.parse(tokenized_tagged_text)
    list_tokens_with_tags = list()
    for token_list in not_conllu_ud:
        list_sent = list()
        for tokens in token_list:
            list_sent.append(tokens)
        list_tokens_with_tags.append(list_sent)
    return list_tokens_with_tags 

def text_tokenization(dict_tokenized_tagged): 
    dict_tokens = collections.defaultdict(list) 
    for dict_language_key, dict_tagged_texts in dict_tokenized_tagged.items():
        for list_sent in dict_tagged_texts:
            forms_list = list()
            for ordered_dict in list_sent:
                form = ordered_dict['form']
                forms_list.append(form)
            dict_tokens[dict_language_key].append(forms_list)
    # print(dict_tokens)
    return dict_tokens 

def build_accordance(dict_feat): 
    words_alignment = list() 
    list_of_sents_eng = dict_feat['eng']
    # print(list_of_sents_eng)
    list_of_sents_fr = dict_feat['fr']
    for id_list_eng, list_ord_dict_eng in enumerate(list_of_sents_eng):
        for id_list_fr, list_ord_dict_fr in enumerate(list_of_sents_fr):
            if id_list_eng == id_list_fr: 
                accordance = match_words(list_ord_dict_eng, list_ord_dict_fr) 
                words_alignment.append(accordance)
    # print(words_alignment)
    return words_alignment 

def match_words(list_dicts_forms_tags_eng, list_dicts_forms_tags_fr): 
    accordance_sent = list()
    for ord_dict_eng in list_dicts_forms_tags_eng:
        for ord_dict_fr in list_dicts_forms_tags_fr:
            equal_words = list()
            if ord_dict_eng['upostag'] == ord_dict_fr['upostag'] and ord_dict_eng['feats'] == ord_dict_fr['feats']:
                if ord_dict_eng['upostag'] == 'PUNCT' and ord_dict_eng['form'] == ord_dict_fr['form']:
                    equal_words.append(ord_dict_eng['form'])
                    equal_words.append(ord_dict_fr['form'])
                    accordance_sent.append(equal_words)
                if ord_dict_eng['upostag'] != 'PUNCT':
                    equal_words.append(ord_dict_eng['form'])
                    equal_words.append(ord_dict_fr['form'])
                    accordance_sent.append(equal_words)
    return accordance_sent 

def matching_words_results(words_alignment): 
    matching_words_list = list() 
    counter = 0
    for units in words_alignment:
        for pair_of_same_words in units: 
            if pair_of_same_words not in matching_words_list:
                matching_words_list.append(pair_of_same_words)
                counter += 1
    print('Выявлено', counter, 'соответствий по словоформам.')
    answer_about_list = input(see_list_of_pairs)
    while answer_about_list != 'да' and answer_about_list != 'нет':
        answer_about_list = input(see_list_of_pairs)
    if answer_about_list == 'нет':
        pass
    if answer_about_list == 'да':
        print('Список соответствий:')
        for number, pair in enumerate(matching_words_list):
            number = number + 1
            print(number, ' ', pair)
    return matching_words_list

def separately_write_equal_list(matching_words_list): 
    same_words = collections.defaultdict(list)
    same_words['same_words'] = matching_words_list
    answer_about_saving = input(save_list_of_pairs)
    while answer_about_saving != 'да' and answer_about_saving != 'нет':
        answer_about_saving = input(save_list_of_pairs)
    if answer_about_saving == 'нет':
        pass
    if answer_about_saving == 'да':
        matching_words_list_filename = input('Выберите имя файла для записи соответствий. Например, results.json (обязательно сохраняя указанное расширение).\nИмя файла: ') 
        with open(matching_words_list_filename, 'w', encoding='utf-8') as f:
            json.dump(same_words, f, sort_keys=True, indent=3)
        print('Список соответствий сохранен.')
        return matching_words_list_filename 

def make_corpora(dict_texts_with_info, dict_sent, dict_tokens, matching_words_list):
    all_information = dict()
    corpora = dict()
    corpora['sentences'] = dict_sent
    corpora['tokens'] = dict_tokens
    corpora['results_same_words'] = matching_words_list
    for dict_texts_with_info_key, dict_texts_with_info_value in dict_texts_with_info.items():
        corpora['full_text'] = dict_texts_with_info_value
    all_information[dict_texts_with_info_value[0]] = corpora
    answer_about_saving_corpora = input(write_corpora)
    
    while answer_about_saving_corpora != '1' and answer_about_saving_corpora != '2':
        answer_about_saving_corpora = input(write_corpora)

    if answer_about_saving_corpora == '1': 
        corpora = all_information
        corpora_list = [corpora]
        results_filename = input('Выберите имя для создания нового файла. Например, new_corpora.json (обязательно сохраняя указанное расширение).\nИмя файла: ')
        with open(results_filename, 'w', encoding='utf-8') as f:
            json.dump(corpora_list, f)
        print('Корпус создан.')
        return corpora_list
    
    if answer_about_saving_corpora == '2': 
        user_corpora_filename = input('Введите имя файла, в котором хранится ваш корпус. Например, corpora.json (обязательно сохраняя указанное расширение).\nИмя файла: ')
        with open(user_corpora_filename, 'r', encoding='utf-8') as readtext:
            corpora = json.load(readtext)
            corpora.append(all_information)
        user_corpora_new_filename = input('Введите имя файла, куда бы вы хотели сохранить дополненный корпус. Например, updated_corpora.json (обязательно сохраняя указанное расширение).\nИмя файла: ')
        with open(user_corpora_new_filename, 'w' , encoding='utf-8') as text:
            json.dump(corpora, text)
        print('Корпус дополнен.')
        return corpora

def read_corpora_file(corpora):
    answer_about_reading_corpora = input(users_corpora_or_made)
    while answer_about_reading_corpora != '1' and answer_about_reading_corpora != '2':
        answer_about_reading_corpora = input(users_corpora_or_made)
    if answer_about_reading_corpora == '1':
        reading_filename = input(users_corpora_filename)
        with open(reading_filename, 'r', encoding='utf-8') as readtext:
            corpora = json.load(readtext)
            # print(read_corpora)
        return corpora
    if answer_about_reading_corpora == '2':
        return corpora

def read_users_corpora_file():
    filename = input(users_corpora_filename)
    with open(filename, 'r', encoding='utf-8') as readtext:
        corpora = json.load(readtext)
        # print(read_corpora)
    return corpora

def search_for_word_form(corpora):
    list_for_saving_sentences = []
    list_for_saving_pairs = []
    list_of_saving_sentences_in_required_language_for_making_pairs = []
    list_of_saving_sentences_in_another_language_for_making_pairs = []    
    test = []
    information_about_language = input('''На каком языке вы собираетесь вводить словоформу? Введите 'английский' или 'французский'.\nЯзык: ''')
    while information_about_language != 'английский' and information_about_language != 'французский':
        information_about_language = input('''На каком языке вы собираетесь вводить словоформу? Введите 'английский' или 'французский'.\nЯзык: ''')
    sought_word_form = input('Введите искомую словоформу: ')
    for part_of_list_corpora in corpora:
        for part_of_list_corpora_key, part_of_list_corpora_value in part_of_list_corpora.items():
            pairs_for_result = part_of_list_corpora_value['results_same_words']
            full_text = part_of_list_corpora_value['full_text']
            sentences = part_of_list_corpora_value['sentences']
    eng_sentences = sentences['eng']
    fr_sentences = sentences['fr']
    counter = 0
    if information_about_language == 'английский':
        sentences_in_required_language = eng_sentences
        sentences_in_another_language = fr_sentences
    if information_about_language == 'французский':
        sentences_in_required_language = fr_sentences
        sentences_in_another_language = eng_sentences
    for sentence in sentences_in_required_language:
        if sought_word_form in sentence:
            counter =+ 1
            list_for_saving_sentences.append(sentence)
    if counter == 0:
        print('Ничего не найдено.')
    if counter != 0:
        for number_sent, sent in enumerate(sentences_in_required_language):
            for number_another_sent, another_sent in enumerate(sentences_in_another_language):
                if sent in list_for_saving_sentences and number_sent == number_another_sent:
                    list_of_saving_sentences_in_required_language_for_making_pairs.append(sent)
                    list_of_saving_sentences_in_another_language_for_making_pairs.append(another_sent)
                    test.append(sent)
                    test.append(another_sent)
        if information_about_language == 'английский':
            required_text = full_text[1]
            another_text = full_text[2]
        if information_about_language == 'французский':
            required_text = full_text[2]
            another_text = full_text[1]
        for part in list_for_saving_sentences:
            if part in required_text:
                metainformation_about_text = full_text[0]
        for pair in pairs_for_result:
            if sought_word_form in pair:
                list_for_saving_pairs.append(pair) 
        eng = test[0::2]
        fr = test[1::2]
        print('Найденные соответствия: ', list_for_saving_pairs, '\n')
        for number_of_sentences in range(len(eng)):
            print('Метаинформация текста: ', metainformation_about_text)
            print('Контекст, в котором встречается искомая словоформа:')
            print('', eng[number_of_sentences], '\n', fr[number_of_sentences], '\n')
    return 42

print('Приветствуем вас в нашей консольной программе!')
print('Она умеет создавать параллельные корпуса на основе текстов на английском и французском языках и осуществлять поиск по словоформе.')
print('Вам будет предложено на выбор 3 функции.')

def users_start_answer():
    users_start_answer = input(make_corpora_or_search_or_exit)
    while users_start_answer != '1' and users_start_answer != '2' and users_start_answer != '3':
        users_start_answer = input(make_corpora_or_search_or_exit)
    return users_start_answer

users_start_answer_result = users_start_answer()

while users_start_answer_result == '1':

    print('Программа произведет поиск соответствий в выбранном текстовом файле и создаст корпус. Для того, чтобы программа прочитала ваш файл, требуется его особое оформление: метаинформация, две пустые строки, первый текст (на английском), две пустые строки, второй текст (на французском).')

    read_file_result = read_file()
    tokenize_and_tag_texts_result = tokenize_and_tag_texts(read_file_result)
    extract_sentences_from_conllu_outputs_result = extract_sentences_from_conllu_outputs(tokenize_and_tag_texts_result)
    parse_conllu_eng = parse_conllu(tokenize_and_tag_texts_result['eng'])
    parse_conllu_fr = parse_conllu(tokenize_and_tag_texts_result['fr'])
    parse_conllu_full_dict = {'eng': parse_conllu_eng, 'fr': parse_conllu_fr}
    # print(parse_conllu_full_dict)
    text_tokenization_result = text_tokenization(parse_conllu_full_dict)
    build_accordance_result = build_accordance(parse_conllu_full_dict)
    matching_words_results_result = matching_words_results(build_accordance_result)
    separately_write_equal_list_result = separately_write_equal_list(matching_words_results_result)
    make_corpora_result = make_corpora(read_file_result, extract_sentences_from_conllu_outputs_result, text_tokenization_result, matching_words_results_result)
    users_search_answer = input(search_or_menu_or_exit)
    while users_search_answer != '1' and users_search_answer != '2' and users_search_answer != '3':
        users_search_answer = input(search_or_menu_or_exit)
    if users_search_answer == '1':
        read_corpora_file_result = read_corpora_file(make_corpora_result)
        search_for_word_form_result = search_for_word_form(make_corpora_result)
        users_action_answer = input(main_menu_or_exit)
        while users_action_answer != '1' and users_action_answer != '2':
            users_action_answer = input(main_menu_or_exit)
        if users_action_answer == '1':
            users_start_answer()
        if users_action_answer == '2':
            print('Конец работы.')
    if users_search_answer == '2':
        users_start_answer()
    if users_search_answer == '3':
        print('Конец работы.')

while users_start_answer_result == '2':
    read_users_corpora_file_result = read_users_corpora_file()
    search_for_word_form_result = search_for_word_form(read_users_corpora_file_result)
    users_action_answer = input(main_menu_or_exit)
    while users_action_answer != '1' and users_action_answer != '2':
        users_action_answer = input(main_menu_or_exit)
    if users_action_answer == '1':
        users_start_answer()
    if users_action_answer == '2':
        print('Конец работы.')

if users_start_answer_result == '3':
    print('Конец работы.')