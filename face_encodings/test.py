import pickle

with open("encodings.pickle", "rb") as f:
    encodings_dict = pickle.load(f)

print("Users in pickle file:")
for user, encodings in encodings_dict.items():
    print(f"{user}: {len(encodings)} encoding(s)")
