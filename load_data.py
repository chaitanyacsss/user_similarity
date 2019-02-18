import pandas as pd
from sqlalchemy import create_engine, MetaData

from utils import *

if not os.path.exists(RESULTS_FOLDER):
    os.makedirs(RESULTS_FOLDER)


def start_connection():
    cnx = create_engine('sqlite:///data/test.db')
    return cnx


def load_data():
    # Initialize connection
    cnx = start_connection()
    metadata = MetaData(bind=cnx)

    print("Understanding course_tags.csv")
    # Understanding course_tags.csv
    course_tags_df = pd.read_csv(os.path.join(DATA_FOLDER, COURSE_TAGS))
    print("Rows/courses with no tags COUNT", len(course_tags_df[course_tags_df['course_tags'].isnull()]))

    course_tags_df.dropna(subset=["course_tags"], inplace=True)

    # Dictionary of course Id vs Tag
    courseId_courseTags = {}
    for index, row in course_tags_df.iterrows():
        curr_course_id = row["course_id"]
        curr_course_tag = row["course_tags"]
        if curr_course_tag:
            courseId_courseTags[curr_course_id] = courseId_courseTags.get(curr_course_id, []) + [curr_course_tag]

    all_course_tags = course_tags_df["course_tags"].unique()

    print("Num of unique course tags = ", len(all_course_tags))
    print("Num rows in course_tags", len(course_tags_df["course_id"]))

    all_course_ids = course_tags_df["course_id"].unique()

    print("Num of unique course ids in course_tags ", len(all_course_ids))

    course_tags_df.to_sql('course_tags', cnx, if_exists='replace')

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
    print("Assessment tags which are NOT in course_tags", set(assessment_tags) - set(all_course_tags))
    print("Assessment tags which are NOT in course_tags COUNT ", len(set(assessment_tags) - set(all_course_tags)))

    assessment_scores = user_assessments["user_assessment_score"]
    make_hist_plot(assessment_scores, "assessment_scores")

    user_assessments.to_sql('user_assessment_scores', cnx, if_exists='replace')

    print("\nUnderstanding user_course_views.csv")
    # Understanding user_course_views.csv
    user_course_views = pd.read_csv(os.path.join(DATA_FOLDER, USER_COURSE_VIEWS))
    # print("User course views columns", user_course_views.columns)

    course_ids = user_course_views["course_id"].unique()

    print("Number of course IDs in user course views", len(course_ids))
    print("Course IDs (from user views) intersection with course tags",
          len(set(all_course_tags).intersection(course_ids)))
    print("Course IDs (from user views) intersection with assessment tags",
          len(set(assessment_tags).intersection(course_ids)))
    print("Course IDs (from user views) intersection with Course Ids from (course tags)",
          len(set(all_course_ids).intersection(course_ids)))

    author_handles = user_course_views["author_handle"].unique()

    print("Number of unique author handles", len(author_handles))

    user_course_views.to_sql('user_course_views', cnx, if_exists='replace')

    print("\nUnderstanding user_interests.csv")
    # Understanding user_interests.csv
    user_interests = pd.read_csv(os.path.join(DATA_FOLDER, USER_INTERESTS))

    interests_tags = user_interests["interest_tag"].unique()
    user_ids = user_interests["user_handle"].unique()

    print("Total number of unique user handles", len(user_ids))
    print("Number of unique interest tags", len(interests_tags))
    print("Intersection of interest tags with course tags", len(set(interests_tags).intersection(all_course_tags)))
    print("Intersection of interest tags with assessment tags", len(set(interests_tags).intersection(assessment_tags)))
    print("Intersection of interest tags with course ids", len(set(interests_tags).intersection(course_ids)))

    print("Left out interest tags from course tags", set(interests_tags) - set(all_course_tags))
    print("Left out interest tags from course tags COUNT", len(set(interests_tags) - set(all_course_tags)))

    print("Left out interest tags from course tags and assessment tags",
          set(interests_tags) - set(all_course_tags) - set(assessment_tags))

    user_interests.to_sql('user_interests', cnx, if_exists='replace')

    # # Check if assessment tags are "contained" in course tags:
    assessmentTag_courseTags = get_matching_course_tags(all_course_tags, courseId_courseTags, assessment_tags)

    # Check if interest tags are "contained" in course tags:
    interestTag_courseTags = get_matching_course_tags(all_course_tags, courseId_courseTags, interests_tags)

    print("Assessment tag matching:", assessmentTag_courseTags)
    print("Interest tag matching", interestTag_courseTags)

    # Create a matrix of users vs tags:
    user_tag_matrix = np.zeros(shape=(len(user_ids), len(all_course_tags)))
    print(user_tag_matrix.shape)

    # Add tags from assessments using assessmentTag_courseTags:
    for index, row in user_assessments.iterrows():
        curr_user_id = row["user_handle"]
        curr_assessment_tag = row["assessment_tag"]
        curr_tags = assessmentTag_courseTags.get(curr_assessment_tag, [curr_assessment_tag])
        for each in curr_tags:
            user_tag_matrix[curr_user_id - 1][np.where(all_course_tags == each)] = 1

    print("Check if tags were added", user_tag_matrix.sum())
    # Add tags from interests using interestTag_courseTags:
    for index, row in user_interests.iterrows():
        curr_user_id = row["user_handle"]
        curr_interest_tag = row["interest_tag"]
        curr_tags = assessmentTag_courseTags.get(curr_interest_tag, [curr_interest_tag])
        for each in curr_tags:
            user_tag_matrix[curr_user_id - 1][np.where(all_course_tags == each)] = 1

    print("Check if tags were added", user_tag_matrix.sum())
    # Add tags from user_course_views using courseId_courseTags:
    for index, row in user_course_views.iterrows():
        curr_user_id = row["user_handle"]
        curr_course_id = row["course_id"]
        curr_tags = courseId_courseTags.get(curr_course_id, [])
        for each in curr_tags:
            user_tag_matrix[curr_user_id - 1][np.where(all_course_tags == each)] = 1

    print("Check if tags were added", user_tag_matrix.sum())

    row_sums = user_tag_matrix.sum(axis=1)
    row_sums[row_sums == 0] = 1
    # Normalizing per user
    user_tag_matrix = user_tag_matrix / row_sums[:, np.newaxis]

    print("Check value before db insert", user_tag_matrix.sum())
    user_tag_df = pd.DataFrame(user_tag_matrix)
    user_tag_df.to_sql('user_course_tags', cnx, if_exists='replace')
    metadata.create_all(cnx)

    return user_course_views, user_assessments, course_tags_df, user_interests


if __name__ == '__main__':
    user_course_views, user_assessments, course_tags_df, user_interests = load_data()
