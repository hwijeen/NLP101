## 자연어처리론 숙제 #1

#### 1. 손으로 형태소 분석하기

- 엄마가 해 주신 밥이 세상에서 제일 맛있다.

엄마/NN + 가/JK

***해/VV*** ('여'불규칙)

주/VV + 시/E + ㄴ/E

밥/NN + 이/JK

세상/NN + 에서/JK

제일 /MA

맛있/VV + 다/E + ./SF



- 화요일에 자연어처리 수업이 있어서 학교에 갑니다.

화요일 / NN +  에/JK

***자연어/NN + 처리/NN***

수업/NN + 이/JK

있/VV + 어서/E

학교/NN + 에/JK

가/VV + ㅂ니다/E + ./SF



- 어제 기온은 아침과 저녁에 낮고, 낮에는 높아서 감기에 걸리기 쉬웠다.

***어제/MA***

기온/NN + 은/JX

아침/NN + 과/JC

저녁/NN + 에/JK

낮/VA + 고/E + ,/SP

낮/NN + 에/JK + 는/JX

높/VA + 아서/E

감기/NN + 에/JK

걸리/VV + 기/E

***쉬웠다/VV + ./SF*** ('ㅂ'불규칙)



#### 2. TRIE 사전 만들기

- class trie에 add_node말고 추가해야하는 메서드가 뭘까!! Tabular parsing시 필요한 거 고민





#### 참고 링크

[불규칙 활용](https://namu.wiki/w/%ED%95%9C%EA%B5%AD%EC%96%B4/%EB%B6%88%EA%B7%9C%EC%B9%99%20%ED%99%9C%EC%9A%A9#s-2.4)

[조사](https://namu.wiki/w/%ED%95%9C%EA%B5%AD%EC%96%B4%EC%9D%98%20%EC%A1%B0%EC%82%AC#s-2.1.6.8)

[어미](https://ko.wikipedia.org/wiki/%ED%95%9C%EA%B5%AD%EC%96%B4_%EB%AC%B8%EB%B2%95#%EC%96%B4%EB%A7%90_%EC%96%B4%EB%AF%B8)

[TRIE 구조](https://gist.github.com/osori/d0200b9bb7665d6a69da61b431e4077f)





#### TODO /  ISSUE

정답 말고도 가능한 형태소 분석 포함해서 사전 만들기

Tabular parsing table fill 규칙 찾기

