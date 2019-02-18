from flask import Flask, jsonify
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import numpy as np
import json
from flask import Response

from utils import run_SVD, get_top_n_similar_users

app = Flask(__name__)

engine = create_engine('sqlite:///data/test.db')
metadata = MetaData(bind=engine)
Session = sessionmaker(bind=engine)

print("All available tables ", engine.table_names())


def default(o):
    if isinstance(o, np.int64): return int(o)
    raise TypeError


def get_users_tags_matrix():
    user_tag_matrix = np.zeros(shape=(10000, 998))
    with engine.connect() as con:
        rs = con.execute('SELECT * FROM user_course_tags')
        for row in rs:
            user_tag_matrix[row[0]] = np.array(row[1:])

    return user_tag_matrix


def get_user_courses(dictionary_userids_similarities):
    user_courses = {}
    with engine.connect() as con:
        rs = con.execute('SELECT * FROM user_course_views')
        for row in rs:
            if row[1] in dictionary_userids_similarities.keys():
                user_courses[row[1]] = user_courses.get(row[1], []) + [row[3]]

    for each in dictionary_userids_similarities.keys():
        user_courses[each] = list(set(user_courses.get(each, []))) + [dictionary_userids_similarities[each]]

    user_courses = sorted(user_courses.items(), key=lambda kv: kv[1][-1], reverse=True)
    return user_courses


U, _, _ = run_SVD(get_users_tags_matrix())


@app.route("/get_similar_users/<userId>/<count>", methods=['GET'])
def prediction(userId, count=100):
    userId = int(userId)
    count = int(count)
    if userId > 10000 or count > 10000:
        return Response(
            json.dumps("User Id/Count out of data limits. please enter an number below 10001", default=default),
            mimetype='application/json')
    dictionary_userids_similarities = get_top_n_similar_users(U, k=50, top_n=count, user_id=userId)
    get_users_courses = get_user_courses(dictionary_userids_similarities)
    print("most similar user ids", dictionary_userids_similarities.keys())
    print(get_users_courses)
    return Response(json.dumps(get_users_courses, default=default),
                    mimetype='application/json')  # json.dumps(get_users_courses, default=default)


@app.teardown_appcontext
def shutdown_session(exception=None):
    Session.close_all()


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001)
