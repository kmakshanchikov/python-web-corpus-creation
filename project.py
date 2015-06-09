# -*- coding: utf-8 -*-				# подключение русского языка
# подключение библиотек и модулей	#!!! - надо доделать
import os							# для проверки существования директории
import errno						# для проверки существования директории
from Tkinter import *				# для графической оболочки программы
import sys							# для установки используемой кодировки
from search import YaSearch			# для поиска словосочетаний (сс) в интернете
import string						# для использования строк в программе
import nltk							# для подсчета статистики
import pymorphy2 					# для проведения морфологического анализа
import urllib2						# для перехода по гиперссылкам
from main import TomitaParser		# для выделения сс из текстов

API_USER = ''			# установка учетных данных для Yandex.XML 
API_KEY = ''

morph = pymorphy2.MorphAnalyzer() 	# подключение морфологического анализатора
jacc = .6							# величина коэффициента Жаккара

def ensureDir(filename): 			# проверка на существование расположения файла
    dir = os.path.dirname(filename)	# на вход поступает файл, определяется его директория
    if not os.path.exists(dir):		# если директория не существует
        os.makedirs(dir)			# то она создается

def make_sure_path_exists(path): 	# функция проверки существования директории
	try:
		os.makedirs(path)
	except OSError as exception:
		if exception.errno != errno.EEXIST:
			raise

