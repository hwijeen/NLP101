# NER Tagging

### Sequence Labeling

- Json파일을 읽어들여 CoNLL형식의 txt파일을 출력한다.

### NER

- utils.py
  - class config()
    - 입/출력 파일 경로, pretrained word embedding 파일 경로, 모델 하이퍼 파라미터 등을 조정
    - \__init__()을 통해 vocab을 생성
  - class data_read()
    - data_build()내부에서 호출되는 helper 함수
    - 데이터를 읽어들이는 이터러블!
    - \__iter__()은 제너레이터로, 단어와 태그를 yield한다
    - \__len__()을 정의해서 len 메서드 사용할 수 있게끔!
  - def load_vocab(filename)
    - config class의 \__init()__에서 vocab을 불러오기 위한 helper 함수
  - def write_vocab(vocab, filename)
    - data_build()에서 호출됨
    - vocab을 파일로 저장
  - def data_build()
    - train 전에 실행되어야하는 함수로, train/dev/test를 토대로 vocab을 만든다
    - pretrained에 있는 단어 & 읽어들인 단어의 교집합으로 vocab 구성
-  model.py
  - def minibatches(data, minibatch_size)	
    - batch를 만들어서 yield하는 제너레이터	
  - class NERmodel()
    - def \__init(self, config)__
    - def build(self)
      - placeholder, embedding, RNN구조, loss, optimizer, session/saver을 포함한 그래프 정의
    - def train(self, train, dev)
    - def restore_session(self, dir_model)
    - def run_evaluate(self, test)
      - dev set에 대한 성능 측정(cross-validation용)
    - def get_feed_dict(self, words, labels=None, lr=None, dropout=None)
    - def predict_batch(self, words)
      - predict를 위한 helper
    - def predict(self, words_raw)
      - inference만 할 때 사용