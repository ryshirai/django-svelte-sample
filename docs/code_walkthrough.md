# このリポジトリのコードの追い方

BTO PC 店舗の実装を、自分でたどれるようにした文書。Svelte 入門でも Django 入門でもない。このリポジトリのファイル名、関数名、画面 URL、API パスだけを使う。

## 誰向けか

想定する読者は次である。

- どれか1つの言語で、関数を追い、ファイルを開き、条件分岐を読んだことがある
- 「画面がサーバにデータを頼む」「データベースに行がある」くらいの感覚がある
- Svelte、Django、TypeScript、Python は初めてでもよい

想定しない読者は次である。

- プログラミング自体が初めて（変数・関数・ファイルの話から始める文書ではない）
- この文書だけで Svelte や Django を一通り習得したい人

他言語から来た人は、§1 の対応表を先に読む。本文の専門語は、初出でこのリポジトリでの意味を書く。一般的な定義の百科事典にはしない。

実装の正本は次の3つである。この文書はそれらを置き換えない。

| 読みたいこと | 文書 |
|---|---|
| 何を作っているか（画面、API、業務ルール） | `docs/bto_pc_store.md` |
| コードをどこに置くか、誰が誰を呼ぶか | `docs/coding_style.md` |
| 見た目・寸法・色の書き方 | `docs/frontend_design.md` |

コードを追うときは、仕様と実装が食い違っていないかをこの3つで確認する。食い違いを見つけても、この文書を正にして実装を変えない。仕様を正にする。

---

## 1. 他言語からの地図

このリポジトリは、よくある「画面用のプログラム」と「データ用のプログラム」の2つに分かれている。

| このリポジトリでの呼び方 | 中身 | 他言語で近いもの |
|---|---|---|
| frontend / Svelte | ブラウザで動く画面 | スマホアプリの UI 層、デスクトップの画面コード |
| backend / Django | データを読み書きするサーバ | API サーバ、Spring / Rails / ASP.NET のサーバ側 |
| HTTP API | 画面とサーバの約束（パスと JSON） | REST エンドポイント、gRPC のサービス定義 |
| JSON | やり取りするデータの形 | 辞書 / map / 構造体を文字にしたもの |

役割の名前は、他フレームワークの単語に近いが、このリポジトリでは置き場が固定されている。

| このリポジトリ | 何をするか | 他言語で近いもの | ここでやらないこと |
|---|---|---|---|
| Svelte の page（`+page.svelte`） | 1 URL の画面。組み立てとボタン処理 | 1画面の UI。Activity / Form / Blade 1枚 | データベースを直接触らない |
| Svelte の component | 見た目の部品。渡された値を描く | UI 部品。props は引数 | サーバへ取りに行かない |
| frontend API client（`lib/api/`） | サーバへ HTTP を送る関数 | API SDK、HTTP クライアント | 在庫判定などの業務を持たない |
| DRF View | HTTP を受けて返す関数 | Controller | SQL を書かない。業務判断を持たない |
| Serializer | 入力の形を検査し、出力の JSON を作る | DTO + バリデーション。リクエスト/レスポンス型 | データベースを触らない |
| Service | 更新・副作用の業務 | Use Case、アプリケーションサービス | 画面や HTTP を知らない |
| Selector | 読み取り専用の取得 | 読み取り専用 Repository / Query | 行を書き換えない |
| Validator | 値だけを見て可否を返す純関数 | ドメインの仕様オブジェクト | データベースを見ない |
| Model | テーブル1種類の定義 | Entity / 行の型 | 保存処理の本体にはしない |
| ORM（`Part.objects.filter(...)`） | Python から SQL 相当を書く仕組み | Hibernate / ActiveRecord / Entity Framework | View や Serializer からは呼ばない |

単語が同じでも、一般的な Django 解説とは置き場が違うことがある。ネットの「Model に業務を書く」「ViewSet を使う」は、このリポジトリでは禁止である。迷ったらネットより `docs/coding_style.md` を正にする。

---

## 2. 読む前に知っておけば足りる用語

ここだけ先に読めば、あとの節で止まらずに済む。

### 2.1 画面とサーバは別プロセス

開発中、次の2つが同時に動く。

- 画面: SvelteKit。ブラウザが開く先は `http://localhost:5173`
- サーバ: Django。データ処理は `http://localhost:8000`

ブラウザのアドレス欄は 5173 のままである。画面のプログラムが `/api/v1/parts` を取りに行くと、開発用の転送（Vite の proxy。設定は `frontend/vite.config.ts`）がそれを 8000 番の Django へ渡す。画面から見ると「同じサイトの `/api/...`」に見える。

```text
ブラウザ  →  画面（:5173）
                │
                │  「/api/v1/parts を取って」
                │  開発ツールが Django へ転送
                v
            サーバ（:8000）
                │
                v
            データベース（PostgreSQL）
```

ブラウザに出る HTML は Svelte が作る。Django が HTML を返す昔ながらの形（テンプレート）は使わない。

### 2.2 HTTP と JSON

画面がサーバに頼むときの約束が HTTP である。このリポジトリで見るのは次くらい。

| 動詞 | このリポジトリでの使い方 |
|---|---|
| `GET` | 読む。パーツ一覧、注文詳細 |
| `POST` | 新しく作る、または操作する。ログイン、決済、発送 |
| `PATCH` | 既存を一部変える。スタッフのパーツ更新 |
| `DELETE` | 消す。ログアウト（session を消す） |

