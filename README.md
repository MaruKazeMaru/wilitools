# wilitools
![test](https://github.com/MaruKazeMaru/wilitools/actions/workflows/python-package.yml/badge.svg)
## 概要
なくしもの位置推定や推定に用いるパラメータの管理等の機能を提供するPythonパッケージです。<br>
本パッケージはなくしもの位置推定用のプログラム群であるWiLIの一部です。具体的な推定方法やその他詳細については[wili_documents](https://github.com/MaruKazeMaru/wili_documents)をご参照ください。


## 依存
* NumPy
  * 修正BSDライセンス
* SQLAlchemy
  * MITライセンス
* pytest
  * テスト時のみ
  * MITライセンス


## テスト環境
||バージョン|
|:-|:-|
|Ubuntu|latest|
|Python|3.9 ~ 3.11|
|NumPy|latest|
|SQLAlchemy|latest|

（注）latestはGitHub Actionsによるテストを行った時点（＝最後にmainブランチにpushした時点）での最新のバージョンという意味です。


## インストール
### 方法1：git cloneしてから
まず本リポジトリをcloneします。
```bash
git clone https://github.com/MaruKazeMaru/wilitools
```
次にcloneしたリポジトリ直下のディレクトリへ移動します。
```bash
cd wilitools
```
最後にpipを用いてインストールします。
```bash
pip install .
```
### 方法2：pipのみ
pipを用いてGitHubからダウンロード、インストールします。
```bash
pip install git+https://github.com/MaruKazeMaru/wilitools
```


# チュートリアル
## はじめに
推定に用いるパラメータは捜索範囲、初期確率、遷移確率、利用者位置分布、遷移失敗確率（の分布）の5種です。
本パッケージではこれらを次の型の変数として扱います。
|パラメータ|型|
|:-|:-|
|捜索範囲|wilitools.Floor|
|初期動作確率|numpy.ndarray|
|遷移確率|numpy.ndarray|
|利用者位置分布|wilitools.Gaussian|
|遷移失敗確率の分布|numpy.ndarray<br>numpy.ndarray|

またこれらをまとめてAreaクラスとして扱います。
本パッケージではAreaクラスを介して各機能

## 推定
Suggesterクラスを用います。
```python
suggester = area_to_suggester(area)
suggester.suggest(x)
```


## 遷移失敗確率の学習
Suggesterクラスを用います。
```python
suggester.update(x_true)
```


## 推定に用いるパラメータの管理
パラメータをデータベース（以下DB）で管理できます。
wiliDBクラスを用います。
```python
db = wiliDB('sqlite:///./db.sqlite3')
db.read_tr_prob(0)
```


## ライセンス
MITライセンスです。<br>
詳しくは[LICENSE](./LICENSE)をお読みください。
