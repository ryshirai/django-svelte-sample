# BTO PC 注文サイト — 詳細計画

空の Django DRF + Svelte 骨格の上に、ログイン必須の BTO PC 店舗を作る。決済は模擬ボタン。カタログ・在庫はスタッフ用 Svelte 画面で管理する。

この文書が実装の製品仕様になる。承認後、本文を `docs/bto_pc_store.md` に保存してからコードを書く。規約は `docs/coding_style.md` と `docs/frontend_design.md`。製品仕様は規約ファイルへ混ぜない。

---

## 1. 目的と正本

顧客はログイン後、掲載中パーツから 1 台分の構成を選び、配送先を入れて「決済完了」する。その瞬間にだけ backend が注文を保存する。保存前の構成はフロントのメモリだけが正。保存後と UUID 再表示は API 応答が正。

スタッフはパーツと在庫を Svelte 画面から更新し、注文の準備・発送・キャンセルを行う。Django admin からの業務更新はしない。

### 1.1 確定要件

- 題材は BTO PC。カタログ管理、在庫、配件一致性、配送先、注文履歴を持つ。
- 未保存ドラフトは画面遷移で残る。リロード・新タブは新セッション。UUID がなければ空のドラフトから始める。
- 決済ボタンで `POST /orders` → 続けて `GET /orders/{uuid}` → フロント state を API 応答で置き換える。
- 新規セッションで `/orders/{uuid}` を開いたら backend から読み、フロントへ返す。
- ログイン必須。注文は作成者のみ読める。他人の UUID は `order.not_found`。
- スタッフは `User.is_staff`。決済プロバイダは使わない。

### 1.2 規約との関係

プロダクト要件が優先する例外は次だけ。

- 未保存ドラフトは client state が正（規約 22.4 の例外）。保存後は例外解除。
- 構成プレビューは QuerySet にならない読み取りなので、Selector が immutable DTO を返す（規約 10.2 の明示例外）。
- 価格・在庫・一致性・所有権の最終判定は backend。フロントの検証は必須・形式の UX だけ。

### 1.3 やらないこと

本物決済、メール、送料・税の自動計算、住所帳、ソフトデリート、独自 User、状態管理ライブラリ、Svelte 4 store、1 カテゴリ複数個、未保存ドラフトの Web Storage、支払後の顧客編集、ゲスト購入、ページング、画像アップロード。

`unit_price` は税込円。送料は 0。小数なし。

---

## 2. 画面フロー

```text
未ログイン
  /login  ⇄  /register
       │
       │ 成功（session cookie）
       v
  /                     ログイン済みなら /configure へ
  /configure            ドラフト編集。GET /parts
  /checkout             確認 + 配送先 + 決済完了
       │
       │ POST /orders → GET /orders/{uuid}
       v
  /orders/{uuid}        syncedOrderState を正として表示
  /orders               自分の履歴。行クリックで詳細

スタッフ（is_staff）
  /staff/parts
  /staff/parts/new
  /staff/parts/{id}/edit
  /staff/orders
  /staff/orders/{uuid}
```

### 2.1 遷移規則

| 条件 | 動作 |
|---|---|
| 未ログインで顧客・スタッフ画面 | `/login` へ。戻り先は持たない |
| ログイン済みで `/login` `/register` `/` | `/configure` へ |
| 非スタッフで `/staff/*` | `/configure` へ（API は 403 相当の staff 拒否にしない。画面で隠す。API は `IsAdminUser` で 403） |
| `/checkout` で必須 6 カテゴリが未選択 | フロントはボタンを非活性。直 URL でも決済は backend が拒否 |
| 決済成功 | ドラフトを空にし `/orders/{uuid}` へ |
| `/orders/{uuid}` で not_found | 注文が見つからない旨を出し、履歴へ戻るリンク |

`$effect` で fetch しない。layout の明示的な初期化と、各 page の `load` / クリックだけが読み書きの起点。

---

## 3. 認証とセッション

Django 標準 `User`。カスタム User は作らない。