やり取りの中身は JSON（`{ "email": "...", "password": "..." }` のような文字）である。成功した応答に包み紙は付かない。失敗したときだけ次の形になる。

```json
{
  "error": {
    "code": "order.not_found",
    "message": "...",
    "details": {}
  }
}
```

`code` がプログラムが分岐に使う名前、`message` が人間向け文言である。画面に出す日本語の正本は frontend 側にある（§11）。

数字の 200 番台は成功、400 番台は呼び出し側の問題、401 は未ログイン、403 は権限なし、404 は無い、と読めば足りる。

### 2.3 ログインの覚え方（cookie と CSRF）

ブラウザは「今だれか」を毎回メールとパスワードで送らない。ログイン成功時、サーバが **session cookie**（小さな覚え書き）をブラウザに置く。以後のリクエストにそれが付く。

**CSRF** は、別のサイトが「今ログイン中のブラウザ」を使って勝手に注文させないための印である。ログイン前の登録・ログイン POST にも同じ印が要る。このリポジトリでは次の順になる。

1. 起動時に `GET /api/v1/csrf` で印（`csrftoken`）を cookie に載せる
2. 更新系のリクエストは、その印をヘッダ `X-CSRFToken` にも載せる
3. 載せ方は全部 `frontend/src/lib/api/client.ts` がやる。画面ごとに書かない
4. サーバ側は `backend/application/api/authentication.py` が、未ログインの POST でも印を見る

中身の暗号を追う必要はない。「ログイン維持は cookie、更新の偽物防止は CSRF、どちらも API client に閉じている」と覚えれば、コードは追える。

### 2.4 `.svelte` ファイルの読み方

1ファイルが「上: プログラム、下: 見た目」になっている。

```svelte
<script lang="ts">
	// 変数・関数。TypeScript
	let { data } = $props();          // 親や load から渡された値
	let selected = $state('cpu');     // この画面の可変データ。変わると再描画
	const count = $derived(data.parts.length); // 他の値から計算
</script>

<main>
	<!-- 見た目。HTML に近い -->
	<h1>{count}</h1>
	<button onclick={doSomething}>押す</button>
</main>
```

このリポジトリで覚える記号は次だけである。

| 記号 | 意味 |
|---|---|
| `$props()` | 外から渡された引数 |
| `$state` | 画面の変数。代入すると表示が追いつく |
| `$derived` | 計算プロパティ。自分では代入しない |
| `{data.parts}` | 見た目の中に値を埋め込む |
| `{#if}` `{#each}` | 条件と繰り返し |
| `onclick={fn}` | クリックで関数を呼ぶ |

`$effect` は「値が変わったら裏で自動実行」である。このリポジトリでは、データ取得や保存に使わない。取る・書くの起点は、画面を開いたときの `load` か、ユーザーのクリックだけ。

Svelte 4 の store や、Redux のような状態ライブラリは入っていない。

### 2.5 `+page` と `+layout`（ファイル名が URL）

SvelteKit は、フォルダ名がブラウザの URL になる。

| ファイル | 役割 |
|---|---|
| `routes/configure/+page.svelte` | `/configure` の見た目 |
| `routes/configure/+page.ts` | `/configure` を開く前のデータ取得（`load`） |
| `routes/+layout.svelte` | 全画面共通の枠（ヘッダなど）。ログアウトと、途中の 401 復旧もここ |
| `routes/+layout.ts` | 全画面の前に一度走る初期化（ログイン確認） |
| `routes/+error.svelte` | `load` が既知の失敗を投げたときの共通画面 |
| `routes/orders/[uuid]/+page.svelte` | `/orders/（何か）`。`[uuid]` は可変部分 |

`+` で始まる名前は SvelteKit の予約である。このリポジトリが足しているのは `+page`、`+layout`、`+error` だけである。自分で別の `+何か` を増やさない。

`load` は「この画面を出す前に走らせる関数」である。戻り値は、同じ画面の `+page.svelte` で `data` として受け取れる。

このリポジトリは **SSR しない**（`+layout.ts` の `ssr = false`）。SSR は「最初の HTML をサーバで組み立てる」方式である。ここでは最初の読み取りもブラウザ上で走る。ログイン cookie をサーバ描画に載せないため。知らなくてよいのは SSR の一般論で、覚えるのは「このアプリはブラウザで取る」ことだけ。

### 2.6 TypeScript の読み方（このリポジトリ分）

frontend は TypeScript である。Java や C# の型注釈に近い。

```ts
export async function getOrder(publicId: string): Promise<OrderOutput> {
	return apiGet<OrderOutput>(`/api/v1/orders/${publicId}`);
}
```

| 書き方 | 意味 |
|---|---|
| `publicId: string` | 引数は文字列 |
| `Promise<OrderOutput>` | あとで `OrderOutput` が届く非同期の戻り |
| `async` / `await` | サーバ応答を待つ。コールバックの入れ子を避ける書き方 |
| `OrderOutput` | `lib/types/order.ts` にある、API 応答の型 |
| `` `/api/v1/orders/${publicId}` `` | 文字列に変数を埋め込む |

`import { getOrder } from '$lib/api/orders'` の `$lib` は `frontend/src/lib` の別名である。`$app/navigation` は SvelteKit 本体で、このリポジトリの中には無い。

### 2.7 Python の読み方（このリポジトリ分）

backend は Python である。

```python
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def part_list(request: Request) -> Response:
    ...
```

