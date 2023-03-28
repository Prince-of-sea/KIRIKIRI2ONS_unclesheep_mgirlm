#!/usr/bin/env python3
from pathlib import Path
import re

# -ONS変数メモ-
# $11  発言時キャラ名
# $21  場所
# $22  音楽
# %200 クリア変数

# デバッグモード
DEBUG_MODE = 0

# effect管理用変数
effect_startnum = 10
effect_list = []

# effect生成時に使う関数
def effect_edit(t,f):
	global effect_list

	# 「何ミリ秒間」、「どの画像効果で」フェードするかを引数で受け取りeffect_listに記録、
	# エフェクト番号を(effect_startnumからの)連番で発行
	# また、過去に同一の秒数/画像の組み合わせを利用した場合は再度同じエフェクト番号になる
	list_num = 0
	if re.fullmatch(r'[0-9]+', t):#timeが数字のみ＝本処理

		for i, e in enumerate(effect_list,effect_startnum + 1):#1からだと番号が競合する可能性あり
			if (e[0] == t) and (e[1] == f):
				list_num = i

		if not list_num:
			effect_list.append([t, f])
			list_num = len(effect_list) + effect_startnum
	
	else:
		print('ERROR: effect指定ミス')

	return str(list_num)


#吉里吉里の命令文及び変数指定をざっくりpythonの辞書に変換するやつ
def krcmd2krdict(c):
	kr_dict = {}

	for p in re.findall(r'([A-z0-9-_]+?)=("(.*?)"|([^\t\s]+))', c):
		kr_dict[p[0]] = p[2] if p[2] else p[3]

	return kr_dict


# ディレクトリの存在チェック関数
def dir_check(path_list):

	CHK = True
	for p in path_list:
		if not p.exists():
			print('ERROR: "' + str(p) + '" is not found!')
			CHK = False
			
	return CHK


# 文字列置換
def message_replace(txt):
	cnvl = [
		['1', '１'], ['2', '２'], ['3', '３'], ['4', '４'], ['5', '５'], ['6', '６'], ['7', '７'], ['8', '８'], ['9', '９'], ['0', '０'],

		['a', 'ａ'], ['b', 'ｂ'], ['c', 'ｃ'], ['d', 'ｄ'], ['e', 'ｅ'], ['f', 'ｆ'], ['g', 'ｇ'], ['h', 'ｈ'], ['i', 'ｉ'], ['j', 'ｊ'],
		['k', 'ｋ'], ['l', 'ｌ'], ['m', 'ｍ'], ['n', 'ｎ'], ['o', 'ｏ'], ['p', 'ｐ'], ['q', 'ｑ'], ['r', 'ｒ'], ['s', 'ｓ'], ['t', 'ｔ'], 
		['u', 'ｕ'], ['v', 'ｖ'], ['w', 'ｗ'], ['x', 'ｘ'], ['y', 'ｙ'], ['z', 'ｚ'], 

		['A', 'Ａ'], ['B', 'Ｂ'], ['C', 'Ｃ'], ['D', 'Ｄ'], ['E', 'Ｅ'], ['F', 'Ｆ'], ['G', 'Ｇ'], ['H', 'Ｈ'], ['I', 'Ｉ'], ['J', 'Ｊ'], 
		['K', 'Ｋ'], ['L', 'Ｌ'], ['M', 'Ｍ'], ['N', 'Ｎ'], ['O', 'Ｏ'], ['P', 'Ｐ'], ['Q', 'Ｑ'], ['R', 'Ｒ'], ['S', 'Ｓ'], ['T', 'Ｔ'], 
		['U', '∪'], ['V', '∨'], ['W', 'Ｗ'], ['X', 'Ｘ'], ['Y', 'Ｙ'], ['Z', 'Ｚ'], 

		['%', '％'], ['!', '！'], ['?', '？'], [' ', '　'], 

		['ｺ', 'コ'], ['ﾎﾟ', 'ポ'], ['ﾎﾞ', 'ボ'], ['ｿ', 'ソ'], ['ｯ', 'ッ'], 
	]

	for v in cnvl:
		txt = txt.replace(v[0], v[1])

	return txt


