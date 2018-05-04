# HMM POS Tagger

### 파일 구성

​	

1. HMM.py

   - preprocess 메서드를 통해 train data를 적절히 가공한다.
   - train 메서드는 HMM의 transition probability와 emission probability를 계산해서 matrix형태로 저장한다. 이때, 확률값 0을 방지하기 위해 laplace smoothing이 사용되었다.
   - predict 메서드 내부에서 viterbi 알고리즘을 통해 가능한 형태소 sequence중 최고 확률을 갖는 형태소 sequence를 찾는다. 어절 단위로 lattice를 구성해 한 어절이 여러 형태소로 나뉘는 문제에 대처했다. viterbi matrix에 확률값을 저장하며, backtrace matrix에 viterbi trail을 저장하여 알고리즘 종료 후 최고 확률 형태소 sequence를  출력할 수 있도록 한다. predict결과는 모니터에 출력 및 output.txt에 저장된다. 

   

2. main.py

   - 입력파일(result.txt)을 읽어와 HMM이 처리할 수 있도록 전처리 해준다.
   - HMM 인스턴스를 만들고, 지정해준 파일(train.txt)을 바탕으로 train 메서드를 실행한다.
   - train이 완료된 후 전처리된 문장에 대한 형태소열 predict를 한다.

   

