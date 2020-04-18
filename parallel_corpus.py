from ufal.udpipe import Model, Pipeline # pylint: disable=no-name-in-module
import nltk
import conllu
import json

print('Для того, чтобы программа прочитала Ваш файл, требуется его особое оформление: метаинформация, две пустые строки, первый текст (на английском), две пустые строки, второй текст (на французском).')

def filename_path():
    flnm_or_path = input('Введите имя файла или путь к нему: ')
    return flnm_or_path

filename_path_function = filename_path()

def reading(filename):
    with open(filename, "r", encoding='utf-8') as text:
        text = text.read()
        parts = text.split('\n\n\n')
        dict_all = dict()
        inf = parts[0]
        eng = parts[1]
        fr = parts[2]
        dict_all[inf] = [eng, fr]
        # print(dict_all)
        return dict_all #, inf, eng, fr

reading_function = reading(filename_path_function)

def tokenize_texts_to_sent(dict_text_all):
    dict_sent = dict()
    for dict_all_texts_key, dict_all_texts in dict_text_all.items():
        for text_all_id, texts_all in enumerate(dict_all_texts):
            tok_eng_sent = nltk.sent_tokenize(dict_all_texts[0])
            tok_fr_sent = nltk.sent_tokenize(dict_all_texts[1])
    dict_sent['eng'] = tok_eng_sent
    dict_sent['fr'] = tok_fr_sent
    # print(dict_sent)
    return dict_sent

tokenize_texts_to_sent_function = tokenize_texts_to_sent(reading_function)

def tokenize_sent_to_words(dict_sents):
    dict_words = dict()
    eng_list = list()
    fr_list = list()
    for eng_sents in dict_sents['eng']:
        # print(eng_sents)
        tok_eng_words = nltk.word_tokenize(eng_sents)
        eng_list.append(tok_eng_words)
        # print(eng_list)
    for fr_sents in dict_sents['fr']:
        tok_fr_words = nltk.word_tokenize(fr_sents)
        fr_list.append(tok_fr_words)
    dict_words['eng'] = eng_list
    dict_words['fr'] = fr_list
    # print(dict_words)
    return dict_words

tokenize_sent_to_words_function = tokenize_sent_to_words(tokenize_texts_to_sent_function)

def tok_and_morph(dict_text):
    dict_tok = dict()
    eng_model = Model.load('english-partut-ud-2.5-191206.udpipe')
    fr_model = Model.load('french-partut-ud-2.5-191206.udpipe')
    eng_pipeline = Pipeline(eng_model, 'generic_tokenizer', '', '', '')
    fr_pipeline = Pipeline(fr_model, 'generic_tokenizer', '', '', '')
    for dict_texts_key, dict_texts in dict_text.items():
        for text_id, texts in enumerate(dict_texts):
            tok_and_morph_eng = eng_pipeline.process(dict_texts[0])
            tok_and_morph_fr = fr_pipeline.process(dict_texts[1])
    dict_tok[dict_texts_key] = [tok_and_morph_eng, tok_and_morph_fr]
    # print(tok_and_morph_eng)
    # print(tok_and_morph_fr)
    return dict_tok

tok_and_morph_function = tok_and_morph(reading_function)

def parcing_conllu(dict_tokens):
    for dict_tok_key, dict_tok_val in dict_tokens.items():
        for text_tok_id, text_tok in enumerate(dict_tok_val):
            not_conllu_tok_eng = conllu.parse(dict_tok_val[0])
            not_conllu_tok_fr = conllu.parse(dict_tok_val[1])
    # print(not_conllu_tok_eng)
    dict_tokens_morph = dict()
    list_tokens_eng = list()
    list_tokens_fr = list()
    for token_list_eng in not_conllu_tok_eng:
        for tokens_eng in token_list_eng:
            list_tokens_eng.append(tokens_eng)
    for token_list_fr in not_conllu_tok_fr:
        for tokens_fr in token_list_fr:
            list_tokens_fr.append(tokens_fr)
    # print(list_tokens_eng)
    # print(list_tokens_fr)
    dict_tokens_morph['eng'] = list_tokens_eng
    dict_tokens_morph['fr'] = list_tokens_fr
    # print(dict_tokens_morph)
    return dict_tokens_morph

parcing_conllu_function = parcing_conllu(tok_and_morph_function)

def writing(dict_sent):
    results_name = input('Выберите имя файла для записи результатов. Например, results.json (обязательно сохраняя указанное расширение).\nИмя файла: ')
    data = dict()
    data['sentences'] = dict_sent
    with open(results_name, 'w', encoding='utf-8') as f:
        json.dump(data, f)
    return results_name

writing_function = writing(tokenize_texts_to_sent_function)

def reading_written(results_name):
    with open(results_name) as rw:
        res = json.load(rw)
        #print (res)
        return res

reading_written_function = reading_written(writing_function)