def main(outdir):							# функция итеративного запуска процедуры сборки веб-корпуса
	print u'Старт работы программы, подключение лога программы\n'
	flog = open(outdir+'/log.txt','w')		# подключение лога программы
	flog.write('Старт работы программы'+'\n\n')
	print u'Директория:',outdir
	flog.write('Директория: '+outdir+'\n')
	print u'Количество десятков сохраняемых веб-страниц по каждому поисковому запросу: ',entry1.get()
	flog.write('Количество десятков сохраняемых веб-страниц по каждому поисковому запросу: '+entry1.get()+'\n')
	print u'Количество итераций: ',entry2.get()
	flog.write('Количество итераций: '+entry2.get()+'\n')
	if var.get() == 1:
		print u'Новые словосочетания извлекаются из СНИППЕТОВ'
		flog.write('Новые словосочетания извлекаются из СНИППЕТОВ\n')
	else:
		print u'Новые словосочетания извлекаются из ТЕКСТОВ'
		flog.write('Новые словосочетания извлекаются из ТЕКСТОВ\n')
	print u'Величина коэффициента Жаккара:',jacc
	flog.write('Величина коэффициента Жаккара: '+str(jacc)+'\n')
	print u'Начальный список словосочетаний:\n',textbox.get('1.0', 'end')
	flog.write('Начальный список словосочетаний:'+'\n'+textbox.get('1.0', 'end').encode('utf-8')+'\n')
	word_list =[]					# список сс для поиска
	word_list_used = []				# список использованных сс
	fwl = open(outdir+'/in.txt','r')		# открытие файла с начальным списком сс
	s = fwl.read().decode('utf-8')	# считывание начального списка сс
	i=0;
	j=0;
	while(i < s.__len__()- 1):
		if (s[i]>=u'а' and s[i]<=u'я' or s[i]>=u'А' and s[i]<=u'Я'):
			n = u''
			k=0;
			while (s[i]!=','): 		# строчка с сс должна заканчиваться ","
				n = n+s[i]			# иначе программа попадает в бесконечный цикл
				if (i < s.__len__()- 1): i=i+1
				else: return 0
			word_list.append(n)
		else: i=i+1;
	fwl.close()						# закрытие файла с начальным списком сс
	numiteration = entry2.get()		# количество итераций в текстовом формате
	numiteration = int(numiteration)# перевод текстового формата в числовой
	n = entry1.get()				
	# количество десятков сохраняемых веб-страниц по каждому поисковому запросу в текстовом формате
	n = int(n)
	# количество десятков сохраняемых веб-страниц по каждому поисковому запросу в числовом формате
	w = 0							# счетчик использованных слов
	count = 0						# счетчик посещенных веб-страниц
	for iteration in range (1, numiteration):		# запуск цикла по итерациям
		make_sure_path_exists(outdir+'/i'+str(iteration))		# создание директорий для данных
		make_sure_path_exists(outdir+'/i'+str(iteration)+'/coll')
		make_sure_path_exists(outdir+'/i'+str(iteration)+'/snip')
		make_sure_path_exists(outdir+'/i'+str(iteration)+'/stat')
		make_sure_path_exists(outdir+'/i'+str(iteration)+'/text')
		make_sure_path_exists(outdir+'/i'+str(iteration)+'/urls')	
		print u'Итерация №',str(iteration)
		flog.write('Итерация №'+str(iteration)+'\n')
		snippets = []				# список сниппетов
		n_o_w = 0					# счетчик сс текущей итерации
		c = [0]						# счетчик сайтов текущей итерации
		for word in word_list:		# запуск цикла по списку сс
			n_o_w += 1
			urls = []				# список гиперссылок
			search(outdir, word, urls, snippets, flog, n_o_w, iteration, n)
			cc = crawler(outdir, urls, iteration, flog, n_o_w)
			c[0] += cc
			c.append(cc)		# cc - число сайтов текущего сс
			cleaner(outdir, cc, iteration, flog, n_o_w)
			word_list_used.append(word)
		print u'  Список использованных словосочетаний'
		flog.write('  Список использованных словосочетаний'+'\n')
		for i in range (w, w + n_o_w):	# вывод списка использованных сс
			print '  >',word_list_used[i]
			flog.write('  >'+word_list_used[i]+'\n')
		w += n_o_w
		count += c[0]
		word_list = []				# очистка списка сс для поиска
		#duplicates(outdir, iteration, c, flog, n_o_w)
		finder(outdir, word_list, word_list_used, flog, iteration, n_o_w, c)
		#statistics(outdir, iteration, flog, c[0], n_o_w) 	# подсчет статистики по итерации
		fstat = open(outdir+'/i'+str(iteration)+'/stat/statistics.txt','w')# задание параметров для подсчета статистики
		fstat.write(outdir+'\n'+str(iteration)+'\n'+str(c[0])+'\n'+str(n_o_w)+'\n')
		fstat.close()
		if len(word_list) == 0:	break
	fnew = open(outdir+'/i'+str(iteration)+'/new.txt','w')	# файл веб-корпуса (пустой)
	for i in range(1,iteration):
		ftext = open(outdir+'/i'+str(iteration)+'/part'+str(iteration)+'.txt','r')# тексты текущей итерации
		fnew.write(ftext.read())
		ftext.close()
	fnew.close()
	print u'   Финальная статистика: '
	flog.write('   Финальная статистика: \n')
	print u'	Посещено сайтов: ', count
	flog.write('	Посещено сайтов: '+str(count)+'\n')
	print u'	Использовано словосочетаний: ',w
	flog.write('	Использовано словосочетаний: '+str(w)+'\n')
	print u'  	Список использованных словосочетаний'
	flog.write('  	Список использованных словосочетаний'+'\n')
	for i in range (w):	# вывод списка использованных сс
			print '    >',word_list_used[i]
			flog.write('    >'+word_list_used[i]+'\n')
	part_size = os.path.getsize(outdir+'/i'+str(iteration)+'/new.txt')
	print u'	Размер собранной коллекции текстов (кб): ', part_size/1024.
	flog.write('	Размер собранной коллекции текстов (кб): '+str(part_size/1024.)+'\n')
	print u'\nРабота завершена!'
	flog.write('\nРабота завершена!'+'\n')
	flog.close()
	raw_input('Press enter to continue...\n')
	exit()

def Clear(ev):						# функция очистки содержания ячеек
	print u'Очистка содержания ячеек'
	textbox.delete(1.0, END)
	entry1.delete(0, END)
	entry2.delete(0, END)

def Test(ev):						# функция установки тестового набора начальных данных
	print u'Тестовый набор данных используется в качестве начального'
	textbox.delete(1.0, END)
	textbox.insert(1.0,'машинное обучение,\nразработка данных,\nанализ данных,\nавтоматическая обработка текстов,\nкомпьютерные науки,\nбольшие данные,')
	entry1.delete(0, END)
	entry1.insert(0, "10")
	entry2.delete(0, END)
	entry2.insert(0, "10")
	var.set("1")
	
