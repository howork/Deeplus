<!-- tools/generators/generate_grammar_reference.py가 생성함; 직접 수정하지 마십시오. -->
# 부록 A — legacy surface-census production 참조

비권위 차등 입력은 `spec/grammar/deeplus.ebnf`입니다. 정확한 구조 문법 권위는 `spec/grammar/deeplus.dpg`와 닫힌 ParserContext 정본입니다. 이 표는 기존 656개 surface-census production의 오른쪽 항을 한 번씩 투영하여 DPG cutover의 CST/AST 책임 추적성을 보존하며, 그 자체가 별도 문법 권위는 아닙니다.

## `LEXICAL` 프로파일 — 87개

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
| `NUMERIC_LITERAL` | `FLOAT_LITERAL \| INTEGER_LITERAL` | 68 |
| `IMAGINARY_LITERAL` | `ScannerImaginaryFloatLiteral` | 73 |
| `RATIONAL_LITERAL` | `ScannerRationalLiteralAtExpressionPrefix` | 78 |
| `INTEGER_LITERAL` | `BinaryInteger \| OctalInteger \| HexInteger \| DECIMAL_INTEGER` | 79 |
| `FLOAT_LITERAL` | `DecimalFraction ExponentPart? \| DECIMAL_INTEGER ExponentPart` | 81 |
| `BinaryInteger` | `("0b" \| "0B") BinaryDigits` | 83 |
| `OctalInteger` | `("0o" \| "0O") OctalDigits` | 84 |
| `HexInteger` | `("0x" \| "0X") HexDigits` | 85 |
| `DECIMAL_INTEGER` | `DecimalDigits` | 86 |
| `DecimalFraction` | `DecimalDigits "." DecimalDigits` | 87 |
| `ExponentPart` | `("e" \| "E") ("+" \| "-")? DecimalDigits` | 88 |
| `BinaryDigits` | `BinaryDigit ("_"? BinaryDigit)*` | 92 |
| `OctalDigits` | `OctalDigit ("_"? OctalDigit)*` | 93 |
| `DecimalDigits` | `DecimalDigit ("_"? DecimalDigit)*` | 94 |
| `HexDigits` | `HexDigit ("_"? HexDigit)*` | 95 |
| `BinaryDigit` | `"0" \| "1"` | 96 |
| `OctalDigit` | `"0" \| "1" \| "2" \| "3" \| "4" \| "5" \| "6" \| "7"` | 97 |
| `DecimalDigit` | `"0" \| "1" \| "2" \| "3" \| "4" \| "5" \| "6" \| "7" \| "8" \| "9"` | 98 |
| `HexDigit` | `DecimalDigit \| "a" \| "b" \| "c" \| "d" \| "e" \| "f" \| "A" \| "B" \| "C" \| "D" \| "E" \| "F"` | 99 |
| `CHAR_LITERAL` | `"'" CharScalar "'"` | 102 |
| `CharScalar` | `DirectCharScalar \| SimpleCharEscape \| UnicodeScalarEscape \| NamedUnicodeEscape` | 103 |
| `SimpleCharEscape` | `"\\\\0" \| "\\\\n" \| "\\\\r" \| "\\\\t" \| "\\\\'" \| "\\\\\\\\"` | 104 |
| `UnicodeScalarEscape` | `"\\\\u{" HexScalarDigits "}"` | 105 |
| `NamedUnicodeEscape` | `"\\\\N{" UnicodeName "}"` | 106 |
| `HexScalarDigits` | `HexDigit HexDigit? HexDigit? HexDigit? HexDigit? HexDigit?` | 107 |
| `PLAIN_STRING_LITERAL` | `ScannerPlainStringLiteral` | 110 |
| `STRING_START` | `ScannerInterpolatedStringStart` | 111 |
| `STRING_TEXT` | `ScannerInterpolatedStringText` | 112 |
| `STRING_ESCAPE` | `ScannerStringEscape` | 113 |
| `INTERPOLATION_BOUNDARY` | `ScannerInterpolationBoundary` | 114 |
| `INTERPOLATION_OPEN` | `ScannerInterpolationOpen` | 115 |
| `INTERPOLATION_CLOSE` | `ScannerInterpolationClose` | 116 |
| `INTERPOLATION_FORMAT_TEXT` | `ScannerInterpolationFormatText` | 117 |
| `STRING_END` | `ScannerInterpolatedStringEnd` | 118 |
| `RAW_STRING_LITERAL` | `ScannerRawStringLiteral` | 122 |
| `MULTILINE_STRING_LITERAL` | `ScannerMultilineStringLiteral` | 123 |
| `BYTES_LITERAL` | `ScannerBytesLiteral` | 124 |
| `PATH_SEP` | `"::"` | 127 |
| `FAT_ARROW` | `"=>"` | 128 |
| `ARROW` | `"->"` | 129 |
| `DOT_DOT` | `".."` | 130 |
| `DOT_DOT_LT` | `"..<"` | 131 |
| `ELLIPSIS` | `"..."` | 132 |
| `DOUBLE_STAR` | `"**"` | 133 |
| `STAR_PLUS` | `"*+"` | 134 |
| `STAR_DOT` | `"*."` | 135 |
| `AMP_AMP` | `"&&"` | 136 |
| `PIPE_PIPE` | `"\|\|"` | 137 |
| `CARET_CARET` | `"^^"` | 138 |
| `QUESTION_COLON` | `"?:"` | 139 |
| `DOUBLE_DOLLAR` | `"$$"` | 140 |
| `EQ_EQ` | `"=="` | 141 |
| `BANG_EQ` | `"!="` | 142 |
| `LT_EQ` | `"<="` | 143 |
| `GT_EQ` | `">="` | 144 |
| `PLUS_EQ` | `"+="` | 145 |
| `MINUS_EQ` | `"-="` | 146 |
| `STAR_EQ` | `"*="` | 147 |
| `SLASH_EQ` | `"/="` | 148 |
| `PERCENT_EQ` | `"%="` | 149 |
| `TILDE_TILDE` | `"~~"` | 150 |
| `COLON_EQ` | `":="` | 151 |
| `BANG_BANG` | `"!!"` | 152 |
| `DOUBLE_L_BRACE` | `"{{"` | 153 |
| `DOUBLE_R_BRACE` | `"}}"` | 154 |
| `DOLLAR_L_BRACE` | `"${"` | 155 |
| `Trivia` | `HorizontalSpace \| LineTerminator \| LineComment \| NestedBlockComment \| DocLineComment \| DocBlockComment \| WordComment` | 160 |
| `EOF_TOKEN` | `EOF` | 163 |
| `NAME_TOKEN` | `ScannerEscapedNameToken` | 165 |
| `EOF` | `ScannerEndOfInput` | 166 |

## `STABLE` 프로파일 — 556개

