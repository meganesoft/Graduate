from secret import twitter_OAuth
from secret import feel
import csv
import time
import calendar
import os
import datetime


# ヘッダにはいってるAPIリクエストのリミットが0になったら現在使用しているインスタンスのflgをオフして
# switch_instance()に投げる
def check_limit(res):
    if res.headers['x-rate-limit-remaining'] == '0':
        '''
        print('API制限にかかるから１５分待って')
        print(time.localtime())
        time.sleep(900)
        '''
        if tw is twA:
            twA_check['time'] = int(res.headers['X-Rate-Limit-Reset'])
            twA_check['flg'] = False
            print('Aのリセット時間(残り):%s', int(res.headers['X-Rate-Limit-Reset'])
                  - time.mktime(datetime.datetime.now().timetuple()))

        if tw is twB:
            twB_check['time'] = int(res.headers['X-Rate-Limit-Reset'])
            twB_check['flg'] = False
            print('Bのリセット時間(残り):%s', int(res.headers['X-Rate-Limit-Reset'])
                  - time.mktime(datetime.datetime.now().timetuple()))
        switch_instance()
    else:
        print('API残り回数：', res.headers['x-rate-limit-remaining'])


# インスタンスのフラグ状況を見て利用するインスタンスを変える、両方ダメなら時間分sleepする
def switch_instance():
    global tw
    if twA_check['flg'] is False and twB_check['flg'] is True:
        print('Bに切り替えたよ')
        tw = twB

    if twA_check['flg'] is True and twB_check['flg'] is False:
        print('Aに切り替えたよ')
        tw = twA

    if twA_check['flg'] is False and twB_check['flg'] is False:
        if twA_check['time'] < twB_check['time']:
            sec = int(twA_check['time'] - time.mktime(datetime.datetime.now().timetuple()))
            print(sec, '秒待ってAに切り替えるよ')
            if sec > 0:
                time.sleep(sec + 10)
            twA_check['flg'] = True
            tw = twA
        if twA_check['time'] > twB_check['time']:
            sec = int(twB_check['time'] - time.mktime(datetime.datetime.now().timetuple()))
            print(sec, '秒待ってBに切り替えるよ')
            if sec > 0:
                time.sleep(sec + 10)
            twB_check['flg'] = True
            tw = twB


# created_atを年月日時分秒に変換する関数
def YmdHMS(created_at):
    time_utc = time.strptime(created_at, '%a %b %d %H:%M:%S +0000 %Y')
    unix_time = calendar.timegm(time_utc)
    time_local = time.localtime(unix_time)
    return int(time.strftime('%Y%m%d%H%M%S', time_local))


# 引数：Twitter認証のインスタンス,ファイル名,取得するツイート数,検索キーワード
# 検索した結果をcsvに出力する（ツイートした時間,ユーザのID,ツイート内容）
def get_post(filename, num, keywords):
    print('running get_post')
    # 書き込むcsvファイルを読み込む
    f = open(filename + '.csv', 'w', encoding='utf-8', newline='')
    writer = csv.writer(f)
    # ヘッダを書き込む
    header = ['day', 'user', 'text']
    writer.writerow(header)
    # 初期化
    total = 0

    # 指定した数までぶん回す
    while total < num:
        response = tw.search.tweets(**keywords)

        if 'statuses' not in response or not response['statuses']:
            break

        metadata = response['search_metadata']
        statuses = response['statuses']
        min_id = statuses[-1]['id']
        total += metadata['count']

        for tweet in statuses:
            day = YmdHMS('{created_at}'.format(**tweet))
            user = '{user[id]}'.format(**tweet)
            txt = '{text}'.format(**tweet).replace('\n', '\\n')
            output = [day, user, txt]
            txt = txt.encode('utf-8')
            print(txt)
            writer.writerow(output)
            if feel.feel_analyze(str(txt)) is True:
                writer.writerow(output)
            else:
                print('false')

        keywords['max_id'] = min_id - 1

        check_limit(response)

    f.close()