def Start(ev):						# функция запуска сборки веб-корпуса 
	print u'Запуск программы'
	if var.get() == 1:
		outdir = 'snip'
	else:
		outdir = 'text'
	outdir += entry1.get()+entry2.get()
	make_sure_path_exists(outdir)
	open(outdir+'/in.txt', 'wt').write(textbox.get('1.0', 'end').encode('utf-8')) 
	main(outdir)

def Quit(ev):						# функция выхода из программы
	global root
	root.destroy()

def search(outdir, word, urls, snippets, flog, n_o_w, iteration, n):
	"""
	Функция поиска словосочетания в интернете
	"""
	print u'\n  Поиск в Яндексе ключевого словосочетания', n_o_w
	flog.write('\n  Поиск в Яндексе ключевого словосочетания '+str(n_o_w)+'\n')
	print '  >>', word
	flog.write('  >>'+word.encode('utf-8')+'\n')
	furls = open(outdir+'/i'+str(iteration)+'/urls/'+str(n_o_w)+'.txt','w')
	fsnip = open(outdir+'/i'+str(iteration)+'/snip/'+str(n_o_w)+'.txt','w')
	reload(sys)
	sys.setdefaultencoding('utf8')
	y = YaSearch(API_USER, API_KEY)  
	# поиск в яндексе, возвращает страницу, состоящую из гиперссылок и сниппетов
	for i in range(1,n+1): 			# цикл поиска первых n страниц
		try:
			results = y.search(word, page = i)
			if results.error is None:
				for result in results.items:
					furls.write(result.url.encode('utf-8')+'\n')	# записываем гиперссылки
					fsnip.write(result.snippet.encode('utf-8')+'\n')# записываем сниппеты
					urls.append(result.url)
					snippets.append(result.snippet)
		except:
			pass
	furls.close()
	fsnip.close()

def parsing(snippets, flog, iteration, n_o_w):
	"""
	Парсим сниппеты, выделяем слова
	"""
	print u'  Парсим сниппеты, выделяем слова'
	flog.write('  Парсим сниппеты, выделяем слова'+'\n')
	words = []
	words_lemmatized = []
	coll = nltk.FreqDist() #частотный словарь слов из NLTK
	coll_lemmatized = nltk.FreqDist()#частотный словарь лемм; лемма – словарная форма слова, например, "стулу" – лемма "стул", "была" – "быть"
	fout3=open(outdir+'/colls/'+str(iteration)+'_'+str(n_o_w)+'_coll.txt','w+')
	fout4=open(outdir+'/colls/'+str(iteration)+'_'+str(n_o_w)+'_coll_lemmatized.txt','w+')
	for snippet in snippets:
		words = []
		words_lemmatized = []
		for word in snippet.split():  #разделяем сниппеты по пробелу
			for punct in string.punctuation:  #убираем символы пунктуации
				word = word.replace(punct,'')
			if word != '':
				words.append(word.lower()) #сохраняем слова в нижнем регистре
				try:
					info = morph.parse(word)[0] #берем первый (самый частотный разбор)
					lemma = info.normal_form #вытаскиваем из разбора лемму
					words_lemmatized.append(lemma)#сохраняем леммы
				except:
					pass #если разбора не было, ничего не делаем
		#for word in words: coll.inc(word) #частоты слов
		for c2 in nltk.ngrams(words, 2): coll.inc(' '.join(c2)) #частоты последовательных пар слов
		for c3 in nltk.ngrams(words, 3): coll.inc(' '.join(c3)) #частоты последовательных троек слов
		for c4 in nltk.ngrams(words, 4): coll.inc(' '.join(c4)) #частоты последовательных четверок слов
		#for word in words_lemmatized: coll_lemmatized.inc(word) #частоты лемм
		for c2 in nltk.ngrams(words_lemmatized, 2): coll_lemmatized.inc(' '.join(c2))
		for c3 in nltk.ngrams(words_lemmatized, 3): coll_lemmatized.inc(' '.join(c3))
		for c4 in nltk.ngrams(words_lemmatized, 4): coll_lemmatized.inc(' '.join(c4))
	for c in coll: fout3.write("%s,%d\n"%(c.encode('utf-8'),coll[c])) #все сохраняем
	for c in coll_lemmatized: fout4.write("%s,%d\n"%(c.encode('utf-8'),coll_lemmatized[c]))
	fout3.close()
	fout4.close()

