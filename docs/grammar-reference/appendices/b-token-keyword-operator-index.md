<!-- tools/generators/generate_grammar_reference.py가 생성함; 직접 수정하지 마십시오. -->
# 부록 B — 토큰, 키워드 및 연산자

## 어휘 토큰 범주

| 토큰/범주 | 문법 줄 |
|---|---:|
| `IDENTIFIER` | 44 |
| `WILDCARD` | 47 |
| `HARD_KEYWORD` | 50 |
| `NUMERIC_LITERAL` | 65 |
| `IMAGINARY_LITERAL` | 70 |
| `RATIONAL_LITERAL` | 75 |
| `INTEGER_LITERAL` | 76 |
| `FLOAT_LITERAL` | 81 |
| `DECIMAL_INTEGER` | 87 |
| `CHAR_LITERAL` | 103 |
| `PLAIN_STRING_LITERAL` | 111 |
| `STRING_START` | 112 |
| `STRING_TEXT` | 113 |
| `STRING_ESCAPE` | 114 |
| `INTERPOLATION_BOUNDARY` | 115 |
| `INTERPOLATION_OPEN` | 116 |
| `INTERPOLATION_CLOSE` | 117 |
| `INTERPOLATION_FORMAT_TEXT` | 118 |
| `STRING_END` | 119 |
| `RAW_STRING_LITERAL` | 123 |
| `MULTILINE_STRING_LITERAL` | 124 |
| `BYTES_LITERAL` | 125 |
| `PATH_SEP` | 128 |
| `FAT_ARROW` | 129 |
| `ARROW` | 130 |
| `DOT_DOT` | 131 |
| `DOT_DOT_LT` | 132 |
| `DOT_DOT_GT` | 133 |
| `ELLIPSIS` | 134 |
| `TRIPLE_STAR` | 135 |
| `DOUBLE_STAR` | 136 |
| `STAR_PLUS` | 137 |
| `STAR_DOT` | 138 |
| `AMP_AMP` | 139 |
| `PIPE_PIPE` | 140 |
| `CARET_CARET` | 141 |
| `QUESTION_COLON` | 142 |
| `DOUBLE_DOLLAR` | 143 |
| `EQ_EQ` | 144 |
| `BANG_EQ` | 145 |
| `LT_EQ` | 146 |
| `GT_EQ` | 147 |
| `PLUS_EQ` | 148 |
| `MINUS_EQ` | 149 |
| `STAR_EQ` | 150 |
| `SLASH_EQ` | 151 |
| `PERCENT_EQ` | 152 |
| `TILDE_TILDE` | 153 |
| `COLON_EQ` | 154 |
| `BANG_BANG` | 155 |
| `DOUBLE_L_BRACE` | 156 |
| `DOUBLE_R_BRACE` | 157 |
| `DOLLAR_L_BRACE` | 158 |
| `EOF_TOKEN` | 166 |
| `NAME_TOKEN` | 168 |
| `EOF` | 169 |

## 하드 키워드

| 단어 |
|---|
| `and` |
| `as` |
| `catch` |
| `class` |
| `def` |
| `defer` |
| `else` |
| `enum` |
| `false` |
| `finally` |
| `for` |
| `if` |
| `import` |
| `in` |
| `let` |
| `match` |
| `module` |
| `not` |
| `null` |
| `or` |
| `repeat` |
| `return` |
| `throw` |
| `trait` |
| `true` |
| `try` |
| `type` |
| `use` |
| `var` |
| `while` |

## 문맥 단어

| 단어 |
|---|
| `C` |
| `abstract` |
| `actor` |
| `any` |
| `async` |
| `await` |
| `backing` |
| `bitfield` |
| `borrow` |
| `borrowed` |
| `break` |
| `budget` |
| `c` |
| `cancellable` |
| `capability` |
| `capacity` |
| `catalog` |
| `cleanup` |
| `clone` |
| `common` |
| `conformance` |
| `conforms` |
| `consume` |
| `context` |
| `continue` |
| `copy` |
| `data` |
| `deep` |
| `delegate` |
| `effects` |
| `ensures` |
| `entry` |
| `equalsRatio` |
| `error` |
| `errors` |
| `export` |
| `extension` |
| `extern` |
| `facet` |
| `final` |
| `flags` |
| `forward` |
| `generate` |
| `get` |
| `group` |
| `guard` |
| `inout` |
| `is` |
| `isolated` |
| `law` |
| `lazy` |
| `lsb0` |
| `mailbox` |
| `map` |
| `move` |
| `mut` |
| `on` |
| `once` |
| `opaque` |
| `open` |
| `order` |
| `otherwise` |
| `out` |
| `owned` |
| `pack` |
| `preview` |
| `private` |
| `protocol` |
| `public` |
| `pure` |
| `raw` |
| `request` |
| `requires` |
| `resource` |
| `ret` |
| `schema` |
| `scope` |
| `scoped` |
| `sealed` |
| `send` |
| `set` |
| `shielded` |
| `signature` |
| `some` |
| `spawn` |
| `static` |
| `super` |
| `task` |
| `then` |
| `throws` |
| `to` |
| `typeof` |
| `typestate` |
| `unit` |
| `unsafe` |
| `using` |
| `value` |
| `via` |
| `where` |
| `witness` |
| `yield` |

## Pratt 연산자 소유자

| 도메인 | ID | 토큰 | 결합력 | 결합 방향 |
|---|---|---|---|---|
| `expression` | `assignment` | `= / += / -= / *= / /= / %=` | 10/9 | right |
| `expression` | `ternary` | `? / :` | 20/19 | right |
| `expression` | `otherwise` | `otherwise` | 30/31 | left |
| `expression` | `or` | `or` | 40/41 | left |
| `expression` | `and_then` | `and then` | 50/51 | left |
| `expression` | `and` | `and` | 60/61 | left |
| `expression` | `comparison` | `== / != / < / <= / > / >= / in / ! in / is / ! is` | 70/71 | checker_bounded_chain |
| `expression` | `option_coalesce` | `?:` | 80/79 | right |
| `expression` | `bitwise_or` | `\|\|` | 90/91 | left |
| `expression` | `bitwise_xor` | `^^` | 100/101 | left |
| `expression` | `bitwise_and` | `&&` | 110/111 | left |
| `expression` | `range` | `.. / ..<` | 120/121 | nonassociative |
| `expression` | `additive` | `+ / -` | 130/131 | left |
| `expression` | `multiplicative` | `* / / / %` | 140/141 | left |
| `expression` | `linear_product` | `** / *+` | 150/151 | left |
| `expression` | `power` | `^` | 160/159 | right |
| `expression` | `numeric_prefix_sign` | `+ / -` | /159 | right |
| `expression` | `prefix` | `not / ~~ / move / borrow / & / await` | /170 | right |
| `expression` | `cast` | `as ? / as !` | 180/ | nonassociative |
| `expression` | `postfix` | `` | 190/ | left |
| `type` | `union` | `\|` | 10/11 |  |
| `type` | `intersection` | `&` | 20/21 |  |
| `type` | `ownership` | `owned / borrowed / mut / inout` | /30 |  |
| `type` | `optional` | `?` | 40/ |  |
| `unit` | `product` | `*` | 20/21 |  |
| `unit` | `division` | `/` | 20/21 |  |
| `unit` | `power` | `^` | 30/ |  |
