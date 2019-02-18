import os

import numpy as np
from matplotlib import pyplot
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import svds

DATA_FOLDER = "data"
COURSE_TAGS = "course_tags.csv"
USER_ASSESSMENT_SCORES = "user_assessment_scores.csv"
USER_COURSE_VIEWS = "user_course_views.csv"
USER_INTERESTS = "user_interests.csv"

RESULTS_FOLDER = "results"

if not os.path.exists(RESULTS_FOLDER):
    os.makedirs(RESULTS_FOLDER)


def top_cosine_similarity(data, user_id, top_n=10):
    top_n += 1
    index = user_id - 1
    user_row = data[index, :]
    magnitude = np.sqrt(np.einsum('ij, ij -> i', data, data))
    print(magnitude)
    magnitude[magnitude == 0] = 10 ** -21
    similarity = np.dot(user_row, data.T) / (magnitude[index] * magnitude)
    sort_indexes = np.argsort(-similarity)
    top_n_similarities = similarity[sort_indexes[:top_n]]
    userIds = [1 + x for x in sort_indexes[:top_n]]
    dictionary_userids_similarities = dict(zip(userIds, top_n_similarities))
    return dictionary_userids_similarities


def make_hist_plot(data, filename):
    pyplot.hist(data, bins=100)
    pyplot.xlabel(filename)
    pyplot.plot()
    pyplot.savefig(os.path.join(RESULTS_FOLDER, filename + ".png"))


def get_matching_course_tags(all_course_tags, courseId_courseTags, other_tags):
    otherTag_courseTag = {}
    for each_other_tag in list(set(other_tags) - set(all_course_tags)):
        max_score_tags = None
        max_score = 0
        other_words = set(each_other_tag.split("-"))
        other_words.add("".join(each_other_tag.split("-")))
        for each_id in courseId_courseTags:
            all_id_words = each_id.split("-")
            curr_score = len(other_words.intersection(all_id_words))
            if curr_score > max_score:
                max_score = curr_score
                max_score_tags = courseId_courseTags[each_id]
            elif curr_score > 0 and curr_score == max_score:
                max_score_tags = list(set(max_score_tags).union(courseId_courseTags[each_id]))

        otherTag_courseTag[each_other_tag] = max_score_tags
    return otherTag_courseTag


def get_missing_course_tags(all_course_tags, course_ids):
    missingTag_courseTag = {}
    for each_id in course_ids:
        max_score_tags = None
        max_score = 0
        other_words = set(each_id.split("-"))

        for each_tag in all_course_tags:
            all_tag_words = each_tag.split("-")
            curr_score = len(other_words.intersection(all_tag_words))
            if curr_score > max_score:
                max_score = curr_score
                max_score_tags = each_tag
        missingTag_courseTag[each_id] = max_score_tags
    return missingTag_courseTag


def get_top_n_similar_users(U, k, top_n, user_id):
    sliced = U[:, :k]
    id_sim_dict = top_cosine_similarity(sliced, user_id, top_n)
    id_sim_dict.pop(user_id, None)
    return id_sim_dict


def run_SVD(user_tag_matrix):
    A = csc_matrix(user_tag_matrix, dtype=float)
    U, _, _ = svds(A)
    print(U.shape)
    return U, _, _