| 項目 | 決め |
|---|---|
| 識別子 | email。`User.username` と `User.email` の両方に正規化済み email を入れる |
| 正規化 | 前後空白除去、小文字化 |
| パスワード | 8 文字以上。Django 既定バリデータも適用 |
| session | `SessionAuthentication`。cookie |
| スタッフ | `is_staff=True`。シードで 1 人作る |
| CSRF | `GET /api/v1/csrf` が `ensure_csrf_cookie`。更新系はヘッダ `X-CSRFToken` |
| CORS | `CORS_ALLOW_CREDENTIALS = True` |
| 開発時の同一オリジン | Vite が `/api` を Django へ proxy。ブラウザからは origin が 5173 のまま `/api/v1/...` を呼ぶ |

### 3.1 フロント初期化順（`+layout.svelte` / `+layout.ts`）

1. `GET /api/v1/csrf`
2. `GET /api/v1/current-user`
3. 200 なら `currentUserState` を埋める
4. 401 なら `currentUserState` を空にする（ログイン画面以外は `/login`）

ログアウトは `DELETE /api/v1/sessions` のあと `currentUserState` と `orderDraftState` と `syncedOrderState` を空にし `/login` へ。

---

## 4. データモデル

主キーは `BigAutoField`。共通 BaseModel は作らない。

### 4.1 Part

| フィールド | 型 | 制約 |
|---|---|---|
| `sku` | `CharField(32)` | unique。`^[A-Z0-9-]{3,32}$` |
| `name` | `CharField(120)` | 空不可 |
| `category` | `CharField(16)` | Choice。下表 |
| `unit_price` | `DecimalField(10, 0)` | `>= 1` |
| `stock_quantity` | `PositiveIntegerField` | `>= 0` |
| `is_listed` | `BooleanField` | 既定 `True` |
| `created_at` | `DateTimeField` | `auto_now_add` |
| `updated_at` | `DateTimeField` | `auto_now` |

カテゴリ別属性。使わない列は空文字または `NULL`。整数は `PositiveIntegerField(null=True, blank=True)`。文字列は `CharField(..., blank=True, default="")`。

| category | 必須属性 |
|---|---|
| `cpu` | `socket`, `tdp_watts` |
| `motherboard` | `socket`, `memory_type`, `form_factor`, `memory_slot_count`, `sata_port_count`, `m2_slot_count` |
| `memory` | `memory_type`, `module_count`, `capacity_gb` |
| `storage` | `interface`（`sata` / `m2`） |
| `psu` | `wattage` |
| `case` | `form_factor`, `max_gpu_length_mm`, `max_cooler_height_mm` |
| `gpu` | `length_mm`, `tdp_watts` |
| `cpu_cooler` | `socket`, `height_mm` |

許容値（文字列は小文字固定）:

- `socket`: `am5` / `lga1700`
- `memory_type`: `ddr4` / `ddr5`
- `form_factor`: `atx` / `m_atx` / `itx`
- `interface`: `sata` / `m2`

1 構成につき各カテゴリ最大 1。数量は常に 1。必須カテゴリは `cpu`, `motherboard`, `memory`, `storage`, `psu`, `case`。`gpu` と `cpu_cooler` は任意。

`validate_part_attributes` がカテゴリに対する必須属性と許容値を見る。失敗は `part.invalid_attributes`。`details.fields` にフィールド名配列。

### 4.2 Order

| フィールド | 型 | 制約 |
|---|---|---|
| `public_id` | `UUIDField` | unique。`default=uuid.uuid4`。editable=False |
| `user` | FK `User` | `PROTECT` |
| `status` | `CharField(16)` | `paid` / `preparing` / `shipped` / `cancelled` |
| `recipient_name` | `CharField(64)` | 空不可 |
| `postal_code` | `CharField(7)` | `^[0-9]{7}$`。ハイフンなし |
| `prefecture` | `CharField(8)` | 空不可。都道府県名をそのまま |
| `city` | `CharField(64)` | 空不可 |
| `address_line` | `CharField(128)` | 空不可 |
| `phone` | `CharField(13)` | `^[0-9]{10,11}$`。ハイフンなし |
| `total_price` | `DecimalField(10, 0)` | 行の `unit_price` 合計 |
| `created_at` / `updated_at` | DateTime | 上と同じ |

ドラフト行は作らない。顧客は作成後に中身を変えない。

### 4.3 OrderLine

| フィールド | 型 | 制約 |
|---|---|---|
| `order` | FK Order | `CASCADE` |
| `part` | FK Part | `PROTECT` |
| `category` | 注文時点の category | |
| `sku` / `name` / `unit_price` | スナップショット | |
| `quantity` | `PositiveSmallIntegerField` | 常に 1 |