| 書き方 | 意味 |
|---|---|
| `def name(...):` | 関数定義 |
| `@何か` | デコレータ。関数の直前に「GET 専用」「ログイン必須」などを付ける |
| `request: Request -> Response` | 引数と戻り値の型 |
| `*, filter: PartFilter` | `*` のあとだけキーワード引数。`list_listed_parts(filter=...)` と書く |
| `Part.objects.filter(...)` | ORM。SQL の `SELECT ... WHERE` に相当 |
| `raise PartNotFoundError()` | 例外を投げる。このリポジトリでは業務失敗もこの形 |

`class` は Model と Error と Serializer と Input 用データのかたまりに使う。Service と Selector の入口は **class ではなく module の関数** である。`OrderService().create()` のような呼び方は無い。`create_order(input=...)` を直接呼ぶ。

### 2.8 このリポジトリだけの役割名

一般の Django 解説に出てこない分割がある。

```text
読み取り
  画面 → API client → View → Selector → Model（テーブル）

更新・副作用
  画面 → API client → View → Service → Model（テーブル）
```

- **Selector** … 読むだけ。在庫を減らさない
- **Service** … 書く・副作用。注文作成、在庫減、ステータス変更
- **Serializer** … HTTP の入口と出口の形。ORM を呼ばない
- **Validator** … 値の組み合わせ（ソケット一致など）。DB を見ない

迷ったら「今見ている関数は、この経路のどこか」を先に決める。View の中で `Part.objects.filter(...)` を探しても出てこない。それは Selector か Service にある。

---

## 3. 開き方の基本

### 3.1 画面から追うか、API から追うか

やりたいことに応じて入口を選ぶ。

| 知りたいこと | 最初に開く場所 |
|---|---|
| この画面は何をしているか | `frontend/src/routes/` のその URL に対応する `+page.svelte` |
| 画面はいつデータを取るか | 同じディレクトリの `+page.ts`（なければ page のクリック処理） |
| HTTP のパスと型 | `frontend/src/lib/api/` |
| Django のどの関数が受けるか | `backend/application/api/urls.py` |
| 入力の形だけか、業務か | View が呼ぶ Serializer か、Service / Selector |
| テーブルの列 | `backend/application/models/` |
| 失敗時の文言 | backend は `errors/` と `messages/`、画面は `frontend/src/lib/messages/` |

「画面のボタンを押したら何が起きるか」は上から下へ追う。  
「この API は誰が呼んでいるか」は `urls.py` の path をコピーして frontend を検索する。

### 3.2 ファイル名が地図になっている

このリポジトリは、扱う対象（resource）の名前でファイルを揃えている。`order`（注文）を追うなら、次をまとめて開く。

```text
仕様の resource     order
画面                frontend/src/routes/orders/
API client          frontend/src/lib/api/orders.ts
型                  frontend/src/lib/types/order.ts
画面文言            frontend/src/lib/messages/order.ts
View                backend/application/api/views/order.py
Serializer          backend/application/api/serializers/order.py
Selector            backend/application/selectors/order.py
Service             backend/application/services/order.py
Model               backend/application/models/order.py
                    backend/application/models/order_line.py
Error               backend/application/errors/order.py
Message             backend/application/messages/order.py
Test                backend/application/tests/test_order_service.py
                    backend/application/tests/test_order_api.py
```

スタッフ用は同じ対象の前に `staff` が付く。

```text
frontend/src/routes/staff/orders/
frontend/src/lib/api/staffOrders.ts
backend/application/api/views/staff_order.py
```

顧客の注文読み取りは `get_order_for_user`、スタッフは `get_order`。所有者で絞るかどうかが関数名に出ている。

`utils.py` や `helpers.ts` はこのリポジトリに無い。責務の分からない置き場を探して時間を使わない。

---

## 4. 画面 URL とファイルの対応

| ブラウザの URL | ファイル |
|---|---|
| すべての画面の共通枠 | `frontend/src/routes/+layout.ts` と `+layout.svelte` |
| `load` 失敗の共通画面 | `frontend/src/routes/+error.svelte` |
| `/` | `frontend/src/routes/+page.ts` と `+page.svelte` |
| `/login` | `frontend/src/routes/login/+page.svelte` |
| `/register` | `frontend/src/routes/register/+page.svelte` |
| `/configure` | `frontend/src/routes/configure/+page.ts` と `+page.svelte` |
| `/checkout` | `frontend/src/routes/checkout/+page.ts` と `+page.svelte` |
| `/orders` | `frontend/src/routes/orders/+page.ts` と `+page.svelte` |
| `/orders/（UUID）` | `frontend/src/routes/orders/[uuid]/+page.ts` と `+page.svelte` |
| `/staff/parts` | `frontend/src/routes/staff/parts/+page.ts` と `+page.svelte` |
| `/staff/parts/new` | `frontend/src/routes/staff/parts/new/+page.svelte` |
| `/staff/parts/（数値）/edit` | `frontend/src/routes/staff/parts/[id]/edit/` |
| `/staff/orders` | `frontend/src/routes/staff/orders/+page.ts` と `+page.svelte` |
| `/staff/orders/（UUID）` | `frontend/src/routes/staff/orders/[uuid]/` |

`[uuid]` と `[id]` は URL の可変部分である。`+page.ts` の `params.uuid` / `params.id` で取り出す。UUID は注文の公開番号（`public_id`）。`id` はパーツの内部番号。

同じディレクトリに置いてあるが URL にならないファイルもある。

- `configure/CategoryRail.svelte` と `PartCard.svelte` … 構成画面専用。他画面では使わない
- `staff/parts/PartForm.svelte` など … スタッフのパーツ画面専用

