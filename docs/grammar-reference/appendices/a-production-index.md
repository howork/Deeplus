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

## `STABLE` 프로파일 — 531개

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
| `ThrowsClause` | `"throws" ErrorSet` | 251 |
| `EffectsClause` | `"effects" EffectRow` | 252 |
| `ContractClause` | `RequiresClause \| EnsuresClause` | 253 |
| `RequiresClause` | `"requires" PredicateExpr` | 254 |
| `EnsuresClause` | `"ensures" PredicateExpr` | 255 |
| `LineBreakBoundary` | `LINE_BREAK_IN_TRIVIA` | 260 |
| `StatementBoundary` | `STATEMENT_BOUNDARY_BY_CONTEXT` | 261 |
| `IdentifierList` | `Identifier ("," Identifier)* ","?` | 263 |
| `ExpressionList` | `Expr ("," Expr)* ","?` | 264 |
| `PatternList` | `Pattern ("," Pattern)* ","?` | 265 |
| `StaticIntLiteral` | `DECIMAL_INTEGER` | 267 |
| `UnitSyntax` | `"(" ")"` | 270 |
| `SignedStaticInt` | `("+" \| "-")? StaticIntLiteral` | 271 |
| `LawDecl` | `"law" Identifier LawBody? StatementBoundary` | 273 |
| `LawBody` | `"{" LawBodyItem* "}"` | 276 |
| `LawBodyItem` | `LawAssertion StatementBoundary` | 277 |
| `LawAssertion` | `("requires" \| "ensures" \| "invariant")? PredicateExpr` | 278 |
| `Deeplus` | `LibrarySourceFile \| ExecutableSourceFile \| ScriptSourceFile` | 286 |
| `LibrarySourceFile` | `ModuleDecl? LibrarySourceItem*` | 288 |
| `ExecutableSourceFile` | `ModuleDecl? ExecutableSourceItem*` | 289 |
| `ScriptSourceFile` | `Shebang? ModuleDecl? ScriptSourceItem*` | 290 |
| `LibrarySourceItem` | `AnnotationAttachment LibraryAnnotatableDecl \| ImportOrUseDecl \| TopLevelDecl` | 292 |
| `ExecutableSourceItem` | `AnnotationAttachment ExecutableAnnotatableDecl \| ImportOrUseDecl \| NonBindingTopLevelDecl \| EntryFunctionDecl` | 295 |
| `ScriptSourceItem` | `AnnotationAttachment ScriptAnnotatableDecl \| ImportOrUseDecl \| NonBindingTopLevelDecl \| Stmt` | 299 |
| `LibraryAnnotatableDecl` | `ImportOrUseDecl \| TopLevelDecl` | 304 |
| `ExecutableAnnotatableDecl` | `ImportOrUseDecl \| NonBindingTopLevelDecl \| EntryFunctionDecl` | 305 |
| `ScriptAnnotatableDecl` | `ImportOrUseDecl \| NonBindingTopLevelDecl` | 306 |
| `ModuleDecl` | `"module" QualifiedPath StatementBoundary` | 308 |
| `ImportOrUseDecl` | `ImportDecl \| UseDecl \| UseExportDecl` | 310 |
| `ImportDecl` | `"import" QualifiedPath ImportTail? StatementBoundary` | 311 |
| `ImportTail` | `ImportAlias \| ImportSelection` | 312 |
| `ImportAlias` | `NameAliasClause` | 313 |
| `ImportSelection` | `"::" "{" IdentifierList "}"` | 314 |
| `UseDecl` | `"use" QualifiedPath StatementBoundary` | 315 |
| `UseExportDecl` | `"use" "export" QualifiedPath StatementBoundary` | 316 |
| `ExportDecl` | `"export" ExportItem StatementBoundary?` | 319 |
| `ExportItem` | `ExportableModuleFunctionDecl \| TypeDecl \| Identifier` | 320 |
| `ExportableModuleFunctionDecl` | `TopLevelVisibility? "def" Identifier FunctionRest` | 321 |
| `TopLevelDecl` | `NonBindingTopLevelDecl \| TopLevelBindingDecl` | 329 |
| `NonBindingTopLevelDecl` | `TypeDecl \| ModuleFunctionDecl \| ExtensionFunctionDecl \| ActorDecl \| ActorProtocolDecl \| TypestateResourceDecl \| NamedEffectCapabilityDecl \| ExtensionSetDecl \| ExtensionPackDecl \| UnitCatalogDecl \| ModuleInterfaceDecl \| ConformanceDecl \| SchemaDecl \| BitfieldDecl` | 330 |
| `TypeDecl` | `ClassDecl \| TraitDecl \| EnumDecl \| TypeAliasDecl` | 345 |
| `DefIntroducer` | `"def" HashTag*` | 349 |
| `ModuleFunctionDecl` | `TopLevelVisibility? DefIntroducer Identifier FunctionRest` | 351 |
| `EntryFunctionDecl` | `DefIntroducer Identifier EntryFunctionRest` | 352 |
| `ExtensionFunctionDecl` | `TopLevelVisibility? DefIntroducer TypeRef ExtensionFunctionTarget Identifier FunctionRest` | 353 |
| `ExtensionFunctionTarget` | `"~" \| "::"` | 354 |
| `LocalFunctionDecl` | `CaptureList? DefIntroducer Identifier FunctionRest` | 355 |
| `FunctionRest` | `TypeParameterList? ParameterList FunctionTail` | 357 |
| `EntryFunctionRest` | `ParameterList ReturnClause? ThrowsClause? EffectsClause? ContractClause* FunctionBody` | 358 |
| `FunctionTail` | `ReturnClause? ThrowsClause? EffectsClause? ContractClause* WhereClause? FunctionBody` | 359 |
| `TraitFunctionTail` | `ReturnClause? ThrowsClause? EffectsClause? ContractClause* WhereClause? (FunctionBody \| StatementBoundary)` | 360 |
| `FunctionBody` | `"=" FunctionBodyContent` | 362 |
| `FunctionBodyContent` | `CallableBlock \| ReturnShorthand \| ClauseFunctionBody` | 363 |
| `CallableBlock` | `"{" BlockPrologue? FunctionStaticActivation? BlockSequence "}"` | 369 |
| `FunctionStaticActivation` | `"static" Block` | 370 |
| `ReturnShorthand` | `"return" ReturnValueSurface StatementBoundary` | 371 |
| `ClauseFunctionBody` | `"{{" LineBreakBoundary? MatchArmSequence "}}"` | 372 |
| `MemberFunctionDecl` | `MemberVisibility? DefIntroducer Identifier ClassDispatchMarker FunctionRest` | 374 |
| `TypeSideMemberFunctionDecl` | `MemberVisibility? "def" "::" Identifier FunctionRest` | 375 |
| `ConstructorDecl` | `MemberVisibility? "def" "!" Identifier ParameterList ConstructorSignatureTail? ConstructorDelegationClause? "=" Block` | 377 |
| `ConstructorSignatureTail` | `ThrowsClause EffectsClause? ContractClause* WhereClause? \| EffectsClause ContractClause* WhereClause? \| ContractClause+ WhereClause? \| WhereClause` | 379 |
| `ConstructorDelegationClause` | `":" ConstructorDelegationArm+` | 383 |
| `ConstructorDelegationArm` | `ConstructorDelegationTarget PositiveGuard?` | 384 |
| `ConstructorDelegationTarget` | `Identifier ArgumentList \| "super" "!" Identifier? ArgumentList` | 385 |
| `CleanupDecl` | `DefIntroducer "(" ")" ThrowsClause? EffectsClause? FunctionBody` | 388 |
| `ParameterList` | `"(" ParameterSequence? ")"` | 392 |
| `ParameterSequence` | `CommaParameterSequence \| LayoutParameterSequence` | 393 |
| `CommaParameterSequence` | `Parameter ("," Parameter)* ","?` | 394 |
| `LayoutParameterSequence` | `LineBreakBoundary Parameter (LineBreakBoundary Parameter)* LineBreakBoundary?` | 395 |
| `Parameter` | `StoredParameter \| ContextParameter \| WitnessParameter \| RepeatedParameter \| NamedRestParameter \| ValueParameter` | 397 |
| `ValueParameter` | `ParameterMode? ParameterPatternSlot TypeAnnotation` | 403 |
| `ParameterPatternSlot` | `Identifier IrrefutableParameterPattern?` | 408 |
| `IrrefutableParameterPattern` | `TuplePattern \| ListPattern \| RecordPattern \| NominalPattern` | 409 |
| `ParameterMode` | `"borrow" \| "mut" \| "move" \| "inout"` | 413 |
| `ContextParameter` | `"context" Identifier ":" TypeRef` | 414 |
| `WitnessParameter` | `"using" Identifier ":" "witness" TypeRef` | 415 |
| `RepeatedParameter` | `Identifier "..." TypeAnnotation` | 416 |
| `NamedRestParameter` | `Identifier "***" TypeAnnotation` | 417 |
| `StoredParameter` | `MemberVisibility? ("let" \| "var") Identifier TypeAnnotation?` | 421 |
| `ClassDecl` | `OrdinaryClassDecl \| DataClassDecl` | 425 |
| `OrdinaryClassDecl` | `TopLevelVisibility? ClassFlavor? ClassModifierSequence? "class" Identifier TypeParameterList? ParameterList? WhereClause? ClassDerivesClause? NominalConformanceClause* CleanupBudgetClause? ClassBody` | 426 |
| `DataClassDecl` | `TopLevelVisibility? "data" "class" Identifier TypeParameterList? ParameterList? WhereClause? NominalConformanceClause* CleanupBudgetClause? ClassBody?` | 430 |
| `ClassFlavor` | `"value" \| "resource"` | 432 |
| `ClassModifierSequence` | `"final" \| "open" \| "abstract" \| "sealed" \| "abstract" "sealed"` | 433 |
| `ClassDerivesClause` | `LineBreakBoundary "derives" TypeRef` | 437 |
| `NominalConformanceClause` | `LineBreakBoundary "conforms" QualifiedTypeReference NominalConformanceRoute? WhereClause?` | 438 |
| `NominalConformanceRoute` | `ConformanceViaClause \| ConformanceAutoClause` | 440 |
| `ClassBody` | `"{" MemberDecl* "}"` | 441 |
| `MemberDecl` | `FieldDecl \| MemberFunctionDecl \| ConstructorDecl \| CleanupDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| ConformBlockDecl \| ForwardDecl` | 443 |
| `FieldDecl` | `MemberVisibility? ("let" \| "var") Identifier TypeAnnotation? Initializer? StatementBoundary` | 453 |
| `TypeSideFieldDecl` | `MemberVisibility? "let" "::" Identifier TypeAnnotation? Initializer? StatementBoundary` | 455 |
| `AccessorPropertyDecl` | `("let" \| "var") Identifier TypeAnnotation ":=" AccessorSpec` | 457 |
| `AccessorSpec` | `AccessorDecl \| "{" AccessorDecl+ "}"` | 458 |
| `AccessorDecl` | `MemberVisibility? "get" Block \| MemberVisibility? "set" "(" Identifier ")" Block` | 459 |
| `ForwardDecl` | `MemberVisibility? "forward" ForwardMemberSpec "to" Expr StatementBoundary` | 461 |
| `ForwardMemberSpec` | `Identifier \| "{" Identifier ("," Identifier)* ","? "}"` | 462 |
| `TraitDecl` | `TopLevelVisibility? "trait" Identifier TypeParameterList? TraitDerivesClause* TraitAutoSupportClause? TraitBody?` | 466 |
| `TraitDerivesClause` | `LineBreakBoundary "derives" QualifiedTypeReference` | 468 |
| `TraitAutoSupportClause` | `LineBreakBoundary "supports" "auto"` | 469 |
| `TraitBody` | `"{" TraitItem* "}"` | 470 |
| `TraitItem` | `TraitMethodDecl \| AssociatedRequirementDecl \| LawDecl` | 471 |
| `TraitMethodDecl` | `MemberVisibility? DefIntroducer Identifier TraitWitnessMarker TypeParameterList? ParameterList TraitFunctionTail` | 473 |
| `AssociatedRequirementDecl` | `AssociatedTypeRequirementDecl \| AssociatedValueRequirementDecl \| AssociatedFunctionRequirementDecl` | 475 |
| `AssociatedTypeRequirementDecl` | `"type" Identifier AssociatedTypeConstraintList? StatementBoundary` | 478 |
| `AssociatedValueRequirementDecl` | `"let" "::" Identifier TypeAnnotation StatementBoundary` | 479 |
| `AssociatedFunctionRequirementDecl` | `"def" "::" Identifier ParameterList ReturnClause? ThrowsClause? EffectsClause? StatementBoundary` | 480 |
| `ConformanceDecl` | `ExplicitConformanceDecl \| AutomaticConformanceDecl` | 483 |
| `ExplicitConformanceDecl` | `TopLevelVisibility? "type" TypeRef "conforms" QualifiedTypeReference NameAliasClause? ConformanceViaClause? WhereClause? (ConformanceBody \| StatementBoundary)` | 484 |
| `AutomaticConformanceDecl` | `TopLevelVisibility? "type" TypeRef "conforms" QualifiedTypeReference NameAliasClause? ConformanceAutoClause WhereClause? StatementBoundary` | 487 |
| `ConformanceViaClause` | `"via" QualifiedPath` | 489 |
| `ConformanceAutoClause` | `"by" "auto"` | 490 |
| `ConformanceBody` | `"{" ConformanceItem* "}"` | 491 |
| `ConformanceMethodDecl` | `MemberVisibility? DefIntroducer ConformanceMethodName TraitWitnessMarker FunctionRest` | 492 |
| `ConformanceMethodName` | `Identifier \| QualifiedTypeReference "::" Identifier` | 494 |
| `ConformBlockDecl` | `"conform" QualifiedTypeReference ConformanceBody` | 495 |
| `ConformanceItem` | `ConformanceMethodDecl \| TypeSideMemberFunctionDecl \| AssociatedRequirementBinding \| ExtensionDelegationDecl \| LawDecl` | 496 |
| `AssociatedRequirementBinding` | `"type" Identifier "=" TypeRef StatementBoundary \| "let" "::" Identifier "=" Expr StatementBoundary` | 501 |
| `ExtensionDelegationDecl` | `"delegate" Identifier "to" QualifiedExtensionSelector StatementBoundary` | 503 |
| `ExtensionSetDecl` | `TopLevelVisibility? "extension" TypeRef "as" Identifier ExtensionSetBody` | 507 |
| `ExtensionSetBody` | `"{" ExtensionSetItem* "}"` | 508 |
| `ExtensionSetItem` | `ExtensionSetFunctionDecl \| TypeSideMemberFunctionDecl` | 509 |
| `ExtensionSetFunctionDecl` | `MemberVisibility? "def" Identifier ParameterList? ReturnClause? ThrowsClause? EffectsClause? WhereClause? FunctionBody` | 510 |
| `ExtensionPackDecl` | `"extension" "pack" QualifiedPath ExtensionPackBody` | 512 |
| `ExtensionPackBody` | `"{" UseExportDecl* "}"` | 513 |
| `EnumDecl` | `TopLevelVisibility? "enum" EnumOrderRole? Identifier TypeParameterList? NominalConformanceClause* EnumBody` | 517 |
| `EnumOrderRole` | `"#" ("increasing" \| "decreasing")` | 519 |
| `EnumBody` | `"{" (EnumCommaCaseSequence \| EnumLayoutBody)? "}"` | 520 |
| `EnumCommaCaseSequence` | `EnumCaseCore ("," EnumCaseCore)+ ","?` | 521 |
| `EnumLayoutBody` | `EnumCaseDecl* EnumMemberDecl*` | 522 |
| `EnumCaseDecl` | `EnumCaseCore StatementBoundary?` | 523 |
| `EnumCaseCore` | `Identifier EnumCasePayload? EnumCaseDisplayMapping?` | 524 |
| `EnumCasePayload` | `"(" EnumCaseFieldList? ")"` | 525 |
| `EnumCaseFieldList` | `EnumCaseField ("," EnumCaseField)* ","?` | 526 |
| `EnumCaseField` | `Identifier TypeAnnotation \| TypeRef` | 527 |
| `EnumMemberDecl` | `MemberFunctionDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| ConformBlockDecl \| EnumVariantSubsetAliasDecl` | 528 |
| `EnumCaseDisplayMapping` | `"~>" RestrictedEnumDisplayTemplate` | 534 |
| `RestrictedEnumDisplayTemplate` | `PLAIN_STRING_LITERAL \| MULTILINE_STRING_LITERAL \| InterpolatedString` | 535 |
| `EnumVariantSubsetAliasDecl` | `"+" "type" Identifier "=" EnumVariantSubsetRhs StatementBoundary?` | 538 |
| `EnumVariantSubsetRhs` | `Identifier ("\|" Identifier)*` | 540 |
| `SchemaDecl` | `TopLevelVisibility? "schema" Identifier TypeParameterList? SchemaBody` | 544 |
| `SchemaBody` | `"{" SchemaFieldSequence? "}"` | 545 |
| `SchemaFieldSequence` | `CommaSchemaFields \| LayoutSchemaFields` | 546 |
| `CommaSchemaFields` | `SchemaFieldDecl ("," SchemaFieldDecl)* ","?` | 547 |
| `LayoutSchemaFields` | `LineBreakBoundary LayoutSchemaFieldDecl (LineBreakBoundary LayoutSchemaFieldDecl)* LineBreakBoundary?` | 548 |
| `SchemaFieldDecl` | `Identifier TypeAnnotation Initializer? SchemaConstraint* StatementBoundary?` | 549 |
| `LayoutSchemaFieldDecl` | `Identifier TypeAnnotation Initializer? SchemaConstraint*` | 550 |
| `SchemaConstraint` | `"where" Expr` | 551 |
| `TypeAliasDecl` | `TopLevelVisibility? "type" Identifier TypeParameterList? "=" TypeAliasRhs StatementBoundary` | 553 |
| `TypeAliasRhs` | `TypeRef RefinementSuffix? \| StaticRangeType` | 554 |
| `StaticRangeType` | `StaticIntLiteral ".." StaticIntLiteral` | 555 |
| `TopLevelBindingDecl` | `TopLevelVisibility? ("let" \| "var") Identifier TypeAnnotation? "=" Expr StatementBoundary` | 557 |
| `NamedEffectCapabilityDecl` | `TopLevelVisibility? "capability" Identifier "for" EffectRow StatementBoundary` | 558 |
| `ActorDecl` | `TopLevelVisibility? "actor" MailboxClause? Identifier ActorBody` | 562 |
| `MailboxClause` | `HashTag "(" "capacity" ":" StaticIntLiteral ")"` | 563 |
| `ActorBody` | `"{" ActorItem* "}"` | 564 |
| `ActorItem` | `ActorOnDecl \| ActorRequestDecl \| MemberDecl` | 565 |
| `ActorOnDecl` | `MemberVisibility? "on" Identifier ParameterList? ThrowsClause? EffectsClause? FunctionBody` | 566 |
| `ActorRequestDecl` | `MemberVisibility? "request" Identifier ParameterList? ReturnClause ThrowsClause? EffectsClause? FunctionBody` | 567 |
| `ActorProtocolDecl` | `TopLevelVisibility? "protocol" Identifier ActorProtocolBody` | 569 |
| `ActorProtocolBody` | `"{" ActorProtocolItem* "}"` | 570 |
| `ActorProtocolItem` | `ActorProtocolSendRequirement \| ActorProtocolRequestRequirement` | 571 |
| `ActorProtocolSendRequirement` | `"send" Identifier ParameterList? ThrowsClause? EffectsClause? StatementBoundary` | 572 |
| `ActorProtocolRequestRequirement` | `"request" Identifier ParameterList? ReturnClause ThrowsClause? EffectsClause? StatementBoundary` | 573 |
| `TypestateResourceDecl` | `TopLevelVisibility? "typestate" Identifier TypeParameterList? TypestateBody` | 577 |
| `TypestateBody` | `"{" TypestateTransitionDecl* "}"` | 578 |
| `TypestateTransitionDecl` | `Identifier "->" Identifier FunctionBody?` | 579 |
| `UnitCatalogDecl` | `TopLevelVisibility? "unit" "catalog" Identifier UnitCatalogBody` | 581 |
| `UnitCatalogBody` | `"{" UnitCatalogEntry* "}"` | 582 |
| `UnitCatalogEntry` | `ExactRatioUnitConversionDecl \| Identifier "=" UnitExpr StatementBoundary` | 583 |
| `ExactRatioUnitConversionDecl` | `"unit" Identifier "equalsRatio" MeasureLiteralExpr "/" StaticIntLiteral StatementBoundary` | 584 |
| `ModuleInterfaceDecl` | `ModuleSignatureDecl \| OpaqueModuleFacadeDecl` | 586 |
| `ModuleSignatureDecl` | `TopLevelVisibility? "module" "signature" QualifiedPath ModuleInterfaceBody` | 587 |
| `OpaqueModuleFacadeDecl` | `TopLevelVisibility? "opaque" "module" QualifiedPath ModuleInterfaceBody` | 588 |
| `ModuleInterfaceBody` | `"{" ModuleInterfaceItem* "}"` | 589 |
| `ModuleInterfaceItem` | `ExportDecl \| UseExportDecl \| OpaqueModuleFacadeDecl` | 590 |
| `CleanupBudgetClause` | `"cleanup" "budget" "{" CleanupBudgetItem* "}"` | 594 |
| `CleanupBudgetItem` | `EffectsBudget \| ErrorsBudget` | 595 |
| `EffectsBudget` | `"effects" "{" IdentifierList? "}"` | 596 |
| `ErrorsBudget` | `"errors" TypeRef` | 597 |
| `BitfieldDecl` | `TopLevelVisibility? BitfieldIntroducer Identifier BitfieldBackingClause BitfieldOrderClause BitfieldBody` | 601 |
| `BitfieldIntroducer` | `"bitfield" HashTag?` | 603 |
| `BitfieldBackingClause` | `"backing" TypeRef` | 604 |
| `BitfieldOrderClause` | `"order" "::" "lsb0"` | 605 |
| `BitfieldBody` | `"{" BitfieldLayoutSection BitfieldMemberDecl* "}"` | 606 |
| `BitfieldLayoutSection` | `BitfieldSlotDecl+ \| FlagSlotDecl+` | 607 |
| `BitfieldSlotDecl` | `BitfieldNamedSlot StatementBoundary \| BitfieldReservedSlot StatementBoundary` | 608 |
| `FlagSlotDecl` | `FlagNamedSlot StatementBoundary \| BitfieldReservedSlot StatementBoundary` | 609 |
| `BitfieldNamedSlot` | `MemberVisibility? Identifier ":" StaticIntLiteral BitfieldDefault?` | 610 |
| `BitfieldReservedSlot` | `"_" ":" StaticIntLiteral` | 611 |
| `FlagNamedSlot` | `MemberVisibility? Identifier` | 612 |
| `BitfieldDefault` | `"=" Literal` | 613 |
| `BitfieldMemberDecl` | `MemberFunctionDecl \| TypeSideFieldDecl \| TypeSideMemberFunctionDecl \| AccessorPropertyDecl \| LawDecl` | 614 |
| `TypeRef` | `PrattType` | 626 |
| `NonFunctionTypeRef` | `PrattNonFunctionType` | 627 |
| `TypePrimary` | `QualifiedTypeReference \| FacetType \| ParenTypeSyntax \| SharpShapeType \| ExistentialType \| OpaqueType \| TypeofType \| AssociatedProjection` | 630 |
| `TypePrefixParselet` | `OwnershipQualifier` | 638 |
| `TypePostfixParselet` | `"?"` | 639 |
| `TypeInfixOperator` | `"&" \| "\|"` | 640 |
| `QualifiedTypeReference` | `QualifiedPath TypeArgumentList?` | 642 |
| `FacetType` | `"Facet" "<" "borrow" "any" QualifiedTypeReference AssociatedTypeConstraintList? ">"` | 644 |
| `OwnershipQualifier` | `"owned" \| "borrowed" \| "mut" \| "inout"` | 645 |
| `ParenTypeSyntax` | `HashTag* "(" ParenTypeItemList? ")" FunctionTypeTail?` | 649 |
| `ParenTypeItemList` | `ParenTypeItem ("," ParenTypeItem)* ","?` | 650 |
| `ParenTypeItem` | `TypeRef \| TypeRef "..." \| TypeRef "***"` | 651 |
| `FunctionTypeTail` | `"->" ReturnTypeSurface ThrowsClause? EffectsClause?` | 652 |
| `SharpShapeType` | `"#" StaticDimensionList "[" TypeRef "]"` | 654 |
| `StaticDimensionList` | `StaticIntLiteral ("," StaticIntLiteral)*` | 655 |
| `ExistentialType` | `"any" QualifiedTypeReference AssociatedTypeConstraintList?` | 657 |
| `OpaqueType` | `"some" QualifiedTypeReference AssociatedTypeConstraintList?` | 658 |
| `TypeofType` | `"typeof" TypeofStaticSampleOperand` | 659 |
| `AssociatedProjection` | `"<" TypeRef "as" QualifiedTypeReference ">" "::" Identifier` | 660 |
| `TypeofStaticSampleOperand` | `Literal \| ListLiteral \| StaticPrefixedCollectionSample \| NumericArrayLiteral \| MeasureLiteralExpr` | 663 |
| `StaticPrefixedCollectionSample` | `MapLiteral \| SetLiteral \| MutListLiteral` | 668 |
| `PrattType` | `TYPE_PRATT_ENTRY` | 671 |
| `PrattNonFunctionType` | `NON_FUNCTION_TYPE_PRATT_ENTRY` | 672 |
| `Pattern` | `OrPattern` | 680 |
| `OrPattern` | `AliasPattern ("\|" AliasPattern)*` | 681 |
| `AliasPattern` | `MovePattern ("as" Identifier)?` | 682 |
| `MovePattern` | `"move"? PatternPrimary` | 683 |
| `PatternPrimary` | `TypedBindingPattern \| Identifier \| PinPattern \| RangePattern \| RelationalPattern \| TuplePattern \| RecordPattern \| ListPattern \| MapPattern \| VariantPattern \| NominalPattern \| "_" \| UnitSyntax \| Literal \| ParenthesizedPattern` | 685 |
| `TypedBindingPattern` | `Identifier ":" TypeRef` | 701 |
| `ParenthesizedPattern` | `"(" Pattern ")"` | 702 |
| `PinPattern` | `"^" StablePatternValue` | 703 |
| `StablePatternValue` | `Identifier \| QualifiedStaticExpr \| Literal` | 704 |
| `RangePattern` | `PatternBound (".." \| "..<") PatternBound` | 705 |
| `RelationalPattern` | `("<" \| "<=" \| ">" \| ">=") PatternBound` | 706 |
| `PatternBound` | `Literal \| PinPattern` | 707 |
| `TuplePattern` | `"(" TuplePatternItems ")"` | 711 |
| `TuplePatternItems` | `Pattern "," \| Pattern "," Pattern ("," Pattern)* ","?` | 712 |
| `BindingPattern` | `BindingOrPattern TypeAnnotation?` | 724 |
| `BindingOrPattern` | `BindingAliasPattern ("\|" BindingAliasPattern)*` | 725 |
| `BindingAliasPattern` | `BindingMovePattern ("as" Identifier)?` | 726 |
| `BindingMovePattern` | `"move"? BindingPatternPrimary` | 727 |
| `BindingPatternPrimary` | `Identifier \| PinPattern \| RangePattern \| RelationalPattern \| TuplePattern \| RecordPattern \| ListPattern \| MapPattern \| VariantPattern \| NominalPattern \| "_" \| UnitSyntax \| Literal \| ParenthesizedPattern` | 728 |
| `RecordPattern` | `"${" RecordPatternEntries? "}"` | 747 |
| `RecordPatternEntries` | `RecordPatternEntry (PatternEntrySeparator RecordPatternEntry)* PatternEntrySeparator?` | 748 |
| `RecordPatternEntry` | `Identifier \| RecordDestination ":" Identifier \| RecordRestPattern` | 750 |
| `RecordDestination` | `Pattern` | 751 |
| `RecordRestPattern` | `".." RestBinder` | 752 |
| `MapPattern` | `"#" "map" "{" MapPatternEntries? "}"` | 754 |
| `MapPatternEntries` | `MapPatternEntry (PatternEntrySeparator MapPatternEntry)* PatternEntrySeparator?` | 755 |
| `MapPatternEntry` | `MapDestination ":" MapKeyPattern \| MapRestPattern` | 757 |
| `MapDestination` | `Pattern` | 758 |
| `MapKeyPattern` | `Literal \| PinPattern` | 759 |
| `MapRestPattern` | `".." RestBinder` | 760 |
| `PatternEntrySeparator` | `"," LineBreakBoundary? \| LineBreakBoundary` | 761 |
| `ListPattern` | `"[" ListPatternBody? "]"` | 767 |
| `ListPatternBody` | `IgnoredAllListRest \| ExactListPattern \| PrefixRestListPattern \| SuffixRestListPattern \| MiddleRestListPattern` | 768 |
| `ExactListPattern` | `Pattern ("," Pattern)* ","?` | 773 |
| `PrefixRestListPattern` | `PrefixListRest "," Pattern ("," Pattern)* ","?` | 774 |
| `SuffixRestListPattern` | `Pattern ("," Pattern)* "," SuffixListRest ","?` | 775 |
| `MiddleRestListPattern` | `Pattern ("," Pattern)* "," MiddleListRest "," Pattern ("," Pattern)* ","?` | 776 |
| `PrefixListRest` | `RestBinder ".."` | 778 |
| `SuffixListRest` | `".." RestBinder` | 779 |
| `MiddleListRest` | `".." RestBinder ".."` | 780 |
| `IgnoredAllListRest` | `".." "_" ","?` | 781 |
| `RestBinder` | `Identifier \| "_"` | 782 |
| `VariantPattern` | `VariantQualifier Identifier VariantPatternPayload?` | 784 |
| `VariantQualifier` | `TypeRef "::" \| "::"` | 785 |
| `VariantPatternPayload` | `VariantPositionalPatternPayload \| RecordPattern` | 786 |
| `VariantPositionalPatternPayload` | `"(" PatternList? ")"` | 787 |
| `NominalPattern` | `TypeRef RecordPattern` | 792 |
| `Stmt` | `ForLoop \| WhileLoop \| RepeatLoop \| AsyncForLoop \| TaskGroupStmt \| MatchStatement \| IfStmt \| LocalBindingStmt \| AssertiveBindingStmt \| PatternAssignmentStmt \| ParallelAssignmentStmt \| ControlTransferStmt \| TryStmt \| DeferStmt \| ScopedUseStmt \| ExprStmt \| ScopedImportStmt` | 800 |
| `ExprStmt` | `Expr StatementBoundary` | 818 |
| `Block` | `"{" BlockPrologue? BlockSequence "}"` | 820 |
| `BlockPrologue` | `(UseDecl \| ImportDecl)+` | 821 |
| `BlockSequence` | `BlockItem* BlockFinalItem?` | 822 |
| `BlockItem` | `LocalFunctionDecl \| Stmt` | 823 |
| `BlockFinalItem` | `ControlTransfer \| BindingCore \| Expr` | 826 |
| `ValueBody` | `SingleExpressionValueBody \| ExplicitRetValueBody` | 829 |
| `SingleExpressionValueBody` | `"{" ReturnValueSurface "}"` | 830 |
| `ExplicitRetValueBody` | `"{" BlockItem* RetTransfer "}"` | 831 |
| `RetTransfer` | `"ret" ReturnValueSurface? GuardClause?` | 832 |
| `BindingCore` | `("let" \| "var") BindingHead "=" BindingValueSurface` | 837 |
| `BindingHead` | `BindingPattern \| BareTupleBindingSurface` | 838 |
| `BareTupleBindingSurface` | `BindingPattern "," BindingPattern ("," BindingPattern)*` | 839 |
| `BindingValueSurface` | `Expr \| BareTupleValueSurface` | 840 |
| `ReturnValueSurface` | `Expr \| BareTupleValueSurface` | 841 |
| `BareTupleValueSurface` | `Expr "," Expr ("," Expr)*` | 842 |
| `LocalBindingStmt` | `BindingCore StatementBoundary \| RightwardLocalBindingSurface \| LazyBindingStmt \| GuardedBindingStmt` | 843 |
| `LazyBindingStmt` | `"let" HashTag Identifier TypeAnnotation? "=" Expr StatementBoundary` | 844 |
| `GuardedBindingStmt` | `("let" \| "var") BindingPattern "=" Expr "else" GuardedBindingFailure StatementBoundary?` | 845 |
| `AssertiveBindingStmt` | `("let" \| "var") "!" BindingPattern "=" Expr StatementBoundary` | 846 |
| `GuardedBindingFailure` | `GuardedBindingExit \| Pattern "=>" GuardedBindingExit` | 848 |
| `GuardedBindingExit` | `GuardedReturnExit \| GuardedThrowExit \| GuardedBreakExit \| GuardedContinueExit` | 849 |
| `GuardedReturnExit` | `"return" Expr?` | 850 |
| `GuardedThrowExit` | `"throw" Expr` | 851 |
| `GuardedBreakExit` | `("break")+ Expr?` | 852 |
| `GuardedContinueExit` | `("break")* "continue"` | 853 |
| `ControlTransferStmt` | `ControlTransfer StatementBoundary` | 856 |
| `ControlTransfer` | `ReturnTransfer \| ThrowTransfer \| BreakTransfer \| ContinueTransfer \| YieldTransfer` | 857 |
| `ReturnTransfer` | `"return" ReturnValueSurface? GuardClause?` | 858 |
| `ThrowTransfer` | `"throw" Expr GuardClause?` | 859 |
| `BreakTransfer` | `("break")+ Expr? GuardClause?` | 860 |
| `ContinueTransfer` | `("break")* "continue" GuardClause?` | 861 |
| `YieldTransfer` | `"yield" Expr? (GuardClause \| YieldResponseBinding)?` | 862 |
| `YieldResponseBinding` | `"->" DollarLocalBinding` | 863 |
| `DollarLocalBinding` | `"$" Identifier TypeAnnotation? \| "$$" Identifier TypeAnnotation?` | 864 |
| `GuardClause` | `PositiveGuard \| NegativeGuard` | 866 |
| `PositiveGuard` | `"if" Expr` | 867 |
| `NegativeGuard` | `"!" "if" Expr` | 868 |
| `IfStmt` | `"if" PatternConditionChain Block ("else" (IfStmt \| Block))?` | 870 |
| `PatternConditionChain` | `PatternControlCondition ("and" "then" PatternControlCondition)*` | 873 |
| `PatternControlCondition` | `Expr \| "let" Pattern "=" Expr` | 875 |
| `ForLoop` | `"for" ("let" Pattern \| Pattern) "in" Expr GuardClause? Block MatchStatement?` | 879 |
| `WhileLoop` | `"while" PatternConditionChain Block MatchStatement?` | 880 |
| `RepeatLoop` | `"repeat" Block "while" Expr MatchStatement?` | 881 |
| `AsyncForLoop` | `"for" "await" ("let" Pattern \| Pattern) "in" Expr GuardClause? Block` | 882 |
| `MatchStatement` | `"match" MatchCore` | 884 |
| `MatchCore` | `MatchSubjectSlot MatchBody` | 885 |
| `MatchSubjectSlot` | `MATCH_SUBJECT_BY_INPUT_SUPPLY_POLICY` | 886 |
| `MatchBody` | `"{" LineBreakBoundary? MatchArmSequence "}"` | 887 |
| `MatchArmSequence` | `MatchArm (MatchArmSeparator MatchArm)* MatchArmSeparator?` | 888 |
| `MatchArm` | `MatchHead GuardClause? "=>" MatchArmBodySlot` | 889 |
| `MatchHead` | `BoundedBinderPattern \| Pattern \| "otherwise"` | 890 |
| `BoundedBinderPattern` | `PatternBound OrderedComparisonOperator Identifier OrderedComparisonOperator PatternBound` | 896 |
| `MatchArmSeparator` | `MATCH_ARM_SEPARATOR_BY_CONTEXT` | 898 |
| `MatchArmBodySlot` | `MATCH_ARM_BODY_BY_CONTEXT` | 899 |
| `TryStmt` | `"try" Block (CatchClause+ FinallyClause? \| FinallyClause)` | 903 |
| `CatchClause` | `"catch" Pattern? GuardClause? Block` | 904 |
| `ValueCatchClause` | `"catch" Pattern? GuardClause? ValueBody` | 905 |
| `FinallyClause` | `"finally" Block` | 906 |
| `DeferStmt` | `"defer" DeferredCleanupInvocation StatementBoundary` | 908 |
| `DeferredCleanupInvocation` | `DeferredDirectCall \| DeferredMessageCall` | 911 |
| `DeferredDirectCall` | `DeferredReceiver ArgumentList` | 912 |
| `DeferredMessageCall` | `DeferredReceiver "~" MessageSelector TildeArgumentSequence?` | 913 |
| `DeferredReceiver` | `DeferredPrimary DeferTargetSuffix*` | 914 |
| `DeferredPrimary` | `Identifier \| QualifiedStaticExpr` | 915 |
| `DeferTargetSuffix` | `IndexSuffix \| MemberSuffix` | 916 |
| `RightwardLocalBindingSurface` | `Expr "->" DollarLocalBinding StatementBoundary` | 920 |
| `PatternAssignmentStmt` | `AssigneePattern "=" Expr StatementBoundary` | 924 |
| `AssigneePattern` | `AssigneeTuplePattern \| AssigneeListPattern \| AssigneeRecordPattern \| AssigneeNominalPattern` | 925 |
| `AssigneePrimary` | `Identifier \| "_"` | 929 |
| `AssigneeTuplePattern` | `"(" AssigneeTupleItems ")"` | 930 |
| `AssigneeTupleItems` | `AssigneePatternItem "," \| AssigneePatternItem "," AssigneePatternItem ("," AssigneePatternItem)* ","?` | 931 |
| `AssigneePatternItem` | `AssigneePrimary \| AssigneeTuplePattern \| AssigneeListPattern \| AssigneeRecordPattern` | 934 |
| `AssigneeListPattern` | `"[" AssigneeListBody? "]"` | 938 |
| `AssigneeListBody` | `AssigneeIgnoredAllRest \| AssigneeExactList \| AssigneePrefixRestList \| AssigneeSuffixRestList \| AssigneeMiddleRestList` | 939 |
| `AssigneeExactList` | `AssigneePatternItem ("," AssigneePatternItem)* ","?` | 944 |
| `AssigneePrefixRestList` | `Identifier ".." "," AssigneeExactList` | 945 |
| `AssigneeSuffixRestList` | `AssigneeExactList "," ".." Identifier ","?` | 946 |
| `AssigneeMiddleRestList` | `AssigneeExactList "," ".." Identifier ".." "," AssigneeExactList` | 947 |
| `AssigneeIgnoredAllRest` | `".." "_" ","?` | 949 |
| `AssigneeRestPattern` | `".." ("_" \| Identifier)` | 950 |
| `AssigneeRecordPattern` | `"${" AssigneeRecordEntries? "}"` | 951 |
| `AssigneeRecordEntries` | `AssigneeRecordEntry (PatternEntrySeparator AssigneeRecordEntry)* PatternEntrySeparator?` | 952 |
| `AssigneeRecordEntry` | `Identifier \| AssigneePrimary ":" Identifier \| AssigneeRestPattern` | 955 |
| `AssigneeNominalPattern` | `TypeRef AssigneeRecordPattern` | 956 |
| `ParallelAssignmentStmt` | `BareTuplePlaceSurface "=" AssignmentValueSurface StatementBoundary` | 957 |
| `BareTuplePlaceSurface` | `Identifier "," Identifier ("," Identifier)*` | 958 |
| `AssignmentValueSurface` | `Expr \| BareTupleValueSurface` | 959 |
| `ScopedUseStmt` | `"use" ScopedPathList "in" Block` | 960 |
| `ScopedImportStmt` | `"import" ScopedPathList "in" Block` | 961 |
| `ScopedPathList` | `QualifiedPath ("," QualifiedPath)*` | 962 |
| `TaskGroupStmt` | `"task" "group" Identifier? Block` | 963 |
| `Expr` | `PrattExpr` | 971 |
| `PredicateExpr` | `PrattPredicateExpr` | 972 |
| `SliceIndexExpr` | `PrattSliceIndexExpr` | 973 |
| `ExpressionPrefixParselet` | `"+" \| "-" \| "not" \| "~~" \| "move" \| "borrow" \| "&" \| "await"` | 979 |
| `ExpressionPostfixParselet` | `CallSuffix \| TildeCallLed \| TupleOrdinalSuffix \| IndexSuffix \| MemberSuffix \| NumericArrayTransposeSuffix \| ConstructorCallSuffix \| NamedConstructorCallSuffix \| PrototypeDerivationSuffix \| CastSuffix` | 981 |
| `PrimaryExpr` | `Literal \| Identifier \| ImplicitAtExpr \| ParenExprSyntax \| ListLiteral \| BoundedListLiteral \| ComprehensionExpr \| MaterializationBody \| TypedMaterializationExpr \| MapLiteral \| SetLiteral \| MutListLiteral \| MapComprehensionExpr \| SetComprehensionExpr \| NumericArrayLiteral \| MeasureLiteralExpr \| QualifiedStaticExpr \| ExpectedVariantExpr \| AtControlExpr \| MatchExpr \| ClosureExpr \| GeneratorExpr \| SpawnExpr \| StructuredTaskScope \| UnsafeBlockExpr \| FacetExpr` | 992 |
| `ParenExprSyntax` | `"(" ParenExprContent? ")"` | 1020 |
| `ParenExprContent` | `Expr ParenExprTail?` | 1021 |
| `ParenExprTail` | `"," \| "," Expr ("," Expr)* ","?` | 1022 |
| `ImplicitAtExpr` | `"@"` | 1023 |
| `ExpectedVariantExpr` | `"::" Identifier` | 1024 |
| `CallSuffix` | `ArgumentList TrailingClosureGroup? \| AtomicCallArgument TrailingClosureGroup` | 1028 |
| `ArgumentList` | `"(" ")" \| "(" CommaArgumentSequence ")" \| "(" LayoutArgumentSequence ")"` | 1031 |
| `CommaArgumentSequence` | `Argument ("," Argument)* ","?` | 1034 |
| `LayoutArgumentSequence` | `LineBreakBoundary NamedLayoutArgument LineBreakBoundary NamedLayoutArgument (LineBreakBoundary NamedLayoutArgument)* LineBreakBoundary?` | 1036 |
| `NamedLayoutArgument` | `NamedArgument \| NamedUnfoldArgument` | 1038 |
| `Argument` | `ContextArgument \| WitnessArgument \| NamedArgument \| PositionalUnfoldArgument \| NamedUnfoldArgument \| Expr` | 1039 |
| `ContextArgument` | `"context" Expr` | 1045 |
| `WitnessArgument` | `"using" WitnessArgumentValue` | 1046 |
| `WitnessArgumentValue` | `Identifier \| ConformanceEvidenceSelector \| NamedConformanceEvidenceSelector` | 1047 |
| `NamedArgument` | `Identifier ":" Expr` | 1048 |
| `PositionalUnfoldArgument` | `"*" Expr` | 1049 |
| `NamedUnfoldArgument` | `"**" Expr` | 1050 |
| `AtomicCallArgument` | `Literal \| Identifier \| QualifiedStaticExpr \| ExpectedVariantExpr` | 1051 |
| `TrailingClosureGroup` | `TrailingClosureArgument+` | 1055 |
| `TrailingClosureArgument` | `ClosureExpr \| Identifier ":" ClosureExpr` | 1056 |
| `IndexSuffix` | `"[" SliceAxisList "]"` | 1060 |
| `SliceAxisList` | `SliceAxis (";" SliceAxis)*` | 1061 |
| `SliceAxis` | `SliceRange \| SliceIndexExpr \| AxisWildcard` | 1062 |
| `SliceRange` | `SliceBound (".." \| "..<") SliceBound` | 1065 |
| `SliceBound` | `SliceIndexExpr \| "^" \| "$" \| "^" OffsetExpr \| "$" OffsetExpr` | 1066 |
| `OffsetExpr` | `("+" \| "-") NumericLiteral` | 1067 |
| `AxisWildcard` | `"*"` | 1068 |
| `TupleOrdinalSuffix` | `"." StaticIntLiteral` | 1070 |
| `MemberSuffix` | `"." Identifier \| "." "\\\\" NAME_TOKEN` | 1071 |
| `TildeCallLed` | `TildeCallToken MessageSelector TildeArgumentSequence? TrailingClosureGroup?` | 1077 |
| `TildeCallToken` | `"~" \| ":~"` | 1079 |
| `MessageSelector` | `Identifier \| QualifiedMessageSelector` | 1080 |
| `QualifiedMessageSelector` | `TypeRef "::" Identifier ("::" Identifier)?` | 1081 |
| `QualifiedExtensionSelector` | `TypeRef "::" Identifier "::" Identifier` | 1082 |
| `TildeArgumentSequence` | `TildeArgument ("," TildeArgument)*` | 1083 |
| `TildeArgument` | `ContextArgument \| WitnessArgument \| NamedArgument \| PositionalUnfoldArgument \| NamedUnfoldArgument \| Expr` | 1084 |
| `NumericArrayTransposeSuffix` | `"^"` | 1091 |
| `ConstructorCallSuffix` | `"!" ArgumentList` | 1092 |
| `NamedConstructorCallSuffix` | `"!" Identifier ArgumentList` | 1093 |
| `PrototypeDerivationSuffix` | `("!" \| "!!") DerivationBody` | 1094 |
| `DerivationBody` | `"{" MaterializationEntryList? "}"` | 1095 |
| `CastSuffix` | `"as" "?" TypeRef \| "as" "!" TypeRef` | 1097 |
| `QualifiedStaticExpr` | `StaticQualifier "::" Identifier \| TraitQualifiedAssociatedSelector` | 1099 |
| `StaticQualifier` | `QualifiedTypeReference \| AssociatedProjection` | 1101 |
| `TraitQualifiedAssociatedSelector` | `"<" TypeRef "as" QualifiedTypeReference ">" "::" Identifier` | 1102 |
| `AtControlExpr` | `AtIfExpr \| AtTryExpr \| AtScopeExpr` | 1108 |
| `AtIfExpr` | `"@" "if" Expr ValueBody "else" ValueBody` | 1110 |
| `AtTryExpr` | `"@" "try" ValueBody (ValueCatchClause+ FinallyClause? \| FinallyClause)` | 1111 |
| `AtScopeExpr` | `"@" "scope" ScopeModifier* ValueBody` | 1112 |
| `ScopeModifier` | `"isolated" \| "cancellable" \| "shielded"` | 1113 |
| `MatchExpr` | `"@" "match" MatchCore` | 1115 |
| `ClosureExpr` | `CaptureList? HashTag* "{" ClosureContent "}"` | 1119 |
| `ClosureContent` | `ExplicitLambdaContent \| LambdaBody?` | 1120 |
| `ExplicitLambdaContent` | `LambdaParameterList? "=>" LambdaBody` | 1121 |
| `LambdaParameterList` | `LambdaParameter ("," LambdaParameter)* ","?` | 1122 |
| `LambdaParameter` | `ParameterMode? LambdaParameterPattern TypeAnnotation?` | 1123 |
| `LambdaParameterPattern` | `Identifier \| IrrefutableParameterPattern` | 1124 |
| `LambdaBody` | `ReturnValueSurface \| LineBreakBoundary LambdaBlockContent` | 1125 |
| `LambdaBlockContent` | `BlockItem* LambdaFinalItem?` | 1126 |
| `LambdaFinalItem` | `RetTransfer \| Expr` | 1127 |
| `CaptureList` | `"[" CaptureItemList? "]"` | 1129 |
| `CaptureItemList` | `CaptureItem ("," CaptureItem)* ","?` | 1130 |
| `CaptureItem` | `("let" \| "var") Identifier "=" Expr \| CaptureMode Identifier \| Identifier` | 1131 |
| `CaptureMode` | `"borrow" \| "inout" \| "move" \| "clone" \| "deep" \| "copy" \| "once"` | 1134 |
| `GeneratorExpr` | `CaptureList? GeneratorCore` | 1147 |
| `GeneratorCore` | `"@" "for" Pattern "in" Expr Block \| "@" "while" Expr Block \| "@" "repeat" Block "while" Expr` | 1148 |
| `SpawnExpr` | `"spawn" TaskBody` | 1152 |
| `TaskBody` | `"{" "=>" TaskBodySequence "}" \| "async" "{" "=>" TaskBodySequence "}"` | 1153 |
| `TaskBodySequence` | `LineBreakBoundary? BlockSequence` | 1155 |
| `StructuredTaskScope` | `"task" "scope" Block` | 1156 |
| `UnsafeBlockExpr` | `"unsafe" Block` | 1157 |
| `FacetExpr` | `"facet" "[" "borrow" Expr "as" QualifiedTypeReference AssociatedTypeConstraintList? "]"` | 1160 |
| `ConformanceEvidenceSelector` | `"conformance" "(" TypeRef "conforms" QualifiedTypeReference ")"` | 1162 |
| `NamedConformanceEvidenceSelector` | `ConformanceEvidenceSelector "::" Identifier` | 1163 |
| `PrattExpr` | `EXPRESSION_PRATT_ENTRY` | 1166 |
| `PrattPredicateExpr` | `PREDICATE_PRATT_ENTRY` | 1167 |
| `PrattSliceIndexExpr` | `SLICE_INDEX_PRATT_ENTRY` | 1168 |
| `Literal` | `BoolLiteral \| NumericLiteral \| ImaginaryLiteralExpr \| RationalLiteralExpr \| StringLiteralExpr \| CharLiteralExpr \| BytesLiteral` | 1176 |
| `BoolLiteral` | `"true" \| "false"` | 1183 |
| `NumericLiteral` | `NUMERIC_LITERAL` | 1184 |
| `ImaginaryLiteralExpr` | `IMAGINARY_LITERAL` | 1185 |
| `RationalLiteralExpr` | `RATIONAL_LITERAL` | 1186 |
| `CharLiteralExpr` | `CHAR_LITERAL` | 1187 |
| `BytesLiteral` | `BYTES_LITERAL` | 1188 |
| `StringLiteralExpr` | `PLAIN_STRING_LITERAL \| RAW_STRING_LITERAL \| MULTILINE_STRING_LITERAL \| InterpolatedString` | 1191 |
| `InterpolatedString` | `STRING_START InterpolatedStringPart* STRING_END` | 1192 |
| `InterpolatedStringPart` | `STRING_TEXT \| STRING_ESCAPE \| InterpolationExpr \| InterpolationPath` | 1193 |
| `InterpolationExpr` | `INTERPOLATION_OPEN Expr InterpolationFormat? INTERPOLATION_CLOSE` | 1197 |
| `InterpolationFormat` | `":" INTERPOLATION_FORMAT_TEXT` | 1198 |
| `InterpolationPath` | `"$" InterpolationPathRoot InterpolationPathSelector* INTERPOLATION_BOUNDARY?` | 1203 |
| `InterpolationPathRoot` | `Identifier \| "@"` | 1204 |
| `InterpolationPathSelector` | `"." Identifier \| "." StaticIntLiteral \| "[" InterpolationIndex "]"` | 1205 |
| `InterpolationIndex` | `StaticIntLiteral \| Identifier` | 1208 |
| `ListLiteral` | `"[" ExpressionList? "]"` | 1213 |
| `BoundedListLiteral` | `"[" StaticIntLiteral ".." StaticIntLiteral ":" ExpressionList? "]"` | 1214 |
| `ComprehensionExpr` | `"[" Expr ComprehensionClause+ "]"` | 1216 |
| `TypedMaterializationExpr` | `TypeRef MaterializationBody` | 1219 |
| `MaterializationBody` | `"${" MaterializationEntryList? "}"` | 1220 |
| `MaterializationEntryList` | `MaterializationEntry (MaterializationSeparator MaterializationEntry)* MaterializationSeparator?` | 1221 |
| `MaterializationEntry` | `Identifier \| Identifier ":" Expr \| StringLiteralExpr ":" Expr \| NamedUnfoldArgument` | 1222 |
| `MaterializationSeparator` | `"," LineBreakBoundary? \| LineBreakBoundary` | 1226 |
| `MapLiteral` | `"#" "map" "{" MapEntryList? "}"` | 1229 |
| `MapEntryList` | `MapEntry (MaterializationSeparator MapEntry)* MaterializationSeparator?` | 1230 |
| `MapEntry` | `Expr ":" Expr \| NamedUnfoldArgument` | 1231 |
| `SetLiteral` | `"#" "set" "{" ExpressionList? "}"` | 1232 |
| `MutListLiteral` | `"#" "mut" "[" ExpressionList? "]"` | 1233 |
| `MapComprehensionExpr` | `"#" "map" "{" MapEntry ComprehensionClause+ "}"` | 1234 |
| `SetComprehensionExpr` | `"#" "set" "{" Expr ComprehensionClause+ "}"` | 1235 |
| `ComprehensionClause` | `ForClause \| PositiveGuard \| IfLetClause \| UnfoldClause` | 1237 |
| `ForClause` | `"for" Pattern "in" Expr` | 1238 |
| `IfLetClause` | `"if" "let" Pattern "=" Expr` | 1239 |
| `UnfoldClause` | `"for" "..." Pattern "in" Expr` | 1240 |
| `NumericArrayLiteral` | `ShapeInferredArrayLiteral \| ShapeInferredColumnVectorLiteral \| ExactShapeArrayLiteral` | 1243 |
| `ShapeInferredArrayLiteral` | `"#" "[" ExpressionList? "]"` | 1246 |
| `ShapeInferredColumnVectorLiteral` | `"#" "[" Expr (";" Expr)+ "]"` | 1247 |
| `ExactShapeArrayLiteral` | `"#" StaticDimensionList "[" ArrayInitializer? "]"` | 1248 |
| `ArrayInitializer` | `ShapedRepeatInitializer \| ShapedGeneratorInitializer \| ShapedElementSequence` | 1249 |
| `ShapedRepeatInitializer` | `"repeat" ":" Expr` | 1252 |
| `ShapedGeneratorInitializer` | `"generate" ":" Expr` | 1253 |
| `ShapedElementSequence` | `Expr (ShapedElementSeparator Expr)* ShapedElementSeparator?` | 1254 |
| `ShapedElementSeparator` | `"," \| ShapedAxisBoundary` | 1255 |
| `ShapedAxisBoundary` | `";" ";"*` | 1256 |
| `MeasureLiteralExpr` | `NumericLiteral "[" UnitExpr "]"` | 1259 |
| `UnitExpr` | `PrattUnitExpr` | 1260 |
| `UnitPrimary` | `Identifier \| QualifiedPath \| "(" UnitExpr ")"` | 1261 |
| `UnitPostfixParselet` | `"^" SignedStaticInt` | 1262 |
| `UnitInfixOperator` | `"*" \| "/"` | 1263 |
| `PrattUnitExpr` | `UNIT_PRATT_ENTRY` | 1264 |

