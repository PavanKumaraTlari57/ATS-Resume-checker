# # # word = "machine learning"
# # # resume_words = ["machine","python", "java"]
# # # keyword_parts = word.split()
# # # print(keyword_parts)
# # # Matched = True

# # # for keyword_part in keyword_parts:
# # #     if keyword_part not in resume_words:
# # #         Matched = False

# # # if Matched:
# # #         print(f"{word} -> Match")

# # # else:
# # #         print(f"{word} -> Mismatch")
# skills = "github"
# # skill = skills.split()
# print(skills)
# print(len(skills.split()))
# skill = "machine learning"
# print(len(skill.split()))
# if len(skill.split()) == 1:
#     print("Single word skill")
# else:
#     print("Multi-word skill")
from skills import TECHNICAL_SKILLS


jd = "Seeking a Python Developer with Machine Learning experience. Knowledge of HTML, CSS, Data Analysis, NumPy, Pandas, and GitHub is preferred"
jds = jd.lower()
print(jds)
for jd in TECHNICAL_SKILLS:
    if len(jds.split()) == 1:
        print("single")

    else:
        print("multi")