再利用する部品だけが `frontend/src/lib/components/` にある。`AppHeader.svelte`、`PartSummaryList.svelte`、`OrderStatusText.svelte` など。これらはサーバへ取りに行かない。親の page または layout が取ったデータと、押されたときに呼ぶ関数を引数（props）で受け取る。ログアウトの HTTP は layout が呼び、ヘッダは `onlogout` を受け取るだけである。

---

## 5. 1つの画面を開いたときに起きる順

例として `/configure`（構成を選ぶ画面）を開く。

```text
1. +layout.ts の load
      CSRF の印を取り、今のユーザーを取る
      未ログインなら /login へ
      ログイン済みなら currentUserState を埋める
2. +layout.svelte
      ログイン済みならヘッダとフッタを出す
      ログアウトと、あとから来た 401 の復旧を登録する
      子ページを描画する
3. configure/+page.ts の load
      listParts() で掲載中パーツを全部取る
      失敗は throwLoadFailure で +error.svelte へ
      戻り値 { parts } が page の data になる
4. configure/+page.svelte
      data.parts を表示する
      クリックで「まだ保存していない選択」（orderDraftState）を更新する
```

ポイントは次の3つ。

- **データ取得の起点は `load` か、ユーザーのクリックである。** 値が変わったから裏で自動取得、という書き方はしない。
- **page はブラウザ標準の `fetch` を直接書かない。** 必ず `lib/api/` の関数を呼ぶ。
- **最初の読み取りもブラウザ上で走る。** サーバが HTML にデータを埋め込まない。

`+page.ts` が返すオブジェクトは、同じ画面の `+page.svelte` で `let { data } = $props()` として受け取る。`configure/+page.ts` が `{ parts }` を返せば、page は `data.parts` を使う。

---

## 6. 読み取りを1本、ファイル順に追う

題材は「構成画面がパーツ一覧を出す」。サーバの約束は `GET /api/v1/parts`（掲載中パーツを読む）。

### 6.1 画面が呼ぶ

`frontend/src/routes/configure/+page.ts`

```ts
export const load: PageLoad = async () => {
	try {
		return { parts: await listParts() };
	} catch (error) {
		throwLoadFailure(error);
	}
};
```

画面を出す前に `listParts` を待ち、結果を `parts` という名前で page に渡す。失敗は `frontend/src/lib/errors/loadFailure.ts` が HTTP の失敗に写し、`+error.svelte` が出る。`listParts` の定義へ進む。

### 6.2 API client

`frontend/src/lib/api/parts.ts`

```ts
export async function listParts(category?: PartCategory): Promise<PartOutput[]> {
	const query = category === undefined ? '' : `?category=${category}`;
	return apiGet<PartOutput[]>(`/api/v1/parts${query}`);
}
```

ここでは業務判断をしない。パスと戻り型だけをサーバの約束に合わせる。`PartOutput` は `frontend/src/lib/types/part.ts` にあり、backend の出力 Serializer と同じフィールドである。`category?` の `?` は「省略できる引数」。

`apiGet` は `frontend/src/lib/api/client.ts` にある共通の送り役である。やっていることは次だけ。

- ログイン cookie を付ける
- CSRF の印をヘッダに載せる
- 失敗 JSON を `ApiError` という例外に変える
- 成功 JSON をそのまま返す

page や部品に同じ送信処理は書かない。cookie と失敗の解釈を1か所に閉じるため。

### 6.3 Django の入口

URL の振り分けは2段である。

1. `backend/config/urls.py` … `/api/v1/` で始まるものをアプリ側へ渡す
2. `backend/application/api/urls.py` … 具体的なパス

```python
path("parts", part_list, name="part_list"),
path("parts/<int:part_id>", part_show, name="part_show"),
```

`GET /api/v1/parts` は `part_list`。定義は `backend/application/api/views/part.py`。  
`<int:part_id>` は「ここに整数が来たら `part_id` という引数にする」。

### 6.4 View は組み立てだけ

```python
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def part_list(request: Request) -> Response:
    query = PartListQuerySerializer(data=request.query_params)
    query.is_valid(raise_exception=True)
    parts = list_listed_parts(
        filter=PartFilter(category=query.validated_data.get("category"))
    )
    output = PartOutputSerializer(
        [part_output_payload(part=part) for part in parts],
        many=True,
    )
    return Response(output.data)
```

上から読むと次である。

1. GET 以外は受けない。ログインしていない人はここで拒否
2. URL の `?category=cpu` のような付属情報を Serializer で検査する
3. 読み取り役 `list_listed_parts` に渡す
4. `part_output_payload`（`api/serializers/part.py`）で JSON 用の辞書にし、出力 Serializer で形を整えて返す

| View がやる | View がやらない |
|---|---|
| クエリを Serializer で受け取る | `Part.objects.filter(...)`（SQL 相当） |
| Selector を呼ぶ | 在庫や掲載の業務判定 |
| 出力を JSON にする | テーブル行オブジェクトをそのまま返す |

未ログインの拒否のあと、共通の失敗処理（§11）が `authentication.required` という code にする。

### 6.5 Selector がテーブルを読む

`backend/application/selectors/part.py` の `list_listed_parts`。

```python
def list_listed_parts(*, filter: PartFilter) -> QuerySet[Part]:
    queryset = Part.objects.filter(is_listed=True).order_by("category", "name")
    if filter.category is not None:
        queryset = queryset.filter(category=filter.category)
    return queryset
```