def crawler(outdir, urls, iteration, flog, n_o_w):
	"""
	Функция сохранения текстов веб-страниц в файлы
	"""
	print u'  Сохранение текстов веб-страниц в файлы'
	flog.write('  Сохранение текстов веб-страниц в файлы'+'\n')
	count = 0	# счетчик веб-страниц, текст которых успешно загружен и сохранен
	c = 0		# счетчик веб-страниц, загрузить текст которых не удалось
	for url in urls:			# сохранение текста веб-страницы по каждой гиперссылке
		if '.ru' in url or '.рф' in url:
			try:
				response = urllib2.urlopen(url,None,3) 	# переход по гиперссылке
				html = response.read()				# считывание кода веб-страницы
				count += 1
				fout = open(outdir+'/i'+str(iteration)+'/text/'+str(n_o_w)+'_'+str(count)+'.txt','w+')
				fout.write(html)
				fout.close()
			except:
				if c == 0:
					print u'   Ошибка перехода по гиперссылке №', str(c+count+1)+',',
					flog.write('   Ошибка перехода по гиперссылке №'+str(c+count+1))
				else:
					print str(c+count+1)+',',
					flog.write(', '+str(c+count+1))
				c += 1
				pass
	print u'\n  Сохранено', count, u'текстов веб-страниц в файлы'
	flog.write('\n  Сохранено '+str(count)+' текстов веб-страниц в файлы'+'\n')
	return count

def cleaner(outdir, cc, iteration, flog, n_o_w):
	"""
	Функция извлечения содержательных данных из файлов веб-страниц
	"""
	print u'  Извлечение содержательных данных из файлов веб-страниц'
	flog.write('  Извлечение содержательных данных из файлов веб-страниц'+'\n')
	q = 0						# индикатор успешного извлечения данных 
	print u'  Количество очищаемых файлов', cc
	flog.write('  Количество очищаемых файлов '+str(cc)+'\n')
	ftext = open(outdir+'/i'+str(iteration)+'/part'+str(iteration)+'.txt','w')# тексты текущей итерации
	for c in range(1,cc+1):
		if os.path.exists(outdir+'/i'+str(iteration)+'/text/'+str(n_o_w)+'_'+str(c)+'.txt'):
			fin = open(outdir+'/i'+str(iteration)+'/text/'+str(n_o_w)+'_'+str(c)+'.txt','r')
			fout = open(outdir+'/i'+str(iteration)+'/text/'+str(n_o_w)+'_'+str(c)+'clean.txt','w')
			try:
				s = fin.read().decode('utf-8')
				i = 0
				p = 0				# индикатор открытия элемента разметки
				while(i < s.__len__()- 1):
					if s[i] == '<': p = 1
					if s[i] == '>': p = 0
					if ((s[i]>=u'а' and s[i]<=u'я' or s[i]>=u'А' and s[i]<=u'Я') and p==0):
						n = u''
						k = 0		# количество пробелов
						while not (s[i]=='<'):	# s[i]>='a' and s[i]<='z' or s[i]>='A' and s[i]<='Z' or  !!!
							if (s[i]==' '):	k=k+1
							n = n + s[i]
							i += 1
						if k>10:
							fout.write(n.encode('utf-8')+'\n')
							ftext.write(n.encode('utf-8')+'\n')
					else: i += 1
			except: 
				if q == 0:
					print u'   Ошибка при извлечении содержательных данных из файла веб-страницы',str(c)+',',
					flog.write('   Ошибка при извлечении содержательных данных из файла веб-страницы '+str(c))
				else:
					print str(c)+',',
					flog.write(', '+str(c))
				q += 1
				pass
			fout.close()
	ftext.close()				# закрытие файла текста текущей итерации
	if q == 0:
		print u'   Извлечение содержательных данных прошло без ошибок\n'
		flog.write('   Извлечение содержательных данных прошло без ошибок\n')
	else: 
		print u'\n   Извлечены содержательные данные из',cc-q,u'веб-страниц\n'
		flog.write('\n   Извлечены содержательные данные из '+str(cc-q)+' веб-страниц\n')

