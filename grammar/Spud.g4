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

// define tokens

Inlinewhitespacetoken : Inlinewhitespace ;
Returnwhitespacetoken : Returnwhitespace ;
Zerotoken : Zero ;
Nonzerotoken : Nonzero ;
Namesegment : '_'? Alpha ('_'? (Alpha | Zero | Nonzero))* ;

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

Catchall : 'A' | (~'A');

// parser rules

nonzerostring : Zerotoken* Nonzerotoken (Zerotoken|Nonzerotoken)* ;

decimallarge : nonzerostring '.' (Zerotoken|Nonzerotoken)* ;
decimalsmall : Zerotoken* '.' nonzerostring ;

fractionsimple : nonzerostring Inlinewhitespacetoken* '/' Inlinewhitespacetoken* nonzerostring ;
fractioncomplex : nonzerostring Inlinewhitespacetoken+ fractionsimple ;

number : nonzerostring
    | decimallarge | decimalsmall
    | fractionsimple | fractioncomplex ;

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
lineingredient : (number Inlinewhitespacetoken+ (basicname Inlinewhitespacetoken+)? )? basicnameplusprops ;

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

singleconvertingleftelem : number Inlinewhitespacetoken+ pownamewithprops ;
singleconvertingrightelem : (number|'$') Inlinewhitespacetoken+ basicwildwithprops ;
singleconvertingleft : singleconvertingleftelem (And singleconvertingleftelem)* ;
singleconvertingright : singleconvertingrightelem (And singleconvertingrightelem)* ;
linesingleconverting : singleconvertingleft Is singleconvertingright ;

doubleconvertingleftsub1 : '$' Inlinewhitespacetoken+ pownamewithprops ;
doubleconvertingleftsub2 : powname Inlinewhitespacetoken+ powwildwithprops ;
doubleconvertingleftelem : number Inlinewhitespacetoken+ (doubleconvertingleftsub1 | doubleconvertingleftsub2) ;
doubleconvertingrightelem : (number|'$') Inlinewhitespacetoken+ (basicname|'$') Inlinewhitespacetoken+ basicwildwithprops ;
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
    'multiply' Inlinewhitespacetoken+ number
    Inlinewhitespacetoken* onelinecomment? ;
atend : Inlinewhitespacetoken* '@end' ;
atsection : atbegin linebreak (line linebreak)* atend ;

lineat : atimport | athold
    | atholdunit | atdec
    | atfrac | atsection ;

verisoncontrol : 'spudversion' (~Returnwhitespacetoken)* ;

line : Inlinewhitespacetoken*
    ((lineingredient | linestandardrule | lineat | verisoncontrol)
        Inlinewhitespacetoken*)?
    onelinecomment? ;

spud : (line linebreak)* line EOF ;