`QuerySet` は「まだ実行しきっていない検索」である。`is_listed=True` は掲載中だけ。並びはカテゴリ、名前。

スタッフ向けは別関数 `list_parts` で、未掲載を含み、並びがカテゴリ、SKU になる。同じテーブルでも関数を分けている。「顧客なのに未掲載が出る」を追うときは、View がどちらを呼んでいるかを見る。

1件取得で行が無いときは `None`（Python の「値なし」）を返さない。`PartNotFoundError` を投げる。これが HTTP 404 と `part.not_found` になる。

### 6.6 画面に戻る

JSON が `data.parts` として `configure/+page.svelte` に入る。page は選んでいるカテゴリで絞って `PartCard` に渡す。`PartCard` は表示と「選ばれた」通知だけである。選択の正は、まだ保存していない画面メモリ（§10）のパーツ番号。

---

## 7. 更新を1本、ファイル順に追う

題材は「レジで決済完了を押す」。仕様上、保存前の構成は画面のメモリが正で、押した瞬間にだけサーバが注文を作る。

### 7.1 page のクリック処理

`frontend/src/routes/checkout/+page.svelte` の `pay`。

```text
1. createOrder({ part_ids, ...shipping })     POST /api/v1/orders   注文を作る
2. 返った public_id を createdPublicId に残す
3. getOrder(createdPublicId)                  GET  /api/v1/orders/{uuid}  作り直さず読み直す
4. setSyncedOrder(order)                      確認画面の正を、今読んだ応答にする
5. resetDraft()                               未保存の選択を空にする
6. goto(/orders/{uuid})                       確認画面へ移る
```

失敗したら途中で止めて文言を出し、未保存の選択は残す。成功の途中で画面を空にしない。

POST が通ったあと GET だけが失敗した場合、`createdPublicId` が残る。次に決済ボタンを押しても POST は繰り返さない。GET の再試行だけをする。同じドラフトで二重に注文を作らないため。

`createOrder` の戻りは `{ public_id }`（公開番号）だけである。行や合計は含まれない。金額の正は直後の読み直しである。作った直後のテーブル行を画面に渡して書き換えさせない、という置き方である。

### 7.2 API client

`frontend/src/lib/api/orders.ts`

- `createOrder` → `POST /api/v1/orders`
- `getOrder` → `GET /api/v1/orders/{publicId}`
- `listOrders` → `GET /api/v1/orders`

入力の型 `CreateOrderInput` は `frontend/src/lib/types/order.ts` にあり、backend の入力 Serializer と同じキーである。`total_price` は TypeScript では文字列。サーバの金額型（小数なしの円）が JSON では `"198000"` のように来る。

### 7.3 View が Service を呼ぶ

`backend/application/api/urls.py` では `orders` が `order_list` 1本である。`backend/application/api/views/order.py` の中で、読む（GET）と作る（POST）を分けている。

```python
@api_view(["GET", "POST"])
def order_list(request):
    if request.method == "POST":
        return order_create(request)
    # GET は Selector
```

作る側の順はいつも同じである。

```text
入力 Serializer で形を検証（郵便番号が7桁か、など）
    → create_order(input=...)          業務
    → 出力 Serializer で public_id だけ返す（成功 201）
```

Serializer はテーブルを触らない。郵便番号の桁数のような **入力の形** だけを見る。在庫やソケット一致は Service の仕事。

今ログインしている人の番号は `authenticated_user_id(request)`（`api/views/auth_user.py`）で取り、Service への入力に載せる。HTTP の request そのものを Service に渡さない。

### 7.4 Service が業務の正

`backend/application/services/order.py` の `create_order`。

```text
途中失敗なら全部なかったことにする（transaction.atomic）
1. パーツ番号を一意化し、番号の小さい順に行をロックして取る
2. 件数が足りなければ part.not_found
3. 元の番号列に同じ ID が2回あれば configuration.duplicate_category（消して通さない）
4. 未掲載なら order.part_unlisted
5. 在庫 0 なら order.insufficient_stock
6. 配件の組み合わせを Validator で見る
7. 今の単価で合計する（画面が送った金額は見ない）
8. 在庫を 1 減らし、注文と注文明細を作る（状態は paid）
9. 公開番号だけ返す
```

ここで覚えることは3つ。

- **更新 Service は Selector を呼ばない。** 必要な行は自分で取る。プレビュー用の読み取りと決済は、同じ Validator をそれぞれ呼ぶ。互いに呼ばない。
- **ひとまとまりの更新は、途中失敗で残さない。** 注文だけできて在庫が減らない、ということが無い。
- **既存の行を変えるときは、先にロックし、どの列を書くかを明示する。** 複数パーツをロックする順は番号の小さい方からで固定。同時に2人が買う衝突を避けるため。

スタッフの準備・発送・キャンセルも同じファイルの `prepare_order` / `ship_order` / `cancel_order` である。外から呼ぶ関数は「やりたいこと」ごとに1つ。その関数同士は呼び合わない。

### 7.5 確認画面は読み直しが正

`frontend/src/routes/orders/[uuid]/+page.ts` は、開くたびに `getOrder(params.uuid)` する。成功したら確認用の画面メモリに置く。他人の番号や存在しない番号は `order.not_found` で、枠組み標準の「ページが無い」画面にはせず、同じ画面で「見つからない」と出す。

確認画面は保存済みの注文だけを見る。未保存の選択は見ない。決済の前と後で、何を正とするかが切り替わる（§10）。

---

## 8. ログインを1本追う

題材は `/login` で送信する。

### 8.1 画面

