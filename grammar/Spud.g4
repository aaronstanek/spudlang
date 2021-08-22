grammar Spud;

// lexer rules

// define alphabet

fragment Inlinewhitespace : ' ' | '\t' ;
fragment Returnwhitespace : '\n' | '\r' ;

fragment Uppercase : [A-Z] ;
fragment Lowercase : [a-z] ;
fragment Alpha : Uppercase | Lowercase ;

fragment Zero : '0' ;
fragment Nonzero : [1-9] ;
fragment Numeral : Zero | Nonzero ;
fragment Nonzerostring : Zero* Nonzero Numeral* ;

fragment Decimallarge : Nonzerostring '.' Numeral* ;
fragment Decimalsmall : Zero* '.' Nonzerostring ;
fragment Decimal : Decimallarge | Decimalsmall ;

fragment FractionSimple : Nonzerostring Inlinewhitespace* '/' Inlinewhitespace* Nonzerostring ;
fragment FractionComplex : Nonzerostring Inlinewhitespace+ FractionSimple ;
fragment Fraction : FractionSimple | FractionComplex ;

// define tokens

Inlinewhitespacetoken : Inlinewhitespace ;
Returnwhitespacetoken : Returnwhitespace ;
Number : Nonzerostring | Decimal | Fraction ;
Namesegment : '_'? Alpha ('_'? (Alpha | Numeral))* ;

And : Inlinewhitespace* '&' Inlinewhitespace* ;
Is : Inlinewhitespace+ ('is'|'are') Inlinewhitespace+ ;
Istype : Inlinewhitespace+ ('is'|'are') Inlinewhitespace+
    ('a' Inlinewhitespace+)?
    'type' 's'? Inlinewhitespace+
    ('of' Inlinewhitespace+)? ;
Issynonym : Inlinewhitespace+ ('is'|'are') Inlinewhitespace+
    ('a' Inlinewhitespace+)?
    'synonym' 's'? Inlinewhitespace+
    ('of' Inlinewhitespace+)? ;

Catchall : (' '..'~') | '\t' ;

// parser rules

onelinecomment : ('#'|'//') (~Returnwhitespacetoken)* ;
multilinecomment : '/*' (~'*/')* '*/' ;
linebreak : Returnwhitespacetoken | multilinecomment ;

propspluselem : Inlinewhitespacetoken* '+' Inlinewhitespacetoken*  Namesegment ;
propsplus : propspluselem* ;
propselem : Inlinewhitespacetoken* ('+'|'-') Inlinewhitespacetoken*  Namesegment ;
props : propselem* ;
propswildelem : Inlinewhitespacetoken* '-' Inlinewhitespacetoken* '$' ;
propswild : (propselem|propswildelem)* ;

basicname : Namesegment ( '.' Namesegment )* ;
basicnameplusprops : basicname propsplus ;
lineingredient : (Number Inlinewhitespacetoken+ (basicname Inlinewhitespacetoken+)? )? basicnameplusprops ;

powname : '!'? basicname '!'? ;

pownamewithprops : powname props ;
basicnamewithpropswild : basicname propswild ;
wildcardwithprops : '$' props ;
wildcardwithpropswild : '$' propswild ;

powwildwithprops : pownamewithprops | wildcardwithprops ;
basicwildwithprops : basicnamewithpropswild | wildcardwithpropswild ;

ruleleftsimple : pownamewithprops (And pownamewithprops)* ;
rulerightsimple : basicnamewithpropswild (And basicnamewithpropswild)* ;
rulerightsimplewild : basicwildwithprops (And basicwildwithprops)* ;
linerenaming : ruleleftsimple Is rulerightsimplewild ;
lineprefixing : ruleleftsimple Istype rulerightsimplewild ;
lineinserting : ruleleftsimple Issynonym rulerightsimple ;

singleconvertingleftelem : Number Inlinewhitespacetoken+ pownamewithprops ;
singleconvertingrightelem : (Number|'$') Inlinewhitespacetoken+ basicwildwithprops ;
singleconvertingleft : singleconvertingleftelem (And singleconvertingleftelem)* ;
singleconvertingright : singleconvertingrightelem (And singleconvertingrightelem)* ;
linesingleconverting : singleconvertingleft Is singleconvertingright ;

doubleconvertingleftsub1 : '$' Inlinewhitespacetoken+ pownamewithprops ;
doubleconvertingleftsub2 : powname Inlinewhitespacetoken+ powwildwithprops ;
doubleconvertingleftelem : Number Inlinewhitespacetoken+ (doubleconvertingleftsub1 | doubleconvertingleftsub2) ;
doubleconvertingrightelem : (Number|'$') Inlinewhitespacetoken+ (basicname|'$') Inlinewhitespacetoken+ basicwildwithprops ;
doubleconvertingleft : doubleconvertingleftelem (And doubleconvertingleftelem)* ;
doubleconvertingright : doubleconvertingrightelem (And doubleconvertingrightelem)* ;
linedoubleconverting : doubleconvertingleft Is doubleconvertingright ;

linestandardrule : linerenaming | lineprefixing
    | lineinserting | linesingleconverting | linedoubleconverting ;

atimport : '@import' Inlinewhitespacetoken+ (~Returnwhitespacetoken)* ;

atsub1 : '$' Inlinewhitespacetoken+ pownamewithprops ;
atsub2 : powname Inlinewhitespacetoken+ (powwildwithprops|'$') ;
atsub : Inlinewhitespacetoken+ (atsub1 | atsub2) ;

athold : '@hold' atsub ;
atholdunit : '@holdunit' atsub ;
atdec : '@dec' atsub ;
atfrac : '@frac' atsub ;

atbegin : '@begin' Inlinewhitespacetoken+
    'multiply' Inlinewhitespacetoken+ Number
    Inlinewhitespacetoken* onelinecomment? ;
atend : Inlinewhitespacetoken* '@end' ;
atsection : atbegin linebreak (line linebreak)* atend ;

lineat : atimport | athold
    | atholdunit | atdec
    | atfrac | atsection ;

line : Inlinewhitespacetoken*
    ((lineingredient | linestandardrule | lineat) Inlinewhitespacetoken*)?
    onelinecomment? ;

spud : (line linebreak)* line EOF ;