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

## `STABLE` 프로파일 — 540개

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
| `ParenTypeSyntax` | `HashTag* "(" ParenTypeItemList? ")" FunctionTypeTail?` | 686 |
| `ParenTypeItemList` | `ParenTypeItem ("," ParenTypeItem)* ","?` | 687 |
| `ParenTypeItem` | `FunctionTypeModeItem \| TypeRef \| TypeRef "..." \| TypeRef "***"` | 688 |
| `FunctionTypeModeItem` | `ParameterMode TypeRef` | 689 |
| `FunctionTypeTail` | `"->" ReturnTypeSurface ThrowsClause* EffectsClause*` | 690 |
| `SharpShapeType` | `"#" StaticDimensionList "[" TypeRef "]"` | 692 |
| `StaticDimensionList` | `StaticIntLiteral ("," StaticIntLiteral)*` | 693 |
| `ExistentialType` | `"any" QualifiedTypeReference AssociatedTypeConstraintList?` | 695 |
| `OpaqueType` | `"some" QualifiedTypeReference AssociatedTypeConstraintList?` | 696 |
| `TypeofType` | `"typeof" TypeofStaticSampleOperand` | 697 |
| `AssociatedProjection` | `"<" TypeRef "as" QualifiedTypeReference ">" "::" Identifier` | 698 |
| `TypeofStaticSampleOperand` | `Literal \| ListLiteral \| StaticPrefixedCollectionSample \| NumericArrayLiteral \| MeasureLiteralExpr` | 701 |
| `StaticPrefixedCollectionSample` | `MapLiteral \| SetLiteral \| MutListLiteral` | 706 |
| `PrattType` | `TYPE_PRATT_ENTRY` | 709 |
| `PrattNonFunctionType` | `NON_FUNCTION_TYPE_PRATT_ENTRY` | 710 |
| `Pattern` | `OrPattern` | 718 |
| `OrPattern` | `AliasPattern ("\|" AliasPattern)*` | 719 |
| `AliasPattern` | `MovePattern ("as" Identifier)?` | 720 |
| `MovePattern` | `"move"? PatternPrimary` | 721 |
| `PatternPrimary` | `TypedBindingPattern \| Identifier \| PinPattern \| RangePattern \| RelationalPattern \| TuplePattern \| RecordPattern \| ListPattern \| MapPattern \| VariantPattern \| NominalPattern \| "_" \| UnitSyntax \| Literal \| ParenthesizedPattern` | 723 |
| `TypedBindingPattern` | `Identifier ":" TypeRef` | 739 |
| `ParenthesizedPattern` | `"(" Pattern ")"` | 740 |
| `PinPattern` | `"^" StablePatternValue` | 741 |
| `StablePatternValue` | `Identifier \| QualifiedStaticExpr \| Literal` | 742 |
| `RangePattern` | `PatternBound (".." \| "..<") PatternBound` | 743 |
| `RelationalPattern` | `("<" \| "<=" \| ">" \| ">=") PatternBound` | 744 |
| `PatternBound` | `Literal \| PinPattern` | 745 |
| `TuplePattern` | `"(" TuplePatternItems ")"` | 749 |
| `TuplePatternItems` | `Pattern "," \| Pattern "," Pattern ("," Pattern)* ","?` | 750 |
| `BindingPattern` | `BindingOrPattern TypeAnnotation?` | 762 |
| `BindingOrPattern` | `BindingAliasPattern ("\|" BindingAliasPattern)*` | 763 |
| `BindingAliasPattern` | `BindingMovePattern ("as" Identifier)?` | 764 |
| `BindingMovePattern` | `"move"? BindingPatternPrimary` | 765 |
| `BindingPatternPrimary` | `Identifier \| PinPattern \| RangePattern \| RelationalPattern \| TuplePattern \| RecordPattern \| ListPattern \| MapPattern \| VariantPattern \| NominalPattern \| "_" \| UnitSyntax \| Literal \| ParenthesizedPattern` | 766 |
| `RecordPattern` | `"${" RecordPatternEntries? "}"` | 785 |
| `RecordPatternEntries` | `RecordPatternEntry (PatternEntrySeparator RecordPatternEntry)* PatternEntrySeparator?` | 786 |
| `RecordPatternEntry` | `Identifier \| RecordDestination ":" Identifier \| RecordRestPattern` | 788 |
| `RecordDestination` | `Pattern` | 789 |
| `RecordRestPattern` | `".." RestBinder` | 790 |
| `MapPattern` | `"#" "map" "{" MapPatternEntries? "}"` | 792 |
| `MapPatternEntries` | `MapPatternEntry (PatternEntrySeparator MapPatternEntry)* PatternEntrySeparator?` | 793 |
| `MapPatternEntry` | `MapDestination ":" MapKeyPattern \| MapRestPattern` | 795 |
| `MapDestination` | `Pattern` | 796 |
| `MapKeyPattern` | `Literal \| PinPattern` | 797 |
| `MapRestPattern` | `".." RestBinder` | 798 |
| `PatternEntrySeparator` | `"," LineBreakBoundary? \| LineBreakBoundary` | 799 |
| `ListPattern` | `"[" ListPatternBody? "]"` | 805 |
| `ListPatternBody` | `IgnoredAllListRest \| ExactListPattern \| PrefixRestListPattern \| SuffixRestListPattern \| MiddleRestListPattern` | 806 |
| `ExactListPattern` | `Pattern ("," Pattern)* ","?` | 811 |
| `PrefixRestListPattern` | `PrefixListRest "," Pattern ("," Pattern)* ","?` | 812 |
| `SuffixRestListPattern` | `Pattern ("," Pattern)* "," SuffixListRest ","?` | 813 |
| `MiddleRestListPattern` | `Pattern ("," Pattern)* "," MiddleListRest "," Pattern ("," Pattern)* ","?` | 814 |
| `PrefixListRest` | `RestBinder ".."` | 816 |
| `SuffixListRest` | `".." RestBinder` | 817 |
| `MiddleListRest` | `".." RestBinder ".."` | 818 |
| `IgnoredAllListRest` | `".." "_" ","?` | 819 |
| `RestBinder` | `Identifier \| "_"` | 820 |
| `VariantPattern` | `VariantQualifier Identifier VariantPatternPayload?` | 822 |
| `VariantQualifier` | `TypeRef "::" \| "::"` | 823 |
| `VariantPatternPayload` | `VariantPositionalPatternPayload \| RecordPattern` | 824 |
| `VariantPositionalPatternPayload` | `"(" PatternList? ")"` | 825 |
| `NominalPattern` | `TypeRef RecordPattern` | 830 |
| `Stmt` | `ForLoop \| WhileLoop \| RepeatLoop \| AsyncForLoop \| MatchStatement \| IfStmt \| LocalBindingStmt \| AssertiveBindingStmt \| PatternAssignmentStmt \| ParallelAssignmentStmt \| ControlTransferStmt \| TryStmt \| DeferStmt \| ScopedUseStmt \| ExprStmt \| ScopedImportStmt` | 838 |
| `ExprStmt` | `Expr StatementBoundary` | 855 |
| `Block` | `"{" BlockPrologue? BlockSequence "}"` | 857 |
| `BlockPrologue` | `(UseDecl \| ImportDecl)+` | 858 |
| `BlockSequence` | `BlockItem* BlockFinalItem?` | 859 |
| `BlockItem` | `LocalFunctionDecl \| Stmt` | 860 |
| `BlockFinalItem` | `ControlTransfer \| BindingCore \| Expr` | 863 |
| `ValueBody` | `SingleExpressionValueBody \| ExplicitRetValueBody` | 866 |
| `SingleExpressionValueBody` | `"{" ReturnValueSurface "}"` | 867 |
| `ExplicitRetValueBody` | `"{" BlockItem* RetTransfer "}"` | 868 |
| `RetTransfer` | `"ret" ReturnValueSurface? GuardClause?` | 869 |
| `BindingCore` | `("let" \| "var") BindingHead "=" BindingValueSurface` | 874 |
| `BindingHead` | `BindingPattern \| BareTupleBindingSurface` | 875 |
| `BareTupleBindingSurface` | `BindingPattern "," BindingPattern ("," BindingPattern)*` | 876 |
| `BindingValueSurface` | `Expr \| BareTupleValueSurface` | 877 |
| `ReturnValueSurface` | `Expr \| BareTupleValueSurface` | 878 |
| `BareTupleValueSurface` | `Expr "," Expr ("," Expr)*` | 879 |
| `LocalBindingStmt` | `BindingCore StatementBoundary \| RightwardLocalBindingSurface \| LazyBindingStmt \| GuardedBindingStmt` | 880 |
| `LazyBindingStmt` | `"let" HashTag Identifier TypeAnnotation? "=" Expr StatementBoundary` | 881 |
| `GuardedBindingStmt` | `("let" \| "var") BindingPattern "=" Expr "else" GuardedBindingFailure StatementBoundary?` | 882 |
| `AssertiveBindingStmt` | `("let" \| "var") "!" BindingPattern "=" Expr StatementBoundary` | 883 |
| `GuardedBindingFailure` | `GuardedBindingExit \| Pattern "=>" GuardedBindingExit` | 885 |
| `GuardedBindingExit` | `GuardedReturnExit \| GuardedThrowExit \| GuardedBreakExit \| GuardedContinueExit` | 886 |
| `GuardedReturnExit` | `"return" Expr?` | 887 |
| `GuardedThrowExit` | `"throw" Expr` | 888 |
| `GuardedBreakExit` | `("break")+ Expr?` | 889 |
| `GuardedContinueExit` | `("break")* "continue"` | 890 |
| `ControlTransferStmt` | `ControlTransfer StatementBoundary` | 893 |
| `ControlTransfer` | `ReturnTransfer \| ThrowTransfer \| BreakTransfer \| ContinueTransfer \| YieldTransfer` | 894 |
| `ReturnTransfer` | `"return" ReturnValueSurface? GuardClause?` | 895 |
| `ThrowTransfer` | `"throw" Expr GuardClause?` | 896 |
| `BreakTransfer` | `("break")+ Expr? GuardClause?` | 897 |
| `ContinueTransfer` | `("break")* "continue" GuardClause?` | 898 |
| `YieldTransfer` | `"yield" Expr? (GuardClause \| YieldResponseBinding)?` | 899 |
| `YieldResponseBinding` | `"->" DollarLocalBinding` | 900 |
| `DollarLocalBinding` | `"$" Identifier TypeAnnotation? \| "$$" Identifier TypeAnnotation?` | 901 |
| `GuardClause` | `PositiveGuard \| NegativeGuard` | 903 |
| `PositiveGuard` | `"if" Expr` | 904 |
| `NegativeGuard` | `"!" "if" Expr` | 905 |
| `IfStmt` | `"if" PatternConditionChain Block ("else" (IfStmt \| Block))?` | 907 |
| `PatternConditionChain` | `PatternControlCondition ("and" "then" PatternControlCondition)*` | 910 |
| `PatternControlCondition` | `Expr \| "let" Pattern "=" Expr` | 912 |
| `ForLoop` | `"for" ("let" Pattern \| Pattern) "in" Expr GuardClause? Block MatchStatement?` | 916 |
| `WhileLoop` | `"while" PatternConditionChain Block MatchStatement?` | 917 |
| `RepeatLoop` | `"repeat" Block "while" Expr MatchStatement?` | 918 |
| `AsyncForLoop` | `"for" ForAwaitRole ("let" Pattern \| Pattern) "in" Expr GuardClause? Block` | 922 |
| `ForAwaitRole` | `"#" "await"` | 923 |
| `MatchStatement` | `"match" MatchCore` | 925 |
| `MatchCore` | `MatchSubjectSlot MatchBody` | 926 |
| `MatchSubjectSlot` | `MATCH_SUBJECT_BY_INPUT_SUPPLY_POLICY` | 927 |
| `MatchBody` | `"{" LineBreakBoundary? MatchArmSequence "}"` | 928 |
| `MatchArmSequence` | `MatchArm (MatchArmSeparator MatchArm)* MatchArmSeparator?` | 929 |
| `MatchArm` | `MatchHead GuardClause? "=>" MatchArmBodySlot` | 930 |
| `MatchHead` | `BoundedBinderPattern \| Pattern \| "otherwise"` | 931 |
| `BoundedBinderPattern` | `PatternBound OrderedComparisonOperator Identifier OrderedComparisonOperator PatternBound` | 937 |
| `MatchArmSeparator` | `MATCH_ARM_SEPARATOR_BY_CONTEXT` | 939 |
| `MatchArmBodySlot` | `MATCH_ARM_BODY_BY_CONTEXT` | 940 |
| `TryStmt` | `"try" Block (CatchClause+ FinallyClause? \| FinallyClause)` | 944 |
| `CatchClause` | `"catch" Pattern? GuardClause? Block` | 945 |
| `ValueCatchClause` | `"catch" Pattern? GuardClause? ValueBody` | 946 |
| `FinallyClause` | `"finally" Block` | 947 |
| `DeferStmt` | `"defer" DeferredCleanupInvocation StatementBoundary` | 949 |
| `DeferredCleanupInvocation` | `DeferredDirectCall \| DeferredMessageCall` | 952 |
| `DeferredDirectCall` | `DeferredReceiver ArgumentList` | 953 |
| `DeferredMessageCall` | `DeferredReceiver "~" MessageSelector TildeArgumentSequence?` | 954 |
| `DeferredReceiver` | `DeferredPrimary DeferTargetSuffix*` | 955 |
| `DeferredPrimary` | `Identifier \| QualifiedStaticExpr` | 956 |
| `DeferTargetSuffix` | `IndexSuffix \| MemberSuffix` | 957 |
| `RightwardLocalBindingSurface` | `Expr "->" DollarLocalBinding StatementBoundary` | 961 |
| `PatternAssignmentStmt` | `AssigneePattern "=" Expr StatementBoundary` | 965 |
| `AssigneePattern` | `AssigneeTuplePattern \| AssigneeListPattern \| AssigneeRecordPattern \| AssigneeNominalPattern` | 966 |
| `AssigneePrimary` | `Identifier \| "_"` | 970 |
| `AssigneeTuplePattern` | `"(" AssigneeTupleItems ")"` | 971 |
| `AssigneeTupleItems` | `AssigneePatternItem "," \| AssigneePatternItem "," AssigneePatternItem ("," AssigneePatternItem)* ","?` | 972 |
| `AssigneePatternItem` | `AssigneePrimary \| AssigneeTuplePattern \| AssigneeListPattern \| AssigneeRecordPattern` | 975 |
| `AssigneeListPattern` | `"[" AssigneeListBody? "]"` | 979 |
| `AssigneeListBody` | `AssigneeIgnoredAllRest \| AssigneeExactList \| AssigneePrefixRestList \| AssigneeSuffixRestList \| AssigneeMiddleRestList` | 980 |
| `AssigneeExactList` | `AssigneePatternItem ("," AssigneePatternItem)* ","?` | 985 |
| `AssigneePrefixRestList` | `Identifier ".." "," AssigneeExactList` | 986 |
| `AssigneeSuffixRestList` | `AssigneeExactList "," ".." Identifier ","?` | 987 |
| `AssigneeMiddleRestList` | `AssigneeExactList "," ".." Identifier ".." "," AssigneeExactList` | 988 |
| `AssigneeIgnoredAllRest` | `".." "_" ","?` | 990 |
| `AssigneeRestPattern` | `".." ("_" \| Identifier)` | 991 |
| `AssigneeRecordPattern` | `"${" AssigneeRecordEntries? "}"` | 992 |
| `AssigneeRecordEntries` | `AssigneeRecordEntry (PatternEntrySeparator AssigneeRecordEntry)* PatternEntrySeparator?` | 993 |
| `AssigneeRecordEntry` | `Identifier \| AssigneePrimary ":" Identifier \| AssigneeRestPattern` | 996 |
| `AssigneeNominalPattern` | `TypeRef AssigneeRecordPattern` | 997 |
| `ParallelAssignmentStmt` | `BareTuplePlaceSurface "=" AssignmentValueSurface StatementBoundary` | 998 |
| `BareTuplePlaceSurface` | `Identifier "," Identifier ("," Identifier)*` | 999 |
| `AssignmentValueSurface` | `Expr \| BareTupleValueSurface` | 1000 |
| `ScopedUseStmt` | `"use" ScopedPathList "in" Block` | 1001 |
| `ScopedImportStmt` | `"import" ScopedPathList "in" Block` | 1002 |
| `ScopedPathList` | `QualifiedPath ("," QualifiedPath)*` | 1003 |
| `Expr` | `PrattExpr` | 1011 |
| `PredicateExpr` | `PrattPredicateExpr` | 1012 |
| `SliceIndexExpr` | `PrattSliceIndexExpr` | 1013 |
| `ExpressionPrefixParselet` | `"+" \| "-" \| "not" \| "~~" \| "move" \| "borrow" \| "&" \| "await"` | 1019 |
| `ExpressionPostfixParselet` | `CallSuffix \| TildeCallLed \| TupleOrdinalSuffix \| IndexSuffix \| MemberSuffix \| NumericArrayTransposeSuffix \| ConstructorCallSuffix \| NamedConstructorCallSuffix \| PrototypeDerivationSuffix \| CastSuffix` | 1021 |
| `PrimaryExpr` | `Literal \| Identifier \| ImplicitAtExpr \| ParenExprSyntax \| ListLiteral \| BoundedListLiteral \| ComprehensionExpr \| MaterializationBody \| TypedMaterializationExpr \| MapLiteral \| SetLiteral \| MutListLiteral \| MapComprehensionExpr \| SetComprehensionExpr \| NumericArrayLiteral \| MeasureLiteralExpr \| QualifiedStaticExpr \| ExpectedVariantExpr \| AtControlExpr \| MatchExpr \| ClosureExpr \| GeneratorExpr \| SpawnExpr \| ConcurExpr \| UnsafeBlockExpr \| FacetExpr` | 1032 |
| `ParenExprSyntax` | `"(" ParenExprContent? ")"` | 1060 |
| `ParenExprContent` | `Expr ParenExprTail?` | 1061 |
| `ParenExprTail` | `"," \| "," Expr ("," Expr)* ","?` | 1062 |
| `ImplicitAtExpr` | `"@"` | 1063 |
| `ExpectedVariantExpr` | `"::" Identifier` | 1064 |
| `CallSuffix` | `ArgumentList TrailingClosureGroup? \| AtomicCallArgument TrailingClosureGroup` | 1068 |
| `ArgumentList` | `"(" ")" \| "(" CommaArgumentSequence ")" \| "(" LayoutArgumentSequence ")"` | 1071 |
| `CommaArgumentSequence` | `Argument ("," Argument)* ","?` | 1074 |
| `LayoutArgumentSequence` | `LineBreakBoundary NamedLayoutArgument LineBreakBoundary NamedLayoutArgument (LineBreakBoundary NamedLayoutArgument)* LineBreakBoundary?` | 1076 |
| `NamedLayoutArgument` | `NamedArgument \| NamedUnfoldArgument` | 1078 |
| `Argument` | `ContextArgument \| WitnessArgument \| NamedArgument \| PositionalUnfoldArgument \| NamedUnfoldArgument \| Expr` | 1079 |
| `ContextArgument` | `"context" Expr` | 1085 |
| `WitnessArgument` | `"using" WitnessArgumentValue` | 1086 |
| `WitnessArgumentValue` | `Identifier \| ConformanceEvidenceSelector \| NamedConformanceEvidenceSelector` | 1087 |
| `NamedArgument` | `Identifier ":" Expr` | 1088 |
| `PositionalUnfoldArgument` | `"*" Expr` | 1089 |
| `NamedUnfoldArgument` | `"**" Expr` | 1090 |
| `AtomicCallArgument` | `Literal \| Identifier \| QualifiedStaticExpr \| ExpectedVariantExpr` | 1091 |
| `TrailingClosureGroup` | `TrailingClosureArgument+` | 1095 |
| `TrailingClosureArgument` | `ClosureExpr \| Identifier ":" ClosureExpr` | 1096 |
| `IndexSuffix` | `"[" SliceAxisList "]"` | 1100 |
| `SliceAxisList` | `SliceAxis (";" SliceAxis)*` | 1101 |
| `SliceAxis` | `SliceRange \| SliceIndexExpr \| AxisWildcard` | 1102 |
| `SliceRange` | `SliceBound (".." \| "..<") SliceBound` | 1105 |
| `SliceBound` | `SliceIndexExpr \| "^" \| "$" \| "^" OffsetExpr \| "$" OffsetExpr` | 1106 |
| `OffsetExpr` | `("+" \| "-") NumericLiteral` | 1107 |
| `AxisWildcard` | `"*"` | 1108 |
| `TupleOrdinalSuffix` | `"." StaticIntLiteral` | 1110 |
| `MemberSuffix` | `"." Identifier \| "." "\\\\" NAME_TOKEN` | 1111 |
| `TildeCallLed` | `TildeCallToken MessageSelector TildeArgumentSequence? TrailingClosureGroup?` | 1117 |
| `TildeCallToken` | `"~" \| ":~"` | 1119 |
| `MessageSelector` | `Identifier \| QualifiedMessageSelector` | 1120 |
| `QualifiedMessageSelector` | `TypeRef "::" Identifier ("::" Identifier)?` | 1121 |
| `QualifiedExtensionSelector` | `TypeRef "::" Identifier "::" Identifier` | 1122 |
| `TildeArgumentSequence` | `TildeArgument ("," TildeArgument)*` | 1123 |
| `TildeArgument` | `ContextArgument \| WitnessArgument \| NamedArgument \| PositionalUnfoldArgument \| NamedUnfoldArgument \| Expr` | 1124 |
| `NumericArrayTransposeSuffix` | `"^"` | 1131 |
| `ConstructorCallSuffix` | `"!" ArgumentList` | 1132 |
| `NamedConstructorCallSuffix` | `"!" Identifier ArgumentList` | 1133 |
| `PrototypeDerivationSuffix` | `("!" \| "!!") DerivationBody` | 1134 |
| `DerivationBody` | `"{" MaterializationEntryList? "}"` | 1135 |
| `CastSuffix` | `"as" "?" TypeRef \| "as" "!" TypeRef` | 1137 |
| `QualifiedStaticExpr` | `StaticQualifier "::" Identifier \| TraitQualifiedAssociatedSelector` | 1139 |
| `StaticQualifier` | `QualifiedTypeReference \| AssociatedProjection` | 1141 |
| `TraitQualifiedAssociatedSelector` | `"<" TypeRef "as" QualifiedTypeReference ">" "::" Identifier` | 1142 |
| `AtControlExpr` | `AtIfExpr \| AtTryExpr \| AtScopeExpr` | 1148 |
| `AtIfExpr` | `"@" "if" Expr ValueBody "else" ValueBody` | 1150 |
| `AtTryExpr` | `"@" "try" ValueBody (ValueCatchClause+ FinallyClause? \| FinallyClause)` | 1151 |
| `AtScopeExpr` | `"@" "scope" ScopeModifier* ValueBody` | 1152 |
| `ScopeModifier` | `"isolated" \| "cancellable" \| "shielded"` | 1153 |
| `MatchExpr` | `"@" "match" MatchCore` | 1155 |
| `ClosureExpr` | `CaptureList? HashTag* "{" ClosureContent "}"` | 1159 |
| `ClosureContent` | `ExplicitLambdaContent \| LambdaBody?` | 1164 |
| `ExplicitLambdaContent` | `LambdaParameterList? "=>" LambdaBody` | 1165 |
| `LambdaParameterList` | `LambdaParameter ("," LambdaParameter)* ","?` | 1166 |
| `LambdaParameter` | `ParameterMode? LambdaParameterPattern TypeAnnotation?` | 1167 |
| `LambdaParameterPattern` | `Identifier \| IrrefutableParameterPattern` | 1168 |
| `LambdaBody` | `ReturnValueSurface \| LineBreakBoundary LambdaBlockContent` | 1169 |
| `LambdaBlockContent` | `BlockItem* LambdaFinalItem?` | 1170 |
| `LambdaFinalItem` | `RetTransfer \| Expr` | 1171 |
| `CaptureList` | `"[" CaptureItemList? "]"` | 1173 |
| `CaptureItemList` | `CaptureItem ("," CaptureItem)* ","?` | 1174 |
| `CaptureItem` | `("let" \| "var") Identifier "=" Expr \| CaptureMode Identifier \| Identifier` | 1175 |
| `CaptureMode` | `"borrow" \| "inout" \| "move" \| "clone" \| "deep" \| "copy" \| "once"` | 1178 |
| `GeneratorExpr` | `CaptureList? GeneratorCore` | 1196 |
| `GeneratorCore` | `"@" "for" Pattern "in" Expr Block \| "@" "while" Expr Block \| "@" "repeat" Block "while" Expr` | 1197 |
| `SpawnExpr` | `"spawn" (SpawnBody \| SpawnOperandSlot)` | 1205 |
| `SpawnBody` | `"{" "=>" SpawnBodySequence "}"` | 1206 |
| `SpawnBodySequence` | `LineBreakBoundary? BlockSequence` | 1207 |
| `SpawnOperandSlot` | `SPAWN_OPERAND_BY_PREFIX_PARSER` | 1208 |
| `ConcurExpr` | `"concur" Block` | 1209 |
| `UnsafeBlockExpr` | `"unsafe" Block` | 1210 |
| `FacetExpr` | `"facet" "[" "borrow" Expr "as" QualifiedTypeReference AssociatedTypeConstraintList? "]"` | 1213 |
| `ConformanceEvidenceSelector` | `"conformance" "(" TypeRef "conforms" QualifiedTypeReference ")"` | 1215 |
| `NamedConformanceEvidenceSelector` | `ConformanceEvidenceSelector "::" Identifier` | 1216 |
| `PrattExpr` | `EXPRESSION_PRATT_ENTRY` | 1219 |
| `PrattPredicateExpr` | `PREDICATE_PRATT_ENTRY` | 1220 |
| `PrattSliceIndexExpr` | `SLICE_INDEX_PRATT_ENTRY` | 1221 |
| `Literal` | `BoolLiteral \| NumericLiteral \| ImaginaryLiteralExpr \| RationalLiteralExpr \| StringLiteralExpr \| CharLiteralExpr \| BytesLiteral` | 1229 |
| `BoolLiteral` | `"true" \| "false"` | 1236 |
| `NumericLiteral` | `NUMERIC_LITERAL` | 1237 |
| `ImaginaryLiteralExpr` | `IMAGINARY_LITERAL` | 1238 |
| `RationalLiteralExpr` | `RATIONAL_LITERAL` | 1239 |
| `CharLiteralExpr` | `CHAR_LITERAL` | 1240 |
| `BytesLiteral` | `BYTES_LITERAL` | 1241 |
| `StringLiteralExpr` | `PLAIN_STRING_LITERAL \| RAW_STRING_LITERAL \| MULTILINE_STRING_LITERAL \| InterpolatedString` | 1244 |
| `InterpolatedString` | `STRING_START InterpolatedStringPart* STRING_END` | 1245 |
| `InterpolatedStringPart` | `STRING_TEXT \| STRING_ESCAPE \| InterpolationExpr \| InterpolationPath` | 1246 |
| `InterpolationExpr` | `INTERPOLATION_OPEN Expr InterpolationFormat? INTERPOLATION_CLOSE` | 1250 |
| `InterpolationFormat` | `":" INTERPOLATION_FORMAT_TEXT` | 1251 |
| `InterpolationPath` | `"$" InterpolationPathRoot InterpolationPathSelector* INTERPOLATION_BOUNDARY?` | 1256 |
| `InterpolationPathRoot` | `Identifier \| "@"` | 1257 |
| `InterpolationPathSelector` | `"." Identifier \| "." StaticIntLiteral \| "[" InterpolationIndex "]"` | 1258 |
| `InterpolationIndex` | `StaticIntLiteral \| Identifier` | 1261 |
| `ListLiteral` | `"[" ExpressionList? "]"` | 1266 |
| `BoundedListLiteral` | `"[" StaticIntLiteral ".." StaticIntLiteral ":" ExpressionList? "]"` | 1267 |
| `ComprehensionExpr` | `"[" Expr ComprehensionClause+ "]"` | 1269 |
| `TypedMaterializationExpr` | `TypeRef MaterializationBody` | 1272 |
| `MaterializationBody` | `"${" MaterializationEntryList? "}"` | 1273 |
| `MaterializationEntryList` | `MaterializationEntry (MaterializationSeparator MaterializationEntry)* MaterializationSeparator?` | 1274 |
| `MaterializationEntry` | `Identifier \| Identifier ":" Expr \| StringLiteralExpr ":" Expr \| NamedUnfoldArgument` | 1275 |
| `MaterializationSeparator` | `"," LineBreakBoundary? \| LineBreakBoundary` | 1279 |
| `MapLiteral` | `"#" "map" "{" MapEntryList? "}"` | 1282 |
| `MapEntryList` | `MapEntry (MaterializationSeparator MapEntry)* MaterializationSeparator?` | 1283 |
| `MapEntry` | `Expr ":" Expr \| NamedUnfoldArgument` | 1284 |
| `SetLiteral` | `"#" "set" "{" ExpressionList? "}"` | 1285 |
| `MutListLiteral` | `"#" "mut" "[" ExpressionList? "]"` | 1286 |
| `MapComprehensionExpr` | `"#" "map" "{" MapEntry ComprehensionClause+ "}"` | 1287 |
| `SetComprehensionExpr` | `"#" "set" "{" Expr ComprehensionClause+ "}"` | 1288 |
| `ComprehensionClause` | `ForClause \| PositiveGuard \| IfLetClause \| UnfoldClause` | 1290 |
| `ForClause` | `"for" Pattern "in" Expr` | 1291 |
| `IfLetClause` | `"if" "let" Pattern "=" Expr` | 1292 |
| `UnfoldClause` | `"for" "..." Pattern "in" Expr` | 1293 |
| `NumericArrayLiteral` | `ShapeInferredArrayLiteral \| ShapeInferredColumnVectorLiteral \| ExactShapeArrayLiteral` | 1296 |
| `ShapeInferredArrayLiteral` | `"#" "[" ExpressionList? "]"` | 1299 |
| `ShapeInferredColumnVectorLiteral` | `"#" "[" Expr (";" Expr)+ "]"` | 1300 |
| `ExactShapeArrayLiteral` | `"#" StaticDimensionList "[" ArrayInitializer? "]"` | 1301 |
| `ArrayInitializer` | `ShapedRepeatInitializer \| ShapedGeneratorInitializer \| ShapedElementSequence` | 1302 |
| `ShapedRepeatInitializer` | `"repeat" ":" Expr` | 1305 |
| `ShapedGeneratorInitializer` | `"generate" ":" Expr` | 1306 |
| `ShapedElementSequence` | `Expr (ShapedElementSeparator Expr)* ShapedElementSeparator?` | 1307 |
| `ShapedElementSeparator` | `"," \| ShapedAxisBoundary` | 1308 |
| `ShapedAxisBoundary` | `";" ";"*` | 1309 |
| `MeasureLiteralExpr` | `NumericLiteral "[" UnitExpr "]"` | 1312 |
| `UnitExpr` | `PrattUnitExpr` | 1313 |
| `UnitPrimary` | `Identifier \| QualifiedPath \| "(" UnitExpr ")"` | 1314 |
| `UnitPostfixParselet` | `"^" SignedStaticInt` | 1315 |
| `UnitInfixOperator` | `"*" \| "/"` | 1316 |
| `PrattUnitExpr` | `UNIT_PRATT_ENTRY` | 1317 |