`UniqueConstraint(order, category)`。表示はスナップショット。`part` は参照とキャンセル時の在庫戻し用。

### 4.4 ステータス

```text
create_order → paid
paid → preparing     prepare_order
preparing → shipped  ship_order
paid|preparing → cancelled  cancel_order
shipped からは動かない
cancelled からは動かない
```

キャンセル時、各行の `part` を ID 昇順で `select_for_update` し `stock_quantity += 1`。

---

## 5. 配件一致性

`validators/pc_configuration.py` の `validate_pc_configuration`。ORM なし。カテゴリ → 属性の mapping を受け、問題のリストを返す。リストが空なら成功。HTTP にするか DTO に載せるかは呼び出し側。

評価対象の属性は Validator 入力の dataclass に明示する。Model を渡さない。

| 条件 | issue code | details |
|---|---|---|
| 必須カテゴリ欠落 | `configuration.incomplete` | `missing_categories` |
| 同一カテゴリが 2 つ | `configuration.duplicate_category` | `category` |
| 未知カテゴリ | `configuration.unknown_category` | `category` |
| CPU.socket != MB.socket | `configuration.socket_mismatch` | `cpu_socket`, `motherboard_socket` |
| Memory.memory_type != MB.memory_type | `configuration.memory_type_mismatch` | 双方の値 |
| Memory.module_count > MB.memory_slot_count | `configuration.memory_slot_exceeded` | 双方の値 |
| Case.form_factor != MB.form_factor | `configuration.form_factor_mismatch` | 双方の値 |
| storage=`m2` かつ m2_slot_count=0 | `configuration.storage_interface_unsupported` | `interface` |
| storage=`sata` かつ sata_port_count=0 | 同上 | |
| GPU ありかつ length > case.max | `configuration.gpu_too_long` | 双方の値 |
| Cooler ありかつ socket != CPU.socket | `configuration.cooler_socket_mismatch` | 双方の値 |
| Cooler ありかつ height > case.max | `configuration.cooler_too_tall` | 双方の値 |
| PSU.wattage < CPU.tdp + GPU.tdp + 100 | `configuration.psu_wattage_insufficient` | `required_wattage`, `psu_wattage` |

GPU なしの TDP は 0。余り 100W は固定。

プレビュー Selector と決済 Service は、各自が Part を読んだあとこの Validator を呼ぶ。互いに呼ばない。

決済時、問題が 1 件でもあれば先頭の code で typed error。`details` に全 issue を入れる。

---

## 6. API 契約

prefix `/api/v1/`。function-based view。Input / Output Serializer 分離。`ModelSerializer` 禁止。成功 JSON に envelope は付けない。失敗だけ次の形。

```json
{
  "error": {
    "code": "order.not_found",
    "message": "...",
    "details": {}
  }
}
```

未ログインの保護エンドポイントは 401、`authentication.required`。スタッフ専用に顧客が来たら 403、`authentication.required` ではなくスタッフ拒否用は **使わない**。403 の code は `authentication.required` と混ぜず、DRF 既定を envelope に載せるために `authentication.staff_required` を定義する。

### 6.1 エンドポイント

| method | path | 認可 | 成功 | View 名 |
|---|---|---|---|---|
| GET | `/csrf` | 不要 | 204 | `csrf_show` |
| POST | `/registrations` | 不要 | 201 `CurrentUserOutput` + session | `registration_create` |
| POST | `/sessions` | 不要 | 200 `CurrentUserOutput` + session | `session_create` |
| DELETE | `/sessions` | ログイン | 204 | `session_delete` |
| GET | `/current-user` | ログイン | 200 | `current_user_show` |
| GET | `/parts` | ログイン | 200 list | `part_list` |
| GET | `/parts/{id}` | ログイン | 200 | `part_show` |
| GET | `/staff/parts` | スタッフ | 200 list（未掲載含む） | `staff_part_list` |
| GET | `/staff/parts/{id}` | スタッフ | 200 | `staff_part_show` |
| POST | `/staff/parts` | スタッフ | 201 | `staff_part_create` |
| PATCH | `/staff/parts/{id}` | スタッフ | 200 | `staff_part_update` |
| POST | `/configurations/evaluations` | ログイン | 200 DTO | `configuration_evaluate` |
| POST | `/orders` | ログイン | 201 `{ "public_id": "..." }` のみ | `order_create` |
| GET | `/orders` | ログイン | 200 list | `order_list` |
| GET | `/orders/{uuid}` | ログイン | 200 detail | `order_show` |
| GET | `/staff/orders` | スタッフ | 200 list | `staff_order_list` |
| GET | `/staff/orders/{uuid}` | スタッフ | 200 detail | `staff_order_show` |
| POST | `/staff/orders/{uuid}/prepare` | スタッフ | 204 | `staff_order_prepare` |
| POST | `/staff/orders/{uuid}/ship` | スタッフ | 204 | `staff_order_ship` |
| POST | `/staff/orders/{uuid}/cancel` | スタッフ | 204 | `staff_order_cancel` |

