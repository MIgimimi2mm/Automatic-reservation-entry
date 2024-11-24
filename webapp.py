# -*- coding: utf-8 -*-
"""webapp.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1nkPObQmB8p-1gCdun9xj0pG4uII_H3T9
"""

!pip install gradio

import gradio as gr
import pandas as pd
from re import A
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from google.colab import auth
from google.auth import default
from datetime import datetime

from google.colab import drive
drive.mount('/content/drive')
from glob import glob

# Google認証
auth.authenticate_user()
creds, _ = default()

# Googleスプレッドシートへのアクセス
gc = gspread.authorize(creds)

# スプレッドシートを新規作成、もしくは既存のシートを開く
# フォルダのIDを取得
folder_id = '1im8MJqQh1HVAMtFRDSzmO_aBnVOkDBsl'

# 新しいスプレッドシートを作成する場合
#spreadsheet = gc.create('reserves',folder_id)

spreadsheet = gc.open('reserves',folder_id)

#作業シートの指定
worksheet = spreadsheet.sheet1

# CSVファイルを処理する関数
def process_csv(file):
    try:

        # アップロードされたCSVを読み込む
        try:
            df = pd.read_csv(file.name, encoding='shift_jis')
        except:
            df = pd.read_csv(file.name, encoding='utf-8')


        # df = pd.read_csv('reserve_list(1) (1).csv')

        first_char = file.name.split('/')[-1]
        first_char = first_char[0]

       # CSVを読み込む
        # site = pd.read_csv(file.name)




        site_filtered = None

        if first_char == 'i':
            site = pd.read_csv(file.name, encoding='shift_jis')
            # 指定された処理を実行
            site_filtered = site[['予約番号', '予約者氏名', '運転者電話番号', '貸出日時', '返却日時',
                                       'キャンセル日', '到着便', '貸出営業所']]
            site_filtered = site_filtered.rename(columns={
                '予約者氏名': '名前',
                '運転者電話番号': '電話番号',
                'キャンセル日': '予約状況'
            })
            site_filtered.insert(0, 'status', '')
            site_filtered['到着便'] = site_filtered['到着便'].fillna('')
            site_filtered['予約状況'] = site_filtered['予約状況'].astype(str)
            site_filtered.loc[site_filtered['予約状況'] == 'nan', '予約状況'] = '予約済'
            site_filtered.loc[site_filtered['予約状況'] != '予約済', '予約状況'] = 'キャンセル'
            site_filtered.loc[site_filtered['貸出営業所'] == '函館空港店', '貸出営業所'] = '函館'
            site_filtered.loc[site_filtered['貸出営業所'] == '伊丹空港店（大阪空港）', '貸出営業所'] = '伊丹'

        elif first_char == '2':
          #たびらい
            site = pd.read_csv(file.name, encoding='shift_jis')
            site_filtered =site[['予約番号','代表者指名', '電話番号','予約日時','返却日時','催行','到着時送迎場所','受取場所']]
            site_filtered =site_filtered.rename(columns={'代表者指名': '名前', '予約日時': '貸出日時','催行':'予約状況','到着時送迎場所':'到着便','受取場所':'貸出営業所'})
            site_filtered.insert(0, 'status', '')
            site_filtered['到着便'] = site_filtered['到着便'].fillna('')
            site_filtered['予約状況'] =site_filtered['予約状況'].astype(str)
            site_filtered['予約番号'] =site_filtered['予約番号'].astype(str)
            site_filtered.loc[site_filtered['予約状況'] == '○', '予約状況'] = '予約済'
            site_filtered.loc[site_filtered['予約状況'] == '×', '予約状況'] = 'キャンセル'
            #site_filtered.loc[site_filtered['予約状況'] == '予約済', '予約状況'] = 'キャンセル'

            site_filtered.loc[site_filtered['貸出営業所'] == '函館空港店', '貸出営業所'] = '函館'
            site_filtered.loc[site_filtered['貸出営業所'] == '伊丹空港店', '貸出営業所'] = '伊丹'



        elif first_char == 'r':
            #公式侍
            site = pd.read_csv(file.name, encoding='utf-8')
            site_filtered = site[site['借受人名（名称）'] != 'J-Trip CarRentals']
            site_filtered = site_filtered[site_filtered['貸渡状況'] != '削除']

            site_filtered['貸出日時'] = site_filtered['出発日'] + ' ' + site_filtered['出発時間'].str[:5]
            site_filtered['返却日時'] = site_filtered['返却日'] + ' ' + site_filtered['返却時間'].str[:5]




            site_filtered =site_filtered[['貸渡No','借受人名（名称）', '電話番号（借受人）','貸出日時','返却日時','貸渡状況','出発営業所']]
            site_filtered.insert(0, 'status', '')
            site_filtered.insert(7, '到着便', '')
            site_filtered =site_filtered.rename(columns={'貸渡No': '予約番号', '借受人名（名称）': '名前','電話番号（借受人）':'電話番号','貸渡状況':'予約状況','出発営業所':'貸出営業所'})

            site_filtered.loc[site_filtered['貸出営業所'] == 'J-Trip Car Rentals 函館空港店', '貸出営業所'] = '函館'
            site_filtered.loc[site_filtered['貸出営業所'] == 'J-Trip Car Rentals 伊丹空港店', '貸出営業所'] = '伊丹'




        # データフレームの最初の数行を返す

        data = worksheet.get_all_values()
        S_data = pd.DataFrame(data[1:], columns=data[0])

        for index, row in  site_filtered.iterrows():
          existing_row = S_data[S_data['予約番号'] == row['予約番号']]

    # 1. 予約番号がすでに存在しない場合のみ追加
          if existing_row.empty:
                  S_data = pd.concat([S_data, pd.DataFrame([row], columns=S_data.columns)], ignore_index=True)
            # 2. 予約番号が既に存在し、'予約状況'が一致しない場合はデータを上書き
          elif not existing_row.empty and existing_row['予約状況'].values[0] != row['予約状況']:
                  S_data.loc[S_data['予約番号'] == row['予約番号'], :] = row.values

              # 3. 予約番号が既に存在し、'予約状況'が一致する場合はそのデータは追加しない
          elif not existing_row.empty and existing_row['予約状況'].values[0] == row['予約状況']:
                  continue


        set_with_dataframe(worksheet, S_data)


        return"ありがとう"
    except Exception as e:
        return f"Error: {e}"



# Gradioインターフェース
interface = gr.Interface(
    fn=process_csv,  # 実行する関数
    inputs=gr.File(label="予約のCSVファイルをアップロードしてください"),  # 入力としてファイルアップロード
    outputs="text",  # 出力をテキストで表示
    title="Googleカレンダー入力ツール",
    description="予約のCSVファイルをアップロードしてください",
    allow_flagging='never'
)

# アプリを起動
interface.launch(share=True,auth=("J-trip", "0727562003"))