def canonize(source):			# Функция канонизации текстов
	stop_symbols = '.,!?:;-\n\r()'
	stop_words = (u'это', u'как', u'так', u'и', u'в', u'над',
	u'к', u'до', u'не',	u'на', u'но', u'за', u'то', u'с', u'ли',
	u'а', u'во', u'от',	u'со', u'для', u'о', u'же', u'ну', u'вы',
	u'бы', u'что', u'кто', u'он', u'она')
	return ( [x for x in [y.strip(stop_symbols) for y in source.lower().split()] if x and (x not in stop_words)] )

def genshingle(source):			# Функция разбиения текста на шинглы
	import binascii
	shingleLen = 5 #длина шингла
	out = [] 
	for i in range(len(source)-(shingleLen-1)):
		out.append (binascii.crc32(' '.join( [x for x in source[i:i+shingleLen]] )))#.encode('utf-8')))
	return out

def compaire (source1,source2):	# Функция подсчета процента отношения схожести
	same = 0
	for i in range(len(source1)):
		if source1[i] in source2:
			same = same + 1
	return same*2/float(len(source1) + len(source2))*100

def duplicates(outdir, iteration, c, flog, n_o_w):
	"""
	Функция проверки текстовых данных на наличие дубликатов.
	"""
	print u'  Проверка текстовых данных на наличие дубликатов:'
	flog.write('  Проверка текстовых данных на наличие дубликатов:'+'\n')
	d = []			# список номеров текстов для удаления
	q = 0			# индикатор нахождения дубликатов
	for j in range (1, n_o_w+1):
		for l in range (1, c[j]+1):		
			file1_size = os.path.getsize(outdir+'/i'+str(iteration)+'/text/'+str(j)+'_'+str(l)+'clean.txt')
			if (file1_size):
				f1 = open(outdir+'/i'+str(iteration)+'/text/'+str(j)+'_'+str(l)+'.txt','r')
				text1 = f1.read()
				for k in range (j, n_o_w+1):
					for m in range (1, c[k]+1):
						if ((j == k) and (l<m) or (j<k)): 
							file2_size = os.path.getsize(outdir+'/i'+str(iteration)+'/text/'+str(k)+'_'+str(m)+'clean.txt')
							if (file2_size):
								f2 = open(outdir+'/i'+str(iteration)+'/text/'+str(k)+'_'+str(m)+'.txt','r')
								text2 = f2.read()
								cmp1 = genshingle(canonize(text1))
								cmp2 = genshingle(canonize(text2))
								comp = compaire(cmp1,cmp2)
								if comp>80:
									if q == 0:
										print u'    Тексты под номерами',str(j)+'_'+str(l),u'и',str(k)+'_'+str(m),u'схожи на','('+str(comp)+'%)',
										flog.write('    Тексты под номерами'+str(j)+'_'+str(l)+' и '+str(k)+'_'+str(m)+'схожи на ('+str(comp)+'%)')
									else:
										print ', '+str(j)+'_'+str(l),u'и',str(k)+'_'+str(m)+' ('+str(comp)+'%)',
										flog.write(', '+str(j)+'_'+str(l)+' и '+str(k)+'_'+str(m)+' ('+str(comp)+'%)')
									q += 1
	if (q == 0):
		print u'   Дубликатов не обнаружено.\n' 
		flog.write('   Дубликатов не обнаружено.'+'\n')
	else:
		print u'   Обнаружено',q,u'текстов, которые являются почти дубликатами.\n' 
		flog.write('   Обнаружено '+str(q)+' текстов, которые являются почти дубликатами\n')