| 문법 production | 정확한 EBNF 오른쪽 항 | 원천 줄 |
|---|---|---:|
| `Identifier` | `IDENTIFIER` | 174 |
| `QualifiedPath` | `Identifier ("::" Identifier)*` | 177 |
| `TopLevelVisibility` | `"public" \| "private" \| "common"` | 179 |
| `MemberVisibility` | `"+" \| "-" \| "#"` | 188 |
| `ClassDispatchMarker` | `"." \| "+" \| "*." \| "*+"` | 189 |
| `TraitWitnessMarker` | `"." \| "+" \| "*." \| "*+"` | 190 |
| `VarianceMarker` | `"out" \| "in"` | 191 |
| `AnnotationAttachment` | `Annotation+` | 193 |
| `Annotation` | `"@" Identifier ArgumentList? LineBreakBoundary` | 194 |
| `RoleWord` | `Identifier \| HARD_KEYWORD` | 199 |
| `HashTag` | `"#" RoleWord` | 200 |
| `TypeParameterList` | `"<" TypeParameter ("," TypeParameter)* ","? ">"` | 203 |
| `TypeParameter` | `VarianceMarker? Identifier TypeParameterKindAnnotation?` | 204 |
| `TypeParameterKindAnnotation` | `":" TypeParameterKind` | 205 |
| `TypeParameterKind` | `"type" \| "StaticInt" \| "EffectRow" \| "ErrorSet"` | 206 |
| `TypeArgumentList` | `"<" TypeArgument ("," TypeArgument)* ","? ">"` | 208 |
| `TypeArgument` | `TypeRef \| StaticIntLiteral \| ErrorTypeArgument` | 209 |
| `ErrorTypeArgument` | `"error" TypeRef` | 210 |
| `TraitReferenceList` | `QualifiedTypeReference ("," QualifiedTypeReference)*` | 212 |
| `AssociatedTypeConstraintList` | `"where" AssociatedTypeConstraint ("," AssociatedTypeConstraint)*` | 213 |
| `AssociatedTypeConstraint` | `Identifier "==" TypeRef \| Identifier "conforms" QualifiedTypeReference` | 214 |
| `WhereClause` | `"where" WherePredicate ("," WherePredicate)*` | 217 |
| `WherePredicate` | `TypeRef "conforms" QualifiedTypeReference \| TypeRef "==" TypeRef \| RowPredicate` | 218 |
| `RowPredicate` | `Identifier "<=" EffectRow` | 221 |
| `EffectRow` | `EffectRowTerm ("\|" EffectRowTerm)*` | 223 |
| `EffectRowTerm` | `Identifier \| QualifiedTypeReference \| EffectSetLiteral` | 224 |
| `ErrorSet` | `ErrorSetTerm ("\|" ErrorSetTerm)*` | 225 |
| `ErrorSetTerm` | `Identifier \| QualifiedTypeReference` | 226 |
| `EffectSetLiteral` | `"{" IdentifierList? "}"` | 227 |
| `TypeAnnotation` | `":" TypeRef RefinementSuffix?` | 229 |
| `RefinementSuffix` | `RefinementClause \| IntervalRefinementClause` | 230 |
| `RefinementClause` | `"where" (PredicateExpr \| ImplicitThisPredicate)` | 231 |
| `ImplicitThisPredicate` | `OrderedComparisonOperator RefinementComparisonOperand` | 235 |
| `RefinementComparisonOperand` | `Literal \| Identifier \| QualifiedStaticExpr` | 236 |
| `IntervalRefinementClause` | `"in" RefinementBound (".." \| "..<") RefinementBound` | 237 |
| `RefinementBound` | `Literal \| Identifier \| QualifiedStaticExpr` | 238 |
| `OrderedComparisonOperator` | `"<" \| "<=" \| ">" \| ">="` | 239 |
| `Initializer` | `"=" Expr` | 240 |
| `NameAliasClause` | `"as" Identifier` | 241 |
| `ReturnClause` | `"->" ReturnTypeSurface` | 245 |
| `ReturnTypeSurface` | `NonFunctionTypeRef \| BareTupleTypeSurface` | 246 |
| `BareTupleTypeSurface` | `NonFunctionTypeRef "," NonFunctionTypeRef ("," NonFunctionTypeRef)*` | 247 |
| `ThrowsClause` | `"throws" ErrorSetTerm` | 252 |
| `EffectsClause` | `"effects" CallableEffectTerm` | 253 |
| `CallableEffectTerm` | `Identifier \| QualifiedTypeReference \| EmptyEffectSet` | 254 |
| `EmptyEffectSet` | `"{" "}"` | 255 |
| `ContractClause` | `RequiresClause \| EnsuresClause` | 256 |
| `RequiresClause` | `"requires" PredicateExpr` | 257 |
| `EnsuresClause` | `"ensures" PredicateExpr` | 258 |
| `LineBreakBoundary` | `LINE_BREAK_IN_TRIVIA` | 263 |
| `StatementBoundary` | `STATEMENT_BOUNDARY_BY_CONTEXT` | 264 |
| `IdentifierList` | `Identifier ("," Identifier)* ","?` | 266 |
| `ExpressionList` | `Expr ("," Expr)* ","?` | 267 |
| `PatternList` | `Pattern ("," Pattern)* ","?` | 268 |
| `StaticIntLiteral` | `DECIMAL_INTEGER` | 270 |
| `UnitSyntax` | `"(" ")"` | 273 |
| `SignedStaticInt` | `("+" \| "-")? StaticIntLiteral` | 274 |
| `LawDecl` | `"law" Identifier LawBody? StatementBoundary` | 276 |
| `LawBody` | `"{" LawBodyItem* "}"` | 279 |
| `LawBodyItem` | `LawAssertion StatementBoundary` | 280 |
| `LawAssertion` | `("requires" \| "ensures" \| "invariant")? PredicateExpr` | 281 |
| `Deeplus` | `LibrarySourceFile \| ExecutableSourceFile \| ScriptSourceFile` | 289 |
| `LibrarySourceFile` | `ModuleDecl? LibrarySourceItem* EOF_TOKEN` | 291 |
| `ExecutableSourceFile` | `ModuleDecl? ExecutableSourceItem* EOF_TOKEN` | 292 |
| `ScriptSourceFile` | `Shebang? ModuleDecl? ScriptSourceItem* EOF_TOKEN` | 293 |
| `LibrarySourceItem` | `AnnotationAttachment LibraryAnnotatableDecl \| ImportOrUseDecl \| TopLevelDecl` | 295 |
| `ExecutableSourceItem` | `AnnotationAttachment ExecutableAnnotatableDecl \| ImportOrUseDecl \| NonBindingTopLevelDecl \| EntryFunctionDecl` | 298 |
| `ScriptSourceItem` | `AnnotationAttachment ScriptAnnotatableDecl \| ImportOrUseDecl \| NonBindingTopLevelDecl \| Stmt` | 302 |
| `LibraryAnnotatableDecl` | `ImportOrUseDecl \| TopLevelDecl` | 307 |
| `ExecutableAnnotatableDecl` | `ImportOrUseDecl \| NonBindingTopLevelDecl \| EntryFunctionDecl` | 308 |
| `ScriptAnnotatableDecl` | `ImportOrUseDecl \| NonBindingTopLevelDecl` | 309 |
| `ModuleDecl` | `"module" QualifiedPath StatementBoundary` | 311 |
| `ImportOrUseDecl` | `ImportDecl \| UseDecl \| UseExportDecl` | 313 |
| `ImportDecl` | `"import" QualifiedPath ImportTail? StatementBoundary` | 314 |
| `ImportTail` | `ImportAlias \| ImportSelection` | 315 |
| `ImportAlias` | `NameAliasClause` | 316 |
| `ImportSelection` | `"::" "{" IdentifierList "}"` | 317 |
| `UseDecl` | `"use" QualifiedPath StatementBoundary` | 318 |
| `UseExportDecl` | `"use" "export" QualifiedPath StatementBoundary` | 319 |
| `ExportDecl` | `"export" ExportItem StatementBoundary?` | 322 |
| `ExportItem` | `ExportableModuleFunctionDecl \| TypeDecl \| Identifier` | 323 |
| `ExportableModuleFunctionDecl` | `TopLevelVisibility? "def" Identifier FunctionRest` | 324 |
| `TopLevelDecl` | `NonBindingTopLevelDecl \| TopLevelBindingDecl` | 332 |
| `NonBindingTopLevelDecl` | `TypeDecl \| ModuleFunctionDecl \| ExtensionFunctionDecl \| ActorDecl \| ActorProtocolDecl \| TypestateResourceDecl \| NamedEffectCapabilityDecl \| ExtensionSetDecl \| ExtensionPackDecl \| UnitCatalogDecl \| ModuleInterfaceDecl \| ConformanceDecl \| SchemaDecl \| BitfieldDecl` | 333 |
| `TypeDecl` | `ClassDecl \| TraitDecl \| EnumDecl \| TypeAliasDecl` | 348 |
| `DefIntroducer` | `"def" HashTag*` | 352 |
| `ModuleFunctionDecl` | `TopLevelVisibility? DefIntroducer Identifier FunctionRest` | 354 |
| `EntryFunctionDecl` | `DefIntroducer Identifier EntryFunctionRest` | 355 |
| `ExtensionFunctionDecl` | `TopLevelVisibility? DefIntroducer TypeRef ExtensionFunctionTarget Identifier FunctionRest` | 356 |
| `ExtensionFunctionTarget` | `"~" \| "::"` | 357 |
| `LocalFunctionDecl` | `CaptureList? DefIntroducer Identifier FunctionRest` | 358 |
| `FunctionRest` | `TypeParameterList? ParameterList FunctionTail` | 360 |
| `EntryFunctionRest` | `ParameterList ReturnClause? ThrowsClause* EffectsClause* ContractClause* FunctionBody` | 361 |
| `FunctionTail` | `ReturnClause? ThrowsClause* EffectsClause* ContractClause* WhereClause? FunctionBody` | 362 |
| `TraitFunctionTail` | `ReturnClause? ThrowsClause* EffectsClause* ContractClause* WhereClause? (FunctionBody \| StatementBoundary)` | 363 |
| `FunctionBody` | `"=" FunctionBodyContent` | 365 |
| `FunctionBodyContent` | `CallableBlock \| ReturnShorthand \| ClauseFunctionBody` | 366 |
| `CallableBlock` | `"{" BlockPrologue? FunctionStaticActivation? BlockSequence "}"` | 372 |
| `FunctionStaticActivation` | `"static" Block` | 373 |
| `ReturnShorthand` | `"return" ReturnValueSurface StatementBoundary` | 374 |
| `ClauseFunctionBody` | `"{{" LineBreakBoundary? MatchArmSequence "}}"` | 375 |
| `MemberFunctionDecl` | `MemberVisibility? DefIntroducer Identifier ClassDispatchMarker FunctionRest` | 377 |
| `TypeSideMemberFunctionDecl` | `MemberVisibility? "def" "::" Identifier FunctionRest` | 378 |
| `ConstructorDecl` | `MemberVisibility? "def" "!" Identifier ParameterList ConstructorSignatureTail? ConstructorDelegationClause? "=" Block` | 380 |
| `ConstructorSignatureTail` | `ThrowsClause+ EffectsClause* ContractClause* WhereClause? \| EffectsClause+ ContractClause* WhereClause? \| ContractClause+ WhereClause? \| WhereClause` | 382 |
| `ConstructorDelegationClause` | `":" ConstructorDelegationArm+` | 386 |
| `ConstructorDelegationArm` | `ConstructorDelegationTarget PositiveGuard?` | 387 |
| `ConstructorDelegationTarget` | `Identifier ArgumentList \| "super" "!" Identifier? ArgumentList` | 388 |
| `CleanupDecl` | `DefIntroducer "(" ")" ThrowsClause* EffectsClause* FunctionBody` | 391 |
| `ParameterList` | `"(" ParameterSequence? ")"` | 395 |
| `ParameterSequence` | `CommaParameterSequence \| LayoutParameterSequence` | 396 |
| `CommaParameterSequence` | `Parameter ("," Parameter)* ","?` | 397 |
| `LayoutParameterSequence` | `LineBreakBoundary Parameter (LineBreakBoundary Parameter)* LineBreakBoundary?` | 398 |
| `Parameter` | `StoredParameter \| ContextParameter \| WitnessParameter \| RepeatedParameter \| NamedRestParameter \| ValueParameter` | 400 |
| `ValueParameter` | `ParameterMode? ParameterPatternSlot TypeAnnotation` | 406 |
| `ParameterPatternSlot` | `Identifier IrrefutableParameterPattern?` | 411 |
| `IrrefutableParameterPattern` | `TuplePattern \| ListPattern \| RecordPattern \| NominalPattern` | 412 |
| `ParameterMode` | `"borrow" \| "mut" \| "move" \| "inout"` | 416 |
| `ContextParameter` | `"context" Identifier ":" TypeRef` | 417 |
| `WitnessParameter` | `"using" Identifier ":" "witness" TypeRef` | 418 |
| `RepeatedParameter` | `Identifier ".." TypeAnnotation` | 419 |
| `NamedRestParameter` | `Identifier "**" NamedRestRequirementClause?` | 420 |
| `NamedRestRequirementClause` | `"requires" "{" NamedRestRequirementEntries "}"` | 421 |
| `NamedRestRequirementEntries` | `NamedRestRequirementEntry (PatternEntrySeparator NamedRestRequirementEntry)* PatternEntrySeparator?` | 422 |
| `NamedRestRequirementEntry` | `Identifier ":" TypeRef` | 425 |
| `StoredParameter` | `MemberVisibility? ("let" \| "var") Identifier TypeAnnotation?` | 429 |
| `ClassDecl` | `OrdinaryClassDecl \| DataClassDecl` | 433 |
| `OrdinaryClassDecl` | `TopLevelVisibility? ClassFlavor? ClassModifierSequence? "class" Identifier TypeParameterList? ParameterList? WhereClause? ClassDerivesClause? NominalConformanceClause* CleanupBudgetClause? ClassBody` | 434 |
| `DataClassDecl` | `TopLevelVisibility? "data" "class" Identifier TypeParameterList? ParameterList? WhereClause? NominalConformanceClause* CleanupBudgetClause? ClassBody?` | 438 |
| `ClassFlavor` | `"value" \| "resource"` | 440 |
| `ClassModifierSequence` | `"final" \| "open" \| "abstract" \| "sealed" \| "abstract" "sealed"` | 441 |
| `ClassDerivesClause` | `LineBreakBoundary "derives" TypeRef` | 445 |
| `NominalConformanceClause` | `LineBreakBoundary "conforms" QualifiedTypeReference NominalConformanceRoute? WhereClause?` | 446 |
| `NominalConformanceRoute` | `ConformanceViaClause \| ConformanceAutoClause` | 448 |
| `ClassBody` | `"{" MemberDecl* "}"` | 449 |
| `MemberDecl` | `FieldDecl \| MemberFunctionDecl \| ConstructorDecl \| CleanupDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| ConformBlockDecl \| ForwardDecl` | 451 |
| `FieldDecl` | `MemberVisibility? ("let" \| "var") Identifier TypeAnnotation? Initializer? StatementBoundary` | 461 |
| `TypeSideFieldDecl` | `MemberVisibility? "let" "::" Identifier TypeAnnotation? Initializer? StatementBoundary` | 463 |
| `AccessorPropertyDecl` | `("let" \| "var") Identifier TypeAnnotation ":=" AccessorSpec` | 465 |
| `AccessorSpec` | `AccessorDecl \| "{" AccessorDecl+ "}"` | 466 |
| `AccessorDecl` | `MemberVisibility? "get" Block \| MemberVisibility? "set" "(" Identifier ")" Block` | 467 |
| `ForwardDecl` | `MemberVisibility? "forward" ForwardMemberSpec "to" Expr StatementBoundary` | 469 |
| `ForwardMemberSpec` | `Identifier \| "{" Identifier ("," Identifier)* ","? "}"` | 470 |
| `TraitDecl` | `TopLevelVisibility? "trait" TraitLanguageRole? Identifier TypeParameterList? TraitDerivesClause* TraitAutoSupportClause? TraitBody?` | 474 |
| `TraitLanguageRole` | `"#" ("operator" \| "iteration" \| "interpolation" \| "binding")` | 476 |
| `TraitDerivesClause` | `LineBreakBoundary "derives" QualifiedTypeReference` | 479 |
| `TraitAutoSupportClause` | `LineBreakBoundary "supports" "auto"` | 480 |
| `TraitBody` | `"{" TraitItem* "}"` | 481 |
| `TraitItem` | `TraitMethodDecl \| AssociatedRequirementDecl \| LawDecl` | 482 |
| `TraitMethodDecl` | `MemberVisibility? DefIntroducer Identifier TraitWitnessMarker TypeParameterList? ParameterList TraitFunctionTail` | 484 |
| `AssociatedRequirementDecl` | `AssociatedTypeRequirementDecl \| AssociatedValueRequirementDecl \| AssociatedFunctionRequirementDecl` | 486 |
| `AssociatedTypeRequirementDecl` | `"type" Identifier AssociatedTypeConstraintList? StatementBoundary` | 489 |
| `AssociatedValueRequirementDecl` | `"let" "::" Identifier TypeAnnotation StatementBoundary` | 490 |
| `AssociatedFunctionRequirementDecl` | `"def" "::" Identifier ParameterList ReturnClause? ThrowsClause* EffectsClause* StatementBoundary` | 491 |
| `ConformanceDecl` | `ExplicitConformanceDecl \| AutomaticConformanceDecl` | 494 |
| `ExplicitConformanceDecl` | `TopLevelVisibility? "type" TypeRef "conforms" QualifiedTypeReference NameAliasClause? ConformanceViaClause? WhereClause? (ConformanceBody \| StatementBoundary)` | 495 |
| `AutomaticConformanceDecl` | `TopLevelVisibility? "type" TypeRef "conforms" QualifiedTypeReference NameAliasClause? ConformanceAutoClause WhereClause? StatementBoundary` | 498 |
| `ConformanceViaClause` | `"via" QualifiedPath` | 500 |
| `ConformanceAutoClause` | `"by" "auto"` | 501 |
| `ConformanceBody` | `"{" ConformanceItem* "}"` | 502 |
| `ConformanceMethodDecl` | `MemberVisibility? DefIntroducer ConformanceMethodName TraitWitnessMarker FunctionRest` | 503 |
| `ConformanceMethodName` | `Identifier \| QualifiedTypeReference "::" Identifier` | 505 |
| `ConformBlockDecl` | `"conform" QualifiedTypeReference ConformanceBody` | 511 |
| `ConformanceItem` | `ConformanceMethodDecl \| TypeSideMemberFunctionDecl \| AssociatedRequirementBinding \| ExtensionDelegationDecl \| LawDecl` | 512 |
| `AssociatedRequirementBinding` | `"type" Identifier "=" TypeRef StatementBoundary \| "let" "::" Identifier "=" Expr StatementBoundary` | 517 |
| `ExtensionDelegationDecl` | `"delegate" Identifier "to" QualifiedExtensionSelector StatementBoundary` | 519 |
| `ExtensionSetDecl` | `TopLevelVisibility? "extension" TypeRef "as" Identifier ExtensionSetBody` | 523 |
| `ExtensionSetBody` | `"{" ExtensionSetItem* "}"` | 524 |
| `ExtensionSetItem` | `ExtensionSetFunctionDecl \| TypeSideMemberFunctionDecl` | 525 |
| `ExtensionSetFunctionDecl` | `MemberVisibility? "def" Identifier ParameterList? ReturnClause? ThrowsClause* EffectsClause* WhereClause? FunctionBody` | 526 |
| `ExtensionPackDecl` | `"extension" "pack" QualifiedPath ExtensionPackBody` | 528 |
| `ExtensionPackBody` | `"{" UseExportDecl* "}"` | 529 |
| `EnumDecl` | `TopLevelVisibility? "enum" EnumOrderRole? Identifier TypeParameterList? NominalConformanceClause* EnumBody` | 533 |
| `EnumOrderRole` | `"#" ("increasing" \| "decreasing")` | 535 |
| `EnumBody` | `"{" (EnumCommaCaseSequence \| EnumLayoutBody) "}"` | 536 |
| `EnumCommaCaseSequence` | `EnumCaseCore ("," EnumCaseCore)+ ","?` | 537 |
| `EnumLayoutBody` | `EnumCaseDecl+ EnumMemberDecl*` | 538 |
| `EnumCaseDecl` | `EnumCaseCore StatementBoundary?` | 539 |
| `EnumCaseCore` | `Identifier EnumCasePayload? EnumCaseDisplayMapping?` | 540 |
| `EnumCasePayload` | `"(" EnumCaseFieldList? ")"` | 541 |
| `EnumCaseFieldList` | `EnumCaseField ("," EnumCaseField)* ","?` | 542 |
| `EnumCaseField` | `Identifier TypeAnnotation \| TypeRef` | 543 |
| `EnumMemberDecl` | `MemberFunctionDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| ConformBlockDecl \| EnumVariantSubsetAliasDecl` | 544 |
| `EnumCaseDisplayMapping` | `"~>" RestrictedEnumDisplayTemplate` | 550 |
| `RestrictedEnumDisplayTemplate` | `PLAIN_STRING_LITERAL \| MULTILINE_STRING_LITERAL \| InterpolatedString` | 551 |
| `EnumVariantSubsetAliasDecl` | `"+" "type" Identifier "=" EnumVariantSubsetRhs StatementBoundary?` | 554 |
| `EnumVariantSubsetRhs` | `Identifier ("\|" Identifier)*` | 556 |
| `SchemaDecl` | `TopLevelVisibility? "schema" Identifier TypeParameterList? SchemaBody` | 560 |
| `SchemaBody` | `"{" SchemaFieldSequence? "}"` | 561 |
| `SchemaFieldSequence` | `CommaSchemaFields \| LayoutSchemaFields` | 562 |
| `CommaSchemaFields` | `SchemaFieldDecl ("," SchemaFieldDecl)* ","?` | 563 |
| `LayoutSchemaFields` | `LineBreakBoundary LayoutSchemaFieldDecl (LineBreakBoundary LayoutSchemaFieldDecl)* LineBreakBoundary?` | 564 |
| `SchemaFieldDecl` | `Identifier TypeAnnotation Initializer? SchemaConstraint* StatementBoundary?` | 565 |
| `LayoutSchemaFieldDecl` | `Identifier TypeAnnotation Initializer? SchemaConstraint*` | 566 |
| `SchemaConstraint` | `"where" Expr` | 567 |
| `TypeAliasDecl` | `TopLevelVisibility? "type" Identifier TypeParameterList? "=" TypeAliasRhs StatementBoundary` | 569 |
| `TypeAliasRhs` | `TypeRef RefinementSuffix? \| StaticRangeType` | 570 |
| `StaticRangeType` | `StaticIntLiteral ".." StaticIntLiteral` | 571 |
| `TopLevelBindingDecl` | `TopLevelVisibility? ("let" \| "var") Identifier TypeAnnotation? "=" Expr StatementBoundary` | 573 |
| `NamedEffectCapabilityDecl` | `TopLevelVisibility? "capability" Identifier "for" EffectRow StatementBoundary` | 574 |
| `ActorDecl` | `TopLevelVisibility? "actor" MailboxClause? Identifier ActorProtocolConformanceClause* ActorBody` | 578 |
| `MailboxClause` | `HashTag "(" "capacity" ":" StaticIntLiteral ")"` | 580 |
| `ActorBody` | `"{" ActorItem* "}"` | 581 |
| `ActorProtocolConformanceClause` | `LineBreakBoundary "conforms" QualifiedTypeReference WhereClause?` | 582 |
| `ActorItem` | `ActorOnDecl \| ActorRequestDecl \| ActorMemberDecl \| ActorProtocolConformBlock` | 584 |
| `ActorMemberDecl` | `FieldDecl \| MemberFunctionDecl \| ConstructorDecl \| CleanupDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| ForwardDecl` | 588 |
| `ActorOnDecl` | `MemberVisibility? "on" Identifier ParameterList? ThrowsClause* EffectsClause* FunctionBody` | 596 |
| `ActorRequestDecl` | `MemberVisibility? "request" Identifier ParameterList? ReturnClause ThrowsClause* EffectsClause* FunctionBody` | 597 |
| `ActorProtocolConformBlock` | `"conform" QualifiedTypeReference ActorProtocolConformanceBody` | 603 |
| `ActorProtocolConformanceBody` | `"{" ActorProtocolConformanceItem* "}"` | 604 |
| `ActorProtocolConformanceItem` | `ActorOnDecl \| ActorRequestDecl` | 605 |
| `ActorProtocolDecl` | `TopLevelVisibility? "protocol" Identifier ActorProtocolBody` | 607 |
| `ActorProtocolBody` | `"{" ActorProtocolItem* "}"` | 608 |
| `ActorProtocolItem` | `ActorProtocolSendRequirement \| ActorProtocolRequestRequirement` | 609 |
| `ActorProtocolSendRequirement` | `"send" Identifier ParameterList? ThrowsClause* EffectsClause* StatementBoundary` | 610 |
| `ActorProtocolRequestRequirement` | `"request" Identifier ParameterList? ReturnClause ThrowsClause* EffectsClause* StatementBoundary` | 611 |
| `TypestateResourceDecl` | `TopLevelVisibility? "typestate" Identifier TypeParameterList? TypestateBody` | 615 |
| `TypestateBody` | `"{" TypestateTransitionDecl* "}"` | 616 |
| `TypestateTransitionDecl` | `Identifier "->" Identifier FunctionBody?` | 617 |
| `UnitCatalogDecl` | `TopLevelVisibility? "unit" "catalog" Identifier UnitCatalogBody` | 619 |
| `UnitCatalogBody` | `"{" UnitCatalogEntry* "}"` | 620 |
| `UnitCatalogEntry` | `ExactRatioUnitConversionDecl \| Identifier "=" UnitExpr StatementBoundary` | 621 |
| `ExactRatioUnitConversionDecl` | `"unit" Identifier "equalsRatio" MeasureLiteralExpr "/" StaticIntLiteral StatementBoundary` | 622 |
| `ModuleInterfaceDecl` | `ModuleSignatureDecl \| OpaqueModuleFacadeDecl` | 624 |
| `ModuleSignatureDecl` | `TopLevelVisibility? "module" "signature" QualifiedPath ModuleInterfaceBody` | 625 |
| `OpaqueModuleFacadeDecl` | `TopLevelVisibility? "opaque" "module" QualifiedPath ModuleInterfaceBody` | 626 |
| `ModuleInterfaceBody` | `"{" ModuleInterfaceItem* "}"` | 627 |
| `ModuleInterfaceItem` | `ExportDecl \| UseExportDecl \| OpaqueModuleFacadeDecl` | 628 |
| `CleanupBudgetClause` | `"cleanup" "budget" "{" CleanupBudgetItem* "}"` | 632 |
| `CleanupBudgetItem` | `EffectsBudget \| ErrorsBudget` | 633 |
| `EffectsBudget` | `"effects" "{" IdentifierList? "}"` | 634 |
| `ErrorsBudget` | `"errors" TypeRef` | 635 |
| `BitfieldDecl` | `TopLevelVisibility? BitfieldIntroducer Identifier BitfieldBackingClause BitfieldOrderClause BitfieldBody` | 639 |
| `BitfieldIntroducer` | `"bitfield" HashTag?` | 641 |
| `BitfieldBackingClause` | `"backing" TypeRef` | 642 |
| `BitfieldOrderClause` | `"order" "::" "lsb0"` | 643 |
| `BitfieldBody` | `"{" BitfieldLayoutSection BitfieldMemberDecl* "}"` | 644 |
| `BitfieldLayoutSection` | `BitfieldSlotDecl+ \| FlagSlotDecl+` | 645 |
| `BitfieldSlotDecl` | `BitfieldNamedSlot StatementBoundary \| BitfieldReservedSlot StatementBoundary` | 646 |
| `FlagSlotDecl` | `FlagNamedSlot StatementBoundary \| BitfieldReservedSlot StatementBoundary` | 647 |
| `BitfieldNamedSlot` | `MemberVisibility? Identifier ":" StaticIntLiteral BitfieldDefault?` | 648 |
| `BitfieldReservedSlot` | `"_" ":" StaticIntLiteral` | 649 |
| `FlagNamedSlot` | `MemberVisibility? Identifier` | 650 |
| `BitfieldDefault` | `"=" Literal` | 651 |
| `BitfieldMemberDecl` | `MemberFunctionDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| LawDecl` | 652 |
| `TypeRef` | `PrattType` | 664 |
| `NonFunctionTypeRef` | `PrattNonFunctionType` | 665 |
| `TypePrimary` | `QualifiedTypeReference \| FacetType \| ParenTypeSyntax \| SharpShapeType \| ExistentialType \| OpaqueType \| TypeofType \| AssociatedProjection` | 668 |
| `TypePrefixParselet` | `OwnershipQualifier` | 676 |
| `TypePostfixParselet` | `"?"` | 677 |
| `TypeInfixOperator` | `"&" \| "\|"` | 678 |
| `QualifiedTypeReference` | `QualifiedPath TypeArgumentList?` | 680 |
| `FacetType` | `"Facet" "<" "borrow" "any" QualifiedTypeReference AssociatedTypeConstraintList? ">"` | 682 |
| `OwnershipQualifier` | `"owned" \| "borrowed" \| "mut" \| "inout"` | 683 |
| `ParenTypeSyntax` | `HashTag* "(" ParenTypeItemList? ")" FunctionTypeTail?` | 691 |
| `ParenTypeItemList` | `ParenTypeItem ("," ParenTypeItem)* ","?` | 692 |
| `ParenTypeItem` | `FunctionTypeModeItem \| TypeRef \| TypeRef ".." \| TypeRef "**"` | 693 |
| `FunctionTypeModeItem` | `ParameterMode TypeRef` | 696 |
| `FunctionTypeTail` | `"->" ReturnTypeSurface ThrowsClause* EffectsClause*` | 697 |
| `SharpShapeType` | `"#" StaticDimensionList "[" TypeRef "]"` | 699 |
| `StaticDimensionList` | `StaticIntLiteral ("," StaticIntLiteral)*` | 700 |
| `ExistentialType` | `"any" QualifiedTypeReference AssociatedTypeConstraintList?` | 702 |
| `OpaqueType` | `"some" QualifiedTypeReference AssociatedTypeConstraintList?` | 703 |
| `TypeofType` | `"typeof" TypeofStaticSampleOperand` | 704 |
| `AssociatedProjection` | `"<" TypeRef "as" QualifiedTypeReference ">" "::" Identifier` | 705 |
| `TypeofStaticSampleOperand` | `Literal \| ListLiteral \| StaticPrefixedCollectionSample \| NumericArrayLiteral \| MeasureLiteralExpr` | 708 |
| `StaticPrefixedCollectionSample` | `MapLiteral \| SetLiteral \| MutListLiteral` | 713 |
| `PrattType` | `TYPE_PRATT_ENTRY` | 716 |
| `PrattNonFunctionType` | `NON_FUNCTION_TYPE_PRATT_ENTRY` | 717 |
| `Pattern` | `OrPattern` | 725 |
| `OrPattern` | `AliasPattern ("\|" AliasPattern)*` | 726 |
| `AliasPattern` | `MovePattern ("as" Identifier)?` | 727 |
| `MovePattern` | `"move"? PatternPrimary` | 728 |
| `PatternPrimary` | `TypedBindingPattern \| Identifier \| PinPattern \| RangePattern \| RelationalPattern \| TuplePattern \| RecordPattern \| ListPattern \| MapPattern \| VariantPattern \| NominalPattern \| "_" \| UnitSyntax \| Literal \| ParenthesizedPattern` | 730 |
| `TypedBindingPattern` | `Identifier ":" TypeRef` | 746 |
| `ParenthesizedPattern` | `"(" Pattern ")"` | 747 |
| `PinPattern` | `"^" StablePatternValue` | 748 |
| `StablePatternValue` | `Identifier \| QualifiedStaticExpr \| Literal` | 749 |
| `RangePattern` | `PatternBound (".." \| "..<") PatternBound` | 750 |
| `RelationalPattern` | `("<" \| "<=" \| ">" \| ">=") PatternBound` | 751 |
| `PatternBound` | `Literal \| PinPattern` | 752 |
| `TuplePattern` | `"(" TuplePatternItems ")"` | 756 |
| `TuplePatternItems` | `Pattern "," \| Pattern "," Pattern ("," Pattern)* ","?` | 757 |
| `BindingPattern` | `BindingOrPattern TypeAnnotation?` | 769 |
| `BindingOrPattern` | `BindingAliasPattern ("\|" BindingAliasPattern)*` | 770 |
| `BindingAliasPattern` | `BindingMovePattern ("as" Identifier)?` | 771 |
| `BindingMovePattern` | `"move"? BindingPatternPrimary` | 772 |
| `BindingPatternPrimary` | `Identifier \| PinPattern \| RangePattern \| RelationalPattern \| TuplePattern \| RecordPattern \| ListPattern \| MapPattern \| VariantPattern \| NominalPattern \| "_" \| UnitSyntax \| Literal \| ParenthesizedPattern` | 773 |
| `RecordPattern` | `"${" RecordPatternEntries? "}"` | 792 |
| `RecordPatternEntries` | `RecordPatternEntry (PatternEntrySeparator RecordPatternEntry)* PatternEntrySeparator?` | 793 |
| `RecordPatternEntry` | `Identifier \| Identifier ":" RecordDestination \| RecordRestPattern` | 795 |
| `RecordDestination` | `Pattern` | 796 |
| `RecordRestPattern` | `RestBinder "**"` | 797 |
| `MapPattern` | `"#" "map" "{" MapPatternEntries? "}"` | 799 |
| `MapPatternEntries` | `MapPatternEntry (PatternEntrySeparator MapPatternEntry)* PatternEntrySeparator?` | 800 |
| `MapPatternEntry` | `MapDestination ":" MapKeyPattern \| MapRestPattern` | 802 |
| `MapDestination` | `Pattern` | 803 |
| `MapKeyPattern` | `Literal \| PinPattern` | 804 |
| `MapRestPattern` | `"*" RestBinder` | 805 |
| `PatternEntrySeparator` | `"," LineBreakBoundary? \| LineBreakBoundary` | 806 |
| `ListPattern` | `"[" ListPatternBody? "]"` | 810 |
| `ListPatternBody` | `IgnoredAllListRest \| ExactListPattern \| PrefixRestListPattern \| SuffixRestListPattern \| MiddleRestListPattern` | 811 |
| `ExactListPattern` | `Pattern ("," Pattern)* ","?` | 816 |
| `PrefixRestListPattern` | `PrefixListRest "," Pattern ("," Pattern)* ","?` | 817 |
| `SuffixRestListPattern` | `Pattern ("," Pattern)* "," SuffixListRest ","?` | 818 |
| `MiddleRestListPattern` | `Pattern ("," Pattern)* "," MiddleListRest "," Pattern ("," Pattern)* ","?` | 819 |
| `PrefixListRest` | `ListRestPattern` | 821 |
| `SuffixListRest` | `ListRestPattern` | 822 |
| `MiddleListRest` | `ListRestPattern` | 823 |
| `IgnoredAllListRest` | `"_" ".." ","?` | 824 |
| `ListRestPattern` | `RestBinder ".."` | 825 |
| `RestBinder` | `Identifier \| "_"` | 826 |
| `VariantPattern` | `VariantQualifier Identifier VariantPatternPayload?` | 828 |
| `VariantQualifier` | `TypeRef "::" \| "::"` | 829 |
| `VariantPatternPayload` | `VariantPositionalPatternPayload \| RecordPattern` | 830 |
| `VariantPositionalPatternPayload` | `"(" PatternList? ")"` | 831 |
| `NominalPattern` | `TypeRef RecordPattern` | 836 |
| `Stmt` | `ForLoop \| WhileLoop \| RepeatLoop \| AsyncForLoop \| MatchStatement \| IfStmt \| LocalBindingStmt \| AssertiveBindingStmt \| MutableListStructuralEditStmt \| PatternAssignmentStmt \| ParallelAssignmentStmt \| ControlTransferStmt \| TryStmt \| DeferStmt \| ScopedUseStmt \| ExprStmt \| ScopedImportStmt` | 844 |
| `ExprStmt` | `Expr StatementBoundary` | 862 |
| `Block` | `"{" BlockPrologue? BlockSequence "}"` | 864 |
| `BlockPrologue` | `(UseDecl \| ImportDecl)+` | 865 |
| `BlockSequence` | `BlockItem* BlockFinalItem?` | 866 |
| `BlockItem` | `LocalFunctionDecl \| Stmt` | 867 |
| `BlockFinalItem` | `ControlTransfer \| BindingCore \| Expr` | 870 |
| `ValueBody` | `SingleExpressionValueBody \| ExplicitRetValueBody` | 873 |
| `SingleExpressionValueBody` | `"{" ReturnValueSurface "}"` | 874 |
| `ExplicitRetValueBody` | `"{" BlockItem* RetTransfer "}"` | 875 |
| `RetTransfer` | `"ret" ReturnValueSurface? GuardClause?` | 876 |
| `BindingCore` | `("let" \| "var") BindingHead "=" BindingValueSurface` | 881 |
| `BindingHead` | `BindingPattern \| BareTupleBindingSurface` | 882 |
| `BareTupleBindingSurface` | `BindingPattern "," BindingPattern ("," BindingPattern)*` | 883 |
| `BindingValueSurface` | `Expr \| BareTupleValueSurface` | 884 |
| `ReturnValueSurface` | `Expr \| BareTupleValueSurface` | 885 |
| `BareTupleValueSurface` | `Expr "," Expr ("," Expr)*` | 886 |
| `LocalBindingStmt` | `BindingCore StatementBoundary \| RightwardLocalBindingSurface \| LazyBindingStmt \| GuardedBindingStmt` | 887 |
| `LazyBindingStmt` | `"let" HashTag Identifier TypeAnnotation? "=" Expr StatementBoundary` | 888 |
| `GuardedBindingStmt` | `"let" "?" BindingPattern "=" Expr "else" Pattern "=>" GuardedBindingExit StatementBoundary?` | 889 |
| `AssertiveBindingStmt` | `("let" \| "var") "!" BindingPattern "=" Expr StatementBoundary` | 890 |
| `GuardedBindingExit` | `GuardedReturnExit \| GuardedThrowExit \| GuardedBreakExit \| GuardedContinueExit` | 893 |
| `GuardedReturnExit` | `"return" Expr?` | 894 |
| `GuardedThrowExit` | `"throw" Expr` | 895 |
| `GuardedBreakExit` | `("break")+ Expr?` | 896 |
| `GuardedContinueExit` | `("break")* "continue"` | 897 |
| `ControlTransferStmt` | `ControlTransfer StatementBoundary` | 900 |
| `ControlTransfer` | `ReturnTransfer \| ThrowTransfer \| BreakTransfer \| ContinueTransfer \| YieldTransfer` | 901 |
| `ReturnTransfer` | `"return" ReturnValueSurface? GuardClause?` | 902 |
| `ThrowTransfer` | `"throw" Expr GuardClause?` | 903 |
| `BreakTransfer` | `("break")+ Expr? GuardClause?` | 904 |
| `ContinueTransfer` | `("break")* "continue" GuardClause?` | 905 |
| `YieldTransfer` | `"yield" Expr? (GuardClause \| YieldResponseBinding)?` | 906 |
| `YieldResponseBinding` | `"->" DollarLocalBinding` | 907 |
| `DollarLocalBinding` | `"$" Identifier TypeAnnotation? \| "$$" Identifier TypeAnnotation?` | 908 |
| `GuardClause` | `PositiveGuard \| NegativeGuard` | 910 |
| `PositiveGuard` | `"if" Expr` | 911 |
| `NegativeGuard` | `"!" "if" Expr` | 912 |
| `IfStmt` | `"if" PatternConditionChain Block ("else" (IfStmt \| Block))?` | 914 |
| `PatternConditionChain` | `PatternControlCondition ("and" "then" PatternControlCondition)*` | 917 |
| `PatternControlCondition` | `Expr \| "let" Pattern "=" Expr` | 919 |
| `ForLoop` | `"for" ("let" Pattern \| Pattern) "in" Expr GuardClause? Block MatchStatement?` | 923 |
| `WhileLoop` | `"while" PatternConditionChain Block MatchStatement?` | 924 |
| `RepeatLoop` | `"repeat" Block "while" Expr MatchStatement?` | 925 |
| `AsyncForLoop` | `"for" ForAwaitRole ("let" Pattern \| Pattern) "in" Expr GuardClause? Block` | 929 |
| `ForAwaitRole` | `"#" "await"` | 930 |
| `MatchStatement` | `"match" MatchCore` | 932 |
| `MatchCore` | `MatchSubjectSlot MatchBody` | 933 |
| `MatchSubjectSlot` | `MATCH_SUBJECT_BY_INPUT_SUPPLY_POLICY` | 934 |
| `MatchBody` | `"{" LineBreakBoundary? MatchArmSequence "}"` | 935 |
| `MatchArmSequence` | `MatchArm (MatchArmSeparator MatchArm)* MatchArmSeparator?` | 936 |
| `MatchArm` | `MatchHead GuardClause? "=>" MatchArmBodySlot` | 937 |
| `MatchHead` | `BoundedBinderPattern \| Pattern \| "otherwise"` | 938 |
| `BoundedBinderPattern` | `PatternBound OrderedComparisonOperator Identifier OrderedComparisonOperator PatternBound` | 944 |
| `MatchArmSeparator` | `MATCH_ARM_SEPARATOR_BY_CONTEXT` | 946 |
| `MatchArmBodySlot` | `MATCH_ARM_BODY_BY_CONTEXT` | 947 |
| `TryStmt` | `"try" Block (CatchClause+ FinallyClause? \| FinallyClause)` | 951 |
| `CatchClause` | `"catch" Pattern? GuardClause? Block` | 952 |
| `ValueCatchClause` | `"catch" Pattern? GuardClause? ValueBody` | 953 |
| `FinallyClause` | `"finally" Block` | 954 |
| `DeferStmt` | `"defer" DeferredCleanupInvocation StatementBoundary` | 956 |
| `DeferredCleanupInvocation` | `DeferredDirectCall \| DeferredMessageCall` | 959 |
| `DeferredDirectCall` | `DeferredReceiver ArgumentList` | 960 |
| `DeferredMessageCall` | `DeferredReceiver "~" MessageSelector TildeArgumentSequence?` | 961 |
| `DeferredReceiver` | `DeferredPrimary DeferTargetSuffix*` | 962 |
| `DeferredPrimary` | `Identifier \| QualifiedStaticExpr` | 963 |
| `DeferTargetSuffix` | `IndexSuffix \| MemberSuffix` | 964 |
| `RightwardLocalBindingSurface` | `Expr "->" DollarLocalBinding StatementBoundary` | 968 |
| `PatternAssignmentStmt` | `AssigneePattern "=" Expr StatementBoundary` | 972 |
| `AssigneePattern` | `AssigneeTuplePattern \| AssigneeListPattern \| AssigneeRecordPattern \| AssigneeNominalPattern` | 973 |
| `AssigneePrimary` | `Identifier \| "_"` | 977 |
| `AssigneeTuplePattern` | `"(" AssigneeTupleItems ")"` | 978 |
| `AssigneeTupleItems` | `AssigneePatternItem "," \| AssigneePatternItem "," AssigneePatternItem ("," AssigneePatternItem)* ","?` | 979 |
| `AssigneePatternItem` | `AssigneePrimary \| AssigneeTuplePattern \| AssigneeListPattern \| AssigneeRecordPattern` | 982 |
| `AssigneeListPattern` | `"[" AssigneeListBody? "]"` | 986 |
| `AssigneeListBody` | `AssigneeIgnoredAllRest \| AssigneeExactList \| AssigneePrefixRestList \| AssigneeSuffixRestList \| AssigneeMiddleRestList` | 987 |
| `AssigneeExactList` | `AssigneePatternItem ("," AssigneePatternItem)* ","?` | 992 |
| `AssigneePrefixRestList` | `AssigneeRestPattern "," AssigneeExactList` | 993 |
| `AssigneeSuffixRestList` | `AssigneeExactList "," AssigneeRestPattern ","?` | 994 |
| `AssigneeMiddleRestList` | `AssigneeExactList "," AssigneeRestPattern "," AssigneeExactList` | 995 |
| `AssigneeIgnoredAllRest` | `"_" ".." ","?` | 997 |
| `AssigneeRestPattern` | `("_" \| Identifier) ".."` | 998 |
| `AssigneeRecordPattern` | `"${" AssigneeRecordEntries? "}"` | 999 |
| `AssigneeRecordEntries` | `AssigneeRecordEntry (PatternEntrySeparator AssigneeRecordEntry)* PatternEntrySeparator?` | 1000 |
| `AssigneeRecordEntry` | `Identifier \| Identifier ":" AssigneePatternItem \| AssigneeRecordRestPattern` | 1003 |
| `AssigneeRecordRestPattern` | `("_" \| Identifier) "**"` | 1004 |
| `AssigneeNominalPattern` | `TypeRef AssigneeRecordPattern` | 1005 |
| `MutableListStructuralEditStmt` | `MutableListInsertStmt \| MutableListRemoveStmt` | 1009 |
| `MutableListInsertStmt` | `MutableListEditReceiver MutableListInsertSuffix "=" MutableListInsertPayload StatementBoundary` | 1010 |
| `MutableListEditReceiver` | `MUTABLE_LIST_EDIT_RECEIVER_BY_OWNER` | 1011 |
| `MutableListInsertSuffix` | `"[" ("@" SliceIndexExpr \| SliceIndexExpr "@" \| "@" "^" \| "$" "@") "]"` | 1012 |
| `MutableListInsertPayload` | `Expr \| "*" Expr` | 1013 |
| `MutableListRemoveStmt` | `MutableListEditReceiver MutableListRemoveSuffix MutableListRemovalCapture? StatementBoundary` | 1014 |
| `MutableListRemoveSuffix` | `"[" ("-" "@" MutableListRemovalSelector \| "-" "^" \| "-" "$") "]"` | 1015 |
| `MutableListRemovalSelector` | `SliceIndexExpr \| SliceRange \| "(" SliceIndexExpr "," SliceIndexExpr ("," SliceIndexExpr)* ","? ")"` | 1016 |
| `MutableListRemovalCapture` | `"->" DollarLocalBinding` | 1019 |
| `ParallelAssignmentStmt` | `BareTuplePlaceSurface "=" AssignmentValueSurface StatementBoundary` | 1020 |
| `BareTuplePlaceSurface` | `Identifier "," Identifier ("," Identifier)*` | 1021 |
| `AssignmentValueSurface` | `Expr \| BareTupleValueSurface` | 1022 |
| `ScopedUseStmt` | `"use" ScopedPathList "in" Block` | 1023 |
| `ScopedImportStmt` | `"import" ScopedPathList "in" Block` | 1024 |
| `ScopedPathList` | `QualifiedPath ("," QualifiedPath)*` | 1025 |
| `Expr` | `PrattExpr` | 1033 |
| `PredicateExpr` | `PrattPredicateExpr` | 1034 |
| `SliceIndexExpr` | `PrattSliceIndexExpr` | 1035 |
| `ExpressionPrefixParselet` | `"+" \| "-" \| "not" \| "~~" \| "move" \| "borrow" \| "&" \| "await"` | 1041 |
| `ExpressionPostfixParselet` | `CallSuffix \| TildeCallLed \| TupleOrdinalSuffix \| IndexSuffix \| MemberSuffix \| NumericArrayTransposeSuffix \| ConstructorCallSuffix \| NamedConstructorCallSuffix \| PrototypeDerivationSuffix \| CastSuffix` | 1047 |
| `PrimaryExpr` | `Literal \| Identifier \| ImplicitAtExpr \| ParenExprSyntax \| ListLiteral \| BoundedListLiteral \| ComprehensionExpr \| MaterializationBody \| TypedMaterializationExpr \| MapLiteral \| SetLiteral \| MutListLiteral \| MapComprehensionExpr \| SetComprehensionExpr \| NumericArrayLiteral \| MeasureLiteralExpr \| QualifiedStaticExpr \| ExpectedVariantExpr \| AtControlExpr \| MatchExpr \| ClosureExpr \| GeneratorExpr \| SpawnExpr \| ConcurExpr \| UnsafeBlockExpr \| FacetExpr` | 1058 |
| `ParenExprSyntax` | `"(" ParenExprContent? ")"` | 1086 |
| `ParenExprContent` | `Expr ParenExprTail?` | 1087 |
| `ParenExprTail` | `"," \| "," Expr ("," Expr)* ","?` | 1088 |
| `ImplicitAtExpr` | `"@"` | 1089 |
| `ExpectedVariantExpr` | `"::" Identifier` | 1090 |
| `CallSuffix` | `ArgumentList TrailingClosureGroup? \| AtomicCallArgument TrailingClosureGroup` | 1094 |
| `ArgumentList` | `"(" ")" \| "(" CommaArgumentSequence ")" \| "(" LayoutArgumentSequence ")"` | 1097 |
| `CommaArgumentSequence` | `Argument ("," Argument)* ","?` | 1100 |
| `LayoutArgumentSequence` | `LineBreakBoundary NamedLayoutArgument LineBreakBoundary NamedLayoutArgument (LineBreakBoundary NamedLayoutArgument)* LineBreakBoundary?` | 1102 |
| `NamedLayoutArgument` | `NamedArgument \| NamedUnfoldArgument` | 1104 |
| `Argument` | `ContextArgument \| WitnessArgument \| NamedArgument \| PositionalUnfoldArgument \| NamedUnfoldArgument \| Expr` | 1105 |
| `ContextArgument` | `"context" Expr` | 1111 |
| `WitnessArgument` | `"using" WitnessArgumentValue` | 1112 |
| `WitnessArgumentValue` | `Identifier \| ConformanceEvidenceSelector \| NamedConformanceEvidenceSelector` | 1113 |
| `NamedArgument` | `Identifier ":" Expr` | 1114 |
| `PositionalUnfoldArgument` | `"*" Expr` | 1115 |
| `NamedUnfoldArgument` | `"**" Expr` | 1116 |
| `AtomicCallArgument` | `Literal \| Identifier \| QualifiedStaticExpr \| ExpectedVariantExpr` | 1117 |
| `TrailingClosureGroup` | `TrailingClosureArgument+` | 1121 |
| `TrailingClosureArgument` | `ClosureExpr \| Identifier ":" ClosureExpr` | 1122 |
| `IndexSuffix` | `"[" SliceAxisList "]"` | 1126 |
| `SliceAxisList` | `SliceAxis ("," SliceAxis)*` | 1127 |
| `SliceAxis` | `SliceRange \| SliceIndexExpr \| AxisWildcard` | 1128 |
| `SliceRange` | `SliceBound? ".." SliceBound? \| SliceBound? "..<" SliceBound` | 1131 |
| `SliceBound` | `SliceIndexExpr \| "^" \| "$" \| "^" OffsetExpr \| "$" OffsetExpr` | 1133 |
| `OffsetExpr` | `("+" \| "-") NumericLiteral` | 1134 |
| `AxisWildcard` | `"*"` | 1135 |
| `TupleOrdinalSuffix` | `"." StaticIntLiteral` | 1137 |
| `MemberSuffix` | `"." Identifier \| "." "\\\\" NAME_TOKEN` | 1138 |
| `TildeCallLed` | `TildeCallToken MessageSelector TildeArgumentSequence? TrailingClosureGroup?` | 1144 |
| `TildeCallToken` | `"~" \| ":~"` | 1146 |
| `MessageSelector` | `Identifier \| QualifiedMessageSelector` | 1147 |
| `QualifiedMessageSelector` | `TypeRef "::" Identifier ("::" Identifier)?` | 1148 |
| `QualifiedExtensionSelector` | `TypeRef "::" Identifier "::" Identifier` | 1149 |
| `TildeArgumentSequence` | `TildeArgument ("," TildeArgument)*` | 1150 |
| `TildeArgument` | `ContextArgument \| WitnessArgument \| NamedArgument \| PositionalUnfoldArgument \| NamedUnfoldArgument \| Expr` | 1151 |
| `NumericArrayTransposeSuffix` | `"^"` | 1158 |
| `ConstructorCallSuffix` | `"!" ArgumentList` | 1159 |
| `NamedConstructorCallSuffix` | `"!" Identifier ArgumentList` | 1160 |
| `PrototypeDerivationSuffix` | `("!" \| "!!") DerivationBody` | 1161 |
| `DerivationBody` | `"{" MaterializationEntryList? "}"` | 1162 |
| `CastSuffix` | `"as" "?" TypeRef \| "as" "!" TypeRef` | 1164 |
| `QualifiedStaticExpr` | `StaticQualifier "::" Identifier \| TraitQualifiedAssociatedSelector` | 1166 |
| `StaticQualifier` | `QualifiedTypeReference \| AssociatedProjection` | 1168 |
| `TraitQualifiedAssociatedSelector` | `"<" TypeRef "as" QualifiedTypeReference ">" "::" Identifier` | 1169 |
| `AtControlExpr` | `AtIfExpr \| AtTryExpr \| AtScopeExpr` | 1175 |
| `AtIfExpr` | `"@" "if" Expr ValueBody "else" ValueBody` | 1177 |
| `AtTryExpr` | `"@" "try" ValueBody (ValueCatchClause+ FinallyClause? \| FinallyClause)` | 1178 |
| `AtScopeExpr` | `"@" "scope" ScopeModifier* ValueBody` | 1179 |
| `ScopeModifier` | `"isolated" \| "cancellable" \| "shielded"` | 1180 |
| `MatchExpr` | `"@" "match" MatchCore` | 1182 |
| `ClosureExpr` | `CaptureList? HashTag* "{" ClosureContent "}"` | 1186 |
| `ClosureContent` | `ExplicitLambdaContent \| LambdaBody?` | 1191 |
| `ExplicitLambdaContent` | `LambdaParameterList? "=>" LambdaBody` | 1192 |
| `LambdaParameterList` | `LambdaParameter ("," LambdaParameter)* ","?` | 1193 |
| `LambdaParameter` | `ParameterMode? LambdaParameterPattern TypeAnnotation?` | 1194 |
| `LambdaParameterPattern` | `Identifier \| IrrefutableParameterPattern` | 1195 |
| `LambdaBody` | `ReturnValueSurface \| LineBreakBoundary LambdaBlockContent` | 1196 |
| `LambdaBlockContent` | `BlockItem* LambdaFinalItem?` | 1197 |
| `LambdaFinalItem` | `RetTransfer \| Expr` | 1198 |
| `CaptureList` | `"[" CaptureItemList? "]"` | 1200 |
| `CaptureItemList` | `CaptureItem ("," CaptureItem)* ","?` | 1201 |
| `CaptureItem` | `("let" \| "var") Identifier "=" Expr \| CaptureMode Identifier \| Identifier` | 1202 |
| `CaptureMode` | `"borrow" \| "inout" \| "move" \| "clone" \| "deep" \| "copy" \| "once"` | 1205 |
| `GeneratorExpr` | `CaptureList? GeneratorCore` | 1223 |
| `GeneratorCore` | `"@" "for" Pattern "in" Expr Block \| "@" "while" Expr Block \| "@" "repeat" Block "while" Expr` | 1224 |
| `SpawnExpr` | `"spawn" (SpawnBody \| SpawnOperandSlot)` | 1232 |
| `SpawnBody` | `"{" "=>" SpawnBodySequence "}"` | 1233 |
| `SpawnBodySequence` | `LineBreakBoundary? BlockSequence` | 1234 |
| `SpawnOperandSlot` | `SPAWN_OPERAND_BY_PREFIX_PARSER` | 1235 |
| `ConcurExpr` | `"concur" Block` | 1236 |
| `UnsafeBlockExpr` | `"unsafe" Block` | 1237 |
| `FacetExpr` | `"facet" "[" "borrow" Expr "as" QualifiedTypeReference AssociatedTypeConstraintList? "]"` | 1240 |
| `ConformanceEvidenceSelector` | `"conformance" "(" TypeRef "conforms" QualifiedTypeReference ")"` | 1242 |
| `NamedConformanceEvidenceSelector` | `ConformanceEvidenceSelector "::" Identifier` | 1243 |
| `PrattExpr` | `EXPRESSION_PRATT_ENTRY` | 1246 |
| `PrattPredicateExpr` | `PREDICATE_PRATT_ENTRY` | 1247 |
| `PrattSliceIndexExpr` | `SLICE_INDEX_PRATT_ENTRY` | 1248 |
| `Literal` | `BoolLiteral \| NumericLiteral \| ImaginaryLiteralExpr \| RationalLiteralExpr \| StringLiteralExpr \| CharLiteralExpr \| BytesLiteral` | 1256 |
| `BoolLiteral` | `"true" \| "false"` | 1263 |
| `NumericLiteral` | `NUMERIC_LITERAL` | 1264 |
| `ImaginaryLiteralExpr` | `IMAGINARY_LITERAL` | 1265 |
| `RationalLiteralExpr` | `RATIONAL_LITERAL` | 1266 |
| `CharLiteralExpr` | `CHAR_LITERAL` | 1267 |
| `BytesLiteral` | `BYTES_LITERAL` | 1268 |
| `StringLiteralExpr` | `PLAIN_STRING_LITERAL \| RAW_STRING_LITERAL \| MULTILINE_STRING_LITERAL \| InterpolatedString` | 1271 |
| `InterpolatedString` | `STRING_START InterpolatedStringPart* STRING_END` | 1272 |
| `InterpolatedStringPart` | `STRING_TEXT \| STRING_ESCAPE \| InterpolationExpr \| InterpolationPath` | 1273 |
| `InterpolationExpr` | `INTERPOLATION_OPEN Expr InterpolationFormat? INTERPOLATION_CLOSE` | 1277 |
| `InterpolationFormat` | `":" INTERPOLATION_FORMAT_TEXT` | 1278 |
| `InterpolationPath` | `"$" InterpolationPathRoot InterpolationPathSelector* INTERPOLATION_BOUNDARY?` | 1283 |
| `InterpolationPathRoot` | `Identifier \| "@"` | 1284 |
| `InterpolationPathSelector` | `"." Identifier \| "." StaticIntLiteral \| "[" InterpolationIndex "]"` | 1285 |
| `InterpolationIndex` | `StaticIntLiteral \| Identifier` | 1288 |
| `ListLiteral` | `"[" ListEntryList? "]"` | 1293 |
| `ListEntryList` | `ListEntry ("," ListEntry)* ","?` | 1294 |
| `ListEntry` | `Expr \| PositionalUnfoldArgument` | 1295 |
| `BoundedListLiteral` | `"[" StaticIntLiteral ".." StaticIntLiteral ":" ListEntryList? "]"` | 1296 |
| `ComprehensionExpr` | `"[" Expr ComprehensionClause+ "]"` | 1298 |
| `TypedMaterializationExpr` | `TypeRef MaterializationBody` | 1301 |
| `MaterializationBody` | `"${" MaterializationEntryList? "}"` | 1302 |
| `MaterializationEntryList` | `MaterializationEntry (MaterializationSeparator MaterializationEntry)* MaterializationSeparator?` | 1303 |
| `MaterializationEntry` | `Identifier \| Identifier ":" Expr \| StringLiteralExpr ":" Expr \| NamedUnfoldArgument` | 1304 |
| `MaterializationSeparator` | `"," LineBreakBoundary? \| LineBreakBoundary` | 1308 |
| `MapLiteral` | `"#" "map" "{" MapEntryList? "}"` | 1311 |
| `MapEntryList` | `MapEntry (MaterializationSeparator MapEntry)* MaterializationSeparator?` | 1312 |
| `MapEntry` | `Expr ":" Expr \| "*" Expr` | 1313 |
| `SetLiteral` | `"#" "set" "{" ExpressionList? "}"` | 1314 |
| `MutListLiteral` | `"#" "mut" "[" ExpressionList? "]"` | 1315 |
| `MapComprehensionExpr` | `"#" "map" "{" Expr ":" Expr ComprehensionClause+ "}"` | 1316 |
| `SetComprehensionExpr` | `"#" "set" "{" Expr ComprehensionClause+ "}"` | 1317 |
| `ComprehensionClause` | `ForClause \| PositiveGuard \| IfLetClause \| UnfoldClause` | 1319 |
| `ForClause` | `"for" Pattern "in" Expr` | 1320 |
| `IfLetClause` | `"if" "let" Pattern "=" Expr` | 1321 |
| `UnfoldClause` | `"for" Pattern "in" "*" Expr` | 1322 |
| `NumericArrayLiteral` | `ShapeInferredArrayLiteral \| ShapeInferredColumnVectorLiteral \| ExactShapeArrayLiteral` | 1325 |
| `ShapeInferredArrayLiteral` | `"#" "[" Expr ("," Expr)* ","? "]"` | 1328 |
| `ShapeInferredColumnVectorLiteral` | `"#" "[" Expr (";" Expr)+ "]"` | 1329 |
| `ExactShapeArrayLiteral` | `"#" StaticDimensionList "[" ArrayInitializer? "]"` | 1330 |
| `ArrayInitializer` | `ShapedRepeatInitializer \| ShapedGeneratorInitializer \| ShapedElementSequence` | 1331 |
| `ShapedRepeatInitializer` | `"repeat" ":" Expr` | 1334 |
| `ShapedGeneratorInitializer` | `"generate" ":" Expr` | 1335 |
| `ShapedElementSequence` | `Expr (ShapedElementSeparator Expr)* ShapedElementSeparator?` | 1336 |
| `ShapedElementSeparator` | `"," \| ShapedAxisBoundary` | 1337 |
| `ShapedAxisBoundary` | `";" ";"*` | 1338 |
| `MeasureLiteralExpr` | `NumericLiteral "[" UnitExpr "]"` | 1341 |
| `UnitExpr` | `PrattUnitExpr` | 1342 |
| `UnitPrimary` | `Identifier \| QualifiedPath \| "(" UnitExpr ")"` | 1343 |
| `UnitPostfixParselet` | `"^" SignedStaticInt` | 1344 |
| `UnitInfixOperator` | `"*" \| "/"` | 1345 |
| `PrattUnitExpr` | `UNIT_PRATT_ENTRY` | 1346 |