# txt置換→0.txt出力関数
def text_cnv(default, zero_txt, scenario):

	#default.txtを読み込み
	with open(default, encoding='cp932', errors='ignore') as f:
		txt = f.read()

	#シナリオファイルを読み込み
	p = Path(scenario / 'のろいルート.ks')
	with open(p, encoding='cp932', errors='ignore') as f:
		fr = f.read()
		fr = re.sub(r'\[ruby\stext\s?=\s?"(.+?)"\](.+?)', r'(\2/\1)', fr)
		fr = re.sub(r'\[serihu (.+?)\]', r'[serihu \1]\n', fr)# 文章とセリフ名が1行になってることが多いので剥がす
		fr = re.sub(r'\[font (.+?)\]', r'[font \1]\n', fr)# 文章とfont指定が1行になってることが多いので剥がす
		fr = fr.replace(r'[resetfont]', '\n' + r'[resetfont]')# resetfontも同様
		fr = re.sub(r'\@(.+?)\n', r'[\1]\n', fr)# @からの命令も[]同様に処理したいので
		fr = fr.replace(r'[pcm]', '\\\nmov $11,""' + r':rsf')# セリフの名前部分を空に
		fr = fr.replace(r'[lr]', '@')# 文章停止


		for line in fr.splitlines():
			kakko_line = re.search(r'\[(.+?)\]', line)

			#改行は無視
			if re.match('\n', line):
				pass

			#アイキャッチ
			elif re.search('あいきゃっち', line): 
				line = 'title_mmmm'

			#元々コメントアウトのやつ目立たせる
			elif re.match(r';', line):
				line = (r';;;;' + line) if DEBUG_MODE else ''

			#gotoと間違えそうなやつ
			elif re.match('\*', line): 
				line = (';' + line) if DEBUG_MODE else ''

			#既に置換済み
			elif re.match('mov ', line): 
				pass

			#多分セリフとか
			elif not re.match(r'\[', line):
				#半角置換予定
				line = message_replace(line)

			#命令文 - []内
			elif kakko_line:
				d = krcmd2krdict('kr_cmd=' + kakko_line[1])
				kr_cmd = d['kr_cmd']

				#発言キャラ名
				if kr_cmd == 'serihu':
					line = ('mov $11,"' + message_replace(d['by']) + '"')

				#吉里吉里での変数代入的な
				elif kr_cmd == 'eval':

					#本来f.musicdummyってのもあるがmusicとループの有無以外変わらないので除外(同一視)
					f_place = re.match(r'f\.place\s?=\s?\'(.+?)\'', d['exp'])
					f_music = re.match(r'f\.music\s?=\s?\'(.+?)\'', d['exp'])
					sf_lastflag = re.match(r'sf\.lastflag\s?=\s?(.+?)', d['exp'])

					if f_place:
						line = ('mov $21,"data\\bgimage\\' + f_place[1] + '.png"')

					elif f_music:
						line = ('mov $22,"data\\bgm\\' + f_music[1] + '.ogg"')

					elif sf_lastflag:
						line = ('mov %200,' + sf_lastflag[1])

					else:
						#print(d['exp'])
						line = (';' + line) if DEBUG_MODE else ''
						
				#待ち
				elif kr_cmd == 'wait':
					line = ('wait ' + d['time'])

				#画面揺れ
				elif kr_cmd == 'quake':
					qmax = max(int(d['hmax']), int(d['vmax']))
					line = ('quake ' + str(qmax) + ',' + d['time'])
				
				#場面転換
				elif re.match(r'newscene[1-5](ar)?', kr_cmd):
					bgimage = '$21' if (d['bgimage'] == r'&f.place') else ('"data\\bgimage\\' + d['bgimage'] + '.png"')

					time1 = '500' if (not d.get('time1')) else d['time1']
					rule1 = 'fade' if (not d.get('rule1')) else d['rule1']

					line = 'csp -1:bg ' + bgimage + ',' + effect_edit(time1, rule1)

					if d.get('bgm'):
						bgm = '$22' if (d['bgm'] == r'&f.music') else ('"data\\bgm\\' + d['bgm'] + '.ogg"')
						line += ('\nbgm ' + bgm)
				
				# 画面切り替え
				elif kr_cmd == 'trans':
					if (d['method'] == 'universal'):
						line = 'print ' + effect_edit(d['time'], d['rule'])

					else:
						line = 'print ' + effect_edit(d['time'], 'fade')

				# 画面切り替え
				elif kr_cmd == 'antenar':
					time1 = '500' if (not d.get('time1')) else d['time1']
					rule1 = 'fade' if (not d.get('rule1')) else d['rule1']

					line = 'print ' + effect_edit(time1, rule1)

				# 立ち絵?
				elif kr_cmd == 'image':
					left = d.get('left') if d.get('left') else '0'
					top = d.get('top') if d.get('top') else '0'

					if (d['layer'] == 'base') or (d['layer'] == '0'):
						storage = ('"data\\bgimage\\' + d['storage'].replace('\'', '') + '.png"') if (not d['storage'] == r'&f.place') else '$21'
					else:
						storage = ('"data\\fgimage\\' + d['storage'].replace('\'', '') + '.png"') if (not d['storage'] == r'&f.place') else '$21'

					if (d['layer'] == '0'):
						var = ('$30')
						var_left = ('%40')
						var_top = ('%50')
						var_layer = ('10')

					if (d['layer'] == '1'):
						var = ('$31')
						var_left = ('%41')
						var_top = ('%51')
						var_layer = ('11')

					if (d['layer'] == '2'):
						var = ('$32')
						var_left = ('%42')
						var_top = ('%52')
						var_layer = ('12')

					if (d['layer'] == 'base'):
						var = ('$35')
						var_left = ('%45')
						var_top = ('%55')
						var_layer = ('13')

					if (d.get('visible') == 'true') or (d['layer'] == 'base'):
						line = ('mov ' + var + ',' + storage + ':mov ' + var_left + ',' + left + ':mov ' + var_top + ',' + top + ':lsp ' + var_layer + ',' + var + ',' + var_left + ',' + var_top + ':print 9')
			
					else:
						line = ('mov ' + var + ',' + storage + ':mov ' + var_left + ',' + left + ':mov ' + var_top + ',' + top + ':lsph ' + var_layer + ',' + var + ',' + var_left + ',' + var_top + ':print 9')

				#画像移動
				elif kr_cmd == 'move':
					path = d.get('path')

					if (d['layer'] == '0'):
						var = ('$30')
						var_left = ('%40')
						var_top = ('%50')
						var_layer = ('10')

					if (d['layer'] == '1'):
						var = ('$31')
						var_left = ('%41')
						var_top = ('%51')
						var_layer = ('11')

					if (d['layer'] == '2'):
						var = ('$32')
						var_left = ('%42')
						var_top = ('%52')
						var_layer = ('12')

					if (d['layer'] == 'base'):
						var = ('$35')
						var_left = ('%45')
						var_top = ('%55')
						var_layer = ('13')

					if path:
						x = re.findall(r'\((-?[0-9]+),(-?[0-9]+),(-?[0-9]+)\)', path)
						line = 'print 1'
						for a in x:

							if (a[2] == '0'):
								line += (':mov ' + var_left + ',' + a[0] + ':mov ' + var_top + ',' + a[1] + ':lsph ' + var_layer + ',' + var + ',' + var_left + ',' + var_top + ':print 9')

							else:
								line += (':mov ' + var_left + ',' + a[0] + ':mov ' + var_top + ',' + a[1] + ':lsp ' + var_layer + ',' + var + ',' + var_left + ',' + var_top + ':print 9')
					
					else:
						line = (';' + line) if DEBUG_MODE else ''
				
				#次回立ち絵読み込み
				elif re.match(r'[1-2]ch', kr_cmd):
					next = ('"data\\fgimage\\' + d['next'].replace('\'', '') + '.png"')
					ch = re.match(r'([1-2])ch', kr_cmd)

					if ch:

						if (ch[1] == '1'):
							var = ('$31')
							var_left = ('%41')
							var_top = ('%51')
							var_layer = ('11')

						if (ch[1] == '2'):
							var = ('$32')
							var_left = ('%42')
							var_top = ('%52')
							var_layer = ('12')

						line = ('lsp ' + var_layer + ',' + next + ',' + var_left + ',' + var_top + ':' + 'print 10')

					else:
						line = (';' + line) if DEBUG_MODE else ''
				
				#bgm
				elif kr_cmd == 'playbgm' or kr_cmd == 'fadeinbgm':
					storage = ('"data\\bgm\\' + d['storage'].replace('\'', '') + '.ogg"') if (not d['storage'] == r'&f.music') else '$22'

					line = ('bgm ' + storage)

				#se
				elif kr_cmd == 'playse' or kr_cmd == 'fadeinse':
					storage = ('"data\\sound\\' + d['storage'].replace('\'', '') + '.ogg"') if (not d['storage'] == r'&f.music') else '$22'
					loop = True if (d.get('loop') == 'true') else False

					if loop:
						line = ('dwaveloop 1,' + storage)

					else:
						line = ('dwave 0,' + storage)
				
				#bgm止める
				elif kr_cmd == 'fadeoutbgm':
					line = 'bgmstop'

				#se止める
				elif kr_cmd == 'stopse' or kr_cmd == 'fadeoutse':
					line = ('dwavestop 1')

				#bgm音量調整
				elif kr_cmd == 'bgmopt' or kr_cmd == 'fadebgm':
					volume = d['volume']
					line = ('bgmvol ' + volume)

				#se音量調整
				elif kr_cmd == 'seopt' or kr_cmd == 'fadese':
					volume = d['volume']
					line = ('sevol ' + volume + ':voicevol ' + volume)

				#クリック待ち
				elif kr_cmd == 'waitclick':
					line = 'click'
				
				#レイヤー初期化？
				elif kr_cmd == 'freeimage':
					if (d['layer'] == '0'):
						var_layer = ('10')

					if (d['layer'] == '1'):
						var_layer = ('11')

					if (d['layer'] == '2'):
						var_layer = ('12')

					if (d['layer'] == 'base'):
						var_layer = ('13')

					line = ('vsp ' + var_layer + ',0')

				#暗転
				elif kr_cmd == 'anten' or kr_cmd == 'anten1':
					line = 'csp -1:bg black,9'

				#フォントサイズ変更
				elif kr_cmd == 'font':
					line = r'setwindow3 32,470,15,4,'+d['size']+r'/3*2,'+d['size']+r'/3*2,0,2,20,1,1,#999999,16,424,783,583'

				#フォントサイズ戻す
				elif kr_cmd == 'resetfont':
					line = r'rsf'

				#他
				else:
					if DEBUG_MODE:
						print(kr_cmd)

					line = (';' + line) if DEBUG_MODE else ''
				
			#その他 - エラー防止の為コメントアウト(多分ない)
			else:
				line = (';' + line) if DEBUG_MODE else ''
			
			#変換した命令行が空ではない場合
			if line:
				txt += (line + '\n')#入力


	# エフェクト定義用の配列を命令文に&置換
	add0txt_effect = ''
	for i,e in enumerate(effect_list,effect_startnum+1):

		if e[1] == 'fade':
			add0txt_effect +='effect ' + str(i) + ',10,'+e[0]+'\n'

		else:
			add0txt_effect +='effect ' + str(i) + ',18,'+e[0]+',"data\\rule\\'+str(e[1]).replace('"','')+'.png"\n'

	txt = txt.replace(r';<<-EFFECT->>', add0txt_effect)
	txt += '\nreset'

	#出力結果を書き込み
	open(zero_txt, 'w', errors='ignore').write(txt)

	return