def running(s):
	tomita = TomitaParser('tomitaparser.exe', 'config.proto', debug=True)
	facts, leads, coll = tomita.run(s)
	return coll

def jaccard(a, b):															# Подсчет коэффициента Жаккара
	mn_a = set()
	mn_b = set()
	for i in range (0,len(a)-1):
		mn_a.add(a[i:i+1])
	for i in range (0,len(b)-1):
		mn_b.add(b[i:i+1])
	k = float(len(mn_a & mn_b))/len(mn_a | mn_b)
	if k>jacc: return 1
	else: return 0

def finder(outdir, word_list, word_list_used, flog, iteration, n_o_w, c):
	"""
	Функция генерации нового списка словосочетаний
	"""
	print u'  Генерация нового списка словосочетаний:',
	flog.write('  Генерация нового списка словосочетаний:')
	wu1 = []				# список уникальных словосочетаний
	wu2 = []
	n = 0
	o = 0
	# записываем найденные словосочетания в файлы
	fout = open(outdir+'/i'+str(iteration)+'/coll/coll.txt','w')
	fw = open(outdir+'/i'+str(iteration)+'/words.txt','w')
	if var.get() == 2:
		print u'по ТЕКСТАМ\n'
		flog.write(' по ТЕКСТАМ\n')
	else:
		print u'по СНИППЕТАМ\n'
		flog.write(' по СНИППЕТАМ\n')
	flog.write('   Количество найденных слов по словосочетаниям (сс, кол-во):\n')
	for k in range (1, n_o_w+1):
		s = ''
		list = []
		if var.get() == 2:
			for l in range (1, c[k]+1):
			# открываем файл с текстом 
				if os.path.exists(outdir+'/i'+str(iteration)+'/text/'+str(k)+'_'+str(l)+'clean.txt'):
					fin = open(outdir+'/i'+str(iteration)+'/text/'+str(k)+'_'+str(l)+'clean.txt','r')
					try:	s = fin.read().decode('utf-8')
					except:
						s = ''
						pass
					fin.close()
					list = running(s)
					o += len(list)
					for e in (list):
						e = e.lower()
						fout.write(e.encode("utf-8")+'\n')
						if wu1.count(e) == 0:
							wu1.append(e)
							wu2.append(1)
						else:	
							wu2[wu1.index(e)] += 1
		else:
			fin = open(outdir+'/i'+str(iteration)+'/snip/'+str(k)+'.txt','r')
			try:	s = fin.read().decode('utf-8')
			except:
				s = ''
				pass
			fin.close()
		# извлекаем словосочетания с помощью Томита-парсера
			list = running(s)
			o += len(list)
			for e in (list):
				e = e.lower()
				fout.write(e.encode("utf-8")+'\n')
				if wu1.count(e) == 0:
					wu1.append(e)
					wu2.append(1)
				else:
					wu2[wu1.index(e)] += 1
		n += o
		print u'    По словосочетанию',k,u'найдено',o,u'словосочетаний'
		flog.write(str(k)+'	'+str(o)+'\n')
	print u'    Общее количество найденных словосочетаний:',n
	flog.write('    Общее количество найденных словосочетаний:'+str(n)+'\n')	
	fout.close()
	max = 0
	for i in range(len(wu1)):
		if max<wu2[i]:
			max = wu2[i]
	print u'   Максимальная частота',max
	# выгружаем полученную статистику и берем 10 частотных словосочетаний
	z = 10
	min = 0
	new = []
	fout=open(outdir+'/i'+str(iteration)+'/stat/coll.txt','w+')
	flog.write('    Потенциальные ключевые словосочетания и их частота: \n')
	print u'    Потенциальные ключевые словосочетания и их частота: \n'
	for i in range (0,max):
		for j in range(len(wu1)):
			if wu2[j] == max - i:
				if (z>0):
					new.append(wu1[j])
					z -= 1
					flog.write(wu1[j].encode("utf-8")+'	'+str(wu2[j])+'\n')
					fw.write(wu1[j].encode("utf-8")+'	'+str(wu2[j])+'\n')
					try:
						print u'	> ',wu1[j],wu2[j]
					except:
						pass
					if (z==0):
						min = wu2[j]
				elif wu1[j] == min:
					flog.write(wu1[j].encode("utf-8")+'	'+str(wu2[j])+'\n')
					fw.write(wu1[j].encode("utf-8")+'	'+str(wu2[j])+'\n')
					try:
						print u'	> ',wu1[j],wu2[j]
					except:
						pass
				else: pass
				fout.write(wu1[j].encode("utf-8")+' '+str(wu2[j])+'\n')
	fout.close()
	# проверка словосочетаний на вложенность
	print u'   Проверка словосочетаний на вложенность'
	flog.write('   Проверка словосочетаний на вложенность\n')
	d = []
	for i in new:
		for j in new:
			if jaccard(i,j):
				if i.__len__()>j.__len__():
					d.append(j)
					print u'    ',i,'>',j
					flog.write('    '+i.encode('utf-8')+'>'+j.encode('utf-8')+'\n')
	# проверка на то, использовались ли найденные словосочетания
	print u'   Проверка на то, использовались ли найденные словосочетания'
	flog.write('   Проверка на то, использовались ли найденные словосочетания\n')
	for i in word_list_used:
		for j in new:
			if jaccard(i,j):
				d.append(j)
				flog.write('    '+i.encode('utf-8')+'->'+j.encode('utf-8')+'\n')
	# удаление неудовлетворительных словосочетаний
	for i in d:
		print u'     Удаление словосочетания',i
		flog.write('    Удаление словосочетания '+i+'\n')
		if i in new: new.remove(i)
	print u'    Использованные словосочетания'
	for i in word_list_used:
		try:
			print u'	> ',i
		except:
			pass
	# вывод прошедших отбор словосочетаний
	print u'    Прошедшие отбор словосочетания:'
	flog.write('   Прошедшие отбор словосочетания:\n')
	for n in new:
		try:
			print u'	> ',n
		except:
			pass
		flog.write(n.encode('utf-8')+'\n')
		fw.write(n.encode('utf-8')+'\n')
		word_list.append(n)
	print u'\n'
	fw.close()
	flog.write('\n')