`{id}` は内部 BigAutoField。`{uuid}` は `public_id`。顧客向け URL に内部 PK を出さない。パーツはカタログなので顧客にも内部 id を出す（ドラフトが id を持つため）。

一覧にページングは付けない。並び:

- 顧客パーツ: `category`, `name`
- スタッフパーツ: `category`, `sku`
- 注文: `created_at` 降順

`GET /parts` は `is_listed=true` のみ。`?category=cpu` を任意フィルタ。未掲載の `GET /parts/{id}` は `part.not_found`。

### 6.2 JSON

**CurrentUserOutput**

```json
{ "id": 1, "email": "user@example.com", "is_staff": false }
```

**CreateRegistrationInput / CreateSessionInput**

```json
{ "email": "user@example.com", "password": "password1" }
```

**PartOutput**（顧客・スタッフ共通形。スタッフも同じフィールド）

```json
{
  "id": 10,
  "sku": "CPU-AM5-7600",
  "name": "Ryzen 5 7600",
  "category": "cpu",
  "unit_price": "24800",
  "stock_quantity": 5,
  "is_listed": true,
  "socket": "am5",
  "tdp_watts": 65,
  "memory_type": "",
  "form_factor": "",
  "memory_slot_count": null,
  "sata_port_count": null,
  "m2_slot_count": null,
  "module_count": null,
  "capacity_gb": null,
  "length_mm": null,
  "interface": "",
  "wattage": null,
  "max_gpu_length_mm": null,
  "max_cooler_height_mm": null,
  "height_mm": null
}
```

使わない属性は空文字または `null`。フロントはカテゴリを見て読む。Decimal は文字列。

**CreatePartInput / UpdatePartInput**

作成は PartOutput から `id` を除いた全フィールド必須（使わない属性は空 / null）。更新は PATCH。送ったフィールドだけ変える。`sku` は作成後も変更可。重複は `part.sku_already_used`。

**EvaluateConfigurationInput**

```json
{ "part_ids": [10, 11, 12, 13, 14, 15] }
```

重複 ID は `configuration.duplicate_category` または入力エラー。存在しない ID は `part.not_found`。

**ConfigurationEvaluationOutput**

```json
{
  "is_valid": false,
  "issues": [
    {
      "code": "configuration.socket_mismatch",
      "details": { "cpu_socket": "am5", "motherboard_socket": "lga1700" }
    }
  ]
}
```

書き込みなし。存在しない Part は 404 相当の `part.not_found`。未掲載 Part はプレビューでも `order.part_unlisted`。

**CreateOrderInput**

```json
{
  "part_ids": [10, 11, 12, 13, 14, 15],
  "recipient_name": "山田太郎",
  "postal_code": "1600022",
  "prefecture": "東京都",
  "city": "新宿区",
  "address_line": "新宿1-1-1",
  "phone": "09012345678"
}
```

**CreateOrderOutput**

```json
{ "public_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6" }
```

フロントは直後に `getOrder(public_id)` する。View は Model を返して mutation させない。

**OrderListItemOutput**

```json
{
  "public_id": "...",
  "status": "paid",
  "total_price": "198000",
  "created_at": "2026-08-13T12:00:00+09:00"
}
```

**OrderOutput**

List のフィールド + `recipient_*` + `phone` + `lines[]`。

**OrderLineOutput**

```json
{
  "category": "cpu",
  "sku": "CPU-AM5-7600",
  "name": "Ryzen 5 7600",
  "unit_price": "24800",
  "quantity": 1
}
```

