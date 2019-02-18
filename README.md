### Finding User Similarity ##
## Introduction ##

The data consists of users(10000) and their interactions with a learning website. There are four different data which have the following information.

1) [course_tags](data/course_tags.csv) : This CSV file consists of courses_Ids and the course tags which are applicable to each course. 

2) [user_assessment_scores](data/user_assessment_scores.csv) : This CSV file consists of user assessment information. Users can take topic assessment tests and test their domain skills.
The file also has an assessment_tag which points to the topic. 

3) [user_course_views.csv](data/user_course_views.csv) : This CSV file has course viewing information for the users, maintains a log of per day time spent on the course by the user.
This also has the course author handle information which can help in identifying author wise user distribution.

4) [user_interests.csv](data/user_interests.csv) : This CSV file contains users and their "interest tags", which again are highlevel representations of topics.

5) We load these tables into SQLite tables.


## Basic Stats ##

1) There are 10000 unique UserIds and 5942 unique courseIds.

2) There are 998 Unique Course tags, 54 unique assessment tags and 748 unique interest tags where the overlap looks like


Intersection(Interest Tags, Course Tags) = 591
Intersection(Assessment Tags, Course Tags) = 16
Intersection(Assessment Tags, Interest Tags) = 17
Intersection(Interest Tags, Course Ids) = 23

3) There are 1412 unique Author handles.


## Problem Statement ##

The similarity between users is to be calculated and given a user Id, similar users and their information should be accessible via a REST API end point.


## Methodology ##


1) Inorder to proceed, understanding the motivation behind the problem statement is helpful. Since the data comprises of users/course/courses tags, it is clear that we want to
identify similar users as a precursor to better recommendations. Identifying user clusters can help scale a recommendations system and thus the problem of user similarity.

2) While Collaborative Filtering(CF) between Users/Courses is the first thought for an approach, user-course interaction is only a part of our available data.
(ex. Interest tags and Assessment Tags are different from user-course interaction). Also, CF has scalability problems and the implementation is not straight forward in our case.

3) Using Tags instead of courses will accomodate utilization of more data (interests/assessments etc.), but we need to standadize the tags before we can use them.

4) From the stats mentioned above, it is clear that course tags is the most complete set and the interesections of other tags with course tags are significant. We 
therefore try to find matching tags for the remaining interest/assessment tags. We do that by observing the overlap of words between tag and courseIds. We assign the corresponding
course_tag for the highest overlap. We also ignore the courses for which there are no tags (Can be considered in a future improvement).

5) We now build a user*tag matrix by collecting the user's tags from all the tables. There is no scoring currently. If a tag appears for a user, the user[tag] = 1.
This matrix is normalized per user.
 
6) The normalized matrix is saved into a new table in the database. This UserxTag matrix is of shape 10000x998. Looking at the tags, it is clear that many of them are correlated and
the the dimensions can be reduced because of the correlations, which makes SVD a viable technique for this data.

7) Using Singular Value Decomposition(SVD) on the User x Tag matrix and Cosine similarity on the top of the result, we get user similarity scores for a given user Id.

8) A Rest API end point is created using Flask and given a User Id and count n, the end-point gives n most similar users for the given id and the courses viewed by them,
which can help in making recommendations, followed by the similairity score. Once hosted, the end point can be accessed at

```
http://localhost:5002/get_similar_users/{UserId}/{ResultCount}
``` 

The resulting json looks like this

```
[
	[214, ["mvc4", "aspdotnet-mvc5-fundamentals", "practical-linq", "responsive-multiplayer-action-web-game-html5-1719", "phonegap-build-fundamentals", "materials-vue-762", "c-sharp-fundamentals-with-visual-studio-2015", "csharp-generics", "entity-framework-6-getting-started", "asp-dotnet-core-api-building-first", "play-by-play-xamarin-mobile-development", "microsoft-web-technology-comparison", "html-helper-library-aspdotnet-mvc5", "vue-js-single-page-applications", "linq-fundamentals", "cross-platform-mobile-game-html5-javascript-1961", "building-mobile-apps-ionic-framework-angularjs", "aspdotnet-core-1-0-fundamentals", "mvc-request-life-cycle", "native-mobile-apps-with-html5", "clean-architecture-patterns-practices-principles", 0.6694032590502362]],
	[7067, ["browser-security-headers", 0.6193983103886171]],
	[1171, ["information-systems-auditor-process-auditing", "information-systems-auditor-protection-assets", "information-systems-auditor-governance-management", 0.6102936254946676]],
	[6549, [0.6078468670529944]],
	[6070, ["malware-analysis-fundamentals", 0.6000254867357465]],
	[6298, [0.5965406696436973]],
	[161, ["https-every-developer-must-know", "python-understanding-machine-learning", "getting-started-kubernetes", "tableau-10-whats-new", "docker-containers-big-picture", 0.5767998011389044]],
	[4176, ["windows-server-2016-active-directory-certificate-services", "windows-server-2012-r2-certificate-services", 0.5747915903975388]],
	[7696, [0.5562233695477509]],
	[1372, ["web-security-owasp-top10-big-picture", "angular-typescript", 0.5495456927642477]]
]
```

If there are no courses viewed by the user, the result just contains the similarity score.


## Future Improvements and Context-based Exploration ##

1) The data contains relatively small number of data points (10000 users). Inorder to scale this model, the folowing steps can be useful.

* User-Tag and SVD matrices are sparse matrices, we can use scipy's csr_matrix to convert to a dictionary of indices,values.

* The SVD calculation is done when the services are started, this is because the matrix has 10000 columns, which is over the sqlite limit. This will be an issue when scaled up.
Using a better backend would be helpful.

* While SVD itself scales considerably, using Something similar to Vector Space Model with inverted index where users and courses can be represented as vectors in a d-dimensional space can be using while scaling.

* Techniques like Approximate Nearest Neighbours, k-d tree and Locality Sensitive Hashing can also be applied which can be pretty effective in large scale environments.