## `PREVIEW` 프로파일 — 13개

| 문법 production | 정확한 EBNF 오른쪽 항 | 원천 줄 |
|---|---|---:|
| `DeeplusPreview` | `PreviewLibrarySourceFile \| PreviewExecutableSourceFile \| PreviewScriptSourceFile` | 1273 |
| `PreviewLibrarySourceFile` | `PreviewGate ModuleDecl? PreviewLibraryItem*` | 1274 |
| `PreviewExecutableSourceFile` | `PreviewGate ModuleDecl? PreviewExecutableItem*` | 1275 |
| `PreviewScriptSourceFile` | `Shebang? PreviewGate ModuleDecl? PreviewScriptItem*` | 1276 |
| `PreviewLibraryItem` | `LibrarySourceItem \| PreviewFfiDecl` | 1278 |
| `PreviewExecutableItem` | `ExecutableSourceItem \| PreviewFfiDecl` | 1279 |
| `PreviewScriptItem` | `ScriptSourceItem \| PreviewFfiDecl` | 1280 |
| `PreviewGate` | `"#" "preview" "(" PreviewFeatureList ")" LineBreakBoundary` | 1282 |
| `PreviewFeatureList` | `Identifier ("," Identifier)*` | 1283 |
| `PreviewFfiDecl` | `PreviewFfiFunctionDecl \| PreviewFfiBlockDecl` | 1286 |
| `PreviewFfiFunctionDecl` | `"extern" "#" "C" "def" "#" "unsafe" Identifier ParameterList ReturnClause? ThrowsClause? EffectsClause? StatementBoundary` | 1287 |
| `PreviewFfiBlockDecl` | `"extern" "c" "(" PLAIN_STRING_LITERAL ")" "{" PreviewFfiBlockMember* "}"` | 1289 |
| `PreviewFfiBlockMember` | `"unsafe" "def" Identifier ParameterList ReturnClause? ThrowsClause? EffectsClause? StatementBoundary` | 1291 |