詳細に内部 `part.id` は出さない。

### 6.3 `create_order`

1. `transaction.atomic`
2. `part_ids` を一意化して昇順で `select_for_update`
3. 件数不一致 → `part.not_found`
4. いずれか `is_listed=False` → `order.part_unlisted`
5. いずれか `stock_quantity < 1` → `order.insufficient_stock`（`details.sku`）
6. 属性を Validator 入力へ写して評価。失敗ならその code
7. 各 Part の **現在の** `unit_price` で合計（入力の金額は見ない）
8. 在庫を 1 減らし `update_fields=["stock_quantity", "updated_at"]`
9. Order `status=paid` と OrderLine を作成
10. `public_id` だけ返す

`prepare_order` / `ship_order` / `cancel_order` も同じ module の public Service。Input は `public_id` のみ。対象を `select_for_update`。不正遷移は `order.invalid_status_transition`。

---

## 7. Error と Message

これ以外の code を実装時に足さない。message は backend `messages/` に日本語で置く。フロントは code を `lib/errors/` で型にし、`lib/messages/` で表示文を持つ。backend の `error.message` をそのまま出してもよいが、画面文言の正本は frontend `lib/messages/`。

| code | HTTP | 画面向け文言 |
|---|---|---|
| `authentication.invalid_credentials` | 401 | メールアドレスまたはパスワードが違います。 |
| `authentication.required` | 401 | ログインしてください。 |
| `authentication.staff_required` | 403 | スタッフ権限が必要です。 |
| `registration.email_already_used` | 400 | このメールアドレスは登録済みです。 |
| `part.not_found` | 404 | パーツが見つかりません。 |
| `part.sku_already_used` | 400 | この SKU は既に使われています。 |
| `part.invalid_attributes` | 400 | パーツ属性がカテゴリの制約を満たしません。 |
| `configuration.incomplete` | 400 | 必須パーツが不足しています。 |
| `configuration.duplicate_category` | 400 | 同じカテゴリのパーツが重複しています。 |
| `configuration.unknown_category` | 400 | 未知のパーツカテゴリです。 |
| `configuration.socket_mismatch` | 400 | CPU とマザーボードのソケットが一致しません。 |
| `configuration.memory_type_mismatch` | 400 | メモリ規格がマザーボードと一致しません。 |
| `configuration.memory_slot_exceeded` | 400 | メモリ枚数がスロット数を超えています。 |
| `configuration.form_factor_mismatch` | 400 | ケースとマザーボードのサイズが一致しません。 |
| `configuration.storage_interface_unsupported` | 400 | ストレージ接続をマザーボードが扱えません。 |
| `configuration.gpu_too_long` | 400 | GPU がケースに収まりません。 |
| `configuration.cooler_socket_mismatch` | 400 | CPU クーラーのソケットが一致しません。 |
| `configuration.cooler_too_tall` | 400 | CPU クーラーが高すぎてケースに収まりません。 |
| `configuration.psu_wattage_insufficient` | 400 | 電源容量が不足しています。 |
| `order.not_found` | 404 | 注文が見つかりません。 |
| `order.part_unlisted` | 400 | 選択したパーツは現在販売していません。 |
| `order.insufficient_stock` | 400 | 在庫が足りません。 |
| `order.invalid_status_transition` | 400 | この注文状態ではその操作はできません。 |

入力形式エラー（email、郵便番号など）は Serializer の field error。code は `input.invalid` を 1 つだけ使い、`details` にフィールド名 → 理由。この code も定義に含める。

画面の固定文言（ボタン、見出し）も `lib/messages/` に置く。component へ日本語リテラルを散らさない。

---

## 8. フロント状態

Svelte 5 runes。ライブラリ追加なし。

### 8.1 `currentUserState`

```ts
{ user: CurrentUserOutput | null }
```

### 8.2 `orderDraftState`

メモリのみ。Web Storage 禁止。

```ts
{
  partIdsByCategory: {
    cpu: number | null
    motherboard: number | null
    memory: number | null
    storage: number | null
    psu: number | null
    case: number | null
    gpu: number | null
    cpu_cooler: number | null
  }
  shipping: {
    recipient_name: string
    postal_code: string
    prefecture: string
    city: string
    address_line: string
    phone: string
  }
}
```

