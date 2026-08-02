<!-- tools/generators/generate_grammar_reference.py가 생성함; 직접 수정하지 마십시오. -->
# 부록 A — 정확한 문법 production 참조

권위 원천은 `spec/grammar/deeplus.ebnf`입니다. 이름만 나열하지 않고 모든 production의 정확한 오른쪽 항을 주석을 제외한 정규화된 EBNF로 한 번씩 투영합니다. 줄 번호는 원천을 찾아가기 위한 보조 정보이며 이 부록 자체가 별도 문법 권위는 아닙니다.

## `LEXICAL` 프로파일 — 91개

| 문법 production | 정확한 EBNF 오른쪽 항 | 원천 줄 |
|---|---|---:|
| `SourceCharacter` | `UnicodeScalar` | 39 |
| `LineTerminator` | `"\\r\\n" \| "\\n"` | 40 |
| `HorizontalSpace` | `" " \| "\\t"` | 41 |
| `IDENTIFIER` | `UnicodeXIDStart IdentifierContinue* \| "_" IdentifierContinue+` | 44 |
| `IdentifierContinue` | `UnicodeXIDContinue` | 46 |
| `WILDCARD` | `"_"` | 47 |
| `HARD_KEYWORD` | `ScannerHardKeywordToken` | 50 |
| `Shebang` | `"#!" ShebangScalar* LineTerminator` | 52 |
| `LineComment` | `"//" LineCommentScalar*` | 53 |
| `DocLineComment` | `"//!" DocLineCommentScalar*` | 54 |
| `NestedBlockComment` | `BlockCommentOpen BlockCommentItem* BlockCommentClose` | 55 |
| `BlockCommentOpen` | `"//" DashRun` | 58 |
| `BlockCommentClose` | `DashRun "//"` | 59 |
| `DashRun` | `"-" "-"*` | 60 |
| `BlockCommentItem` | `NestedBlockComment \| BlockCommentScalar` | 61 |
| `DocBlockComment` | `"//!!" DocBlockCommentScalar* "!!//"` | 62 |
| `WordComment` | `"\`" WordCommentScalar+` | 63 |
| `NUMERIC_LITERAL` | `FLOAT_LITERAL \| INTEGER_LITERAL` | 65 |
| `IMAGINARY_LITERAL` | `ScannerImaginaryFloatLiteral` | 70 |
| `RATIONAL_LITERAL` | `ScannerRationalLiteralAtExpressionPrefix` | 75 |
| `INTEGER_LITERAL` | `BinaryInteger IntegerSuffix? \| OctalInteger IntegerSuffix? \| HexInteger IntegerSuffix? \| DECIMAL_INTEGER IntegerSuffix?` | 76 |
| `FLOAT_LITERAL` | `DecimalFraction ExponentPart? FloatSuffix? \| DECIMAL_INTEGER ExponentPart FloatSuffix? \| DECIMAL_INTEGER FloatSuffix` | 81 |
| `BinaryInteger` | `("0b" \| "0B") BinaryDigits` | 84 |
| `OctalInteger` | `("0o" \| "0O") OctalDigits` | 85 |
| `HexInteger` | `("0x" \| "0X") HexDigits` | 86 |
| `DECIMAL_INTEGER` | `DecimalDigits` | 87 |
| `DecimalFraction` | `DecimalDigits "." DecimalDigits` | 88 |
| `ExponentPart` | `("e" \| "E") ("+" \| "-")? DecimalDigits` | 89 |
| `IntegerSuffix` | `"i8" \| "i16" \| "i32" \| "i64" \| "i128" \| "isize" \| "u8" \| "u16" \| "u32" \| "u64" \| "u128" \| "usize"` | 90 |
| `FloatSuffix` | `"f32" \| "f64"` | 92 |
| `BinaryDigits` | `BinaryDigit ("_"? BinaryDigit)*` | 93 |
| `OctalDigits` | `OctalDigit ("_"? OctalDigit)*` | 94 |
| `DecimalDigits` | `DecimalDigit ("_"? DecimalDigit)*` | 95 |
| `HexDigits` | `HexDigit ("_"? HexDigit)*` | 96 |
| `BinaryDigit` | `"0" \| "1"` | 97 |
| `OctalDigit` | `"0" \| "1" \| "2" \| "3" \| "4" \| "5" \| "6" \| "7"` | 98 |
| `DecimalDigit` | `"0" \| "1" \| "2" \| "3" \| "4" \| "5" \| "6" \| "7" \| "8" \| "9"` | 99 |
| `HexDigit` | `DecimalDigit \| "a" \| "b" \| "c" \| "d" \| "e" \| "f" \| "A" \| "B" \| "C" \| "D" \| "E" \| "F"` | 100 |
| `CHAR_LITERAL` | `"'" CharScalar "'"` | 103 |
| `CharScalar` | `DirectCharScalar \| SimpleCharEscape \| UnicodeScalarEscape \| NamedUnicodeEscape` | 104 |
| `SimpleCharEscape` | `"\\\\0" \| "\\\\n" \| "\\\\r" \| "\\\\t" \| "\\\\'" \| "\\\\\\\\"` | 105 |
| `UnicodeScalarEscape` | `"\\\\u{" HexScalarDigits "}"` | 106 |
| `NamedUnicodeEscape` | `"\\\\N{" UnicodeName "}"` | 107 |
| `HexScalarDigits` | `HexDigit HexDigit? HexDigit? HexDigit? HexDigit? HexDigit?` | 108 |
| `PLAIN_STRING_LITERAL` | `ScannerPlainStringLiteral` | 111 |
| `STRING_START` | `ScannerInterpolatedStringStart` | 112 |
| `STRING_TEXT` | `ScannerInterpolatedStringText` | 113 |
| `STRING_ESCAPE` | `ScannerStringEscape` | 114 |
| `INTERPOLATION_BOUNDARY` | `ScannerInterpolationBoundary` | 115 |
| `INTERPOLATION_OPEN` | `ScannerInterpolationOpen` | 116 |
| `INTERPOLATION_CLOSE` | `ScannerInterpolationClose` | 117 |
| `INTERPOLATION_FORMAT_TEXT` | `ScannerInterpolationFormatText` | 118 |
| `STRING_END` | `ScannerInterpolatedStringEnd` | 119 |
| `RAW_STRING_LITERAL` | `ScannerRawStringLiteral` | 123 |
| `MULTILINE_STRING_LITERAL` | `ScannerMultilineStringLiteral` | 124 |
| `BYTES_LITERAL` | `ScannerBytesLiteral` | 125 |
| `PATH_SEP` | `"::"` | 128 |
| `FAT_ARROW` | `"=>"` | 129 |
| `ARROW` | `"->"` | 130 |
| `DOT_DOT` | `".."` | 131 |
| `DOT_DOT_LT` | `"..<"` | 132 |
| `DOT_DOT_GT` | `"..>"` | 133 |
| `ELLIPSIS` | `"..."` | 134 |
| `TRIPLE_STAR` | `"***"` | 135 |
| `DOUBLE_STAR` | `"**"` | 136 |
| `STAR_PLUS` | `"*+"` | 137 |
| `STAR_DOT` | `"*."` | 138 |
| `AMP_AMP` | `"&&"` | 139 |
| `PIPE_PIPE` | `"\|\|"` | 140 |
| `CARET_CARET` | `"^^"` | 141 |
| `QUESTION_COLON` | `"?:"` | 142 |
| `DOUBLE_DOLLAR` | `"$$"` | 143 |
| `EQ_EQ` | `"=="` | 144 |
| `BANG_EQ` | `"!="` | 145 |
| `LT_EQ` | `"<="` | 146 |
| `GT_EQ` | `">="` | 147 |
| `PLUS_EQ` | `"+="` | 148 |
| `MINUS_EQ` | `"-="` | 149 |
| `STAR_EQ` | `"*="` | 150 |
| `SLASH_EQ` | `"/="` | 151 |
| `PERCENT_EQ` | `"%="` | 152 |
| `TILDE_TILDE` | `"~~"` | 153 |
| `COLON_EQ` | `":="` | 154 |
| `BANG_BANG` | `"!!"` | 155 |
| `DOUBLE_L_BRACE` | `"{{"` | 156 |
| `DOUBLE_R_BRACE` | `"}}"` | 157 |
| `DOLLAR_L_BRACE` | `"${"` | 158 |
| `Trivia` | `HorizontalSpace \| LineTerminator \| LineComment \| NestedBlockComment \| DocLineComment \| DocBlockComment \| WordComment` | 163 |
| `EOF_TOKEN` | `EOF` | 166 |
| `NAME_TOKEN` | `ScannerEscapedNameToken` | 168 |
| `EOF` | `ScannerEndOfInput` | 169 |

## `STABLE` 프로파일 — 539개