## `PREVIEW` 프로파일 — 13개

| 문법 production | 정확한 EBNF 오른쪽 항 | 원천 줄 |
|---|---|---:|
| `DeeplusPreview` | `PreviewLibrarySourceFile \| PreviewExecutableSourceFile \| PreviewScriptSourceFile` | 1326 |
| `PreviewLibrarySourceFile` | `PreviewGate ModuleDecl? PreviewLibraryItem*` | 1327 |
| `PreviewExecutableSourceFile` | `PreviewGate ModuleDecl? PreviewExecutableItem*` | 1328 |
| `PreviewScriptSourceFile` | `Shebang? PreviewGate ModuleDecl? PreviewScriptItem*` | 1329 |
| `PreviewLibraryItem` | `LibrarySourceItem \| PreviewFfiDecl` | 1331 |
| `PreviewExecutableItem` | `ExecutableSourceItem \| PreviewFfiDecl` | 1332 |
| `PreviewScriptItem` | `ScriptSourceItem \| PreviewFfiDecl` | 1333 |
| `PreviewGate` | `"#" "preview" "(" PreviewFeatureList ")" LineBreakBoundary` | 1335 |
| `PreviewFeatureList` | `Identifier ("," Identifier)*` | 1336 |
| `PreviewFfiDecl` | `PreviewFfiFunctionDecl \| PreviewFfiBlockDecl` | 1339 |
| `PreviewFfiFunctionDecl` | `"extern" "#" "C" "def" "#" "unsafe" Identifier ParameterList ReturnClause? ThrowsClause* EffectsClause* StatementBoundary` | 1340 |
| `PreviewFfiBlockDecl` | `"extern" "c" "(" PLAIN_STRING_LITERAL ")" "{" PreviewFfiBlockMember* "}"` | 1342 |
| `PreviewFfiBlockMember` | `"unsafe" "def" Identifier ParameterList ReturnClause? ThrowsClause* EffectsClause* StatementBoundary` | 1344 |