def statistics(outdir, iteration, flog, count, n):
	"""
	Функция подсчета статистики по итерации
	"""
	ftext = open(outdir+'/i'+str(iteration)+'/stat/statistics.txt','w')# тексты текущей итерации
	ftext.write(outdir+'\n'+str(iteration)+'\n'+str(flog)+'\n'+str(count)+'\n'+str(n)+'\n')
	ftext.close()
	print u'\n  Подсчет статистики по итерации №', iteration,'\n'
	flog.write('\n  Подсчет статистики по итерации №'+str(iteration)+'\n\n')
	ftext = open(outdir+'/i'+str(iteration)+'/part'+str(iteration)+'.txt','r')
	s = ftext.read().decode('utf-8')
	words = []
	words_lemmatized = []
	coll = nltk.FreqDist() #частотный словарь слов из NLTK
	coll_lemmatized = nltk.FreqDist()#частотный словарь лемм; лемма – словарная форма слова, например, "стулу" – лемма "стул", "была" – "быть"
	words = []
	words_lemmatized = []
	pos = ['NOUN','ADJF','ADJS','COMP','VERB','INFN','PRTF','PRTS','GRND','NUMR','ADVB','NPRO','PRED','PREP','CONJ','PRCL','INTJ','OTHR','NONE']
	poses = []
	for p in pos:
		poses.append([p,0])
	for word in s.split():  #разделяем текст по пробелам
		for punct in string.punctuation:  #убираем символы пунктуации
			word = word.replace(punct,'')
		if word != '':
			words.append(word.lower()) #сохраняем слова в нижнем регистре
			try:
				info = morph.parse(word)[0] #берем первый (самый частотный разбор)
				q = 0
				for i in range (len(pos)):
					if poses[i][0]==info.tag.POS:
						q = 1
						poses[i][1]=poses[i][1]+1
						break
					if q == 0: poses[len(pos)-2][1]+=1
				lemma = info.normal_form #вытаскиваем из разбора лемму
				words_lemmatized.append(lemma)#сохраняем леммы
			except:
				poses[len(pos)-1][1]+=1
				pass #если разбора не было, ничего не делаем
	print u'	Посещено сайтов: ', count
	flog.write('	Посещено сайтов: '+str(count)+'\n')
	print u'	Использовано словосочетаний: ', n
	flog.write('	Использовано словосочетаний: '+str(n)+'\n')
	part_size = os.path.getsize(outdir+'/i'+str(iteration)+'/part'+str(iteration)+'.txt')
	print u'	Размер собранной коллекции текстов (кб): ', part_size/1024.
	flog.write('	Размер собранной коллекции текстов (кб): '+str(part_size/1024.)+'\n')
	print u'   Количество лемм ', len(words_lemmatized)
	flog.write('   Количество лемм '+str(len(words_lemmatized))+'\n')
	print u'   Количество слов ', len(words)
	flog.write('   Количество слов '+str(len(words))+'\n')
	print u'   Части речи:'
	flog.write('   Части речи:\n')
	for i in range (len(pos)):
		print u'   ',poses[i][0],poses[i][1]
		flog.write('   '+poses[i][0]+' '+str(poses[i][1])+'\n')
			