`frontend/src/routes/login/+page.svelte` の送信処理。

```text
createSession({ email, password })
  → 画面側の「今のユーザー」を更新する
  → /configure へ移る
```

見た目の枠は `AuthPanel`（`lib/components/`）。サーバへは行かない。

### 8.2 API と View

- 画面側: `frontend/src/lib/api/sessions.ts` の `createSession` → `POST /api/v1/sessions`
- サーバ側: `backend/application/api/views/session.py` の `session_create`

認証では View の分担が少し特殊である。

```text
Serializer でメールとパスワードの形を見る
  → create_session（パスワード照合だけ。cookie は触らない）
  → login(request, user)     ← 覚え書き cookie を付けるのは View
  → 今のユーザー情報を返す
```

Service が cookie を付けない。HTTP の「ログイン状態をブラウザに残す」は境界（View）の仕事で、「このパスワードは正しいか」は Service の仕事。

`create_session`（`services/session.py`）は、整えたメールを Django 標準ユーザーの名前欄として探す。無い、パスワードが違う、無効、のどれも同じ失敗にする。「メールが無い」と「パスワードが違う」を分けない（メールの存在を外に漏らさない）。

登録は対になる `POST /api/v1/registrations`。`create_registration` は、整えたメールが名前欄またはメール欄に既にあれば拒否し、Django 既定のパスワード検証も通す。成功時も cookie を付け、同じ「今のユーザー」形を返す。

ログアウトは `DELETE /api/v1/sessions`。呼ぶのは `+layout.svelte` である。ヘッダは `onlogout` を受け取るだけで、API client は呼ばない。サーバ側の切断が失敗しても、画面側のユーザー・未保存選択・保存済み注文を全部空にして `/login` へ行く。

---

## 9. Django 側のフォルダ（サーバを開くとき）

業務アプリは `backend/application/` 1つだけである。`backend/config/` は起動設定と一番外側の URL である。

| フォルダ | 開く理由 |
|---|---|
| `api/urls.py` | パスの目次 |
| `api/views/` | HTTP の入口。次に誰を呼ぶか |
| `api/serializers/` | JSON の入口と出口。出力用の辞書化もここ |
| `api/authentication.py` | 未ログインの更新でも CSRF を見る |
| `api/exception_handler.py` | 失敗を決まった JSON にする |
| `services/` | 更新の本体 |
| `selectors/` | 読み取りの本体 |
| `validators/` | DB を見ない判定 |
| `models/` | テーブル |
| `errors/` | 失敗の名前（code） |
| `messages/` | 失敗の日本語（サーバ側） |
| `tests/` | 仕様を英文のテスト名で読める |
| `management/commands/seed_catalog.py` | 開発用の初期データ |

`models.py` という1ファイルは無い。`models/part.py`、`models/order.py`、`models/order_line.py` に分かれている。

ユーザーは Django 標準の `User` を使う。独自の User テーブルは無い。識別はメール。同じ文字列を名前欄にも入れる。

---

## 10. 画面をまたぐ状態

1画面の中だけの変数は、その `+page.svelte` の `$state` に置く。画面をまたいで残すものだけが `frontend/src/lib/states/` にある。状態そのものは次の3つだけ。空にする処理は `clientSession.ts` の `clearClientSession` にまとまっている。

| ファイル | 中身 | 誰が書くか | どれを正とするか |
|---|---|---|---|
| `currentUserState.svelte.ts` | 今のユーザー、または未ログイン | 共通 layout、ログイン、登録、ログアウト | サーバの session が正。これは画面用の写し |
| `orderDraftState.svelte.ts` | まだ保存していない選択と配送先 | 構成画面とレジ | **未保存のあいだだけ正。** メモリだけ。再読み込みで消える |
| `syncedOrderState.svelte.ts` | 保存済み注文 | 決済成功と注文詳細を開いたとき | **保存後の正。** 中身はサーバ応答 |

`.svelte.ts` は、「画面ファイルでなくても `$state` を使ってよい」という Svelte の拡張子である。

構成画面で CPU を選ぶと `selectPart('cpu', 番号)` が走る。レジに行って戻っても残る。別タブや再読み込みでは残らない。ブラウザに永続保存しない。

価格の表示は、page が取ったパーツ一覧から番号で引く。これは見せ方である。決済金額は Service が **今の** 単価で計算する。画面の合計を信用しない。

必須6カテゴリが揃っているかの判定も見せ方である。アドレス欄にレジの URL を直接入れても、サーバ側の Validator が不足を拒否する。

---

## 11. エラーを追う

失敗は次の一本道になる。

```text
Service / Selector / Validator が、名前付きの例外を投げる
    → 共通の失敗処理が決まった JSON にする
    → API client が ApiError にする
    → page が日本語に写して出す
```

### 11.1 サーバの失敗の名前と文言

例: 他人の注文番号を開く。

1. `get_order_for_user` は所有者でも絞り込む。無ければ `OrderNotFoundError`
2. class は `backend/application/errors/order.py`。名前は `order.not_found`、HTTP は 404
3. `backend/application/api/exception_handler.py` が、決まった JSON にする

サーバ側の日本語は `backend/application/messages/` から名前で引く。View や Service に文言を直書きしない。

「無い」と「あるが今は操作できない」は別の名前である。注文が無いのは `order.not_found`。発送済みをキャンセルするのは `order.invalid_status_transition`。読み取りが「キャンセル不可」を「無い」に見せかけない。

### 11.2 画面の写し

