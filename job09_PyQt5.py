import pandas as pd
from sklearn.metrics.pairwise import linear_kernel
from scipy.io import mmread, mmwrite
import pickle
from gensim.models import Word2Vec
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QPixmap
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
from PyQt5.QtWebEngineWidgets import QWebEngineView

form_window = uic.loadUiType('./webWidget.ui')[0]
class WebView(QWebEngineView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def release(self):
        self.deleteLater()
        self.close()

class Exam(QWidget, form_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self._webview = WebView()
        self.web.addWidget(self._webview)
        # self._webview.load(QUrl('http://www.naver.com'))
        self._webview.load(QUrl('http://localhost:63342/Unsupervised_NLP_for_place_recommend2/html/search_place_main.html?_ijt=8qjrtd7rv06g0t2osit3t9d8eh&_ij_reload=RELOAD_ON_SAVE'))
        self.df_contents = pd.read_csv('./refined_data/cleaned_data.csv')
        self.Tfidf_matrix = mmread('./models/Tfidf_tour.mtx').tocsr()
        with open('./models/tfidf01.pickle', 'rb') as f:
            self.Tfidf = pickle.load(f)
        self.btn_recommend.clicked.connect(self.btn_recommend_slot)

    #검색버튼함수
    def btn_recommend_slot(self):
        sentence = self.te_keyword.toPlainText()
        print(sentence)
        input_words = sentence.split()
        if len(input_words) >= 10:
            sentence_vec = self.Tfidf.transform([sentence])
            recommendation_titles = self.recommend_by_sentence(sentence)
            self._webview.load(QUrl('http://localhost:63342/Unsupervised_NLP_for_place_recommend2/html/search_place_result.html?_ijt=95tk70fdqitcn4f7rq1o6ufcks&_ij_reload=RELOAD_ON_SAVE'))
            self.te_keyword.hide()
            self.btn_recommend.hide()
        else:
            key_word = input_words[0]
            embedding_model = Word2Vec.load('./models/word2vecModel.model')
            try:
                sim_word = embedding_model.wv.most_similar(key_word, topn=10)
            except:
                self._webview.load(QUrl('http://localhost:63342/Unsupervised_NLP_for_place_recommend2/html/empty_place_result.html?_ijt=95tk70fdqitcn4f7rq1o6ufcks&_ij_reload=RELOAD_ON_SAVE'))
                self.te_keyword.show()
                self.btn_recommend.show()
                return
            sentence = [key_word] * 11
            words = []
            for word, _ in sim_word:
                words.append(word)
            for i, word in enumerate(words):
                sentence += [word] * (10 - i)

            sentence = ' '.join(sentence)
            recommendation_titles = self.recommend_by_sentence(sentence)
            print('debug01')
            self._webview.load(QUrl('http://localhost:63342/Unsupervised_NLP_for_place_recommend2/html/search_place_result.html?_ijt=95tk70fdqitcn4f7rq1o6ufcks&_ij_reload=RELOAD_ON_SAVE'))
            self.te_keyword.hide()
            self.btn_recommend.hide()



    def recommend_by_sentence(self, sentence):
        sentence_vec = self.Tfidf.transform([sentence])
        cosin_sim = linear_kernel(sentence_vec,
                                  self.Tfidf_matrix)
        recommendation_titles = self.getRecommendation(cosin_sim)
        # recommendation_titles = '\n'.join(list(recommendation_titles))
        # return recommendation_titles
        recommendation_titles.to_json('./output/recommendation.json') #제이슨파일 생성은 이 위치에서?

    def getRecommendation(self, cosine_sim):
        simScore = list(enumerate(cosine_sim[-1]))
        simScore = sorted(simScore, key=lambda x: x[1],
                              reverse=True)
        simScore = simScore[1:11]
        touridx = [i[0] for i in simScore]
        recTourList = self.df_contents.iloc[touridx, :]
        return recTourList



app = QApplication(sys.argv)
mainWindow = Exam()
mainWindow.show()
sys.exit(app.exec_())