## `PREVIEW` 프로파일 — 13개

| 문법 production | 정확한 EBNF 오른쪽 항 | 원천 줄 |
|---|---|---:|
| `DeeplusPreview` | `PreviewLibrarySourceFile \| PreviewExecutableSourceFile \| PreviewScriptSourceFile` | 1355 |
| `PreviewLibrarySourceFile` | `PreviewGate ModuleDecl? PreviewLibraryItem* EOF_TOKEN` | 1356 |
| `PreviewExecutableSourceFile` | `PreviewGate ModuleDecl? PreviewExecutableItem* EOF_TOKEN` | 1357 |
| `PreviewScriptSourceFile` | `Shebang? PreviewGate ModuleDecl? PreviewScriptItem* EOF_TOKEN` | 1358 |
| `PreviewLibraryItem` | `LibrarySourceItem \| PreviewFfiDecl` | 1360 |
| `PreviewExecutableItem` | `ExecutableSourceItem \| PreviewFfiDecl` | 1361 |
| `PreviewScriptItem` | `ScriptSourceItem \| PreviewFfiDecl` | 1362 |
| `PreviewGate` | `"#" "preview" "(" PreviewFeatureList ")" LineBreakBoundary` | 1364 |
| `PreviewFeatureList` | `Identifier ("," Identifier)*` | 1365 |
| `PreviewFfiDecl` | `PreviewFfiFunctionDecl \| PreviewFfiBlockDecl` | 1368 |
| `PreviewFfiFunctionDecl` | `"extern" "#" "C" "def" "#" "unsafe" Identifier ParameterList ReturnClause? ThrowsClause* EffectsClause* StatementBoundary` | 1369 |
| `PreviewFfiBlockDecl` | `"extern" "c" "(" PLAIN_STRING_LITERAL ")" "{" PreviewFfiBlockMember* "}"` | 1371 |
| `PreviewFfiBlockMember` | `"unsafe" "def" Identifier ParameterList ReturnClause? ThrowsClause* EffectsClause* StatementBoundary` | 1373 |
