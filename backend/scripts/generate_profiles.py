import json
import random
from pathlib import Path


COMMUNITIES = {
    "Bengali": {
        "places": [("Kolkata", "West Bengal"), ("Siliguri", "West Bengal")],
        "languages": ["Bengali", "English", "Hindi"],
        "religions": ["Hindu", "Muslim", "Christian", "Prefer not to say"],
        "male_names": ["Aritra", "Deb", "Ishaan", "Ritwik", "Sayan", "Anik"],
        "female_names": ["Aditi", "Moumita", "Riya", "Sohini", "Ishita", "Ananya"],
        "surnames": ["Sen", "Mukherjee", "Das", "Roy", "Basu", "Chatterjee"],
    },
    "Punjabi": {
        "places": [("Chandigarh", "Chandigarh"), ("Amritsar", "Punjab")],
        "languages": ["Punjabi", "Hindi", "English"],
        "religions": ["Sikh", "Hindu", "Muslim", "Prefer not to say"],
        "male_names": ["Aman", "Arjun", "Gurpreet", "Harjit", "Jas", "Karan"],
        "female_names": ["Amrita", "Gurleen", "Jasleen", "Meher", "Navneet", "Simran"],
        "surnames": ["Gill", "Kaur", "Sandhu", "Singh", "Dhillon", "Bedi"],
    },
    "Gujarati": {
        "places": [("Ahmedabad", "Gujarat"), ("Surat", "Gujarat")],
        "languages": ["Gujarati", "Hindi", "English"],
        "religions": ["Hindu", "Jain", "Muslim", "Prefer not to say"],
        "male_names": ["Aarav", "Darsh", "Dhruv", "Harsh", "Kunal", "Mihir"],
        "female_names": ["Aashi", "Diya", "Heer", "Jhanvi", "Mira", "Riddhi"],
        "surnames": ["Mehta", "Shah", "Patel", "Desai", "Trivedi", "Joshi"],
    },
    "Tamil": {
        "places": [("Chennai", "Tamil Nadu"), ("Coimbatore", "Tamil Nadu")],
        "languages": ["Tamil", "English", "Hindi"],
        "religions": ["Hindu", "Christian", "Muslim", "Prefer not to say"],
        "male_names": ["Adithya", "Aravind", "Kavin", "Pranav", "Rohan", "Vikram"],
        "female_names": ["Ananya", "Harini", "Kavya", "Meera", "Nila", "Priya"],
        "surnames": ["Iyer", "Rajan", "Kumar", "Subramanian", "Ravi", "Pillai"],
    },
    "Telugu": {
        "places": [("Hyderabad", "Telangana"), ("Vijayawada", "Andhra Pradesh")],
        "languages": ["Telugu", "English", "Hindi"],
        "religions": ["Hindu", "Muslim", "Christian", "Prefer not to say"],
        "male_names": ["Abhinav", "Charan", "Karthik", "Nikhil", "Sai", "Teja"],
        "female_names": ["Akshara", "Bhavana", "Divya", "Keerthi", "Sahithi", "Sravya"],
        "surnames": ["Reddy", "Rao", "Naidu", "Varma", "Chowdary", "Shetty"],
    },
    "Kannada": {
        "places": [("Bengaluru", "Karnataka"), ("Mysuru", "Karnataka")],
        "languages": ["Kannada", "English", "Hindi"],
        "religions": ["Hindu", "Muslim", "Christian", "Jain", "Prefer not to say"],
        "male_names": ["Adarsh", "Arun", "Darshan", "Rohit", "Sandeep", "Yash"],
        "female_names": ["Aishwarya", "Anu", "Bhoomika", "Nandini", "Pooja", "Sneha"],
        "surnames": ["Hegde", "Rao", "Gowda", "Bhat", "Kulkarni", "Shetty"],
    },
    "Malayali": {
        "places": [("Kochi", "Kerala"), ("Thiruvananthapuram", "Kerala")],
        "languages": ["Malayalam", "English", "Hindi"],
        "religions": ["Hindu", "Muslim", "Christian", "Prefer not to say"],
        "male_names": ["Akhil", "Arun", "Dino", "Nikhil", "Rahul", "Vishnu"],
        "female_names": ["Anjali", "Diya", "Lakshmi", "Maya", "Parvathy", "Riya"],
        "surnames": ["Nair", "Menon", "Thomas", "Varghese", "Pillai", "Kurian"],
    },
    "Marathi": {
        "places": [("Mumbai", "Maharashtra"), ("Pune", "Maharashtra")],
        "languages": ["Marathi", "Hindi", "English"],
        "religions": ["Hindu", "Muslim", "Buddhist", "Jain", "Prefer not to say"],
        "male_names": ["Atharva", "Om", "Rohan", "Siddharth", "Vedant", "Vivek"],
        "female_names": ["Aarya", "Ira", "Mugdha", "Neha", "Rucha", "Vaishnavi"],
        "surnames": ["Deshmukh", "Kulkarni", "Patil", "Joshi", "More", "Pawar"],
    },
    "Assamese": {
        "places": [("Guwahati", "Assam"), ("Jorhat", "Assam")],
        "languages": ["Assamese", "English", "Hindi"],
        "religions": ["Hindu", "Muslim", "Christian", "Prefer not to say"],
        "male_names": ["Anupam", "Debojit", "Himanshu", "Kunal", "Parth", "Rishav"],
        "female_names": ["Ankita", "Barsha", "Daisy", "Junali", "Pallavi", "Rupali"],
        "surnames": ["Bora", "Das", "Gogoi", "Saikia", "Deka", "Hazarika"],
    },
    "Odia": {
        "places": [("Bhubaneswar", "Odisha"), ("Cuttack", "Odisha")],
        "languages": ["Odia", "English", "Hindi"],
        "religions": ["Hindu", "Christian", "Muslim", "Prefer not to say"],
        "male_names": ["Anubhav", "Debashish", "Ishan", "Sourav", "Suman", "Swayam"],
        "female_names": ["Ananya", "Ipsita", "Lipika", "Madhumita", "Sasmita", "Swati"],
        "surnames": ["Das", "Mishra", "Mohanty", "Nayak", "Sahu", "Patnaik"],
    },
    "Kashmiri": {
        "places": [("Srinagar", "Jammu and Kashmir"), ("Jammu", "Jammu and Kashmir")],
        "languages": ["Kashmiri", "Urdu", "Hindi", "English"],
        "religions": ["Muslim", "Hindu", "Sikh", "Prefer not to say"],
        "male_names": ["Aadil", "Amaan", "Danish", "Faris", "Irfan", "Zaid"],
        "female_names": ["Aaliya", "Hina", "Inaya", "Mahira", "Sana", "Zoya"],
        "surnames": ["Bhat", "Dar", "Lone", "Mir", "Shah", "Wani"],
    },
    "Rajasthani": {
        "places": [("Jaipur", "Rajasthan"), ("Udaipur", "Rajasthan")],
        "languages": ["Hindi", "Rajasthani", "English"],
        "religions": ["Hindu", "Jain", "Muslim", "Prefer not to say"],
        "male_names": ["Abhay", "Keshav", "Manav", "Prithvi", "Raghav", "Yuvraj"],
        "female_names": ["Avni", "Bhumika", "Kritika", "Mansi", "Nandita", "Tanya"],
        "surnames": ["Choudhary", "Jain", "Rathore", "Shekhawat", "Singh", "Sharma"],
    },
    "Bihari": {
        "places": [("Patna", "Bihar"), ("Gaya", "Bihar")],
        "languages": ["Hindi", "Bhojpuri", "English"],
        "religions": ["Hindu", "Muslim", "Christian", "Prefer not to say"],
        "male_names": ["Aditya", "Aman", "Manish", "Ravi", "Saurabh", "Vivek"],
        "female_names": ["Anushka", "Khushi", "Neelam", "Priti", "Shreya", "Sweta"],
        "surnames": ["Kumar", "Mishra", "Prasad", "Sinha", "Singh", "Verma"],
    },
    "Northeast Indian": {
        "places": [("Shillong", "Meghalaya"), ("Imphal", "Manipur")],
        "languages": ["English", "Hindi", "Khasi", "Manipuri", "Bengali"],
        "religions": ["Christian", "Hindu", "Muslim", "Buddhist", "Prefer not to say"],
        "male_names": ["Ajoy", "Bikash", "Ibungo", "Lanchenba", "Rohan", "Tashi"],
        "female_names": ["Bina", "Ima", "Lalita", "Maya", "Ritika", "Thangjam"],
        "surnames": ["Das", "Lyngdoh", "Nongrum", "Singh", "Thongam", "Zeliang"],
    },
    "Goan": {
        "places": [("Panaji", "Goa"), ("Margao", "Goa")],
        "languages": ["Konkani", "English", "Hindi", "Marathi"],
        "religions": ["Christian", "Hindu", "Muslim", "Prefer not to say"],
        "male_names": ["Aarush", "Darren", "Joel", "Neil", "Rohan", "Ryan"],
        "female_names": ["Aanya", "Alisha", "Lara", "Mira", "Natasha", "Rhea"],
        "surnames": ["D'Souza", "Fernandes", "Naik", "Pereira", "Rane", "Rodrigues"],
    },
}