`frontend/src/lib/errors/apiError.ts` に、仕様で決まった名前の一覧がある。知らない名前は `unknown` にする。画面側が新しい失敗名を作らない。

画面に出す日本語の正本は `frontend/src/lib/messages/` である。`errorDisplay.ts` が名前を文言に写す。サーバ JSON の `message` は画面では使わない。

ボタンや見出しの固定文言は `lib/messages/ui.ts`。部品に日本語を直書きしない。文言を直したいときは、まず `lib/messages/` を開く。

`+page.ts` の `load` が失敗したとき、注文詳細の `order.not_found` のように page が自分で出す場合を除き、`throwLoadFailure` が `+error.svelte` へ渡す。共通画面は名前を日本語に写し、401 ならログインへ、それ以外なら構成へ戻す導線を出す。

### 11.3 認証まわり

| 状況 | HTTP | 名前 |
|---|---|---|
| 未ログインで、ログインが必要な API | 401 | `authentication.required` |
| 顧客がスタッフ用 API に来た | 403 | `authentication.staff_required` |
| メールまたはパスワード違い | 401 | `authentication.invalid_credentials` |
| 郵便番号の桁が違うなど | 400 | `input.invalid`（どこが悪いかは `details`） |
| CSRF の印が無い・違う | 403 | `input.invalid` |

画面でスタッフメニューを隠すことと、API が拒否することは別である。スタッフでない人が `/staff/parts` を開くと、共通 layout が構成画面へ飛ばす。それでも API を直接叩けばサーバが 403 を返す。画面で隠したことが権限の代わりにはならない。

初期化のあと、決済など別の API が `authentication.required` の 401 を返した場合、`lib/api/client.ts` が layout に知らせる。layout は `clearClientSession` して `/login` へ移す。画面ごとに同じ復旧を書かない。

---

## 12. 配件の一致判定だけ別扱い

CPU とマザーボードのソケットが合うか、などは、テーブルを書かない読み取りでも、「検索結果の行の列」としては返せない。複数パーツを合成した判定だからである。仕様がこの例外を明示している。

- プレビュー（書く前の確認）: `POST /api/v1/configurations/evaluations`  
  View → 読み取り役 → 判定結果のかたまり
- 決済: 注文作成の中で同じ Validator を呼ぶ

プレビューの読み取り役は、受け取った番号列の重複を消さない。同じ ID が2回あれば Validator が `configuration.duplicate_category` を返す。決済はロック用に番号を一意化したあと、元の列に重複があれば同じ名前で拒否する。

Validator 本体は `backend/application/validators/pc_configuration.py`。テーブルを見ない。カテゴリと属性の値だけを受け、問題のリストを返す。リストが空なら成功。

構成画面の「一致性を確認」と、レジへ進む直前だけがプレビューを呼ぶ。入力のたびに自動では呼ばない。呼び始めるとき、前回の成功結果はいったん捨てる。失敗したあとに古い「一致している」が残ってレジへ進まないため。

---

## 13. 対応早見表

画面や API から実装へ飛ぶとき使う。関数名の正は仕様 `docs/bto_pc_store.md` のモジュール一覧。

| やりたいこと | 画面 | frontend の関数 | HTTP | View | その先 |
|---|---|---|---|---|---|
| CSRF の印 | 共通 layout | `ensureCsrfCookie` | `GET /api/v1/csrf` | `csrf_show` | cookie を置くだけ |
| 今のユーザー | 共通 layout | `getCurrentUser` | `GET /api/v1/current-user` | `current_user_show` | request 上のユーザー |
| 登録 | `/register` | `createRegistration` | `POST /api/v1/registrations` | `registration_create` | `create_registration` |
| ログイン | `/login` | `createSession` | `POST /api/v1/sessions` | `session_create` | `create_session` |
| ログアウト | 共通 layout | `deleteSession` | `DELETE /api/v1/sessions` | `session_delete` | cookie を消す |
| 掲載パーツ一覧 | `/configure` | `listParts` | `GET /api/v1/parts` | `part_list` | `list_listed_parts` |
| 一致性プレビュー | 構成・レジ | `evaluateConfiguration` | `POST /api/v1/configurations/evaluations` | `configuration_evaluate` | `evaluate_pc_configuration` |
| 決済 | `/checkout` | `createOrder` | `POST /api/v1/orders` | `order_create` | `create_order` |
| 自分の注文詳細 | `/orders/[uuid]` | `getOrder` | `GET /api/v1/orders/{uuid}` | `order_show` | `get_order_for_user` |
| 自分の履歴 | `/orders` | `listOrders` | `GET /api/v1/orders` | `order_list` | `list_orders_for_user` |
| スタッフがパーツ作成 | `/staff/parts/new` | `createStaffPart` | `POST /api/v1/staff/parts` | `staff_part_create` | `create_part` |
| スタッフがパーツ更新 | `/staff/parts/[id]/edit` | `updateStaffPart` | `PATCH /api/v1/staff/parts/{id}` | `staff_part_update` | `update_part` |
| 準備する | スタッフ注文詳細 | `prepareStaffOrder` | `POST .../prepare` | `staff_order_prepare` | `prepare_order` |
| 発送する | 同上 | `shipStaffOrder` | `POST .../ship` | `staff_order_ship` | `ship_order` |
| キャンセル | 同上 | `cancelStaffOrder` | `POST .../cancel` | `staff_order_cancel` | `cancel_order` |

顧客向け注文 URL の番号は、テーブル内部の連番ではなく公開番号（UUID）である。パーツはカタログなので顧客にも内部番号を出す。未保存の選択が番号を持つため。

