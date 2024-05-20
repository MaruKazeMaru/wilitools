# wilitools
![test](https://github.com/MaruKazeMaru/wilitools/actions/workflows/python-package.yml/badge.svg)
## 概要
なくしもの位置推定や推定に用いるパラメータの管理等の機能を提供するPythonパッケージです。<br>
本パッケージはなくしもの位置推定用のプログラム群であるWiLIの一部です。WiLIについての詳細は[wili_documents](https://github.com/MaruKazeMaru/wili_documents)をご参照ください。


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
リポジトリ直下のディレクトリで下記のコマンドを実行してください。
```bash
pip install .
```


## 推定と遷移失敗確率の更新
どちらもSuggesterクラスを用います。


## DB操作
wiliDBクラスを用います。


## ライセンス
MITライセンスです。<br>
詳しくは[LICENSE](./LICENSE)をお読みください。
