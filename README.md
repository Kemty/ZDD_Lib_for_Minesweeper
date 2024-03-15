# ZDD_Lib_for_Minesweeper

大学の卒研で作ったマインスイーパーをZDDで解くライブラリです.  
ついでにN-Queen問題をZDDで解く手法の改良案が得られたので一緒に置いときます.

# 「情報処理学会 第86回全国大会」での講演内容に関する訂正

「情報処理学会 第86回全国大会」の学生セッションにて本研究の講演を行いましたが,
その際申し込み時に提出した講演論文について記載に誤りがあったため, この場を借りてお詫びと訂正をさせていただきます.

## ・式(1),(2) (items, flags) の計算量について

講演論文では「返り値を共有リストで持つことにより空間計算量を節点数の定数倍に抑えられる.」と記載しましたが, **これは誤りです.**

すなわち, 返り値を共有リストで持っても計算量改善には至らない(節点数の2乗のオーダーになる)ケースが存在します.

寄稿した時点では見落としておりました. 謹んでお詫び申し上げます.

## ・計算機実験での, テスト入力値の変更について

寄稿後に行った追加の研究にて, 実装上想定外のところが消費メモリのボトルネックとなっていることが発覚し修正したところ, ソルバーの性能が大きく向上したため, テスト入力時の値が大きくなりました.

## ・不要節点の削除機能について

寄稿後に行った追加の研究にて, 「まとめ」に記していた「適切なメモリの解放」を実現できたため, 講演内容に追加しました.

# 参考資料
1. 鈴木 浩史, 孫 浩, 湊 真一. BDD/ZDDを用いたマインスイーパーの爆弾配置パタンの列挙. The 30th Annual Conference of the Japanese Society for Artificial Intelligence, 1D5-OS-02b-3in2, 2016. 
2. 湊 真一. Zero-suppressed BDDs for Set Manipulation in Combinational Problems. 30th ACM/IEEE Design Automation Conference,1993. 
3. 湊 真一. Zero-suppressed BDDs and their applications. Int. J. Softw. Tools Technol. Transf. (STTT), vol. 3, no. 2, pp. 156-170, Springer 2001
4. [【python】コードブロックにタイムアウトを付けようと試行錯誤する話](https://qiita.com/Jacomb/items/92503b11aef68ec4748a#%E3%82%BF%E3%82%A4%E3%83%A0%E3%82%A2%E3%82%A6%E3%83%88%E3%81%AE%E3%82%B3%E3%83%B3%E3%83%86%E3%82%AD%E3%82%B9%E3%83%88%E3%83%9E%E3%83%8D%E3%83%BC%E3%82%B8%E3%83%A3%E3%82%92%E4%BD%9C%E3%81%A3%E3%81%A6%E3%81%BF%E3%82%8B)