# 引数：csvファイル名
# 指定したcsvから2列目の要素（user）を取ってくる
def csv_read(filename):
    print('running csv_read')
    data = []

    # csvファイルを読み込み、配列に格納
    with open(filename + '.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        reader.__next__()
        for row in reader:
            if row[1] not in data:
                data.append(row[1])
    return data


# 引数：Twitter認証のインスタンス、ユーザid
# idを受け取ってそのidのフォローリストを取ってくる
def get_friendslist(user_id):
    print('running get_friendslist')
    next_cursor = -1
    friends = [user_id]
    while next_cursor:
        response = tw.friends.ids(
            user_id=user_id,
            # idをstr型で取ってくる（いらないのでCO
            # stringify_ids=True,
            cursor=next_cursor, )

        friends += response['ids']

        next_cursor = response['next_cursor']

        check_limit(response)
    return friends


# 　引数：Twitter認証のインスタンス、ユーザ、フォローしている人、作成するファイル名
#  指定したidのユーザのツイートを取得
def get_friendstweet(user, follow_id, filename, num):
    print('running get_friendstweet')
    # 書き込むcsvファイルを読み込む
    total = 0
    min_id = 1
    min_id_buf = 1
    while total < num:
        with open(filename + '_' + user + '.csv', 'a', encoding='utf-8', newline='') as f:
            try:
                response = tw.statuses.user_timeline(**friend_keyword)

                for tweet in response:
                    txt = '{text}'.format(**tweet).replace('\n', '\\n')
                    # 2017/01/12 生成ファイル数多すぎ問題解消のためにツイート毎にidを付与
                    # 読み込むときにlow[0]を見て同一ユーザかの判断してからlow[1]のツイート内容取れば良いかなと
                    # これに伴いエラー発生したらそのファイルを削除する処理を削除
                    # csvなのでカンマを、に置換
                    f.write(follow_id + ',' + txt.replace(',', '、') + '\n')
                    min_id = int('{id}'.format(**tweet))
                    total += 1

                friend_keyword['max_id'] = min_id - 1
                check_limit(response)
                if min_id is min_id_buf:
                    print(friend_keyword['user_id'], 'は', total, '件しかツイートがなかったよ')
                    break
                min_id_buf = min_id

            # ツイートを取得しようとしたアカウントが鍵垢の場合エラーが発生する（認証したインスタンスに権限がないよ的な）
            except:
                global follow_count
                if follow_count > 0:
                    follow_count -= 1
                print('なんか発生？（鍵垢かも）')
                break




if __name__ == '__main__':
    # 書き込むcsvファイルの指定、CSVのヘッダ、取得するツイート数(1で8個取ってくる)、検索キーワード
    folder = './test'
    filename = 'shadowverse'
    numberToGet = 60

    keywords = dict(
        q='シャドウバース -rt -bot',
        include_entities=False, )

    friend_keyword = dict(
        user_id='megane_soft',
        count=200,
        trim_user=False,
        contributor_details=False,
        include_entities=False,
        exclude_replies=True,
        include_rts=False,
    )

    # 大量のcsvを吐き出すためのフォルダ作成,移動
    if not os.path.exists(folder):
        os.mkdir(folder)
    os.chdir(folder)

    # Twitter認証する
    # アカウントAをとりあえず使用
    global tw, twA, twB, count
    twA_check = dict(
        time=0,
        flg=True)
    twB_check = dict(
        time=0,
        flg=True)

    twA, twB = twitter_OAuth.twitter_instance()
    tw = twA

    search_user_count = 0
    search_user_limit = 50

    # 指定したキーワード、件数をもとに検索してcsv出力
    get_post(filename, numberToGet, keywords)
    print(u'ツイート取得完了')

    # 検索結果のcsvからユーザIDだけを重複無く取り出す
    user_list = csv_read(filename)
    print(u'ユーザIDの抽出完了')

    # 取り出したユーザID毎にフォローしているユーザID一覧をcsvに出力
    with open(filename + '_friends.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for user_id in user_list:
            friend_list = get_friendslist(user_id)
            writer.writerow(friend_list)

    # フォローしているユーザID一覧をもとに、フォローしているユーザのツイートを取得
    with open(filename + '_friends.csv', 'r', encoding='utf-8', newline='') as f:
        while search_user_count < search_user_limit:
            follow_count = 0
            data = f.readline()
            if not data:
                break
            user_name = data.split(',')

            for i in range(len(user_name)):
                follow_count += 1
                friend_keyword['user_id'] = user_name[i]
                get_friendstweet(user_name[0], user_name[i].replace('\r\n', ''), filename, num=1000)
                if 'max_id' in friend_keyword:
                    del friend_keyword['max_id']
                if follow_count > 100:
                    break
            search_user_count += 1