PROFESSIONS = [
    "Doctor / Physician",
    "Software Engineer",
    "Civil Engineer",
    "Teacher / Educator",
    "Nurse",
    "Product Designer",
    "Lawyer",
    "Architect",
    "Data Analyst",
    "Entrepreneur",
    "Researcher",
    "Chef",
    "Financial Analyst",
    "Journalist",
    "Public Health Specialist",
    "Environmental Scientist",
    "UX Researcher",
    "Marketing Manager",
]
EDUCATION = [
    "Bachelor's degree in Computer Science",
    "Bachelor's degree in Commerce",
    "Bachelor's degree in Arts",
    "Bachelor's degree in Engineering",
    "Master's degree in Business Administration",
    "Master's degree in Public Health",
    "Master's degree in Design",
    "Master's degree in Science",
    "Bachelor of Medicine and Bachelor of Surgery",
    "Master's degree in Law",
    "Bachelor's degree in Education",
    "Master's degree in Environmental Science",
    "Bachelor's degree in Nursing",
    "Bachelor's degree in Journalism",
    "Diploma in Culinary Arts",
    "Bachelor's degree in Marketing",
    "Bachelor's degree in Psychology",
]
EDUCATION_BY_PROFESSION = {
    "Doctor / Physician": [
        "Bachelor of Medicine and Bachelor of Surgery",
        "Master's degree in Public Health",
    ],
    "Software Engineer": [
        "Bachelor's degree in Computer Science",
        "Bachelor's degree in Engineering",
        "Master's degree in Science",
    ],
    "Civil Engineer": [
        "Bachelor's degree in Engineering",
        "Master's degree in Science",
    ],
    "Teacher / Educator": [
        "Bachelor's degree in Education",
        "Bachelor's degree in Arts",
        "Master's degree in Science",
    ],
    "Nurse": [
        "Bachelor's degree in Nursing",
        "Master's degree in Public Health",
    ],
    "Product Designer": [
        "Master's degree in Design",
        "Bachelor's degree in Arts",
        "Bachelor's degree in Engineering",
    ],
    "Lawyer": ["Master's degree in Law", "Bachelor's degree in Arts"],
    "Architect": [
        "Bachelor's degree in Engineering",
        "Master's degree in Design",
    ],
    "Data Analyst": [
        "Bachelor's degree in Computer Science",
        "Bachelor's degree in Commerce",
        "Master's degree in Science",
    ],
    "Entrepreneur": [
        "Master's degree in Business Administration",
        "Bachelor's degree in Commerce",
        "Bachelor's degree in Arts",
    ],
    "Researcher": [
        "Master's degree in Science",
        "Master's degree in Public Health",
        "Master's degree in Environmental Science",
    ],
    "Chef": ["Diploma in Culinary Arts", "Bachelor's degree in Arts"],
    "Financial Analyst": [
        "Bachelor's degree in Commerce",
        "Master's degree in Business Administration",
    ],
    "Journalist": [
        "Bachelor's degree in Journalism",
        "Bachelor's degree in Arts",
    ],
    "Public Health Specialist": [
        "Master's degree in Public Health",
        "Bachelor of Medicine and Bachelor of Surgery",
    ],
    "Environmental Scientist": [
        "Master's degree in Environmental Science",
        "Master's degree in Science",
    ],
    "UX Researcher": [
        "Master's degree in Design",
        "Master's degree in Science",
        "Bachelor's degree in Psychology",
    ],
    "Marketing Manager": [
        "Bachelor's degree in Marketing",
        "Master's degree in Business Administration",
        "Bachelor's degree in Commerce",
    ],
}
INTERESTS = [
    "cooking", "classical music", "live music", "hiking", "reading", "film",
    "photography", "cricket", "badminton", "yoga", "running", "gardening",
    "travel", "history", "board games", "food markets", "volunteering",
    "painting", "technology", "dance", "birdwatching", "cycling",
]
GOALS = ["Long-term relationship", "Marriage-minded", "Committed partnership"]
BIO_TEMPLATES = [
    "A {profession_lower} who enjoys {first_interest} and {second_interest}. I value kindness, curiosity, and time with family and friends.",
    "My work as a {profession_lower} keeps me curious. Outside work, you will find me {first_interest} or exploring {second_interest}.",
    "I care about community, good conversation, and making time for {first_interest}. I also enjoy {second_interest} when I can.",
    "An optimistic {profession_lower} who likes {first_interest}, learning new things, and sharing a relaxed meal with loved ones.",
]