| 문법 production | 정확한 EBNF 오른쪽 항 | 원천 줄 |
|---|---|---:|
| `Identifier` | `IDENTIFIER` | 177 |
| `QualifiedPath` | `Identifier ("::" Identifier)*` | 180 |
| `TopLevelVisibility` | `"public" \| "private" \| "common"` | 182 |
| `MemberVisibility` | `"+" \| "-" \| "#"` | 191 |
| `ClassDispatchMarker` | `"." \| "+" \| "*." \| "*+"` | 192 |
| `TraitWitnessMarker` | `"." \| "+" \| "*." \| "*+"` | 193 |
| `VarianceMarker` | `"out" \| "in"` | 194 |
| `AnnotationAttachment` | `Annotation+` | 196 |
| `Annotation` | `"@" Identifier ArgumentList? LineBreakBoundary` | 197 |
| `RoleWord` | `Identifier \| HARD_KEYWORD` | 202 |
| `HashTag` | `"#" RoleWord` | 203 |
| `TypeParameterList` | `"<" TypeParameter ("," TypeParameter)* ","? ">"` | 206 |
| `TypeParameter` | `VarianceMarker? Identifier TypeParameterKindAnnotation?` | 207 |
| `TypeParameterKindAnnotation` | `":" TypeParameterKind` | 208 |
| `TypeParameterKind` | `"type" \| "StaticInt" \| "EffectRow" \| "ErrorSet"` | 209 |
| `TypeArgumentList` | `"<" TypeArgument ("," TypeArgument)* ","? ">"` | 211 |
| `TypeArgument` | `TypeRef \| StaticIntLiteral \| ErrorTypeArgument` | 212 |
| `ErrorTypeArgument` | `"error" TypeRef` | 213 |
| `TraitReferenceList` | `QualifiedTypeReference ("," QualifiedTypeReference)*` | 215 |
| `AssociatedTypeConstraintList` | `"where" AssociatedTypeConstraint ("," AssociatedTypeConstraint)*` | 216 |
| `AssociatedTypeConstraint` | `Identifier "==" TypeRef \| Identifier "conforms" QualifiedTypeReference` | 217 |
| `WhereClause` | `"where" WherePredicate ("," WherePredicate)*` | 220 |
| `WherePredicate` | `TypeRef "conforms" QualifiedTypeReference \| TypeRef "==" TypeRef \| RowPredicate` | 221 |
| `RowPredicate` | `Identifier "<=" EffectRow` | 224 |
| `EffectRow` | `EffectRowTerm ("\|" EffectRowTerm)*` | 226 |
| `EffectRowTerm` | `Identifier \| QualifiedTypeReference \| EffectSetLiteral` | 227 |
| `ErrorSet` | `ErrorSetTerm ("\|" ErrorSetTerm)*` | 228 |
| `ErrorSetTerm` | `Identifier \| QualifiedTypeReference` | 229 |
| `EffectSetLiteral` | `"{" IdentifierList? "}"` | 230 |
| `TypeAnnotation` | `":" TypeRef RefinementSuffix?` | 232 |
| `RefinementSuffix` | `RefinementClause \| IntervalRefinementClause` | 233 |
| `RefinementClause` | `"where" (PredicateExpr \| ImplicitThisPredicate)` | 234 |
| `ImplicitThisPredicate` | `OrderedComparisonOperator RefinementComparisonOperand` | 238 |
| `RefinementComparisonOperand` | `Literal \| Identifier \| QualifiedStaticExpr` | 239 |
| `IntervalRefinementClause` | `"in" RefinementBound (".." \| "..<") RefinementBound` | 240 |
| `RefinementBound` | `Literal \| Identifier \| QualifiedStaticExpr` | 241 |
| `OrderedComparisonOperator` | `"<" \| "<=" \| ">" \| ">="` | 242 |
| `Initializer` | `"=" Expr` | 243 |
| `NameAliasClause` | `"as" Identifier` | 244 |
| `ReturnClause` | `"->" ReturnTypeSurface` | 248 |
| `ReturnTypeSurface` | `NonFunctionTypeRef \| BareTupleTypeSurface` | 249 |
| `BareTupleTypeSurface` | `NonFunctionTypeRef "," NonFunctionTypeRef ("," NonFunctionTypeRef)*` | 250 |
| `ThrowsClause` | `"throws" ErrorSetTerm` | 255 |
| `EffectsClause` | `"effects" CallableEffectTerm` | 256 |
| `CallableEffectTerm` | `Identifier \| QualifiedTypeReference \| EmptyEffectSet` | 257 |
| `EmptyEffectSet` | `"{" "}"` | 258 |
| `ContractClause` | `RequiresClause \| EnsuresClause` | 259 |
| `RequiresClause` | `"requires" PredicateExpr` | 260 |
| `EnsuresClause` | `"ensures" PredicateExpr` | 261 |
| `LineBreakBoundary` | `LINE_BREAK_IN_TRIVIA` | 266 |
| `StatementBoundary` | `STATEMENT_BOUNDARY_BY_CONTEXT` | 267 |
| `IdentifierList` | `Identifier ("," Identifier)* ","?` | 269 |
| `ExpressionList` | `Expr ("," Expr)* ","?` | 270 |
| `PatternList` | `Pattern ("," Pattern)* ","?` | 271 |
| `StaticIntLiteral` | `DECIMAL_INTEGER` | 273 |
| `UnitSyntax` | `"(" ")"` | 276 |
| `SignedStaticInt` | `("+" \| "-")? StaticIntLiteral` | 277 |
| `LawDecl` | `"law" Identifier LawBody? StatementBoundary` | 279 |
| `LawBody` | `"{" LawBodyItem* "}"` | 282 |
| `LawBodyItem` | `LawAssertion StatementBoundary` | 283 |
| `LawAssertion` | `("requires" \| "ensures" \| "invariant")? PredicateExpr` | 284 |
| `Deeplus` | `LibrarySourceFile \| ExecutableSourceFile \| ScriptSourceFile` | 292 |
| `LibrarySourceFile` | `ModuleDecl? LibrarySourceItem*` | 294 |
| `ExecutableSourceFile` | `ModuleDecl? ExecutableSourceItem*` | 295 |
| `ScriptSourceFile` | `Shebang? ModuleDecl? ScriptSourceItem*` | 296 |
| `LibrarySourceItem` | `AnnotationAttachment LibraryAnnotatableDecl \| ImportOrUseDecl \| TopLevelDecl` | 298 |
| `ExecutableSourceItem` | `AnnotationAttachment ExecutableAnnotatableDecl \| ImportOrUseDecl \| NonBindingTopLevelDecl \| EntryFunctionDecl` | 301 |
| `ScriptSourceItem` | `AnnotationAttachment ScriptAnnotatableDecl \| ImportOrUseDecl \| NonBindingTopLevelDecl \| Stmt` | 305 |
| `LibraryAnnotatableDecl` | `ImportOrUseDecl \| TopLevelDecl` | 310 |
| `ExecutableAnnotatableDecl` | `ImportOrUseDecl \| NonBindingTopLevelDecl \| EntryFunctionDecl` | 311 |
| `ScriptAnnotatableDecl` | `ImportOrUseDecl \| NonBindingTopLevelDecl` | 312 |
| `ModuleDecl` | `"module" QualifiedPath StatementBoundary` | 314 |
| `ImportOrUseDecl` | `ImportDecl \| UseDecl \| UseExportDecl` | 316 |
| `ImportDecl` | `"import" QualifiedPath ImportTail? StatementBoundary` | 317 |
| `ImportTail` | `ImportAlias \| ImportSelection` | 318 |
| `ImportAlias` | `NameAliasClause` | 319 |
| `ImportSelection` | `"::" "{" IdentifierList "}"` | 320 |
| `UseDecl` | `"use" QualifiedPath StatementBoundary` | 321 |
| `UseExportDecl` | `"use" "export" QualifiedPath StatementBoundary` | 322 |
| `ExportDecl` | `"export" ExportItem StatementBoundary?` | 325 |
| `ExportItem` | `ExportableModuleFunctionDecl \| TypeDecl \| Identifier` | 326 |
| `ExportableModuleFunctionDecl` | `TopLevelVisibility? "def" Identifier FunctionRest` | 327 |
| `TopLevelDecl` | `NonBindingTopLevelDecl \| TopLevelBindingDecl` | 335 |
| `NonBindingTopLevelDecl` | `TypeDecl \| ModuleFunctionDecl \| ExtensionFunctionDecl \| ActorDecl \| ActorProtocolDecl \| TypestateResourceDecl \| NamedEffectCapabilityDecl \| ExtensionSetDecl \| ExtensionPackDecl \| UnitCatalogDecl \| ModuleInterfaceDecl \| ConformanceDecl \| SchemaDecl \| BitfieldDecl` | 336 |
| `TypeDecl` | `ClassDecl \| TraitDecl \| EnumDecl \| TypeAliasDecl` | 351 |
| `DefIntroducer` | `"def" HashTag*` | 355 |
| `ModuleFunctionDecl` | `TopLevelVisibility? DefIntroducer Identifier FunctionRest` | 357 |
| `EntryFunctionDecl` | `DefIntroducer Identifier EntryFunctionRest` | 358 |
| `ExtensionFunctionDecl` | `TopLevelVisibility? DefIntroducer TypeRef ExtensionFunctionTarget Identifier FunctionRest` | 359 |
| `ExtensionFunctionTarget` | `"~" \| "::"` | 360 |
| `LocalFunctionDecl` | `CaptureList? DefIntroducer Identifier FunctionRest` | 361 |
| `FunctionRest` | `TypeParameterList? ParameterList FunctionTail` | 363 |
| `EntryFunctionRest` | `ParameterList ReturnClause? ThrowsClause* EffectsClause* ContractClause* FunctionBody` | 364 |
| `FunctionTail` | `ReturnClause? ThrowsClause* EffectsClause* ContractClause* WhereClause? FunctionBody` | 365 |
| `TraitFunctionTail` | `ReturnClause? ThrowsClause* EffectsClause* ContractClause* WhereClause? (FunctionBody \| StatementBoundary)` | 366 |
| `FunctionBody` | `"=" FunctionBodyContent` | 368 |
| `FunctionBodyContent` | `CallableBlock \| ReturnShorthand \| ClauseFunctionBody` | 369 |
| `CallableBlock` | `"{" BlockPrologue? FunctionStaticActivation? BlockSequence "}"` | 375 |
| `FunctionStaticActivation` | `"static" Block` | 376 |
| `ReturnShorthand` | `"return" ReturnValueSurface StatementBoundary` | 377 |
| `ClauseFunctionBody` | `"{{" LineBreakBoundary? MatchArmSequence "}}"` | 378 |
| `MemberFunctionDecl` | `MemberVisibility? DefIntroducer Identifier ClassDispatchMarker FunctionRest` | 380 |
| `TypeSideMemberFunctionDecl` | `MemberVisibility? "def" "::" Identifier FunctionRest` | 381 |
| `ConstructorDecl` | `MemberVisibility? "def" "!" Identifier ParameterList ConstructorSignatureTail? ConstructorDelegationClause? "=" Block` | 383 |
| `ConstructorSignatureTail` | `ThrowsClause+ EffectsClause* ContractClause* WhereClause? \| EffectsClause+ ContractClause* WhereClause? \| ContractClause+ WhereClause? \| WhereClause` | 385 |
| `ConstructorDelegationClause` | `":" ConstructorDelegationArm+` | 389 |
| `ConstructorDelegationArm` | `ConstructorDelegationTarget PositiveGuard?` | 390 |
| `ConstructorDelegationTarget` | `Identifier ArgumentList \| "super" "!" Identifier? ArgumentList` | 391 |
| `CleanupDecl` | `DefIntroducer "(" ")" ThrowsClause* EffectsClause* FunctionBody` | 394 |
| `ParameterList` | `"(" ParameterSequence? ")"` | 398 |
| `ParameterSequence` | `CommaParameterSequence \| LayoutParameterSequence` | 399 |
| `CommaParameterSequence` | `Parameter ("," Parameter)* ","?` | 400 |
| `LayoutParameterSequence` | `LineBreakBoundary Parameter (LineBreakBoundary Parameter)* LineBreakBoundary?` | 401 |
| `Parameter` | `StoredParameter \| ContextParameter \| WitnessParameter \| RepeatedParameter \| NamedRestParameter \| ValueParameter` | 403 |
| `ValueParameter` | `ParameterMode? ParameterPatternSlot TypeAnnotation` | 409 |
| `ParameterPatternSlot` | `Identifier IrrefutableParameterPattern?` | 414 |
| `IrrefutableParameterPattern` | `TuplePattern \| ListPattern \| RecordPattern \| NominalPattern` | 415 |
| `ParameterMode` | `"borrow" \| "mut" \| "move" \| "inout"` | 419 |
| `ContextParameter` | `"context" Identifier ":" TypeRef` | 420 |
| `WitnessParameter` | `"using" Identifier ":" "witness" TypeRef` | 421 |
| `RepeatedParameter` | `Identifier "..." TypeAnnotation` | 422 |
| `NamedRestParameter` | `Identifier "***" TypeAnnotation` | 423 |
| `StoredParameter` | `MemberVisibility? ("let" \| "var") Identifier TypeAnnotation?` | 427 |
| `ClassDecl` | `OrdinaryClassDecl \| DataClassDecl` | 431 |
| `OrdinaryClassDecl` | `TopLevelVisibility? ClassFlavor? ClassModifierSequence? "class" Identifier TypeParameterList? ParameterList? WhereClause? ClassDerivesClause? NominalConformanceClause* CleanupBudgetClause? ClassBody` | 432 |
| `DataClassDecl` | `TopLevelVisibility? "data" "class" Identifier TypeParameterList? ParameterList? WhereClause? NominalConformanceClause* CleanupBudgetClause? ClassBody?` | 436 |
| `ClassFlavor` | `"value" \| "resource"` | 438 |
| `ClassModifierSequence` | `"final" \| "open" \| "abstract" \| "sealed" \| "abstract" "sealed"` | 439 |
| `ClassDerivesClause` | `LineBreakBoundary "derives" TypeRef` | 443 |
| `NominalConformanceClause` | `LineBreakBoundary "conforms" QualifiedTypeReference NominalConformanceRoute? WhereClause?` | 444 |
| `NominalConformanceRoute` | `ConformanceViaClause \| ConformanceAutoClause` | 446 |
| `ClassBody` | `"{" MemberDecl* "}"` | 447 |
| `MemberDecl` | `FieldDecl \| MemberFunctionDecl \| ConstructorDecl \| CleanupDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| ConformBlockDecl \| ForwardDecl` | 449 |
| `FieldDecl` | `MemberVisibility? ("let" \| "var") Identifier TypeAnnotation? Initializer? StatementBoundary` | 459 |
| `TypeSideFieldDecl` | `MemberVisibility? "let" "::" Identifier TypeAnnotation? Initializer? StatementBoundary` | 461 |
| `AccessorPropertyDecl` | `("let" \| "var") Identifier TypeAnnotation ":=" AccessorSpec` | 463 |
| `AccessorSpec` | `AccessorDecl \| "{" AccessorDecl+ "}"` | 464 |
| `AccessorDecl` | `MemberVisibility? "get" Block \| MemberVisibility? "set" "(" Identifier ")" Block` | 465 |
| `ForwardDecl` | `MemberVisibility? "forward" ForwardMemberSpec "to" Expr StatementBoundary` | 467 |
| `ForwardMemberSpec` | `Identifier \| "{" Identifier ("," Identifier)* ","? "}"` | 468 |
| `TraitDecl` | `TopLevelVisibility? "trait" Identifier TypeParameterList? TraitDerivesClause* TraitAutoSupportClause? TraitBody?` | 472 |
| `TraitDerivesClause` | `LineBreakBoundary "derives" QualifiedTypeReference` | 474 |
| `TraitAutoSupportClause` | `LineBreakBoundary "supports" "auto"` | 475 |
| `TraitBody` | `"{" TraitItem* "}"` | 476 |
| `TraitItem` | `TraitMethodDecl \| AssociatedRequirementDecl \| LawDecl` | 477 |
| `TraitMethodDecl` | `MemberVisibility? DefIntroducer Identifier TraitWitnessMarker TypeParameterList? ParameterList TraitFunctionTail` | 479 |
| `AssociatedRequirementDecl` | `AssociatedTypeRequirementDecl \| AssociatedValueRequirementDecl \| AssociatedFunctionRequirementDecl` | 481 |
| `AssociatedTypeRequirementDecl` | `"type" Identifier AssociatedTypeConstraintList? StatementBoundary` | 484 |
| `AssociatedValueRequirementDecl` | `"let" "::" Identifier TypeAnnotation StatementBoundary` | 485 |
| `AssociatedFunctionRequirementDecl` | `"def" "::" Identifier ParameterList ReturnClause? ThrowsClause* EffectsClause* StatementBoundary` | 486 |
| `ConformanceDecl` | `ExplicitConformanceDecl \| AutomaticConformanceDecl` | 489 |
| `ExplicitConformanceDecl` | `TopLevelVisibility? "type" TypeRef "conforms" QualifiedTypeReference NameAliasClause? ConformanceViaClause? WhereClause? (ConformanceBody \| StatementBoundary)` | 490 |
| `AutomaticConformanceDecl` | `TopLevelVisibility? "type" TypeRef "conforms" QualifiedTypeReference NameAliasClause? ConformanceAutoClause WhereClause? StatementBoundary` | 493 |
| `ConformanceViaClause` | `"via" QualifiedPath` | 495 |
| `ConformanceAutoClause` | `"by" "auto"` | 496 |
| `ConformanceBody` | `"{" ConformanceItem* "}"` | 497 |
| `ConformanceMethodDecl` | `MemberVisibility? DefIntroducer ConformanceMethodName TraitWitnessMarker FunctionRest` | 498 |
| `ConformanceMethodName` | `Identifier \| QualifiedTypeReference "::" Identifier` | 500 |
| `ConformBlockDecl` | `"conform" QualifiedTypeReference ConformanceBody` | 506 |
| `ConformanceItem` | `ConformanceMethodDecl \| TypeSideMemberFunctionDecl \| AssociatedRequirementBinding \| ExtensionDelegationDecl \| LawDecl` | 507 |
| `AssociatedRequirementBinding` | `"type" Identifier "=" TypeRef StatementBoundary \| "let" "::" Identifier "=" Expr StatementBoundary` | 512 |
| `ExtensionDelegationDecl` | `"delegate" Identifier "to" QualifiedExtensionSelector StatementBoundary` | 514 |
| `ExtensionSetDecl` | `TopLevelVisibility? "extension" TypeRef "as" Identifier ExtensionSetBody` | 518 |
| `ExtensionSetBody` | `"{" ExtensionSetItem* "}"` | 519 |
| `ExtensionSetItem` | `ExtensionSetFunctionDecl \| TypeSideMemberFunctionDecl` | 520 |
| `ExtensionSetFunctionDecl` | `MemberVisibility? "def" Identifier ParameterList? ReturnClause? ThrowsClause* EffectsClause* WhereClause? FunctionBody` | 521 |
| `ExtensionPackDecl` | `"extension" "pack" QualifiedPath ExtensionPackBody` | 523 |
| `ExtensionPackBody` | `"{" UseExportDecl* "}"` | 524 |
| `EnumDecl` | `TopLevelVisibility? "enum" EnumOrderRole? Identifier TypeParameterList? NominalConformanceClause* EnumBody` | 528 |
| `EnumOrderRole` | `"#" ("increasing" \| "decreasing")` | 530 |
| `EnumBody` | `"{" (EnumCommaCaseSequence \| EnumLayoutBody)? "}"` | 531 |
| `EnumCommaCaseSequence` | `EnumCaseCore ("," EnumCaseCore)+ ","?` | 532 |
| `EnumLayoutBody` | `EnumCaseDecl* EnumMemberDecl*` | 533 |
| `EnumCaseDecl` | `EnumCaseCore StatementBoundary?` | 534 |
| `EnumCaseCore` | `Identifier EnumCasePayload? EnumCaseDisplayMapping?` | 535 |
| `EnumCasePayload` | `"(" EnumCaseFieldList? ")"` | 536 |
| `EnumCaseFieldList` | `EnumCaseField ("," EnumCaseField)* ","?` | 537 |
| `EnumCaseField` | `Identifier TypeAnnotation \| TypeRef` | 538 |
| `EnumMemberDecl` | `MemberFunctionDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| ConformBlockDecl \| EnumVariantSubsetAliasDecl` | 539 |
| `EnumCaseDisplayMapping` | `"~>" RestrictedEnumDisplayTemplate` | 545 |
| `RestrictedEnumDisplayTemplate` | `PLAIN_STRING_LITERAL \| MULTILINE_STRING_LITERAL \| InterpolatedString` | 546 |
| `EnumVariantSubsetAliasDecl` | `"+" "type" Identifier "=" EnumVariantSubsetRhs StatementBoundary?` | 549 |
| `EnumVariantSubsetRhs` | `Identifier ("\|" Identifier)*` | 551 |
| `SchemaDecl` | `TopLevelVisibility? "schema" Identifier TypeParameterList? SchemaBody` | 555 |
| `SchemaBody` | `"{" SchemaFieldSequence? "}"` | 556 |
| `SchemaFieldSequence` | `CommaSchemaFields \| LayoutSchemaFields` | 557 |
| `CommaSchemaFields` | `SchemaFieldDecl ("," SchemaFieldDecl)* ","?` | 558 |
| `LayoutSchemaFields` | `LineBreakBoundary LayoutSchemaFieldDecl (LineBreakBoundary LayoutSchemaFieldDecl)* LineBreakBoundary?` | 559 |
| `SchemaFieldDecl` | `Identifier TypeAnnotation Initializer? SchemaConstraint* StatementBoundary?` | 560 |
| `LayoutSchemaFieldDecl` | `Identifier TypeAnnotation Initializer? SchemaConstraint*` | 561 |
| `SchemaConstraint` | `"where" Expr` | 562 |
| `TypeAliasDecl` | `TopLevelVisibility? "type" Identifier TypeParameterList? "=" TypeAliasRhs StatementBoundary` | 564 |
| `TypeAliasRhs` | `TypeRef RefinementSuffix? \| StaticRangeType` | 565 |
| `StaticRangeType` | `StaticIntLiteral ".." StaticIntLiteral` | 566 |
| `TopLevelBindingDecl` | `TopLevelVisibility? ("let" \| "var") Identifier TypeAnnotation? "=" Expr StatementBoundary` | 568 |
| `NamedEffectCapabilityDecl` | `TopLevelVisibility? "capability" Identifier "for" EffectRow StatementBoundary` | 569 |
| `ActorDecl` | `TopLevelVisibility? "actor" MailboxClause? Identifier ActorProtocolConformanceClause* ActorBody` | 573 |
| `MailboxClause` | `HashTag "(" "capacity" ":" StaticIntLiteral ")"` | 575 |
| `ActorBody` | `"{" ActorItem* "}"` | 576 |
| `ActorProtocolConformanceClause` | `LineBreakBoundary "conforms" QualifiedTypeReference WhereClause?` | 577 |
| `ActorItem` | `ActorOnDecl \| ActorRequestDecl \| ActorMemberDecl \| ActorProtocolConformBlock` | 579 |
| `ActorMemberDecl` | `FieldDecl \| MemberFunctionDecl \| ConstructorDecl \| CleanupDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| ForwardDecl` | 583 |
| `ActorOnDecl` | `MemberVisibility? "on" Identifier ParameterList? ThrowsClause* EffectsClause* FunctionBody` | 591 |
| `ActorRequestDecl` | `MemberVisibility? "request" Identifier ParameterList? ReturnClause ThrowsClause* EffectsClause* FunctionBody` | 592 |
| `ActorProtocolConformBlock` | `"conform" QualifiedTypeReference ActorProtocolConformanceBody` | 598 |
| `ActorProtocolConformanceBody` | `"{" ActorProtocolConformanceItem* "}"` | 599 |
| `ActorProtocolConformanceItem` | `ActorOnDecl \| ActorRequestDecl` | 600 |
| `ActorProtocolDecl` | `TopLevelVisibility? "protocol" Identifier ActorProtocolBody` | 602 |
| `ActorProtocolBody` | `"{" ActorProtocolItem* "}"` | 603 |
| `ActorProtocolItem` | `ActorProtocolSendRequirement \| ActorProtocolRequestRequirement` | 604 |
| `ActorProtocolSendRequirement` | `"send" Identifier ParameterList? ThrowsClause* EffectsClause* StatementBoundary` | 605 |
| `ActorProtocolRequestRequirement` | `"request" Identifier ParameterList? ReturnClause ThrowsClause* EffectsClause* StatementBoundary` | 606 |
| `TypestateResourceDecl` | `TopLevelVisibility? "typestate" Identifier TypeParameterList? TypestateBody` | 610 |
| `TypestateBody` | `"{" TypestateTransitionDecl* "}"` | 611 |
| `TypestateTransitionDecl` | `Identifier "->" Identifier FunctionBody?` | 612 |
| `UnitCatalogDecl` | `TopLevelVisibility? "unit" "catalog" Identifier UnitCatalogBody` | 614 |
| `UnitCatalogBody` | `"{" UnitCatalogEntry* "}"` | 615 |
| `UnitCatalogEntry` | `ExactRatioUnitConversionDecl \| Identifier "=" UnitExpr StatementBoundary` | 616 |
| `ExactRatioUnitConversionDecl` | `"unit" Identifier "equalsRatio" MeasureLiteralExpr "/" StaticIntLiteral StatementBoundary` | 617 |
| `ModuleInterfaceDecl` | `ModuleSignatureDecl \| OpaqueModuleFacadeDecl` | 619 |
| `ModuleSignatureDecl` | `TopLevelVisibility? "module" "signature" QualifiedPath ModuleInterfaceBody` | 620 |
| `OpaqueModuleFacadeDecl` | `TopLevelVisibility? "opaque" "module" QualifiedPath ModuleInterfaceBody` | 621 |
| `ModuleInterfaceBody` | `"{" ModuleInterfaceItem* "}"` | 622 |
| `ModuleInterfaceItem` | `ExportDecl \| UseExportDecl \| OpaqueModuleFacadeDecl` | 623 |
| `CleanupBudgetClause` | `"cleanup" "budget" "{" CleanupBudgetItem* "}"` | 627 |
| `CleanupBudgetItem` | `EffectsBudget \| ErrorsBudget` | 628 |
| `EffectsBudget` | `"effects" "{" IdentifierList? "}"` | 629 |
| `ErrorsBudget` | `"errors" TypeRef` | 630 |
| `BitfieldDecl` | `TopLevelVisibility? BitfieldIntroducer Identifier BitfieldBackingClause BitfieldOrderClause BitfieldBody` | 634 |
| `BitfieldIntroducer` | `"bitfield" HashTag?` | 636 |
| `BitfieldBackingClause` | `"backing" TypeRef` | 637 |
| `BitfieldOrderClause` | `"order" "::" "lsb0"` | 638 |
| `BitfieldBody` | `"{" BitfieldLayoutSection BitfieldMemberDecl* "}"` | 639 |
| `BitfieldLayoutSection` | `BitfieldSlotDecl+ \| FlagSlotDecl+` | 640 |
| `BitfieldSlotDecl` | `BitfieldNamedSlot StatementBoundary \| BitfieldReservedSlot StatementBoundary` | 641 |
| `FlagSlotDecl` | `FlagNamedSlot StatementBoundary \| BitfieldReservedSlot StatementBoundary` | 642 |
| `BitfieldNamedSlot` | `MemberVisibility? Identifier ":" StaticIntLiteral BitfieldDefault?` | 643 |
| `BitfieldReservedSlot` | `"_" ":" StaticIntLiteral` | 644 |
| `FlagNamedSlot` | `MemberVisibility? Identifier` | 645 |
| `BitfieldDefault` | `"=" Literal` | 646 |
| `BitfieldMemberDecl` | `MemberFunctionDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| LawDecl` | 647 |
| `TypeRef` | `PrattType` | 659 |
| `NonFunctionTypeRef` | `PrattNonFunctionType` | 660 |
| `TypePrimary` | `QualifiedTypeReference \| FacetType \| ParenTypeSyntax \| SharpShapeType \| ExistentialType \| OpaqueType \| TypeofType \| AssociatedProjection` | 663 |
| `TypePrefixParselet` | `OwnershipQualifier` | 671 |
| `TypePostfixParselet` | `"?"` | 672 |
| `TypeInfixOperator` | `"&" \| "\|"` | 673 |
| `QualifiedTypeReference` | `QualifiedPath TypeArgumentList?` | 675 |
| `FacetType` | `"Facet" "<" "borrow" "any" QualifiedTypeReference AssociatedTypeConstraintList? ">"` | 677 |
| `OwnershipQualifier` | `"owned" \| "borrowed" \| "mut" \| "inout"` | 678 |
| `ParenTypeSyntax` | `HashTag* "(" ParenTypeItemList? ")" FunctionTypeTail?` | 682 |
| `ParenTypeItemList` | `ParenTypeItem ("," ParenTypeItem)* ","?` | 683 |
| `ParenTypeItem` | `TypeRef \| TypeRef "..." \| TypeRef "***"` | 684 |
| `FunctionTypeTail` | `"->" ReturnTypeSurface ThrowsClause* EffectsClause*` | 685 |
| `SharpShapeType` | `"#" StaticDimensionList "[" TypeRef "]"` | 687 |
| `StaticDimensionList` | `StaticIntLiteral ("," StaticIntLiteral)*` | 688 |
| `ExistentialType` | `"any" QualifiedTypeReference AssociatedTypeConstraintList?` | 690 |
| `OpaqueType` | `"some" QualifiedTypeReference AssociatedTypeConstraintList?` | 691 |
| `TypeofType` | `"typeof" TypeofStaticSampleOperand` | 692 |
| `AssociatedProjection` | `"<" TypeRef "as" QualifiedTypeReference ">" "::" Identifier` | 693 |
| `TypeofStaticSampleOperand` | `Literal \| ListLiteral \| StaticPrefixedCollectionSample \| NumericArrayLiteral \| MeasureLiteralExpr` | 696 |
| `StaticPrefixedCollectionSample` | `MapLiteral \| SetLiteral \| MutListLiteral` | 701 |
| `PrattType` | `TYPE_PRATT_ENTRY` | 704 |
| `PrattNonFunctionType` | `NON_FUNCTION_TYPE_PRATT_ENTRY` | 705 |
| `Pattern` | `OrPattern` | 713 |
| `OrPattern` | `AliasPattern ("\|" AliasPattern)*` | 714 |
| `AliasPattern` | `MovePattern ("as" Identifier)?` | 715 |
| `MovePattern` | `"move"? PatternPrimary` | 716 |
| `PatternPrimary` | `TypedBindingPattern \| Identifier \| PinPattern \| RangePattern \| RelationalPattern \| TuplePattern \| RecordPattern \| ListPattern \| MapPattern \| VariantPattern \| NominalPattern \| "_" \| UnitSyntax \| Literal \| ParenthesizedPattern` | 718 |
| `TypedBindingPattern` | `Identifier ":" TypeRef` | 734 |
| `ParenthesizedPattern` | `"(" Pattern ")"` | 735 |
| `PinPattern` | `"^" StablePatternValue` | 736 |
| `StablePatternValue` | `Identifier \| QualifiedStaticExpr \| Literal` | 737 |
| `RangePattern` | `PatternBound (".." \| "..<") PatternBound` | 738 |
| `RelationalPattern` | `("<" \| "<=" \| ">" \| ">=") PatternBound` | 739 |
| `PatternBound` | `Literal \| PinPattern` | 740 |
| `TuplePattern` | `"(" TuplePatternItems ")"` | 744 |
| `TuplePatternItems` | `Pattern "," \| Pattern "," Pattern ("," Pattern)* ","?` | 745 |
| `BindingPattern` | `BindingOrPattern TypeAnnotation?` | 757 |
| `BindingOrPattern` | `BindingAliasPattern ("\|" BindingAliasPattern)*` | 758 |
| `BindingAliasPattern` | `BindingMovePattern ("as" Identifier)?` | 759 |
| `BindingMovePattern` | `"move"? BindingPatternPrimary` | 760 |
| `BindingPatternPrimary` | `Identifier \| PinPattern \| RangePattern \| RelationalPattern \| TuplePattern \| RecordPattern \| ListPattern \| MapPattern \| VariantPattern \| NominalPattern \| "_" \| UnitSyntax \| Literal \| ParenthesizedPattern` | 761 |
| `RecordPattern` | `"${" RecordPatternEntries? "}"` | 780 |
| `RecordPatternEntries` | `RecordPatternEntry (PatternEntrySeparator RecordPatternEntry)* PatternEntrySeparator?` | 781 |
| `RecordPatternEntry` | `Identifier \| RecordDestination ":" Identifier \| RecordRestPattern` | 783 |
| `RecordDestination` | `Pattern` | 784 |
| `RecordRestPattern` | `".." RestBinder` | 785 |
| `MapPattern` | `"#" "map" "{" MapPatternEntries? "}"` | 787 |
| `MapPatternEntries` | `MapPatternEntry (PatternEntrySeparator MapPatternEntry)* PatternEntrySeparator?` | 788 |
| `MapPatternEntry` | `MapDestination ":" MapKeyPattern \| MapRestPattern` | 790 |
| `MapDestination` | `Pattern` | 791 |
| `MapKeyPattern` | `Literal \| PinPattern` | 792 |
| `MapRestPattern` | `".." RestBinder` | 793 |
| `PatternEntrySeparator` | `"," LineBreakBoundary? \| LineBreakBoundary` | 794 |
| `ListPattern` | `"[" ListPatternBody? "]"` | 800 |
| `ListPatternBody` | `IgnoredAllListRest \| ExactListPattern \| PrefixRestListPattern \| SuffixRestListPattern \| MiddleRestListPattern` | 801 |
| `ExactListPattern` | `Pattern ("," Pattern)* ","?` | 806 |
| `PrefixRestListPattern` | `PrefixListRest "," Pattern ("," Pattern)* ","?` | 807 |
| `SuffixRestListPattern` | `Pattern ("," Pattern)* "," SuffixListRest ","?` | 808 |
| `MiddleRestListPattern` | `Pattern ("," Pattern)* "," MiddleListRest "," Pattern ("," Pattern)* ","?` | 809 |
| `PrefixListRest` | `RestBinder ".."` | 811 |
| `SuffixListRest` | `".." RestBinder` | 812 |
| `MiddleListRest` | `".." RestBinder ".."` | 813 |
| `IgnoredAllListRest` | `".." "_" ","?` | 814 |
| `RestBinder` | `Identifier \| "_"` | 815 |
| `VariantPattern` | `VariantQualifier Identifier VariantPatternPayload?` | 817 |
| `VariantQualifier` | `TypeRef "::" \| "::"` | 818 |
| `VariantPatternPayload` | `VariantPositionalPatternPayload \| RecordPattern` | 819 |
| `VariantPositionalPatternPayload` | `"(" PatternList? ")"` | 820 |
| `NominalPattern` | `TypeRef RecordPattern` | 825 |
| `Stmt` | `ForLoop \| WhileLoop \| RepeatLoop \| AsyncForLoop \| MatchStatement \| IfStmt \| LocalBindingStmt \| AssertiveBindingStmt \| PatternAssignmentStmt \| ParallelAssignmentStmt \| ControlTransferStmt \| TryStmt \| DeferStmt \| ScopedUseStmt \| ExprStmt \| ScopedImportStmt` | 833 |
| `ExprStmt` | `Expr StatementBoundary` | 850 |
| `Block` | `"{" BlockPrologue? BlockSequence "}"` | 852 |
| `BlockPrologue` | `(UseDecl \| ImportDecl)+` | 853 |
| `BlockSequence` | `BlockItem* BlockFinalItem?` | 854 |
| `BlockItem` | `LocalFunctionDecl \| Stmt` | 855 |
| `BlockFinalItem` | `ControlTransfer \| BindingCore \| Expr` | 858 |
| `ValueBody` | `SingleExpressionValueBody \| ExplicitRetValueBody` | 861 |
| `SingleExpressionValueBody` | `"{" ReturnValueSurface "}"` | 862 |
| `ExplicitRetValueBody` | `"{" BlockItem* RetTransfer "}"` | 863 |
| `RetTransfer` | `"ret" ReturnValueSurface? GuardClause?` | 864 |
| `BindingCore` | `("let" \| "var") BindingHead "=" BindingValueSurface` | 869 |
| `BindingHead` | `BindingPattern \| BareTupleBindingSurface` | 870 |
| `BareTupleBindingSurface` | `BindingPattern "," BindingPattern ("," BindingPattern)*` | 871 |
| `BindingValueSurface` | `Expr \| BareTupleValueSurface` | 872 |
| `ReturnValueSurface` | `Expr \| BareTupleValueSurface` | 873 |
| `BareTupleValueSurface` | `Expr "," Expr ("," Expr)*` | 874 |
| `LocalBindingStmt` | `BindingCore StatementBoundary \| RightwardLocalBindingSurface \| LazyBindingStmt \| GuardedBindingStmt` | 875 |
| `LazyBindingStmt` | `"let" HashTag Identifier TypeAnnotation? "=" Expr StatementBoundary` | 876 |
| `GuardedBindingStmt` | `("let" \| "var") BindingPattern "=" Expr "else" GuardedBindingFailure StatementBoundary?` | 877 |
| `AssertiveBindingStmt` | `("let" \| "var") "!" BindingPattern "=" Expr StatementBoundary` | 878 |
| `GuardedBindingFailure` | `GuardedBindingExit \| Pattern "=>" GuardedBindingExit` | 880 |
| `GuardedBindingExit` | `GuardedReturnExit \| GuardedThrowExit \| GuardedBreakExit \| GuardedContinueExit` | 881 |
| `GuardedReturnExit` | `"return" Expr?` | 882 |
| `GuardedThrowExit` | `"throw" Expr` | 883 |
| `GuardedBreakExit` | `("break")+ Expr?` | 884 |
| `GuardedContinueExit` | `("break")* "continue"` | 885 |
| `ControlTransferStmt` | `ControlTransfer StatementBoundary` | 888 |
| `ControlTransfer` | `ReturnTransfer \| ThrowTransfer \| BreakTransfer \| ContinueTransfer \| YieldTransfer` | 889 |
| `ReturnTransfer` | `"return" ReturnValueSurface? GuardClause?` | 890 |
| `ThrowTransfer` | `"throw" Expr GuardClause?` | 891 |
| `BreakTransfer` | `("break")+ Expr? GuardClause?` | 892 |
| `ContinueTransfer` | `("break")* "continue" GuardClause?` | 893 |
| `YieldTransfer` | `"yield" Expr? (GuardClause \| YieldResponseBinding)?` | 894 |
| `YieldResponseBinding` | `"->" DollarLocalBinding` | 895 |
| `DollarLocalBinding` | `"$" Identifier TypeAnnotation? \| "$$" Identifier TypeAnnotation?` | 896 |
| `GuardClause` | `PositiveGuard \| NegativeGuard` | 898 |
| `PositiveGuard` | `"if" Expr` | 899 |
| `NegativeGuard` | `"!" "if" Expr` | 900 |
| `IfStmt` | `"if" PatternConditionChain Block ("else" (IfStmt \| Block))?` | 902 |
| `PatternConditionChain` | `PatternControlCondition ("and" "then" PatternControlCondition)*` | 905 |
| `PatternControlCondition` | `Expr \| "let" Pattern "=" Expr` | 907 |
| `ForLoop` | `"for" ("let" Pattern \| Pattern) "in" Expr GuardClause? Block MatchStatement?` | 911 |
| `WhileLoop` | `"while" PatternConditionChain Block MatchStatement?` | 912 |
| `RepeatLoop` | `"repeat" Block "while" Expr MatchStatement?` | 913 |
| `AsyncForLoop` | `"for" ForAwaitRole ("let" Pattern \| Pattern) "in" Expr GuardClause? Block` | 917 |
| `ForAwaitRole` | `"#" "await"` | 918 |
| `MatchStatement` | `"match" MatchCore` | 920 |
| `MatchCore` | `MatchSubjectSlot MatchBody` | 921 |
| `MatchSubjectSlot` | `MATCH_SUBJECT_BY_INPUT_SUPPLY_POLICY` | 922 |
| `MatchBody` | `"{" LineBreakBoundary? MatchArmSequence "}"` | 923 |
| `MatchArmSequence` | `MatchArm (MatchArmSeparator MatchArm)* MatchArmSeparator?` | 924 |
| `MatchArm` | `MatchHead GuardClause? "=>" MatchArmBodySlot` | 925 |
| `MatchHead` | `BoundedBinderPattern \| Pattern \| "otherwise"` | 926 |
| `BoundedBinderPattern` | `PatternBound OrderedComparisonOperator Identifier OrderedComparisonOperator PatternBound` | 932 |
| `MatchArmSeparator` | `MATCH_ARM_SEPARATOR_BY_CONTEXT` | 934 |
| `MatchArmBodySlot` | `MATCH_ARM_BODY_BY_CONTEXT` | 935 |
| `TryStmt` | `"try" Block (CatchClause+ FinallyClause? \| FinallyClause)` | 939 |
| `CatchClause` | `"catch" Pattern? GuardClause? Block` | 940 |
| `ValueCatchClause` | `"catch" Pattern? GuardClause? ValueBody` | 941 |
| `FinallyClause` | `"finally" Block` | 942 |
| `DeferStmt` | `"defer" DeferredCleanupInvocation StatementBoundary` | 944 |
| `DeferredCleanupInvocation` | `DeferredDirectCall \| DeferredMessageCall` | 947 |
| `DeferredDirectCall` | `DeferredReceiver ArgumentList` | 948 |
| `DeferredMessageCall` | `DeferredReceiver "~" MessageSelector TildeArgumentSequence?` | 949 |
| `DeferredReceiver` | `DeferredPrimary DeferTargetSuffix*` | 950 |
| `DeferredPrimary` | `Identifier \| QualifiedStaticExpr` | 951 |
| `DeferTargetSuffix` | `IndexSuffix \| MemberSuffix` | 952 |
| `RightwardLocalBindingSurface` | `Expr "->" DollarLocalBinding StatementBoundary` | 956 |
| `PatternAssignmentStmt` | `AssigneePattern "=" Expr StatementBoundary` | 960 |
| `AssigneePattern` | `AssigneeTuplePattern \| AssigneeListPattern \| AssigneeRecordPattern \| AssigneeNominalPattern` | 961 |
| `AssigneePrimary` | `Identifier \| "_"` | 965 |
| `AssigneeTuplePattern` | `"(" AssigneeTupleItems ")"` | 966 |
| `AssigneeTupleItems` | `AssigneePatternItem "," \| AssigneePatternItem "," AssigneePatternItem ("," AssigneePatternItem)* ","?` | 967 |
| `AssigneePatternItem` | `AssigneePrimary \| AssigneeTuplePattern \| AssigneeListPattern \| AssigneeRecordPattern` | 970 |
| `AssigneeListPattern` | `"[" AssigneeListBody? "]"` | 974 |
| `AssigneeListBody` | `AssigneeIgnoredAllRest \| AssigneeExactList \| AssigneePrefixRestList \| AssigneeSuffixRestList \| AssigneeMiddleRestList` | 975 |
| `AssigneeExactList` | `AssigneePatternItem ("," AssigneePatternItem)* ","?` | 980 |
| `AssigneePrefixRestList` | `Identifier ".." "," AssigneeExactList` | 981 |
| `AssigneeSuffixRestList` | `AssigneeExactList "," ".." Identifier ","?` | 982 |
| `AssigneeMiddleRestList` | `AssigneeExactList "," ".." Identifier ".." "," AssigneeExactList` | 983 |
| `AssigneeIgnoredAllRest` | `".." "_" ","?` | 985 |
| `AssigneeRestPattern` | `".." ("_" \| Identifier)` | 986 |
| `AssigneeRecordPattern` | `"${" AssigneeRecordEntries? "}"` | 987 |
| `AssigneeRecordEntries` | `AssigneeRecordEntry (PatternEntrySeparator AssigneeRecordEntry)* PatternEntrySeparator?` | 988 |
| `AssigneeRecordEntry` | `Identifier \| AssigneePrimary ":" Identifier \| AssigneeRestPattern` | 991 |
| `AssigneeNominalPattern` | `TypeRef AssigneeRecordPattern` | 992 |
| `ParallelAssignmentStmt` | `BareTuplePlaceSurface "=" AssignmentValueSurface StatementBoundary` | 993 |
| `BareTuplePlaceSurface` | `Identifier "," Identifier ("," Identifier)*` | 994 |
| `AssignmentValueSurface` | `Expr \| BareTupleValueSurface` | 995 |
| `ScopedUseStmt` | `"use" ScopedPathList "in" Block` | 996 |
| `ScopedImportStmt` | `"import" ScopedPathList "in" Block` | 997 |
| `ScopedPathList` | `QualifiedPath ("," QualifiedPath)*` | 998 |
| `Expr` | `PrattExpr` | 1006 |
| `PredicateExpr` | `PrattPredicateExpr` | 1007 |
| `SliceIndexExpr` | `PrattSliceIndexExpr` | 1008 |
| `ExpressionPrefixParselet` | `"+" \| "-" \| "not" \| "~~" \| "move" \| "borrow" \| "&" \| "await"` | 1014 |
| `ExpressionPostfixParselet` | `CallSuffix \| TildeCallLed \| TupleOrdinalSuffix \| IndexSuffix \| MemberSuffix \| NumericArrayTransposeSuffix \| ConstructorCallSuffix \| NamedConstructorCallSuffix \| PrototypeDerivationSuffix \| CastSuffix` | 1016 |
| `PrimaryExpr` | `Literal \| Identifier \| ImplicitAtExpr \| ParenExprSyntax \| ListLiteral \| BoundedListLiteral \| ComprehensionExpr \| MaterializationBody \| TypedMaterializationExpr \| MapLiteral \| SetLiteral \| MutListLiteral \| MapComprehensionExpr \| SetComprehensionExpr \| NumericArrayLiteral \| MeasureLiteralExpr \| QualifiedStaticExpr \| ExpectedVariantExpr \| AtControlExpr \| MatchExpr \| ClosureExpr \| GeneratorExpr \| SpawnExpr \| ConcurExpr \| UnsafeBlockExpr \| FacetExpr` | 1027 |
| `ParenExprSyntax` | `"(" ParenExprContent? ")"` | 1055 |
| `ParenExprContent` | `Expr ParenExprTail?` | 1056 |
| `ParenExprTail` | `"," \| "," Expr ("," Expr)* ","?` | 1057 |
| `ImplicitAtExpr` | `"@"` | 1058 |
| `ExpectedVariantExpr` | `"::" Identifier` | 1059 |
| `CallSuffix` | `ArgumentList TrailingClosureGroup? \| AtomicCallArgument TrailingClosureGroup` | 1063 |
| `ArgumentList` | `"(" ")" \| "(" CommaArgumentSequence ")" \| "(" LayoutArgumentSequence ")"` | 1066 |
| `CommaArgumentSequence` | `Argument ("," Argument)* ","?` | 1069 |
| `LayoutArgumentSequence` | `LineBreakBoundary NamedLayoutArgument LineBreakBoundary NamedLayoutArgument (LineBreakBoundary NamedLayoutArgument)* LineBreakBoundary?` | 1071 |
| `NamedLayoutArgument` | `NamedArgument \| NamedUnfoldArgument` | 1073 |
| `Argument` | `ContextArgument \| WitnessArgument \| NamedArgument \| PositionalUnfoldArgument \| NamedUnfoldArgument \| Expr` | 1074 |
| `ContextArgument` | `"context" Expr` | 1080 |
| `WitnessArgument` | `"using" WitnessArgumentValue` | 1081 |
| `WitnessArgumentValue` | `Identifier \| ConformanceEvidenceSelector \| NamedConformanceEvidenceSelector` | 1082 |
| `NamedArgument` | `Identifier ":" Expr` | 1083 |
| `PositionalUnfoldArgument` | `"*" Expr` | 1084 |
| `NamedUnfoldArgument` | `"**" Expr` | 1085 |
| `AtomicCallArgument` | `Literal \| Identifier \| QualifiedStaticExpr \| ExpectedVariantExpr` | 1086 |
| `TrailingClosureGroup` | `TrailingClosureArgument+` | 1090 |
| `TrailingClosureArgument` | `ClosureExpr \| Identifier ":" ClosureExpr` | 1091 |
| `IndexSuffix` | `"[" SliceAxisList "]"` | 1095 |
| `SliceAxisList` | `SliceAxis (";" SliceAxis)*` | 1096 |
| `SliceAxis` | `SliceRange \| SliceIndexExpr \| AxisWildcard` | 1097 |
| `SliceRange` | `SliceBound (".." \| "..<") SliceBound` | 1100 |
| `SliceBound` | `SliceIndexExpr \| "^" \| "$" \| "^" OffsetExpr \| "$" OffsetExpr` | 1101 |
| `OffsetExpr` | `("+" \| "-") NumericLiteral` | 1102 |
| `AxisWildcard` | `"*"` | 1103 |
| `TupleOrdinalSuffix` | `"." StaticIntLiteral` | 1105 |
| `MemberSuffix` | `"." Identifier \| "." "\\\\" NAME_TOKEN` | 1106 |
| `TildeCallLed` | `TildeCallToken MessageSelector TildeArgumentSequence? TrailingClosureGroup?` | 1112 |
| `TildeCallToken` | `"~" \| ":~"` | 1114 |
| `MessageSelector` | `Identifier \| QualifiedMessageSelector` | 1115 |
| `QualifiedMessageSelector` | `TypeRef "::" Identifier ("::" Identifier)?` | 1116 |
| `QualifiedExtensionSelector` | `TypeRef "::" Identifier "::" Identifier` | 1117 |
| `TildeArgumentSequence` | `TildeArgument ("," TildeArgument)*` | 1118 |
| `TildeArgument` | `ContextArgument \| WitnessArgument \| NamedArgument \| PositionalUnfoldArgument \| NamedUnfoldArgument \| Expr` | 1119 |
| `NumericArrayTransposeSuffix` | `"^"` | 1126 |
| `ConstructorCallSuffix` | `"!" ArgumentList` | 1127 |
| `NamedConstructorCallSuffix` | `"!" Identifier ArgumentList` | 1128 |
| `PrototypeDerivationSuffix` | `("!" \| "!!") DerivationBody` | 1129 |
| `DerivationBody` | `"{" MaterializationEntryList? "}"` | 1130 |
| `CastSuffix` | `"as" "?" TypeRef \| "as" "!" TypeRef` | 1132 |
| `QualifiedStaticExpr` | `StaticQualifier "::" Identifier \| TraitQualifiedAssociatedSelector` | 1134 |
| `StaticQualifier` | `QualifiedTypeReference \| AssociatedProjection` | 1136 |
| `TraitQualifiedAssociatedSelector` | `"<" TypeRef "as" QualifiedTypeReference ">" "::" Identifier` | 1137 |
| `AtControlExpr` | `AtIfExpr \| AtTryExpr \| AtScopeExpr` | 1143 |
| `AtIfExpr` | `"@" "if" Expr ValueBody "else" ValueBody` | 1145 |
| `AtTryExpr` | `"@" "try" ValueBody (ValueCatchClause+ FinallyClause? \| FinallyClause)` | 1146 |
| `AtScopeExpr` | `"@" "scope" ScopeModifier* ValueBody` | 1147 |
| `ScopeModifier` | `"isolated" \| "cancellable" \| "shielded"` | 1148 |
| `MatchExpr` | `"@" "match" MatchCore` | 1150 |
| `ClosureExpr` | `CaptureList? HashTag* "{" ClosureContent "}"` | 1154 |
| `ClosureContent` | `ExplicitLambdaContent \| LambdaBody?` | 1159 |
| `ExplicitLambdaContent` | `LambdaParameterList? "=>" LambdaBody` | 1160 |
| `LambdaParameterList` | `LambdaParameter ("," LambdaParameter)* ","?` | 1161 |
| `LambdaParameter` | `ParameterMode? LambdaParameterPattern TypeAnnotation?` | 1162 |
| `LambdaParameterPattern` | `Identifier \| IrrefutableParameterPattern` | 1163 |
| `LambdaBody` | `ReturnValueSurface \| LineBreakBoundary LambdaBlockContent` | 1164 |
| `LambdaBlockContent` | `BlockItem* LambdaFinalItem?` | 1165 |
| `LambdaFinalItem` | `RetTransfer \| Expr` | 1166 |
| `CaptureList` | `"[" CaptureItemList? "]"` | 1168 |
| `CaptureItemList` | `CaptureItem ("," CaptureItem)* ","?` | 1169 |
| `CaptureItem` | `("let" \| "var") Identifier "=" Expr \| CaptureMode Identifier \| Identifier` | 1170 |
| `CaptureMode` | `"borrow" \| "inout" \| "move" \| "clone" \| "deep" \| "copy" \| "once"` | 1173 |
| `GeneratorExpr` | `CaptureList? GeneratorCore` | 1186 |
| `GeneratorCore` | `"@" "for" Pattern "in" Expr Block \| "@" "while" Expr Block \| "@" "repeat" Block "while" Expr` | 1187 |
| `SpawnExpr` | `"spawn" (SpawnBody \| SpawnOperandSlot)` | 1195 |
| `SpawnBody` | `"{" "=>" SpawnBodySequence "}"` | 1196 |
| `SpawnBodySequence` | `LineBreakBoundary? BlockSequence` | 1197 |
| `SpawnOperandSlot` | `SPAWN_OPERAND_BY_PREFIX_PARSER` | 1198 |
| `ConcurExpr` | `"concur" Block` | 1199 |
| `UnsafeBlockExpr` | `"unsafe" Block` | 1200 |
| `FacetExpr` | `"facet" "[" "borrow" Expr "as" QualifiedTypeReference AssociatedTypeConstraintList? "]"` | 1203 |
| `ConformanceEvidenceSelector` | `"conformance" "(" TypeRef "conforms" QualifiedTypeReference ")"` | 1205 |
| `NamedConformanceEvidenceSelector` | `ConformanceEvidenceSelector "::" Identifier` | 1206 |
| `PrattExpr` | `EXPRESSION_PRATT_ENTRY` | 1209 |
| `PrattPredicateExpr` | `PREDICATE_PRATT_ENTRY` | 1210 |
| `PrattSliceIndexExpr` | `SLICE_INDEX_PRATT_ENTRY` | 1211 |
| `Literal` | `BoolLiteral \| NumericLiteral \| ImaginaryLiteralExpr \| RationalLiteralExpr \| StringLiteralExpr \| CharLiteralExpr \| BytesLiteral` | 1219 |
| `BoolLiteral` | `"true" \| "false"` | 1226 |
| `NumericLiteral` | `NUMERIC_LITERAL` | 1227 |
| `ImaginaryLiteralExpr` | `IMAGINARY_LITERAL` | 1228 |
| `RationalLiteralExpr` | `RATIONAL_LITERAL` | 1229 |
| `CharLiteralExpr` | `CHAR_LITERAL` | 1230 |
| `BytesLiteral` | `BYTES_LITERAL` | 1231 |
| `StringLiteralExpr` | `PLAIN_STRING_LITERAL \| RAW_STRING_LITERAL \| MULTILINE_STRING_LITERAL \| InterpolatedString` | 1234 |
| `InterpolatedString` | `STRING_START InterpolatedStringPart* STRING_END` | 1235 |
| `InterpolatedStringPart` | `STRING_TEXT \| STRING_ESCAPE \| InterpolationExpr \| InterpolationPath` | 1236 |
| `InterpolationExpr` | `INTERPOLATION_OPEN Expr InterpolationFormat? INTERPOLATION_CLOSE` | 1240 |
| `InterpolationFormat` | `":" INTERPOLATION_FORMAT_TEXT` | 1241 |
| `InterpolationPath` | `"$" InterpolationPathRoot InterpolationPathSelector* INTERPOLATION_BOUNDARY?` | 1246 |
| `InterpolationPathRoot` | `Identifier \| "@"` | 1247 |
| `InterpolationPathSelector` | `"." Identifier \| "." StaticIntLiteral \| "[" InterpolationIndex "]"` | 1248 |
| `InterpolationIndex` | `StaticIntLiteral \| Identifier` | 1251 |
| `ListLiteral` | `"[" ExpressionList? "]"` | 1256 |
| `BoundedListLiteral` | `"[" StaticIntLiteral ".." StaticIntLiteral ":" ExpressionList? "]"` | 1257 |
| `ComprehensionExpr` | `"[" Expr ComprehensionClause+ "]"` | 1259 |
| `TypedMaterializationExpr` | `TypeRef MaterializationBody` | 1262 |
| `MaterializationBody` | `"${" MaterializationEntryList? "}"` | 1263 |
| `MaterializationEntryList` | `MaterializationEntry (MaterializationSeparator MaterializationEntry)* MaterializationSeparator?` | 1264 |
| `MaterializationEntry` | `Identifier \| Identifier ":" Expr \| StringLiteralExpr ":" Expr \| NamedUnfoldArgument` | 1265 |
| `MaterializationSeparator` | `"," LineBreakBoundary? \| LineBreakBoundary` | 1269 |
| `MapLiteral` | `"#" "map" "{" MapEntryList? "}"` | 1272 |
| `MapEntryList` | `MapEntry (MaterializationSeparator MapEntry)* MaterializationSeparator?` | 1273 |
| `MapEntry` | `Expr ":" Expr \| NamedUnfoldArgument` | 1274 |
| `SetLiteral` | `"#" "set" "{" ExpressionList? "}"` | 1275 |
| `MutListLiteral` | `"#" "mut" "[" ExpressionList? "]"` | 1276 |
| `MapComprehensionExpr` | `"#" "map" "{" MapEntry ComprehensionClause+ "}"` | 1277 |
| `SetComprehensionExpr` | `"#" "set" "{" Expr ComprehensionClause+ "}"` | 1278 |
| `ComprehensionClause` | `ForClause \| PositiveGuard \| IfLetClause \| UnfoldClause` | 1280 |
| `ForClause` | `"for" Pattern "in" Expr` | 1281 |
| `IfLetClause` | `"if" "let" Pattern "=" Expr` | 1282 |
| `UnfoldClause` | `"for" "..." Pattern "in" Expr` | 1283 |
| `NumericArrayLiteral` | `ShapeInferredArrayLiteral \| ShapeInferredColumnVectorLiteral \| ExactShapeArrayLiteral` | 1286 |
| `ShapeInferredArrayLiteral` | `"#" "[" ExpressionList? "]"` | 1289 |
| `ShapeInferredColumnVectorLiteral` | `"#" "[" Expr (";" Expr)+ "]"` | 1290 |
| `ExactShapeArrayLiteral` | `"#" StaticDimensionList "[" ArrayInitializer? "]"` | 1291 |
| `ArrayInitializer` | `ShapedRepeatInitializer \| ShapedGeneratorInitializer \| ShapedElementSequence` | 1292 |
| `ShapedRepeatInitializer` | `"repeat" ":" Expr` | 1295 |
| `ShapedGeneratorInitializer` | `"generate" ":" Expr` | 1296 |
| `ShapedElementSequence` | `Expr (ShapedElementSeparator Expr)* ShapedElementSeparator?` | 1297 |
| `ShapedElementSeparator` | `"," \| ShapedAxisBoundary` | 1298 |
| `ShapedAxisBoundary` | `";" ";"*` | 1299 |
| `MeasureLiteralExpr` | `NumericLiteral "[" UnitExpr "]"` | 1302 |
| `UnitExpr` | `PrattUnitExpr` | 1303 |
| `UnitPrimary` | `Identifier \| QualifiedPath \| "(" UnitExpr ")"` | 1304 |
| `UnitPostfixParselet` | `"^" SignedStaticInt` | 1305 |
| `UnitInfixOperator` | `"*" \| "/"` | 1306 |
| `PrattUnitExpr` | `UNIT_PRATT_ENTRY` | 1307 |

