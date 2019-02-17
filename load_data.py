import os

import pandas as pd
from matplotlib import pyplot

DATA_FOLDER = "data"
COURSE_TAGS = "course_tags.csv"
USER_ASSESSMENT_SCORES = "user_assessment_scores.csv"
USER_COURSE_VIEWS = "user_course_views.csv"
USER_INTERESTS = "user_interests.csv"

RESULTS_FOLDER = "results"

if not os.path.exists(RESULTS_FOLDER):
    os.makedirs(RESULTS_FOLDER)


def make_hist_plot(data, filename):
    pyplot.hist(data, bins=100)
    pyplot.xlabel(filename)
    pyplot.plot()
    pyplot.savefig(os.path.join(RESULTS_FOLDER, filename + ".png"))


def load_csv():
    print("Understanding course_tags.csv")
    # Understanding course_tags.csv
    course_tags = pd.read_csv(os.path.join(DATA_FOLDER, COURSE_TAGS))

    # print("course_tags columns ", course_tags.columns)

    all_course_tags = course_tags["course_tags"].unique()

    print("Num of unique course tags = ", len(all_course_tags))
    print("Num rows in course_tags", len(course_tags["course_tags"]))

    all_course_ids = course_tags["course_id"].unique()

    print("Num of unique course ids in course_tags ", len(all_course_ids))

    print("\nUnderstanding user_assessment_scores.csv")
    # Understanding user_assessment_scores.csv
    user_assessments = pd.read_csv(os.path.join(DATA_FOLDER, USER_ASSESSMENT_SCORES))
    # print("User assessment scores columns \n", user_assessments.columns)

    assessment_tags = user_assessments["assessment_tag"].unique()

    # print("All unique assessment tags = ", assessment_tags)
    print("Number of unique assessment tags", len(assessment_tags))

    print("total num of assessments", len(user_assessments["user_handle"]))

    intersection_set = set(assessment_tags).intersection(all_course_tags)
    print("Number of assessment tags which are also in course_tags", len(intersection_set))

    # print("all unique assessment tags", assessment_tags)
    # print("assessment tags which are also in course_tags", intersection_set)

    assessment_scores = user_assessments["user_assessment_score"]
    # print(assessment_scores)
    make_hist_plot(assessment_scores, "assessment_scores")

    print("\nUnderstanding user_course_views.csv")
    # Understanding user_course_views.csv
    user_course_views = pd.read_csv(os.path.join(DATA_FOLDER, USER_COURSE_VIEWS))
    # print("User course views columns", user_course_views.columns)

    course_ids = user_course_views["course_id"].unique()

    print("Number of course IDs in user course views", len(course_ids))
    print("Course IDs (from user views) intersection with course tags", len(set(course_tags).intersection(course_ids)))
    print("Course IDs (from user views) intersection with assessment tags",
          len(set(assessment_tags).intersection(course_ids)))
    print("Course IDs (from user views) intersection with Course Ids from (course tags)",
          len(set(all_course_ids).intersection(course_ids)))

    author_handles = user_course_views["author_handle"].unique()

    print("Number of unique author handles", len(author_handles))

    print("\nUnderstanding user_interests.csv")
    # Understanding user_interests.csv
    user_interests = pd.read_csv(os.path.join(DATA_FOLDER, USER_INTERESTS))

    interests_tags = user_interests["interest_tag"].unique()
    user_ids = user_interests["user_handle"].unique()

    print("Total number of unique user handles", len(user_ids))
    print("Number of unique interest tags", len(interests_tags))
    print("Intersection of interest tags with course tags", len(set(interests_tags).intersection(course_tags)))
    print("Intersection of interest tags with assessment tags", len(set(interests_tags).intersection(assessment_tags)))
    print("Intersection of interest tags with course ids", len(set(interests_tags).intersection(course_ids)))


load_csv()