def build_profiles():
    rng = random.Random(20261126)
    profiles = []
    community_names = list(COMMUNITIES)
    used_names = set()

    for index in range(500):
        community_name = community_names[index % len(community_names)]
        community = COMMUNITIES[community_name]
        gender = "Female" if index % 2 else "Male"
        first_names = community["female_names"] if gender == "Female" else community["male_names"]
        name_candidates = [
            f"{first_name} {surname}"
            for first_name in first_names
            for surname in community["surnames"]
            if f"{first_name} {surname}" not in used_names
        ]
        if name_candidates:
            name = rng.choice(name_candidates)
        else:
            first_name = first_names[(index // 2) % len(first_names)]
            surname = community["surnames"][index % len(community["surnames"])]
            middle_initial = chr(ord("A") + index % 26)
            name = f"{first_name} {middle_initial}. {surname}"
            while name in used_names:
                middle_initial = chr(ord(middle_initial) + 1)
                name = f"{first_name} {middle_initial}. {surname}"
        used_names.add(name)
        community_index = index % len(community_names)
        community_round = index // len(community_names)
        profession_index = community_round % len(PROFESSIONS)
        place_index = (community_round // len(PROFESSIONS)) % len(community["places"])
        city, region = community["places"][place_index]
        age = 21 + (
            community_index * 5 + profession_index * 7 + place_index * 11 + 8
        ) % 25
        profession = PROFESSIONS[profession_index]
        interests = rng.sample(INTERESTS, 4)
        preferred_age_min = max(21, age - rng.randint(2, 5))
        preferred_age_max = min(45, age + rng.randint(2, 5))
        religion = rng.choice(community["religions"])
        profile = {
            "id": f"profile-{index + 1:04d}",
            "name": name,
            "gender": gender,
            "age": age,
            "city": city,
            "region": region,
            "culture_community": community_name,
            "languages": rng.sample(community["languages"], k=min(3, len(community["languages"]))),
            "religion": religion,
            "profession": profession,
            "education": rng.choice(EDUCATION_BY_PROFESSION.get(profession, EDUCATION)),
            "interests": interests,
            "short_bio": rng.choice(BIO_TEMPLATES).format(
                profession_lower=profession.lower(),
                first_interest=interests[0],
                second_interest=interests[1],
            ),
            "relationship_preferences": {
                "relationship_goal": rng.choice(GOALS),
                "preferred_age_range": {
                    "min": preferred_age_min,
                    "max": preferred_age_max,
                },
            },
        }
        profiles.append(profile)

    return profiles


def main():
    output_path = Path(__file__).resolve().parents[1] / "app" / "data" / "profiles.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataset = {
        "dataset_name": "Synthetic Matchmaking Profiles",
        "synthetic": True,
        "profile_count": 500,
        "age_range": {"min": 21, "max": 45},
        "profiles": build_profiles(),
    }
    output_path.write_text(json.dumps(dataset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(dataset['profiles'])} synthetic profiles to {output_path}")


if __name__ == "__main__":
    main()
