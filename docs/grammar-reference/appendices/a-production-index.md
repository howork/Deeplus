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

## `STABLE` 프로파일 — 533개

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
| `ConformBlockDecl` | `"conform" QualifiedTypeReference ConformanceBody` | 505 |
| `ConformanceItem` | `ConformanceMethodDecl \| TypeSideMemberFunctionDecl \| AssociatedRequirementBinding \| ExtensionDelegationDecl \| LawDecl` | 506 |
| `AssociatedRequirementBinding` | `"type" Identifier "=" TypeRef StatementBoundary \| "let" "::" Identifier "=" Expr StatementBoundary` | 511 |
| `ExtensionDelegationDecl` | `"delegate" Identifier "to" QualifiedExtensionSelector StatementBoundary` | 513 |
| `ExtensionSetDecl` | `TopLevelVisibility? "extension" TypeRef "as" Identifier ExtensionSetBody` | 517 |
| `ExtensionSetBody` | `"{" ExtensionSetItem* "}"` | 518 |
| `ExtensionSetItem` | `ExtensionSetFunctionDecl \| TypeSideMemberFunctionDecl` | 519 |
| `ExtensionSetFunctionDecl` | `MemberVisibility? "def" Identifier ParameterList? ReturnClause? ThrowsClause* EffectsClause* WhereClause? FunctionBody` | 520 |
| `ExtensionPackDecl` | `"extension" "pack" QualifiedPath ExtensionPackBody` | 522 |
| `ExtensionPackBody` | `"{" UseExportDecl* "}"` | 523 |
| `EnumDecl` | `TopLevelVisibility? "enum" EnumOrderRole? Identifier TypeParameterList? NominalConformanceClause* EnumBody` | 527 |
| `EnumOrderRole` | `"#" ("increasing" \| "decreasing")` | 529 |
| `EnumBody` | `"{" (EnumCommaCaseSequence \| EnumLayoutBody)? "}"` | 530 |
| `EnumCommaCaseSequence` | `EnumCaseCore ("," EnumCaseCore)+ ","?` | 531 |
| `EnumLayoutBody` | `EnumCaseDecl* EnumMemberDecl*` | 532 |
| `EnumCaseDecl` | `EnumCaseCore StatementBoundary?` | 533 |
| `EnumCaseCore` | `Identifier EnumCasePayload? EnumCaseDisplayMapping?` | 534 |
| `EnumCasePayload` | `"(" EnumCaseFieldList? ")"` | 535 |
| `EnumCaseFieldList` | `EnumCaseField ("," EnumCaseField)* ","?` | 536 |
| `EnumCaseField` | `Identifier TypeAnnotation \| TypeRef` | 537 |
| `EnumMemberDecl` | `MemberFunctionDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| ConformBlockDecl \| EnumVariantSubsetAliasDecl` | 538 |
| `EnumCaseDisplayMapping` | `"~>" RestrictedEnumDisplayTemplate` | 544 |
| `RestrictedEnumDisplayTemplate` | `PLAIN_STRING_LITERAL \| MULTILINE_STRING_LITERAL \| InterpolatedString` | 545 |
| `EnumVariantSubsetAliasDecl` | `"+" "type" Identifier "=" EnumVariantSubsetRhs StatementBoundary?` | 548 |
| `EnumVariantSubsetRhs` | `Identifier ("\|" Identifier)*` | 550 |
| `SchemaDecl` | `TopLevelVisibility? "schema" Identifier TypeParameterList? SchemaBody` | 554 |
| `SchemaBody` | `"{" SchemaFieldSequence? "}"` | 555 |
| `SchemaFieldSequence` | `CommaSchemaFields \| LayoutSchemaFields` | 556 |
| `CommaSchemaFields` | `SchemaFieldDecl ("," SchemaFieldDecl)* ","?` | 557 |
| `LayoutSchemaFields` | `LineBreakBoundary LayoutSchemaFieldDecl (LineBreakBoundary LayoutSchemaFieldDecl)* LineBreakBoundary?` | 558 |
| `SchemaFieldDecl` | `Identifier TypeAnnotation Initializer? SchemaConstraint* StatementBoundary?` | 559 |
| `LayoutSchemaFieldDecl` | `Identifier TypeAnnotation Initializer? SchemaConstraint*` | 560 |
| `SchemaConstraint` | `"where" Expr` | 561 |
| `TypeAliasDecl` | `TopLevelVisibility? "type" Identifier TypeParameterList? "=" TypeAliasRhs StatementBoundary` | 563 |
| `TypeAliasRhs` | `TypeRef RefinementSuffix? \| StaticRangeType` | 564 |
| `StaticRangeType` | `StaticIntLiteral ".." StaticIntLiteral` | 565 |
| `TopLevelBindingDecl` | `TopLevelVisibility? ("let" \| "var") Identifier TypeAnnotation? "=" Expr StatementBoundary` | 567 |
| `NamedEffectCapabilityDecl` | `TopLevelVisibility? "capability" Identifier "for" EffectRow StatementBoundary` | 568 |
| `ActorDecl` | `TopLevelVisibility? "actor" MailboxClause? Identifier ActorBody` | 572 |
| `MailboxClause` | `HashTag "(" "capacity" ":" StaticIntLiteral ")"` | 573 |
| `ActorBody` | `"{" ActorItem* "}"` | 574 |
| `ActorItem` | `ActorOnDecl \| ActorRequestDecl \| MemberDecl` | 575 |
| `ActorOnDecl` | `MemberVisibility? "on" Identifier ParameterList? ThrowsClause* EffectsClause* FunctionBody` | 576 |
| `ActorRequestDecl` | `MemberVisibility? "request" Identifier ParameterList? ReturnClause ThrowsClause* EffectsClause* FunctionBody` | 577 |
| `ActorProtocolDecl` | `TopLevelVisibility? "protocol" Identifier ActorProtocolBody` | 579 |
| `ActorProtocolBody` | `"{" ActorProtocolItem* "}"` | 580 |
| `ActorProtocolItem` | `ActorProtocolSendRequirement \| ActorProtocolRequestRequirement` | 581 |
| `ActorProtocolSendRequirement` | `"send" Identifier ParameterList? ThrowsClause* EffectsClause* StatementBoundary` | 582 |
| `ActorProtocolRequestRequirement` | `"request" Identifier ParameterList? ReturnClause ThrowsClause* EffectsClause* StatementBoundary` | 583 |
| `TypestateResourceDecl` | `TopLevelVisibility? "typestate" Identifier TypeParameterList? TypestateBody` | 587 |
| `TypestateBody` | `"{" TypestateTransitionDecl* "}"` | 588 |
| `TypestateTransitionDecl` | `Identifier "->" Identifier FunctionBody?` | 589 |
| `UnitCatalogDecl` | `TopLevelVisibility? "unit" "catalog" Identifier UnitCatalogBody` | 591 |
| `UnitCatalogBody` | `"{" UnitCatalogEntry* "}"` | 592 |
| `UnitCatalogEntry` | `ExactRatioUnitConversionDecl \| Identifier "=" UnitExpr StatementBoundary` | 593 |
| `ExactRatioUnitConversionDecl` | `"unit" Identifier "equalsRatio" MeasureLiteralExpr "/" StaticIntLiteral StatementBoundary` | 594 |
| `ModuleInterfaceDecl` | `ModuleSignatureDecl \| OpaqueModuleFacadeDecl` | 596 |
| `ModuleSignatureDecl` | `TopLevelVisibility? "module" "signature" QualifiedPath ModuleInterfaceBody` | 597 |
| `OpaqueModuleFacadeDecl` | `TopLevelVisibility? "opaque" "module" QualifiedPath ModuleInterfaceBody` | 598 |
| `ModuleInterfaceBody` | `"{" ModuleInterfaceItem* "}"` | 599 |
| `ModuleInterfaceItem` | `ExportDecl \| UseExportDecl \| OpaqueModuleFacadeDecl` | 600 |
| `CleanupBudgetClause` | `"cleanup" "budget" "{" CleanupBudgetItem* "}"` | 604 |
| `CleanupBudgetItem` | `EffectsBudget \| ErrorsBudget` | 605 |
| `EffectsBudget` | `"effects" "{" IdentifierList? "}"` | 606 |
| `ErrorsBudget` | `"errors" TypeRef` | 607 |
| `BitfieldDecl` | `TopLevelVisibility? BitfieldIntroducer Identifier BitfieldBackingClause BitfieldOrderClause BitfieldBody` | 611 |
| `BitfieldIntroducer` | `"bitfield" HashTag?` | 613 |
| `BitfieldBackingClause` | `"backing" TypeRef` | 614 |
| `BitfieldOrderClause` | `"order" "::" "lsb0"` | 615 |
| `BitfieldBody` | `"{" BitfieldLayoutSection BitfieldMemberDecl* "}"` | 616 |
| `BitfieldLayoutSection` | `BitfieldSlotDecl+ \| FlagSlotDecl+` | 617 |
| `BitfieldSlotDecl` | `BitfieldNamedSlot StatementBoundary \| BitfieldReservedSlot StatementBoundary` | 618 |
| `FlagSlotDecl` | `FlagNamedSlot StatementBoundary \| BitfieldReservedSlot StatementBoundary` | 619 |
| `BitfieldNamedSlot` | `MemberVisibility? Identifier ":" StaticIntLiteral BitfieldDefault?` | 620 |
| `BitfieldReservedSlot` | `"_" ":" StaticIntLiteral` | 621 |
| `FlagNamedSlot` | `MemberVisibility? Identifier` | 622 |
| `BitfieldDefault` | `"=" Literal` | 623 |
| `BitfieldMemberDecl` | `MemberFunctionDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| LawDecl` | 624 |
| `TypeRef` | `PrattType` | 636 |
| `NonFunctionTypeRef` | `PrattNonFunctionType` | 637 |
| `TypePrimary` | `QualifiedTypeReference \| FacetType \| ParenTypeSyntax \| SharpShapeType \| ExistentialType \| OpaqueType \| TypeofType \| AssociatedProjection` | 640 |
| `TypePrefixParselet` | `OwnershipQualifier` | 648 |
| `TypePostfixParselet` | `"?"` | 649 |
| `TypeInfixOperator` | `"&" \| "\|"` | 650 |
| `QualifiedTypeReference` | `QualifiedPath TypeArgumentList?` | 652 |
| `FacetType` | `"Facet" "<" "borrow" "any" QualifiedTypeReference AssociatedTypeConstraintList? ">"` | 654 |
| `OwnershipQualifier` | `"owned" \| "borrowed" \| "mut" \| "inout"` | 655 |
| `ParenTypeSyntax` | `HashTag* "(" ParenTypeItemList? ")" FunctionTypeTail?` | 659 |
| `ParenTypeItemList` | `ParenTypeItem ("," ParenTypeItem)* ","?` | 660 |
| `ParenTypeItem` | `TypeRef \| TypeRef "..." \| TypeRef "***"` | 661 |
| `FunctionTypeTail` | `"->" ReturnTypeSurface ThrowsClause* EffectsClause*` | 662 |
| `SharpShapeType` | `"#" StaticDimensionList "[" TypeRef "]"` | 664 |
| `StaticDimensionList` | `StaticIntLiteral ("," StaticIntLiteral)*` | 665 |
| `ExistentialType` | `"any" QualifiedTypeReference AssociatedTypeConstraintList?` | 667 |
| `OpaqueType` | `"some" QualifiedTypeReference AssociatedTypeConstraintList?` | 668 |
| `TypeofType` | `"typeof" TypeofStaticSampleOperand` | 669 |
| `AssociatedProjection` | `"<" TypeRef "as" QualifiedTypeReference ">" "::" Identifier` | 670 |
| `TypeofStaticSampleOperand` | `Literal \| ListLiteral \| StaticPrefixedCollectionSample \| NumericArrayLiteral \| MeasureLiteralExpr` | 673 |
| `StaticPrefixedCollectionSample` | `MapLiteral \| SetLiteral \| MutListLiteral` | 678 |
| `PrattType` | `TYPE_PRATT_ENTRY` | 681 |
| `PrattNonFunctionType` | `NON_FUNCTION_TYPE_PRATT_ENTRY` | 682 |
| `Pattern` | `OrPattern` | 690 |
| `OrPattern` | `AliasPattern ("\|" AliasPattern)*` | 691 |
| `AliasPattern` | `MovePattern ("as" Identifier)?` | 692 |
| `MovePattern` | `"move"? PatternPrimary` | 693 |
| `PatternPrimary` | `TypedBindingPattern \| Identifier \| PinPattern \| RangePattern \| RelationalPattern \| TuplePattern \| RecordPattern \| ListPattern \| MapPattern \| VariantPattern \| NominalPattern \| "_" \| UnitSyntax \| Literal \| ParenthesizedPattern` | 695 |
| `TypedBindingPattern` | `Identifier ":" TypeRef` | 711 |
| `ParenthesizedPattern` | `"(" Pattern ")"` | 712 |
| `PinPattern` | `"^" StablePatternValue` | 713 |
| `StablePatternValue` | `Identifier \| QualifiedStaticExpr \| Literal` | 714 |
| `RangePattern` | `PatternBound (".." \| "..<") PatternBound` | 715 |
| `RelationalPattern` | `("<" \| "<=" \| ">" \| ">=") PatternBound` | 716 |
| `PatternBound` | `Literal \| PinPattern` | 717 |
| `TuplePattern` | `"(" TuplePatternItems ")"` | 721 |
| `TuplePatternItems` | `Pattern "," \| Pattern "," Pattern ("," Pattern)* ","?` | 722 |
| `BindingPattern` | `BindingOrPattern TypeAnnotation?` | 734 |
| `BindingOrPattern` | `BindingAliasPattern ("\|" BindingAliasPattern)*` | 735 |
| `BindingAliasPattern` | `BindingMovePattern ("as" Identifier)?` | 736 |
| `BindingMovePattern` | `"move"? BindingPatternPrimary` | 737 |
| `BindingPatternPrimary` | `Identifier \| PinPattern \| RangePattern \| RelationalPattern \| TuplePattern \| RecordPattern \| ListPattern \| MapPattern \| VariantPattern \| NominalPattern \| "_" \| UnitSyntax \| Literal \| ParenthesizedPattern` | 738 |
| `RecordPattern` | `"${" RecordPatternEntries? "}"` | 757 |
| `RecordPatternEntries` | `RecordPatternEntry (PatternEntrySeparator RecordPatternEntry)* PatternEntrySeparator?` | 758 |
| `RecordPatternEntry` | `Identifier \| RecordDestination ":" Identifier \| RecordRestPattern` | 760 |
| `RecordDestination` | `Pattern` | 761 |
| `RecordRestPattern` | `".." RestBinder` | 762 |
| `MapPattern` | `"#" "map" "{" MapPatternEntries? "}"` | 764 |
| `MapPatternEntries` | `MapPatternEntry (PatternEntrySeparator MapPatternEntry)* PatternEntrySeparator?` | 765 |
| `MapPatternEntry` | `MapDestination ":" MapKeyPattern \| MapRestPattern` | 767 |
| `MapDestination` | `Pattern` | 768 |
| `MapKeyPattern` | `Literal \| PinPattern` | 769 |
| `MapRestPattern` | `".." RestBinder` | 770 |
| `PatternEntrySeparator` | `"," LineBreakBoundary? \| LineBreakBoundary` | 771 |
| `ListPattern` | `"[" ListPatternBody? "]"` | 777 |
| `ListPatternBody` | `IgnoredAllListRest \| ExactListPattern \| PrefixRestListPattern \| SuffixRestListPattern \| MiddleRestListPattern` | 778 |
| `ExactListPattern` | `Pattern ("," Pattern)* ","?` | 783 |
| `PrefixRestListPattern` | `PrefixListRest "," Pattern ("," Pattern)* ","?` | 784 |
| `SuffixRestListPattern` | `Pattern ("," Pattern)* "," SuffixListRest ","?` | 785 |
| `MiddleRestListPattern` | `Pattern ("," Pattern)* "," MiddleListRest "," Pattern ("," Pattern)* ","?` | 786 |
| `PrefixListRest` | `RestBinder ".."` | 788 |
| `SuffixListRest` | `".." RestBinder` | 789 |
| `MiddleListRest` | `".." RestBinder ".."` | 790 |
| `IgnoredAllListRest` | `".." "_" ","?` | 791 |
| `RestBinder` | `Identifier \| "_"` | 792 |
| `VariantPattern` | `VariantQualifier Identifier VariantPatternPayload?` | 794 |
| `VariantQualifier` | `TypeRef "::" \| "::"` | 795 |
| `VariantPatternPayload` | `VariantPositionalPatternPayload \| RecordPattern` | 796 |
| `VariantPositionalPatternPayload` | `"(" PatternList? ")"` | 797 |
| `NominalPattern` | `TypeRef RecordPattern` | 802 |
| `Stmt` | `ForLoop \| WhileLoop \| RepeatLoop \| AsyncForLoop \| TaskGroupStmt \| MatchStatement \| IfStmt \| LocalBindingStmt \| AssertiveBindingStmt \| PatternAssignmentStmt \| ParallelAssignmentStmt \| ControlTransferStmt \| TryStmt \| DeferStmt \| ScopedUseStmt \| ExprStmt \| ScopedImportStmt` | 810 |
| `ExprStmt` | `Expr StatementBoundary` | 828 |
| `Block` | `"{" BlockPrologue? BlockSequence "}"` | 830 |
| `BlockPrologue` | `(UseDecl \| ImportDecl)+` | 831 |
| `BlockSequence` | `BlockItem* BlockFinalItem?` | 832 |
| `BlockItem` | `LocalFunctionDecl \| Stmt` | 833 |
| `BlockFinalItem` | `ControlTransfer \| BindingCore \| Expr` | 836 |
| `ValueBody` | `SingleExpressionValueBody \| ExplicitRetValueBody` | 839 |
| `SingleExpressionValueBody` | `"{" ReturnValueSurface "}"` | 840 |
| `ExplicitRetValueBody` | `"{" BlockItem* RetTransfer "}"` | 841 |
| `RetTransfer` | `"ret" ReturnValueSurface? GuardClause?` | 842 |
| `BindingCore` | `("let" \| "var") BindingHead "=" BindingValueSurface` | 847 |
| `BindingHead` | `BindingPattern \| BareTupleBindingSurface` | 848 |
| `BareTupleBindingSurface` | `BindingPattern "," BindingPattern ("," BindingPattern)*` | 849 |
| `BindingValueSurface` | `Expr \| BareTupleValueSurface` | 850 |
| `ReturnValueSurface` | `Expr \| BareTupleValueSurface` | 851 |
| `BareTupleValueSurface` | `Expr "," Expr ("," Expr)*` | 852 |
| `LocalBindingStmt` | `BindingCore StatementBoundary \| RightwardLocalBindingSurface \| LazyBindingStmt \| GuardedBindingStmt` | 853 |
| `LazyBindingStmt` | `"let" HashTag Identifier TypeAnnotation? "=" Expr StatementBoundary` | 854 |
| `GuardedBindingStmt` | `("let" \| "var") BindingPattern "=" Expr "else" GuardedBindingFailure StatementBoundary?` | 855 |
| `AssertiveBindingStmt` | `("let" \| "var") "!" BindingPattern "=" Expr StatementBoundary` | 856 |
| `GuardedBindingFailure` | `GuardedBindingExit \| Pattern "=>" GuardedBindingExit` | 858 |
| `GuardedBindingExit` | `GuardedReturnExit \| GuardedThrowExit \| GuardedBreakExit \| GuardedContinueExit` | 859 |
| `GuardedReturnExit` | `"return" Expr?` | 860 |
| `GuardedThrowExit` | `"throw" Expr` | 861 |
| `GuardedBreakExit` | `("break")+ Expr?` | 862 |
| `GuardedContinueExit` | `("break")* "continue"` | 863 |
| `ControlTransferStmt` | `ControlTransfer StatementBoundary` | 866 |
| `ControlTransfer` | `ReturnTransfer \| ThrowTransfer \| BreakTransfer \| ContinueTransfer \| YieldTransfer` | 867 |
| `ReturnTransfer` | `"return" ReturnValueSurface? GuardClause?` | 868 |
| `ThrowTransfer` | `"throw" Expr GuardClause?` | 869 |
| `BreakTransfer` | `("break")+ Expr? GuardClause?` | 870 |
| `ContinueTransfer` | `("break")* "continue" GuardClause?` | 871 |
| `YieldTransfer` | `"yield" Expr? (GuardClause \| YieldResponseBinding)?` | 872 |
| `YieldResponseBinding` | `"->" DollarLocalBinding` | 873 |
| `DollarLocalBinding` | `"$" Identifier TypeAnnotation? \| "$$" Identifier TypeAnnotation?` | 874 |
| `GuardClause` | `PositiveGuard \| NegativeGuard` | 876 |
| `PositiveGuard` | `"if" Expr` | 877 |
| `NegativeGuard` | `"!" "if" Expr` | 878 |
| `IfStmt` | `"if" PatternConditionChain Block ("else" (IfStmt \| Block))?` | 880 |
| `PatternConditionChain` | `PatternControlCondition ("and" "then" PatternControlCondition)*` | 883 |
| `PatternControlCondition` | `Expr \| "let" Pattern "=" Expr` | 885 |
| `ForLoop` | `"for" ("let" Pattern \| Pattern) "in" Expr GuardClause? Block MatchStatement?` | 889 |
| `WhileLoop` | `"while" PatternConditionChain Block MatchStatement?` | 890 |
| `RepeatLoop` | `"repeat" Block "while" Expr MatchStatement?` | 891 |
| `AsyncForLoop` | `"for" "await" ("let" Pattern \| Pattern) "in" Expr GuardClause? Block` | 892 |
| `MatchStatement` | `"match" MatchCore` | 894 |
| `MatchCore` | `MatchSubjectSlot MatchBody` | 895 |
| `MatchSubjectSlot` | `MATCH_SUBJECT_BY_INPUT_SUPPLY_POLICY` | 896 |
| `MatchBody` | `"{" LineBreakBoundary? MatchArmSequence "}"` | 897 |
| `MatchArmSequence` | `MatchArm (MatchArmSeparator MatchArm)* MatchArmSeparator?` | 898 |
| `MatchArm` | `MatchHead GuardClause? "=>" MatchArmBodySlot` | 899 |
| `MatchHead` | `BoundedBinderPattern \| Pattern \| "otherwise"` | 900 |
| `BoundedBinderPattern` | `PatternBound OrderedComparisonOperator Identifier OrderedComparisonOperator PatternBound` | 906 |
| `MatchArmSeparator` | `MATCH_ARM_SEPARATOR_BY_CONTEXT` | 908 |
| `MatchArmBodySlot` | `MATCH_ARM_BODY_BY_CONTEXT` | 909 |
| `TryStmt` | `"try" Block (CatchClause+ FinallyClause? \| FinallyClause)` | 913 |
| `CatchClause` | `"catch" Pattern? GuardClause? Block` | 914 |
| `ValueCatchClause` | `"catch" Pattern? GuardClause? ValueBody` | 915 |
| `FinallyClause` | `"finally" Block` | 916 |
| `DeferStmt` | `"defer" DeferredCleanupInvocation StatementBoundary` | 918 |
| `DeferredCleanupInvocation` | `DeferredDirectCall \| DeferredMessageCall` | 921 |
| `DeferredDirectCall` | `DeferredReceiver ArgumentList` | 922 |
| `DeferredMessageCall` | `DeferredReceiver "~" MessageSelector TildeArgumentSequence?` | 923 |
| `DeferredReceiver` | `DeferredPrimary DeferTargetSuffix*` | 924 |
| `DeferredPrimary` | `Identifier \| QualifiedStaticExpr` | 925 |
| `DeferTargetSuffix` | `IndexSuffix \| MemberSuffix` | 926 |
| `RightwardLocalBindingSurface` | `Expr "->" DollarLocalBinding StatementBoundary` | 930 |
| `PatternAssignmentStmt` | `AssigneePattern "=" Expr StatementBoundary` | 934 |
| `AssigneePattern` | `AssigneeTuplePattern \| AssigneeListPattern \| AssigneeRecordPattern \| AssigneeNominalPattern` | 935 |
| `AssigneePrimary` | `Identifier \| "_"` | 939 |
| `AssigneeTuplePattern` | `"(" AssigneeTupleItems ")"` | 940 |
| `AssigneeTupleItems` | `AssigneePatternItem "," \| AssigneePatternItem "," AssigneePatternItem ("," AssigneePatternItem)* ","?` | 941 |
| `AssigneePatternItem` | `AssigneePrimary \| AssigneeTuplePattern \| AssigneeListPattern \| AssigneeRecordPattern` | 944 |
| `AssigneeListPattern` | `"[" AssigneeListBody? "]"` | 948 |
| `AssigneeListBody` | `AssigneeIgnoredAllRest \| AssigneeExactList \| AssigneePrefixRestList \| AssigneeSuffixRestList \| AssigneeMiddleRestList` | 949 |
| `AssigneeExactList` | `AssigneePatternItem ("," AssigneePatternItem)* ","?` | 954 |
| `AssigneePrefixRestList` | `Identifier ".." "," AssigneeExactList` | 955 |
| `AssigneeSuffixRestList` | `AssigneeExactList "," ".." Identifier ","?` | 956 |
| `AssigneeMiddleRestList` | `AssigneeExactList "," ".." Identifier ".." "," AssigneeExactList` | 957 |
| `AssigneeIgnoredAllRest` | `".." "_" ","?` | 959 |
| `AssigneeRestPattern` | `".." ("_" \| Identifier)` | 960 |
| `AssigneeRecordPattern` | `"${" AssigneeRecordEntries? "}"` | 961 |
| `AssigneeRecordEntries` | `AssigneeRecordEntry (PatternEntrySeparator AssigneeRecordEntry)* PatternEntrySeparator?` | 962 |
| `AssigneeRecordEntry` | `Identifier \| AssigneePrimary ":" Identifier \| AssigneeRestPattern` | 965 |
| `AssigneeNominalPattern` | `TypeRef AssigneeRecordPattern` | 966 |
| `ParallelAssignmentStmt` | `BareTuplePlaceSurface "=" AssignmentValueSurface StatementBoundary` | 967 |
| `BareTuplePlaceSurface` | `Identifier "," Identifier ("," Identifier)*` | 968 |
| `AssignmentValueSurface` | `Expr \| BareTupleValueSurface` | 969 |
| `ScopedUseStmt` | `"use" ScopedPathList "in" Block` | 970 |
| `ScopedImportStmt` | `"import" ScopedPathList "in" Block` | 971 |
| `ScopedPathList` | `QualifiedPath ("," QualifiedPath)*` | 972 |
| `TaskGroupStmt` | `"task" "group" Identifier? Block` | 973 |
| `Expr` | `PrattExpr` | 981 |
| `PredicateExpr` | `PrattPredicateExpr` | 982 |
| `SliceIndexExpr` | `PrattSliceIndexExpr` | 983 |
| `ExpressionPrefixParselet` | `"+" \| "-" \| "not" \| "~~" \| "move" \| "borrow" \| "&" \| "await"` | 989 |
| `ExpressionPostfixParselet` | `CallSuffix \| TildeCallLed \| TupleOrdinalSuffix \| IndexSuffix \| MemberSuffix \| NumericArrayTransposeSuffix \| ConstructorCallSuffix \| NamedConstructorCallSuffix \| PrototypeDerivationSuffix \| CastSuffix` | 991 |
| `PrimaryExpr` | `Literal \| Identifier \| ImplicitAtExpr \| ParenExprSyntax \| ListLiteral \| BoundedListLiteral \| ComprehensionExpr \| MaterializationBody \| TypedMaterializationExpr \| MapLiteral \| SetLiteral \| MutListLiteral \| MapComprehensionExpr \| SetComprehensionExpr \| NumericArrayLiteral \| MeasureLiteralExpr \| QualifiedStaticExpr \| ExpectedVariantExpr \| AtControlExpr \| MatchExpr \| ClosureExpr \| GeneratorExpr \| SpawnExpr \| StructuredTaskScope \| UnsafeBlockExpr \| FacetExpr` | 1002 |
| `ParenExprSyntax` | `"(" ParenExprContent? ")"` | 1030 |
| `ParenExprContent` | `Expr ParenExprTail?` | 1031 |
| `ParenExprTail` | `"," \| "," Expr ("," Expr)* ","?` | 1032 |
| `ImplicitAtExpr` | `"@"` | 1033 |
| `ExpectedVariantExpr` | `"::" Identifier` | 1034 |
| `CallSuffix` | `ArgumentList TrailingClosureGroup? \| AtomicCallArgument TrailingClosureGroup` | 1038 |
| `ArgumentList` | `"(" ")" \| "(" CommaArgumentSequence ")" \| "(" LayoutArgumentSequence ")"` | 1041 |
| `CommaArgumentSequence` | `Argument ("," Argument)* ","?` | 1044 |
| `LayoutArgumentSequence` | `LineBreakBoundary NamedLayoutArgument LineBreakBoundary NamedLayoutArgument (LineBreakBoundary NamedLayoutArgument)* LineBreakBoundary?` | 1046 |
| `NamedLayoutArgument` | `NamedArgument \| NamedUnfoldArgument` | 1048 |
| `Argument` | `ContextArgument \| WitnessArgument \| NamedArgument \| PositionalUnfoldArgument \| NamedUnfoldArgument \| Expr` | 1049 |
| `ContextArgument` | `"context" Expr` | 1055 |
| `WitnessArgument` | `"using" WitnessArgumentValue` | 1056 |
| `WitnessArgumentValue` | `Identifier \| ConformanceEvidenceSelector \| NamedConformanceEvidenceSelector` | 1057 |
| `NamedArgument` | `Identifier ":" Expr` | 1058 |
| `PositionalUnfoldArgument` | `"*" Expr` | 1059 |
| `NamedUnfoldArgument` | `"**" Expr` | 1060 |
| `AtomicCallArgument` | `Literal \| Identifier \| QualifiedStaticExpr \| ExpectedVariantExpr` | 1061 |
| `TrailingClosureGroup` | `TrailingClosureArgument+` | 1065 |
| `TrailingClosureArgument` | `ClosureExpr \| Identifier ":" ClosureExpr` | 1066 |
| `IndexSuffix` | `"[" SliceAxisList "]"` | 1070 |
| `SliceAxisList` | `SliceAxis (";" SliceAxis)*` | 1071 |
| `SliceAxis` | `SliceRange \| SliceIndexExpr \| AxisWildcard` | 1072 |
| `SliceRange` | `SliceBound (".." \| "..<") SliceBound` | 1075 |
| `SliceBound` | `SliceIndexExpr \| "^" \| "$" \| "^" OffsetExpr \| "$" OffsetExpr` | 1076 |
| `OffsetExpr` | `("+" \| "-") NumericLiteral` | 1077 |
| `AxisWildcard` | `"*"` | 1078 |
| `TupleOrdinalSuffix` | `"." StaticIntLiteral` | 1080 |
| `MemberSuffix` | `"." Identifier \| "." "\\\\" NAME_TOKEN` | 1081 |
| `TildeCallLed` | `TildeCallToken MessageSelector TildeArgumentSequence? TrailingClosureGroup?` | 1087 |
| `TildeCallToken` | `"~" \| ":~"` | 1089 |
| `MessageSelector` | `Identifier \| QualifiedMessageSelector` | 1090 |
| `QualifiedMessageSelector` | `TypeRef "::" Identifier ("::" Identifier)?` | 1091 |
| `QualifiedExtensionSelector` | `TypeRef "::" Identifier "::" Identifier` | 1092 |
| `TildeArgumentSequence` | `TildeArgument ("," TildeArgument)*` | 1093 |
| `TildeArgument` | `ContextArgument \| WitnessArgument \| NamedArgument \| PositionalUnfoldArgument \| NamedUnfoldArgument \| Expr` | 1094 |
| `NumericArrayTransposeSuffix` | `"^"` | 1101 |
| `ConstructorCallSuffix` | `"!" ArgumentList` | 1102 |
| `NamedConstructorCallSuffix` | `"!" Identifier ArgumentList` | 1103 |
| `PrototypeDerivationSuffix` | `("!" \| "!!") DerivationBody` | 1104 |
| `DerivationBody` | `"{" MaterializationEntryList? "}"` | 1105 |
| `CastSuffix` | `"as" "?" TypeRef \| "as" "!" TypeRef` | 1107 |
| `QualifiedStaticExpr` | `StaticQualifier "::" Identifier \| TraitQualifiedAssociatedSelector` | 1109 |
| `StaticQualifier` | `QualifiedTypeReference \| AssociatedProjection` | 1111 |
| `TraitQualifiedAssociatedSelector` | `"<" TypeRef "as" QualifiedTypeReference ">" "::" Identifier` | 1112 |
| `AtControlExpr` | `AtIfExpr \| AtTryExpr \| AtScopeExpr` | 1118 |
| `AtIfExpr` | `"@" "if" Expr ValueBody "else" ValueBody` | 1120 |
| `AtTryExpr` | `"@" "try" ValueBody (ValueCatchClause+ FinallyClause? \| FinallyClause)` | 1121 |
| `AtScopeExpr` | `"@" "scope" ScopeModifier* ValueBody` | 1122 |
| `ScopeModifier` | `"isolated" \| "cancellable" \| "shielded"` | 1123 |
| `MatchExpr` | `"@" "match" MatchCore` | 1125 |
| `ClosureExpr` | `CaptureList? HashTag* "{" ClosureContent "}"` | 1129 |
| `ClosureContent` | `ExplicitLambdaContent \| LambdaBody?` | 1130 |
| `ExplicitLambdaContent` | `LambdaParameterList? "=>" LambdaBody` | 1131 |
| `LambdaParameterList` | `LambdaParameter ("," LambdaParameter)* ","?` | 1132 |
| `LambdaParameter` | `ParameterMode? LambdaParameterPattern TypeAnnotation?` | 1133 |
| `LambdaParameterPattern` | `Identifier \| IrrefutableParameterPattern` | 1134 |
| `LambdaBody` | `ReturnValueSurface \| LineBreakBoundary LambdaBlockContent` | 1135 |
| `LambdaBlockContent` | `BlockItem* LambdaFinalItem?` | 1136 |
| `LambdaFinalItem` | `RetTransfer \| Expr` | 1137 |
| `CaptureList` | `"[" CaptureItemList? "]"` | 1139 |
| `CaptureItemList` | `CaptureItem ("," CaptureItem)* ","?` | 1140 |
| `CaptureItem` | `("let" \| "var") Identifier "=" Expr \| CaptureMode Identifier \| Identifier` | 1141 |
| `CaptureMode` | `"borrow" \| "inout" \| "move" \| "clone" \| "deep" \| "copy" \| "once"` | 1144 |
| `GeneratorExpr` | `CaptureList? GeneratorCore` | 1157 |
| `GeneratorCore` | `"@" "for" Pattern "in" Expr Block \| "@" "while" Expr Block \| "@" "repeat" Block "while" Expr` | 1158 |
| `SpawnExpr` | `"spawn" TaskBody` | 1162 |
| `TaskBody` | `"{" "=>" TaskBodySequence "}" \| "async" "{" "=>" TaskBodySequence "}"` | 1163 |
| `TaskBodySequence` | `LineBreakBoundary? BlockSequence` | 1165 |
| `StructuredTaskScope` | `"task" "scope" Block` | 1166 |
| `UnsafeBlockExpr` | `"unsafe" Block` | 1167 |
| `FacetExpr` | `"facet" "[" "borrow" Expr "as" QualifiedTypeReference AssociatedTypeConstraintList? "]"` | 1170 |
| `ConformanceEvidenceSelector` | `"conformance" "(" TypeRef "conforms" QualifiedTypeReference ")"` | 1172 |
| `NamedConformanceEvidenceSelector` | `ConformanceEvidenceSelector "::" Identifier` | 1173 |
| `PrattExpr` | `EXPRESSION_PRATT_ENTRY` | 1176 |
| `PrattPredicateExpr` | `PREDICATE_PRATT_ENTRY` | 1177 |
| `PrattSliceIndexExpr` | `SLICE_INDEX_PRATT_ENTRY` | 1178 |
| `Literal` | `BoolLiteral \| NumericLiteral \| ImaginaryLiteralExpr \| RationalLiteralExpr \| StringLiteralExpr \| CharLiteralExpr \| BytesLiteral` | 1186 |
| `BoolLiteral` | `"true" \| "false"` | 1193 |
| `NumericLiteral` | `NUMERIC_LITERAL` | 1194 |
| `ImaginaryLiteralExpr` | `IMAGINARY_LITERAL` | 1195 |
| `RationalLiteralExpr` | `RATIONAL_LITERAL` | 1196 |
| `CharLiteralExpr` | `CHAR_LITERAL` | 1197 |
| `BytesLiteral` | `BYTES_LITERAL` | 1198 |
| `StringLiteralExpr` | `PLAIN_STRING_LITERAL \| RAW_STRING_LITERAL \| MULTILINE_STRING_LITERAL \| InterpolatedString` | 1201 |
| `InterpolatedString` | `STRING_START InterpolatedStringPart* STRING_END` | 1202 |
| `InterpolatedStringPart` | `STRING_TEXT \| STRING_ESCAPE \| InterpolationExpr \| InterpolationPath` | 1203 |
| `InterpolationExpr` | `INTERPOLATION_OPEN Expr InterpolationFormat? INTERPOLATION_CLOSE` | 1207 |
| `InterpolationFormat` | `":" INTERPOLATION_FORMAT_TEXT` | 1208 |
| `InterpolationPath` | `"$" InterpolationPathRoot InterpolationPathSelector* INTERPOLATION_BOUNDARY?` | 1213 |
| `InterpolationPathRoot` | `Identifier \| "@"` | 1214 |
| `InterpolationPathSelector` | `"." Identifier \| "." StaticIntLiteral \| "[" InterpolationIndex "]"` | 1215 |
| `InterpolationIndex` | `StaticIntLiteral \| Identifier` | 1218 |
| `ListLiteral` | `"[" ExpressionList? "]"` | 1223 |
| `BoundedListLiteral` | `"[" StaticIntLiteral ".." StaticIntLiteral ":" ExpressionList? "]"` | 1224 |
| `ComprehensionExpr` | `"[" Expr ComprehensionClause+ "]"` | 1226 |
| `TypedMaterializationExpr` | `TypeRef MaterializationBody` | 1229 |
| `MaterializationBody` | `"${" MaterializationEntryList? "}"` | 1230 |
| `MaterializationEntryList` | `MaterializationEntry (MaterializationSeparator MaterializationEntry)* MaterializationSeparator?` | 1231 |
| `MaterializationEntry` | `Identifier \| Identifier ":" Expr \| StringLiteralExpr ":" Expr \| NamedUnfoldArgument` | 1232 |
| `MaterializationSeparator` | `"," LineBreakBoundary? \| LineBreakBoundary` | 1236 |
| `MapLiteral` | `"#" "map" "{" MapEntryList? "}"` | 1239 |
| `MapEntryList` | `MapEntry (MaterializationSeparator MapEntry)* MaterializationSeparator?` | 1240 |
| `MapEntry` | `Expr ":" Expr \| NamedUnfoldArgument` | 1241 |
| `SetLiteral` | `"#" "set" "{" ExpressionList? "}"` | 1242 |
| `MutListLiteral` | `"#" "mut" "[" ExpressionList? "]"` | 1243 |
| `MapComprehensionExpr` | `"#" "map" "{" MapEntry ComprehensionClause+ "}"` | 1244 |
| `SetComprehensionExpr` | `"#" "set" "{" Expr ComprehensionClause+ "}"` | 1245 |
| `ComprehensionClause` | `ForClause \| PositiveGuard \| IfLetClause \| UnfoldClause` | 1247 |
| `ForClause` | `"for" Pattern "in" Expr` | 1248 |
| `IfLetClause` | `"if" "let" Pattern "=" Expr` | 1249 |
| `UnfoldClause` | `"for" "..." Pattern "in" Expr` | 1250 |
| `NumericArrayLiteral` | `ShapeInferredArrayLiteral \| ShapeInferredColumnVectorLiteral \| ExactShapeArrayLiteral` | 1253 |
| `ShapeInferredArrayLiteral` | `"#" "[" ExpressionList? "]"` | 1256 |
| `ShapeInferredColumnVectorLiteral` | `"#" "[" Expr (";" Expr)+ "]"` | 1257 |
| `ExactShapeArrayLiteral` | `"#" StaticDimensionList "[" ArrayInitializer? "]"` | 1258 |
| `ArrayInitializer` | `ShapedRepeatInitializer \| ShapedGeneratorInitializer \| ShapedElementSequence` | 1259 |
| `ShapedRepeatInitializer` | `"repeat" ":" Expr` | 1262 |
| `ShapedGeneratorInitializer` | `"generate" ":" Expr` | 1263 |
| `ShapedElementSequence` | `Expr (ShapedElementSeparator Expr)* ShapedElementSeparator?` | 1264 |
| `ShapedElementSeparator` | `"," \| ShapedAxisBoundary` | 1265 |
| `ShapedAxisBoundary` | `";" ";"*` | 1266 |
| `MeasureLiteralExpr` | `NumericLiteral "[" UnitExpr "]"` | 1269 |
| `UnitExpr` | `PrattUnitExpr` | 1270 |
| `UnitPrimary` | `Identifier \| QualifiedPath \| "(" UnitExpr ")"` | 1271 |
| `UnitPostfixParselet` | `"^" SignedStaticInt` | 1272 |
| `UnitInfixOperator` | `"*" \| "/"` | 1273 |
| `PrattUnitExpr` | `UNIT_PRATT_ENTRY` | 1274 |

