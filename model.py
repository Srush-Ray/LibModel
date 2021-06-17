from flask import Flask, request, jsonify
import psycopg2
import json
import os
# from asgiref.sync import async_to_sync
# from .data_analysis import text_mining
#from .Similarity import demo
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
import nltk
import gensim
from gensim import corpora
from nltk.corpus import stopwords


app = Flask(__name__)


@app.route('/')
def home():
    return "Chatbot home open"


@app.route('/flask', methods=['POST'])
def index():
    asked_question = " "
    print("ohh haa")
    try:
        # conn = psycopg2.connect(database="d8vvied9p5rnob", user="dyhgctjqbmdgzi",
        #                         password="f42f02ba1dec14620f2ee83428f08c834f39edf81ed018d48669ebbfdbc4bb44", host="ec2-23-22-191-232.compute-1.amazonaws.com", port="5432")

        conn = psycopg2.connect(database="dfl4jabh70qmq2", user="xymanbcpmaetso",
                                password="380616dfaa56e873b66e3cd42bf259c513a1ed1fb8613aca732bffc7c230f3a5", host="ec2-23-22-191-232.compute-1.amazonaws.com", port="5432")
        asked_question = request.form['message']
        # print("hey", request.args)
        # user = request.args.get('key')
        # print(user)
        # text_data_json = json.loads(text_data)
        # asked_question = text_data_json['message']
        flag = request.form['flag']
        message = request.form['message']
        ans = 'not found'
        ans_id = ''
        # print(flag=="1")
        if flag == "1":
            t = None
            #obj = demo()
            que_list = []
            ans_list = []
            id_list = []
            db_cursor = conn.cursor()
            s = 'SELECT * FROM "query_table"'
            try:
                db_cursor.execute(s)
                # Retrieve records from Postgres into a Python List
                db_questions = db_cursor.fetchall()
                for row in db_questions:
                    # print(row[0])
                    id_list.append(row[0])
                    que_list.append(row[1])
                    ans_list.append(row[2])
                # print(que_list)
                file2_docs = []

                gen_docs = [[w.lower() for w in word_tokenize(text)]
                            for text in que_list]
                dictionary = gensim.corpora.Dictionary(gen_docs)
                corpus = [dictionary.doc2bow(gen_doc) for gen_doc in gen_docs]
                tf_idf = gensim.models.TfidfModel(corpus)
                sims = gensim.similarities.Similarity(
                    None, tf_idf[corpus], num_features=len(dictionary))

                tokens = sent_tokenize(asked_question)
                for line in tokens:
                    file2_docs.append(line)

                for line in file2_docs:
                    query_doc = [w.lower() for w in word_tokenize(line)]
                    query_doc_bow = dictionary.doc2bow(query_doc)

                query_doc_tf_idf = tf_idf[query_doc_bow]
                similarity_list = sims[query_doc_tf_idf]
                sims.destroy()

                max_similarity = max(similarity_list)

                similarity_list = similarity_list.tolist()
                max_similarity_index = similarity_list.index(max_similarity)

                ans = ans_list[max_similarity_index]
                ans_id = id_list[max_similarity_index]
                print("answer id", ans_id)

                # hold = Query_table.objects.get(id = ans_id)
                # hold.viewed = hold.viewed + 1
                # hold.save()

            except psycopg2.Error as e:
                t_message = "Database error: " + e + "/n SQL: " + s
                return "Error in database query"
            db_cursor.close()
            conn.close()
        # if flag == 0:
        #     print("In flag =0")
        #     t=None
        #     find_name = text_mining(message)
        #     name = find_name.identify_name()

        #     if(name == '0'):
        #         name = 'User'
        #         flag = 2

        response = {
            "qid": ans_id,
            "flag": "0"
        }
        # print(jsonify(response))
        return jsonify(response), 200
    except:
        return "Lost connection to database try again"


if __name__ == "__main__":
    osPort = os.getenv("PORT")
    if osPort == None:
        port = 33507
    else:
        port = int(osPort)
    app.run(host='0.0.0.0', port=port)

    # port = int(os.environ.get("PORT", 33507))
    # print(port)
    # app.run(host='0.0.0.0', port=port, debug=True)
    # app.run(port=5000, debug=True)