選択の正は ID。価格表示はページが `GET /parts` した一覧から引く UX。決済金額の正ではない。

公開関数: `selectPart(category, id)`, `clearPart(category)`, `setShipping(partial)`, `resetDraft()`, `toPartIds()`（null を除く）。

### 8.3 `syncedOrderState`

```ts
{ order: OrderOutput | null }
```

決済成功後と `/orders/[uuid]` の `load` だけが書く。確認画面はこれだけを見る。ドラフトを見ない。

### 8.4 決済ハンドラ（`/checkout` の page）

1. UX: 郵便番号・電話が数字か、必須 6 カテゴリがあるか
2. `createOrder({ part_ids, ...shipping })`
3. `getOrder(public_id)`
4. `syncedOrderState.order =` 応答
5. `resetDraft()`
6. `goto(/orders/{uuid})`

失敗時は `lib/messages` で表示。ドラフトは残す。

`/orders/[uuid]` の `+page.ts` は `getOrder`。失敗なら page が not_found 表示。成功なら `syncedOrderState` を埋めてから描画。

---

## 9. 画面仕様

対象幅 1024–3840 で構図固定。幅バリアント・`px`・画面 `<style>`・デフォルトパレット色は禁止。

共通ヘッダ（`z-10`）: サイト名「BTO PC」、ナビ「構成」「注文」「レジ」、スタッフなら「パーツ」「受注」、右側に email と「ログアウト」。

### 9.1 `/login` `/register`

全対象幅で 2 列のまま。左: 店舗写真とキャッチ。右: 見出し、email、password、送信、反対側へのリンク。エラーはフォーム上。

### 9.2 `/configure`

上段: カテゴリを横一列のタイル。必須の未選択を補助色で示す。
下段: 全対象幅で 2 列のまま。左: 選択中カテゴリのパーツ（2 列グリッド。名前、税込価格、在庫。在庫 0 は選択不可）。右: 選択中サマリ。各カテゴリの名前と価格、UX 合計、「レジへ」。

カテゴリ切替は page の状態。パーツ取得は `+page.ts` で全掲載パーツを一度取る。component は fetch しない。

一致性の再計算は「一致性を確認」クリック、またはレジへ進む直前の page ハンドラ。`$effect` では呼ばない。

### 9.3 `/checkout`

全対象幅で 2 列のまま。左: 配件確認と配送先 6 フィールド。右: 構成行と UX 合計、「決済完了」。決済はプレビュー invalid のとき非活性。活性でも backend が再判定する。

### 9.4 `/orders`

幅いっぱいの注文カード一覧。UUID、状態、合計、日時。カード全体が詳細へのリンク。空なら「注文はまだありません」。

### 9.5 `/orders/[uuid]`

全対象幅で 2 列のまま。左: 行。右: UUID、状態、合計、配送先。編集なし。

### 9.6 スタッフパーツ

一覧は表（SKU、名前、カテゴリ、価格、在庫、掲載）。「新規」。行から編集。

新規・編集は `max-w-3xl`。カテゴリを選ぶと、そのカテゴリの属性入力だけ出す。これは業務カテゴリの分岐であり、幅分岐ではない。

### 9.7 スタッフ注文

表。詳細は 2 列（行 / 状態・配送先・操作）。押せる遷移だけ活性。成功後は `getStaffOrder` で再表示。

状態表示に色が要る場合は、先に `frontend_design.md` §6 と `app.css` へ意味付きトークンを足す。例: `--color-success`。未追加のまま `text-green-600` は使わない。

---

## 10. モジュールとファイル

### Backend

```text
backend/application/
  models/part.py
  models/order.py
  models/order_line.py
  services/part.py          create_part, update_part
  services/order.py         create_order, prepare_order, ship_order, cancel_order
  selectors/part.py         get_part, get_listed_part, list_listed_parts, list_parts, PartFilter
  selectors/order.py        get_order_for_user, list_orders_for_user, get_order, list_orders
  selectors/configuration.py  evaluate_pc_configuration → DTO
  validators/part_attributes.py
  validators/pc_configuration.py
  errors/authentication.py
  errors/part.py
  errors/configuration.py
  errors/order.py
  messages/authentication.py
  messages/part.py
  messages/configuration.py
  messages/order.py
  api/exception_handler.py
  api/permissions.py        標準クラスの指定のみ。独自認可ロジックは置かない
  api/serializers/authentication.py
  api/serializers/part.py
  api/serializers/configuration.py
  api/serializers/order.py
  api/views/csrf.py
  api/views/registration.py
  api/views/session.py
  api/views/current_user.py
  api/views/part.py
  api/views/staff_part.py
  api/views/configuration.py
  api/views/order.py
  api/views/staff_order.py
  api/urls.py
  management/commands/seed_catalog.py
```