#GUI																		# создание графической оболочки программы

root = Tk()
root.title(u'Web corpus construction')
root.geometry('+100+100')

setFrame = Frame(root, height = 130, width = 520)
textFrame = Frame(root, height = 150, width = 300, bd = 10)
panelFrame = Frame(root, height = 60, width = 100, bd = 10)

setFrame.pack(side = 'top', fill = 'both')
textFrame.pack(fill = 'both', expand = 10)
panelFrame.pack(side = 'bottom', fill = 'x')

label1 = Label(setFrame, text = 'Количество десятков сохраняемых веб-страниц по каждому поисковому запросу: ')
entry1 = Entry(setFrame, width = 5)
entry1.insert(0, "10")
label2 = Label(setFrame, text = 'Количество итераций: ')
entry2 = Entry(setFrame, width = 5, textvariable = 10)
entry2.insert(0, "10")
label4 = Label(setFrame, text = 'Начальный список словосочетаний: ')
label3 = Label(setFrame, text = 'Новые словосочетания извлекаются из: ')
var = IntVar()
rbutton1 = Radiobutton(setFrame, text='snip', variable=var, value=1, indicatoron=0, width = 15)
rbutton2 = Radiobutton(setFrame, text='text', variable=var, value=2, indicatoron=0, width = 15)
var.set(1)

textbox = Text(textFrame, height = 10, width = 70, font='Arial 10', wrap='word')
textbox.insert(1.0,'машинное обучение,\nразработка данных,\nанализ данных,\nавтоматическая обработка текстов,\nкомпьютерные науки,\nбольшие данные,')
scrollbar = Scrollbar(textFrame)

scrollbar['command'] = textbox.yview
textbox['yscrollcommand'] = scrollbar.set

textbox.pack(side = 'left')
scrollbar.pack(side = 'right', fill = 'y')

clearBtn = Button(panelFrame, text = 'Clear')
testBtn = Button(panelFrame, text = 'Test')
startBtn = Button(panelFrame, text = 'Start')
quitBtn = Button(panelFrame, text = 'Quit')

clearBtn.bind("<Button-1>", Clear)
testBtn.bind("<Button-1>", Test)
startBtn.bind("<Button-1>", Start)
quitBtn.bind("<Button-1>", Quit)

label1.place(x=10, y=10)
entry1.place(x=483, y=11)
label2.place(x=10, y=40)
entry2.place(x=483, y=41)
label3.place(x=10, y=70)
label4.place(x=10,y=100)
rbutton1.place(x = 402, y = 70)
rbutton2.place(x = 402, y = 96)
clearBtn.place(x = 0, y = 0, width = 120, height = 40)
testBtn.place(x = 130, y = 0, width = 120, height = 40)
startBtn.place(x = 260, y = 0, width = 120, height = 40)
quitBtn.place(x = 390, y = 0, width = 120, height = 40)

root.mainloop()