---

## 14. よくある迷い方

### 「View に SQL が無い」

それが正しい。読み取りは Selector、更新は Service。View から `objects.filter` を探さない。

### 「Model に `submit()` が無い」

テーブル定義のファイルは、列の定義と、自分の列だけから分かる判定に限る。保存の本体は Service。注文を作る処理は `services/order.py`。

### 「Serializer がテーブルを知らない」

一般の Django 解説に出てくる「テーブルから自動で JSON を作る Serializer」は使わない。入力用と出力用を別の class で手書きする。`CreateOrderInputSerializer` と `OrderOutputSerializer` を見比べると役割が分かる。

### 「部品から API を追えない」

`PartCard` や `PartSummaryList`、`AppHeader` はデータを取らない。親 page または layout が渡した値と、「押されたとき呼ぶ関数」を見る。API を追う入口は page、`+page.ts`、または `+layout.svelte` である。

### 「同じ判定が画面とサーバにある」

画面の必須チェックや、ボタンを押せなくすることは見せ方である。最終判定はサーバ。画面だけ直して「直った」と思わない。Service のテストを見る。

### 「プレビューの読み取りと決済が似ている」

意図的である。読み取り役と更新役が呼び合わない置き方を守るため。共通なのは、DB を見ない Validator だけ。

### 「`GET` と `POST` が同じ View 関数」

注文一覧とスタッフのパーツ一覧がそうなっている。関数の先頭で動詞を分けている。URL の目次にパスが1本しかなくても、中を読む。

### 「管理画面（Django admin）で直したくなる」

この製品の業務更新は、Svelte のスタッフ画面だけである。`admin.py` は中を見る用。管理画面から在庫を変える経路は仕様に無い。

### 「ネットの Svelte / Django の書き方と違う」

そのことが多い。このリポジトリは再現性のために置き場を固定している。一般解説より `docs/coding_style.md` を正にする。

---

## 15. 自分で追う練習

エディタの「定義へ移動」（関数名を辿る機能）を使い、次を最後までたどる。途中で View がテーブルを直接触っていないこと、page が送信を直書きしていないことを確認する。

1. **未掲載パーツが顧客一覧に出ない**  
   `list_listed_parts` の掲載中だけ、まで行く。スタッフ一覧 `list_parts` との差を見る。初期データの `CPU-HIDDEN` が題材。

2. **ソケットが合わない構成で決済できない**  
   構成画面の確認 → プレビュー API → 読み取り役 → Validator。同じ構成で決済すると、注文作成 → 同じ Validator → 先頭の問題の名前で失敗。

3. **他人の注文番号**  
   `get_order_for_user` が本人でも絞り込む。無い失敗 → 404 → 注文詳細画面の「見つからない」。

4. **キャンセルで在庫が戻る**  
   スタッフ詳細のボタン → 画面の関数 → View → `cancel_order` → 在庫を戻す処理。発送済みでは「今の状態ではできない」。

5. **再読み込みで未保存の選択が消える**  
   未保存の状態にブラウザ永続保存が無いこと。共通 layout がそれを復元していないこと。

テストから入ってもよい。仕様の英文がテスト名になっている。

- `test_create_order_rejects_incompatible_socket`
- `test_get_order_for_user_hides_other_users_order`
- `test_cancel_order_restores_stock`
- `test_list_listed_parts_excludes_unlisted`

テストは外から呼ぶ関数を叩く。ファイル内の下請け（名前が `_` で始まるもの）を直接叩かない。まず外の関数名で実装を開く。

---

## 16. 検索の型

リポジトリ全体を検索して足りることが多い。

| 手がかり | 検索例 | 着く場所 |
|---|---|---|
| 画面 URL | `routes/checkout` | page |
| API のパス | `/api/v1/orders` | frontend の API client |
| Django のパス | `staff/orders` | `api/urls.py` |
| やりたいことの関数名 | `create_order` | Service、それを呼ぶ View、画面の `createOrder` |
| 失敗の名前 | `order.not_found` | errors、messages、画面の `apiError.ts`、page の分岐 |
| テーブル | `class Order` | `models/order.py` |
| 画面文言 | `uiMessages.pay` | `lib/messages/ui.ts` |
| 画面をまたぐ状態 | `orderDraftState` | 書き手（構成・レジ）と読み手 |

関数名の規則も検索に使える。

- 1件読む: `get_...` / `getOrder`
- 一覧: `list_...` / `listOrders`
- 更新: `create_order` / `createOrder`、`prepare_order` / `prepareStaffOrder`

---

## 17. 最初に読む順番（初回）

Svelte も Django も初めてなら、次の順で開く。§2 を読んでからの方が早い。

1. `docs/bto_pc_store.md` の冒頭（何の店か、画面の順）
2. この文書の §1 と §2（他言語からの地図と用語）
3. `frontend/src/routes/+layout.ts`（ログインの入口）
4. `frontend/src/lib/api/client.ts`（画面がサーバへ送る共通部分）
5. `backend/application/api/urls.py`（サーバの目次）
6. `configure/+page.ts` から §6 の読み取り
7. `checkout/+page.svelte` の `pay` から §7 の更新
8. `services/order.py` の `create_order`
9. `api/exception_handler.py` と `lib/errors/apiError.ts`

そのあと自分の疑問を §15 の練習に当てる。コードを書き始める前に `docs/coding_style.md` を全文読む。見た目を触るなら続けて `docs/frontend_design.md` を全文読む。
