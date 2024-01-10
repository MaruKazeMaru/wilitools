# wilitools
## 概要
WiLIのなくしもの位置推定、遷移失敗確率の更新、各種パラメータのDBへの保存を行うPythonパッケージです。<br>
WiLIとはなくしもの位置推定用のプログラム群です。詳細は近日中に[wili_documents](https://github.com/MaruKazeMaru/wili_documents)に書きます。


## 依存
### Pythonパッケージ
* NumPy

### その他
* SQLite3


## 推定と遷移失敗確率の更新
どちらも[suggester.py](./src/wilitools/suggester.py)で定義されたSuggesterクラスを用います。


## DB操作
[db.py](./src/wilitools/db.py)で定義されたWiliDBクラスを用います。


## ライセンス
MITライセンスです。<br>
詳しくは[LICENSE](./LICENSE)をお読みください。