Service / Selector の公開関数名はこの一覧が正。

### Frontend

```text
frontend/src/
  app.css
  lib/api/client.ts
  lib/api/csrf.ts
  lib/api/registrations.ts
  lib/api/sessions.ts
  lib/api/currentUser.ts
  lib/api/parts.ts
  lib/api/staffParts.ts
  lib/api/configurations.ts
  lib/api/orders.ts
  lib/api/staffOrders.ts
  lib/types/currentUser.ts
  lib/types/part.ts
  lib/types/configuration.ts
  lib/types/order.ts
  lib/errors/apiError.ts
  lib/messages/authentication.ts
  lib/messages/part.ts
  lib/messages/configuration.ts
  lib/messages/order.ts
  lib/messages/ui.ts
  lib/states/currentUserState.ts
  lib/states/orderDraftState.ts
  lib/states/syncedOrderState.ts
  lib/components/AppHeader.svelte
  lib/components/PartSummaryList.svelte
  lib/components/OrderStatusText.svelte
  routes/+layout.ts
  routes/+layout.svelte
  routes/+page.ts
  routes/+page.svelte
  routes/login/+page.svelte
  routes/register/+page.svelte
  routes/configure/+page.ts
  routes/configure/+page.svelte
  routes/checkout/+page.ts
  routes/checkout/+page.svelte
  routes/orders/+page.ts
  routes/orders/+page.svelte
  routes/orders/[uuid]/+page.ts
  routes/orders/[uuid]/+page.svelte
  routes/staff/parts/+page.ts
  routes/staff/parts/+page.svelte
  routes/staff/parts/new/+page.svelte
  routes/staff/parts/[id]/edit/+page.ts
  routes/staff/parts/[id]/edit/+page.svelte
  routes/staff/orders/+page.ts
  routes/staff/orders/+page.svelte
  routes/staff/orders/[uuid]/+page.ts
  routes/staff/orders/[uuid]/+page.svelte
```

`vite.config.ts` に `server.proxy["/api"] = "http://localhost:8000"`（preview も同じ）。

設定追加:

- `CORS_ALLOW_CREDENTIALS = True`
- `REST_FRAMEWORK["EXCEPTION_HANDLER"]`
- `REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = SessionAuthentication`
- `CSRF_COOKIE_HTTPONLY = False`（JS が読む）
- `SESSION_COOKIE_SAMESITE = "Lax"`
- `CSRF_COOKIE_SAMESITE = "Lax"`

---

## 11. シード

`seed_catalog` は Service 経由。既存 SKU は更新せずスキップ（冪等）。スタッフもここで作る。

| 種別 | 値 |
|---|---|
| スタッフ | `staff@example.com` / `staffpass` / `is_staff=True` |
| 顧客（任意） | `buyer@example.com` / `buyerpass` |

通る構成（全部掲載、在庫 10）:

| sku | category | 要点 | 価格 |
|---|---|---|---|
| `CPU-AM5-7600` | cpu | am5 / 65W | 24800 |
| `MB-AM5-ATX` | motherboard | am5 / ddr5 / atx / slot4 / sata4 / m2=2 | 19800 |
| `MEM-DDR5-32` | memory | ddr5 / 2枚 / 32GB | 12800 |
| `SSD-M2-1T` | storage | m2 | 9800 |
| `PSU-650` | psu | 650W | 9800 |
| `CASE-ATX` | case | atx / GPU360 / cooler160 | 8900 |
| `GPU-4070` | gpu | 304mm / 200W | 89800 |
| `CLR-AM5-155` | cpu_cooler | am5 / 155mm | 6800 |

意図的に落ちる部品（掲載、在庫 10）:

| sku | 落ちる理由 |
|---|---|
| `CPU-1700-13400` | lga1700。AM5 MB と不一致 |
| `MEM-DDR4-16` | ddr4 |
| `CASE-ITX` | itx |
| `PSU-300` | 300W |
| `GPU-LONG` | 400mm |
| `CLR-TALL` | 180mm |