## `PREVIEW` 프로파일 — 13개

| 문법 production | 정확한 EBNF 오른쪽 항 | 원천 줄 |
|---|---|---:|
| `DeeplusPreview` | `PreviewLibrarySourceFile \| PreviewExecutableSourceFile \| PreviewScriptSourceFile` | 1283 |
| `PreviewLibrarySourceFile` | `PreviewGate ModuleDecl? PreviewLibraryItem*` | 1284 |
| `PreviewExecutableSourceFile` | `PreviewGate ModuleDecl? PreviewExecutableItem*` | 1285 |
| `PreviewScriptSourceFile` | `Shebang? PreviewGate ModuleDecl? PreviewScriptItem*` | 1286 |
| `PreviewLibraryItem` | `LibrarySourceItem \| PreviewFfiDecl` | 1288 |
| `PreviewExecutableItem` | `ExecutableSourceItem \| PreviewFfiDecl` | 1289 |
| `PreviewScriptItem` | `ScriptSourceItem \| PreviewFfiDecl` | 1290 |
| `PreviewGate` | `"#" "preview" "(" PreviewFeatureList ")" LineBreakBoundary` | 1292 |
| `PreviewFeatureList` | `Identifier ("," Identifier)*` | 1293 |
| `PreviewFfiDecl` | `PreviewFfiFunctionDecl \| PreviewFfiBlockDecl` | 1296 |
| `PreviewFfiFunctionDecl` | `"extern" "#" "C" "def" "#" "unsafe" Identifier ParameterList ReturnClause? ThrowsClause* EffectsClause* StatementBoundary` | 1297 |
| `PreviewFfiBlockDecl` | `"extern" "c" "(" PLAIN_STRING_LITERAL ")" "{" PreviewFfiBlockMember* "}"` | 1299 |
| `PreviewFfiBlockMember` | `"unsafe" "def" Identifier ParameterList ReturnClause? ThrowsClause* EffectsClause* StatementBoundary` | 1301 |