def junk_del(delete_list):

	#リスト内のディレクトリパスでfor
	for d in delete_list:

		#ディレクトリパス内のファイル一覧でfor
		for p in d.glob('*'):

			#削除
			p.unlink()
		
		#ディレクトリも削除
		d.rmdir()

	return


# メイン関数
def main(debug):

	#同一階層のパスを変数へ代入
	same_hierarchy = Path.cwd()

	#debug時にtestフォルダに入れないやつ(default.txt等)はこっちを利用
	same_hierarchy_const = same_hierarchy

	if debug:
		#デバッグ時はtestディレクトリ直下
		same_hierarchy = (same_hierarchy / '_test')

	#利用するパスを辞書に入れ一括代入
	PATH_DICT = {
		#先に準備しておくべきファイル一覧
		'bgimage' :(same_hierarchy / 'data' / 'bgimage'),
		'bgm' :(same_hierarchy / 'data' / 'bgm'),
		'fgimage' :(same_hierarchy / 'data' / 'fgimage'),
		'image' :(same_hierarchy / 'data' / 'image'),
		'rule' :(same_hierarchy / 'data' / 'rule'),
		'scenario' :(same_hierarchy / 'data' / 'scenario'),
		'sound' :(same_hierarchy / 'data' / 'sound'),
		'system' :(same_hierarchy / 'data' / 'system'),
		'video' :(same_hierarchy / 'data' / 'video'),

		'startup_tjs' :(same_hierarchy / 'data' / 'startup.tjs'),

		'default':(same_hierarchy_const / 'default.txt'),
	}

	PATH_DICT2 = {
		#変換後に出力されるファイル一覧
		'0_txt'  :(same_hierarchy / '0.txt'),
	}

	#ディレクトリの存在チェック
	dir_check_result = dir_check(PATH_DICT.values())

	#存在しない場合終了
	if not dir_check_result:
		return

	#txt置換→0.txt出力
	text_cnv(PATH_DICT['default'], PATH_DICT2['0_txt'], PATH_DICT['scenario'])

	#不要データ削除
	if not debug:
		junk_del([
			PATH_DICT['scenario'],
			PATH_DICT['video'],
		])


main(DEBUG_MODE)