未掲載 1 個 `CPU-HIDDEN` を置き、顧客一覧に出ないことを確認する。

名前は実装時に上表の sku を変えず、通る / 落ちる属性を守る。

---

## 12. テスト

名前は仕様を英語で書く。private は直接叩かない。

Service 例:

- `test_create_order_persists_snapshot_and_decrements_stock`
- `test_create_order_rejects_incompatible_socket`
- `test_create_order_rejects_unlisted_part`
- `test_create_order_rejects_insufficient_stock`
- `test_create_order_locks_parts_in_id_order`（順序の固定を読める範囲で）
- `test_cancel_order_restores_stock`
- `test_cancel_order_rejects_shipped`
- `test_prepare_order_rejects_cancelled`

Selector 例:

- `test_list_listed_parts_excludes_unlisted`
- `test_get_order_for_user_hides_other_users_order`
- `test_evaluate_pc_configuration_returns_socket_mismatch_issue`

API 例:

- 未ログイン 401
- 顧客の staff 403
- 決済 201 のあと GET が一致
- 他人 UUID 404 + `order.not_found`

Frontend 例:

- API client が envelope を typed error にする
- draft が select 後も別 page import で残る
- `resetDraft` 後は空
- 決済成功シーケンスが create → get の順

---

## 13. 実装順

各段のあと backend は Ruff / mypy / pytest、frontend は format / lint / check / test。UI 段はブラウザで操作確認。見た目だけのスクショでは完了にしない。

### 0. 仕様ファイル

この計画を `docs/bto_pc_store.md` に保存する。コードは触らない。

### 1. API 基盤

exception handler、CSRF cookie、CORS credentials、Vite proxy、`lib/api/client.ts`、`input.invalid` と認証系の error/message 枠。Model はまだ作らない。

完了: `GET /api/v1/csrf` が cookie を返し、存在しない path 以外の共通 envelope がテストできる。

### 2. 認証

登録・ログイン・ログアウト・current-user。`currentUserState`。`/login` `/register`。layout 初期化。未ログイン制限。

完了: ブラウザで登録 → リロード後もログイン維持 → ログアウト。

### 3. カタログ

Part Model / migration / Service / Selector / 顧客 GET / スタッフ CRUD。スタッフ画面。シード。

完了: スタッフがパーツを作り、顧客一覧に出る。未掲載は出ない。属性不正は 400。

### 4. 構成ドラフト

`orderDraftState`。`/configure`。プレビュー API。ヘッダナビ。

完了: 選択して `/checkout` に行って戻っても残る。リロードで消える。一致性ボタンが issue を出す。

### 5. 決済と同期

Order / OrderLine。`create_order`。`/checkout` `/orders` `/orders/[uuid]`。`syncedOrderState`。

完了: 通る構成で決済 → 在庫減 → 確認が GET と一致。壊れた構成は DB に行がない。リロード後 UUID で復元。他人は 404。

### 6. スタッフ注文

一覧・詳細・prepare / ship / cancel。在庫復帰。

完了: キャンセルで在庫が戻る。shipped はキャンセル不可。顧客画面に操作ボタンがない。

---

## 14. ブラウザ検証

1024px と 3840px の両方で構図を見る。

1. 登録 → ログイン → 構成 → 履歴へ行って戻る → ドラフト残
2. リロード → ドラフト消
3. 壊れた構成で決済 → エラー表示、注文なし
4. 通る構成で決済 → 在庫減、確認 = API
5. リロードして同じ UUID → backend から復元
6. 別ユーザーでその UUID → 見つからない
7. スタッフが価格・在庫・掲載を変更。顧客に反映
8. スタッフがキャンセル → 在庫戻る
9. 構成画面が両幅で 3 列

---

## 15. Definition of Done（仕様）

- 未保存中は `orderDraftState` が正。保存後は `syncedOrderState` = 最新 GET
- ドラフトを保存する API が存在しない
- 決済以外で Order が作られない
- 顧客 API に他人の注文が漏れない
- 配件・在庫・価格の最終判定が Service / Validator にある
- 画面の HTTP が `lib/api/` だけ
- 仕様に無い endpoint / error code / 色トークン / 依存が無い
