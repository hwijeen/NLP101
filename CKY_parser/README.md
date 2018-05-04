# CKY Parser

자연어처리 과제2 - 안휘진

#### 파일 설명

1.  CKYParser.py

- Node class와 CKYParser class가 정의되어 있다. 
- Node는 parsing table(DP table)의 cell에 저장되는 단위로, 음절과 문법 요소 등을 포함한다.
- CKYParser.parse는 tabular parsing 방식으로 parsing을 한다. 셀을 순차적으로 방문하면서 grammar_check를 하고,  문법 검사 성공시 두 cell을 merge한다. parsing 완료시 print_tree를 통해 콘솔창과 output.txt에 결과를 출력한다.

2. main.py

- grammar.txt를 읽고 unary_grammar, binary_grammar, full_lexicon을 추출한다.
- input.txt에서 테스트 문장들을 읽어들인다
- 테스트 문장에 대해 파싱을 한다.