## `PREVIEW` 프로파일 — 13개

| 문법 production | 정확한 EBNF 오른쪽 항 | 원천 줄 |
|---|---|---:|
| `DeeplusPreview` | `PreviewLibrarySourceFile \| PreviewExecutableSourceFile \| PreviewScriptSourceFile` | 1316 |
| `PreviewLibrarySourceFile` | `PreviewGate ModuleDecl? PreviewLibraryItem*` | 1317 |
| `PreviewExecutableSourceFile` | `PreviewGate ModuleDecl? PreviewExecutableItem*` | 1318 |
| `PreviewScriptSourceFile` | `Shebang? PreviewGate ModuleDecl? PreviewScriptItem*` | 1319 |
| `PreviewLibraryItem` | `LibrarySourceItem \| PreviewFfiDecl` | 1321 |
| `PreviewExecutableItem` | `ExecutableSourceItem \| PreviewFfiDecl` | 1322 |
| `PreviewScriptItem` | `ScriptSourceItem \| PreviewFfiDecl` | 1323 |
| `PreviewGate` | `"#" "preview" "(" PreviewFeatureList ")" LineBreakBoundary` | 1325 |
| `PreviewFeatureList` | `Identifier ("," Identifier)*` | 1326 |
| `PreviewFfiDecl` | `PreviewFfiFunctionDecl \| PreviewFfiBlockDecl` | 1329 |
| `PreviewFfiFunctionDecl` | `"extern" "#" "C" "def" "#" "unsafe" Identifier ParameterList ReturnClause? ThrowsClause* EffectsClause* StatementBoundary` | 1330 |
| `PreviewFfiBlockDecl` | `"extern" "c" "(" PLAIN_STRING_LITERAL ")" "{" PreviewFfiBlockMember* "}"` | 1332 |
| `PreviewFfiBlockMember` | `"unsafe" "def" Identifier ParameterList ReturnClause? ThrowsClause* EffectsClause* StatementBoundary` | 1334 |
